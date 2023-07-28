from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, Customers
from django.conf import settings

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_customer(sender, instance, created, **kwargs):
    if created:
        Customers.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_customer(sender, instance, **kwargs):
    instance.customer.save()