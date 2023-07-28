from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin

from accounts.models import *


class UserModel(UserAdmin):
    pass

admin.site.register(CustomUser,UserModel)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'user_type')

admin.site.register( Clients)
admin.site.register(Customers)
admin.site.register(TurfDetails)
# admin.site.register(TimeSlot)

class ReservationAdmin(admin.ModelAdmin):
    list_display = ('customer', 'date', 'start_time', 'end_time', 'turf_name')
    list_filter = ('turf', 'time_slot__start_time')
    
    def date(self, obj):
        return obj.time_slot.start_time.date()

    def start_time(self, obj):
        return obj.time_slot.start_time.time()

    def end_time(self, obj):
        return obj.time_slot.end_time.time()

    def turf_name(self, obj):
        return obj.turf.name

    date.admin_order_field = 'time_slot__start_time'
    start_time.admin_order_field = 'time_slot__start_time'
    end_time.admin_order_field = 'time_slot__end_time'
    turf_name.admin_order_field = 'turf__name'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        selected_date = request.GET.get('date')  # Date filter value from admin panel
        
        if selected_date:
            queryset = queryset.filter(time_slot__start_time__date=selected_date)

        return queryset

admin.site.register(TimeSlot)    

# admin.site.register(Reservation, ReservationAdmin)