from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone







# Create your models here.
class CustomUser(AbstractUser):
    user_type_data=((1,"ADMIN"),(2,"CLIENT"),(3,"USER"))
    user_type=models.CharField(default=1,choices=user_type_data,max_length=10)
    is_blocked = models.BooleanField(default=False)
    
    
class Clients(models.Model):
    id=models.AutoField(primary_key=True)
    admin=models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    mobile = models.CharField(max_length=20,default='')
    address=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    commission_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.0,
        help_text="Commission percentage for bookings (e.g., 10.00 for 10%)"
    )
    account_details=models.CharField(max_length=100,null=True)
    upi_num_or_id=models.CharField(max_length=50,null=True)
    objects=models.Manager()
    def __str__(self):
        return f"Client ID: {self.id}, Username: {self.admin.username if self.admin else None}"


    
class Customers(models.Model):
    id=models.AutoField(primary_key=True)
    admin=models.OneToOneField(get_user_model(),on_delete=models.CASCADE)
    mobile = models.CharField(max_length=20,default='')
    address=models.TextField(null=True)


    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
    
    def __str__(self):
        return self.user.username
    

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.user_type == 2:  # Check if the user is of type CLIENT
        Clients.objects.create(admin=instance, address="", mobile="")
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         if instance.user_type == 1:
#             MainAdmin.objects.create(admin=instance)
#         elif instance.user_type == 2:
#             address = ""  
#             mobile = ""  
#             Clients.objects.create(admin=instance, address=address, mobile=mobile)
#         elif instance.user_type == 3:
#             Customers.objects.create(admin=instance, address="",mobile="")

# @receiver(post_save, sender=CustomUser)
# def save_user_profile(sender, instance, **kwargs):
#     if instance.user_type == 1:
#         instance.mainadmin.save()
#     elif instance.user_type == 2:
#         if hasattr(instance, 'clients'):
#             instance.clients.address = instance.clients.address
#             instance.clients.mobile = instance.clients.mobile
#             instance.clients.save()
#     elif instance.user_type == 3:
#         instance.customers.save()

class Places(models.Model):
    place=models.CharField(max_length = 100, null=True)

class TurfDetails(models.Model):
    turf_name = models.CharField(max_length = 100, null=True)
    added_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='uploaded_turfs')
    place = models.ForeignKey(Places, on_delete=models.CASCADE, null=True)
    phone = models.CharField(max_length=15,null=True,default=0) 
    image = models.ImageField(upload_to='turf_images/', null=True, blank=True)
    cafe = models.BooleanField(default=False, null=True)
    first_aid = models.BooleanField(default=False, null=True)
    locker = models.BooleanField(default=False, null=True)
    parking = models.BooleanField(default=False, null=True)
    shower = models.BooleanField(default=False, null=True)
    def __str__(self):
        return self.turf_name
    
class Ground(models.Model):
    turf = models.ForeignKey(TurfDetails, on_delete=models.CASCADE)
    category = models.CharField(max_length=100)  
    ground_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return self.ground_name


class TimeSlot(models.Model):
    added_by=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    ground = models.ForeignKey(Ground, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.ground.turf.turf_name} - {self.ground.ground_name} - {self.start_time} to {self.end_time}"



User = get_user_model()
class Reservation(models.Model):
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE)
    ground = models.ForeignKey(Ground, on_delete=models.CASCADE)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    reservation_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.user.username} - {self.turf.name} - {self.reservation_date}"
    

class Bookings(models.Model):
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE)
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    razorpay_payment_id = models.CharField(max_length=100, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    turf_added_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    PAYMENT_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    )
    payment_status = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='Pending')
    payment_status_timestamp = models.DateTimeField(null=True, blank=True)
    commission = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    amount_to_client = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    
    def save(self, *args, **kwargs):
        # Check if the payment_status field is changing
        if self._state.adding or self.payment_status != self._original_payment_status:
            # If it's changing, update the payment_status_timestamp field
            self.payment_status_timestamp = timezone.now()
        super().save(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_payment_status = self.payment_status

       
    



class Enquiry(models.Model):
    name=models.CharField(max_length=50,null=True)
    place=models.CharField(max_length=50,null=True)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    message = models.TextField()
    timestamp_enquiry = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.email  