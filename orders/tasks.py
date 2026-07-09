from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

from orders.models import Order


@shared_task(bind=True, max_retries=3)
def send_order_confirmation_task(self, order_id):
    try:
        order = Order.objects.select_related("user").prefetch_related("items").get(id=order_id)
    except Order.DoesNotExist:
        return {"status": "skipped", "reason": "order_not_found", "order_id": order_id}

    subject = f"Order Confirmation - {order.order_number}"

    item_lines = []
    for item in order.items.all():
        item_lines.append(
            f"- {item.product_name} x {item.quantity}: ${item.line_total}"
        )

    message = f"""
Hi {order.user.first_name or order.user.username},

Your order has been created successfully.

Order Number: {order.order_number}
Status: {order.status}
Subtotal: ${order.subtotal_amount}
Tax: ${order.tax_amount}
Shipping: ${order.shipping_fee}
Total: ${order.total_amount}

Items:
{chr(10).join(item_lines)}

Thank you for shopping with us.
"""

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.user.email],
        fail_silently=False,
    )

    return {
        "status": "sent",
        "order_id": order.id,
        "order_number": order.order_number,
        "recipient": order.user.email,
    }
