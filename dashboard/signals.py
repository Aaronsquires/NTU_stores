from django.db.models import signals
from django.dispatch import receiver

from .models import Purchase


@receiver(signals.post_delete, sender=Purchase)
def increment_product_quantity(sender, instance, **kwargs):
    instance.product.quantity += instance.quantity
    instance.product.save()


@receiver(signals.post_save, sender=Purchase)
def update_product_quantity(sender, instance, created, **kwargs):
    if created:
        instance.product.quantity -= instance.quantity
        instance.product.save()
