from django.conf import settings
from django.db import transaction
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import Order
from .models import Payment, PaymentEvent
from .serializers import (
    FakeWebhookSerializer,
    PaymentInitiateSerializer,
    PaymentSerializer,
)
from .services import FakePaymentProvider
from .tasks import send_payment_receipt_task


def apply_payment_status(payment, new_status, message="", response_payload=None):
    order = payment.order

    payment.status = new_status
    payment.failure_reason = "" if new_status == Payment.Status.SUCCEEDED else message
    if response_payload is not None:
        payment.response_payload = response_payload

    payment.save(update_fields=[
        "status",
        "failure_reason",
        "response_payload",
        "updated_at",
    ])

    if new_status == Payment.Status.SUCCEEDED:
        order.status = Order.Status.PAID
        order.save(update_fields=["status", "updated_at"])
        transaction.on_commit(lambda: send_payment_receipt_task.delay(payment.id))

    elif new_status in [Payment.Status.FAILED, Payment.Status.TIMEOUT]:
        order.status = Order.Status.PAYMENT_FAILED
        order.save(update_fields=["status", "updated_at"])


class InitiatePaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = PaymentInitiateSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        order = (
            Order.objects
            .select_for_update()
            .get(id=serializer.validated_data["order"].id)
        )

        idempotency_key = serializer.validated_data["idempotency_key"]

        existing_payment = (
            Payment.objects
            .select_related("order", "user")
            .prefetch_related("events")
            .filter(idempotency_key=idempotency_key)
            .first()
        )

        if existing_payment:
            return Response(
                PaymentSerializer(existing_payment).data,
                status=status.HTTP_200_OK,
            )

        payment = Payment.objects.create(
            order=order,
            user=order.user,
            provider=Payment.Provider.FAKE,
            status=Payment.Status.PROCESSING,
            amount=order.total_amount,
            currency="USD",
            idempotency_key=idempotency_key,
            request_payload={
                "order_id": order.id,
                "order_number": order.order_number,
                "amount": str(order.total_amount),
                "force_outcome": serializer.validated_data.get("force_outcome"),
            },
        )

        PaymentEvent.objects.create(
            payment=payment,
            event_type="payment.initiated",
            payload={
                "status": payment.status,
                "amount": str(payment.amount),
                "currency": payment.currency,
            },
        )

        provider_response = FakePaymentProvider.process(
            payment,
            force_outcome=serializer.validated_data.get("force_outcome"),
        )

        payment.provider_reference = provider_response["provider_reference"]
        payment.response_payload = provider_response
        payment.save(update_fields=["provider_reference", "response_payload", "updated_at"])

        PaymentEvent.objects.create(
            payment=payment,
            event_type=f"payment.{provider_response['status'].lower()}",
            payload=provider_response,
        )

        apply_payment_status(
            payment=payment,
            new_status=provider_response["status"],
            message=provider_response["message"],
            response_payload=provider_response,
        )

        payment = (
            Payment.objects
            .select_related("order", "user")
            .prefetch_related("events")
            .get(id=payment.id)
        )

        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)


class PaymentListView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        queryset = (
            Payment.objects
            .select_related("order", "user")
            .prefetch_related("events")
        )

        if user.role in ["ADMIN", "SUPPORT"]:
            return queryset

        return queryset.filter(user=user)


class PaymentDetailView(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        queryset = (
            Payment.objects
            .select_related("order", "user")
            .prefetch_related("events")
        )

        if user.role in ["ADMIN", "SUPPORT"]:
            return queryset

        return queryset.filter(user=user)


class FakeWebhookView(APIView):
    permission_classes = [permissions.AllowAny]

    @transaction.atomic
    def post(self, request):
        secret = request.headers.get("X-Fake-Webhook-Secret")

        if secret != settings.FAKE_WEBHOOK_SECRET:
            return Response(
                {"detail": "Invalid webhook secret."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = FakeWebhookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            payment = (
                Payment.objects
                .select_for_update()
                .select_related("order", "user")
                .get(payment_number=serializer.validated_data["payment_number"])
            )
        except Payment.DoesNotExist:
            return Response(
                {"detail": "Payment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        new_status = serializer.validated_data["status"]
        event_type = serializer.validated_data.get("event_type") or f"webhook.payment.{new_status.lower()}"
        message = serializer.validated_data.get("message") or f"Webhook updated payment to {new_status}"

        payload = {
            "payment_number": payment.payment_number,
            "status": new_status,
            "message": message,
        }

        PaymentEvent.objects.create(
            payment=payment,
            event_type=event_type,
            payload=payload,
        )

        apply_payment_status(
            payment=payment,
            new_status=new_status,
            message=message,
            response_payload=payload,
        )

        return Response(
            {
                "message": "Webhook processed successfully.",
                "payment_number": payment.payment_number,
                "status": payment.status,
                "order_status": payment.order.status,
            },
            status=status.HTTP_200_OK,
        )
