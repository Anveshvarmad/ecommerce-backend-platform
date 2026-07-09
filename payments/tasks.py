from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

from payments.models import Payment


@shared_task(bind=True, max_retries=3)
def send_payment_receipt_task(self, payment_id):
    try:
        payment = (
            Payment.objects
            .select_related("user", "order")
            .get(id=payment_id)
        )
    except Payment.DoesNotExist:
        return {"status": "skipped", "reason": "payment_not_found", "payment_id": payment_id}

    if payment.status != Payment.Status.SUCCEEDED:
        return {
            "status": "skipped",
            "reason": "payment_not_succeeded",
            "payment_id": payment.id,
            "payment_status": payment.status,
        }

    subject = f"Payment Receipt - {payment.payment_number}"

    message = f"""
Hi {payment.user.first_name or payment.user.username},

Your payment was successful.

Payment Number: {payment.payment_number}
Order Number: {payment.order.order_number}
Amount: ${payment.amount} {payment.currency}
Status: {payment.status}
Provider: {payment.provider}

Thank you.
"""

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[payment.user.email],
        fail_silently=False,
    )

    return {
        "status": "sent",
        "payment_id": payment.id,
        "payment_number": payment.payment_number,
        "recipient": payment.user.email,
    }
