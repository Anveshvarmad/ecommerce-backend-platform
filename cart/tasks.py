from celery import shared_task
from django.utils import timezone

from datetime import timedelta

from cart.models import Cart


@shared_task
def cleanup_abandoned_carts_task(days_old=7):
    cutoff = timezone.now() - timedelta(days=days_old)

    updated_count = (
        Cart.objects
        .filter(
            status=Cart.Status.ACTIVE,
            updated_at__lt=cutoff,
        )
        .update(status=Cart.Status.ABANDONED)
    )

    return {
        "status": "completed",
        "abandoned_carts": updated_count,
        "days_old": days_old,
    }
