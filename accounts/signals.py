from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, Customers
from django.conf import settings


# @receiver(post_save, sender=CustomUser)
# def save_customer(sender, instance, **kwargs):
#     # Check if the user has a related customer instance
#     try:
#         customer = instance.customer
#     except Customers.DoesNotExist:
#         # If the customer does not exist, create a new one
#         customer = Customers.objects.create(user=instance)
#     # Update any relevant fields in the customer model based on the user data
#     customer.save()