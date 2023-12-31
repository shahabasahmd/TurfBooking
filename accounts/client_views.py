from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import *
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth import update_session_auth_hash,authenticate
from datetime import datetime, timedelta
from django.core.paginator import Paginator
from django.db.models import Sum,Count
from django.db.models.functions import TruncMonth
from decimal import Decimal
import json
from django.views.decorators.cache import never_cache

@login_required
def success_page_client(request):
    return render(request,'client/clientinclude/success_client.html')


@never_cache
@login_required
def client_dashboard(request):
    user = request.user
    total_turfs = TurfDetails.objects.filter(added_by=user).count()
    total_grounds = Ground.objects.filter(turf__added_by=user).count()
    total_profit = Bookings.objects.filter(turf_added_by=user, payment_status='completed').aggregate(total_profit=Sum('amount_to_client'))['total_profit'] or Decimal('0.00')
    total_pending_transactions = Bookings.objects.filter(turf_added_by=user, payment_status='pending').count()
    
    
    monthly_profit_data = Bookings.objects.filter(
        turf_added_by=user,
        payment_status='completed',
    ).annotate(
        month=TruncMonth('timestamp')
    ).values(
        'month'
    ).annotate(
        total_profit=Sum('amount_to_client')
    ).order_by('month')

   
    monthly_booking_data = Bookings.objects.filter(
        turf_added_by=user,
    ).annotate(
        month=TruncMonth('timestamp')
    ).values(
        'month'
    ).annotate(
        total_bookings=Count('id')
    ).order_by('month')

   
    profit_labels = [entry['month'].strftime('%b %Y') for entry in monthly_profit_data]
    profit_values = [float(entry['total_profit'] or 0) for entry in monthly_profit_data]

    booking_labels = [entry['month'].strftime('%b %Y') for entry in monthly_booking_data]
    booking_values = [entry['total_bookings'] for entry in monthly_booking_data]

    context = {
        'total_turfs': total_turfs,
        'total_grounds': total_grounds,
        'total_profit': float(total_profit),  
        'total_pending_transactions': total_pending_transactions,
        'profit_labels': json.dumps(profit_labels),
        'profit_values': json.dumps(profit_values),
        'booking_labels': json.dumps(booking_labels),
        'booking_values': json.dumps(booking_values),
    }
    return render(request, 'client/client_dashboard.html', context)



@login_required(login_url='/')
def clienthome(request ):
    user = request.user
    client = Clients.objects.filter(admin=user).first()
    return render(request, 'client/clienthome.html', {'client': client})


@login_required
def edit_profile(request):
    client = get_object_or_404(Clients, admin=request.user)
    context = {
        'client': client,
    }

    return render(request, 'client/edit_profile.html', context)


@login_required
def update_profile(request):
    if request.method == 'POST':
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')
        account_details = request.POST.get('account_details')
        upi_num_or_id = request.POST.get('upi')

        
        user = request.user

        
        if user.is_authenticated :
            client = Clients.objects.get(admin=user)
            client.mobile = mobile
            client.address = address
            client.account_details = account_details
            client.upi_num_or_id = upi_num_or_id
            client.save()
            messages.success(request, 'Your personal details have been updated successfully.')
            return redirect('success_page_client') 
        else:
            messages.error(request, 'You do not have permission to perform this action.')
    else:
        pass

    return render(request, 'client/edit_profile.html')


@login_required
def change_password_view(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        
        user = request.user
        if user.check_password(current_password):
            
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)  
            messages.success(request, 'Your password has been changed successfully.')
            return redirect('success_page_client')  
        else:
            messages.error(request, 'Invalid current password. Please try again.')

    return render(request, 'client/clienthome.html')




@login_required
def customer_list_client(request):
    customers = Customers.objects.all()
    return render(request, 'client/customer_list_client.html', {'customers': customers})

@login_required
def delete_customer_client(request, customer_id):
    customer = get_object_or_404(Customers, id=customer_id)
    user = customer.admin
    customer.delete()
    user.delete()
    return redirect('customer_list_admin')


@login_required
def add_turf_client(request):
    places = Places.objects.all()
    return render(request, 'client/addturf_client.html', {'places': places})


  
@login_required
def add_turf_save_client(request):
    if request.method == 'POST':
        turf_name = request.POST.get('turf_name')
        place_name = request.POST.get('place') 
        phone = request.POST.get('mobile')
        cafe = request.POST.get('cafe')
        first_aid = request.POST.get('firstaid')
        locker = request.POST.get('locker')
        parking = request.POST.get('parking')
        shower = request.POST.get('shower')
        image = request.FILES.get('turf_image')

        try:
            place = Places.objects.get(place=place_name)
        except Places.DoesNotExist:
            place = None
        
        if place is not None:
            turf = TurfDetails.objects.create(
                added_by=request.user,  
                turf_name=turf_name,
                place=place,
                phone=phone,
                cafe=(cafe == 'cafe_yes'),
                first_aid=(first_aid == 'firstaid_yes'),
                locker=(locker == 'locker_yes'),
                parking=(parking == 'parking_yes'),
                shower=(shower == 'shower_yes'),
                image=image,
            )
        return redirect('success_page_client') 

    else:
        return render(request, 'client/addturf_client.html')



@login_required
def client_turf_list(request):
    user = request.user
    turf_details = TurfDetails.objects.filter(added_by=user)
    return render(request, 'client/list_turf_client.html', {'turf_details': turf_details})


@login_required
def add_ground_client(request):
    user = request.user
    turf_names = TurfDetails.objects.filter(added_by=user).values('id', 'turf_name')

    return render(request, 'client/add_ground_client.html', {'turfs': turf_names})


@login_required
def save_ground_client(request):
    if request.method == 'POST':
        turf_id = request.POST.get('turf')
        category = request.POST.get('category')
        ground_name = request.POST.get('ground_name')
        price = request.POST.get('price')
        
        
        ground = Ground(
            turf_id=turf_id,
            category=category,
            ground_name=ground_name,
            price=price,
            
            
        )
        ground.save()
        return redirect('success_page_client')  

    else:
        turfs = TurfDetails.objects.filter(added_by=request.user)
        return render(request, 'client/add_ground_client.html', {'turfs': turfs})


@login_required
def ground_list_by_turf(request, turf_id):
    grounds = Ground.objects.filter(turf_id=turf_id)
    return render(request, 'client/list_ground_client.html', {'grounds': grounds})



@login_required
def delete_ground(request, ground_id):
    
    try:
        ground = Ground.objects.get(id=ground_id)
    except Ground.DoesNotExist:
        return redirect('ground_list_by_turf')  

    
    if ground.turf.added_by == request.user:
        ground.delete()
    
    turf_id = ground.turf.id
    return redirect('ground_list_by_turf', turf_id=turf_id)

@login_required
def delete_turf_confirmation_page(request, turf_id):  
    turf = get_object_or_404(TurfDetails, id=turf_id, added_by=request.user)
    return render(request, 'client/delete_turf_confirmation.html', {'turf': turf})

@login_required
def delete_turf_confirmation(request, turf_id):
    turf = get_object_or_404(TurfDetails, id=turf_id, added_by=request.user)

    if request.method == 'POST':
        turf.delete()
        return redirect('client_turf_list')  
    
    return render(request, 'client/delete_turf_confirmation.html', {'turf': turf})
    


@login_required
def client_turf_list_timeslot(request):
    turfs = TurfDetails.objects.filter(added_by=request.user)
    context = {
        'turfs': turfs,
    }

    return render(request, 'client/timeslotpage_client.html', context)

  



    
@login_required
def add_time_slot_client(request):
    if request.method == 'POST':
        turf_id = request.POST.get('turf_name')
        ground_id = request.POST.get('ground_name')
        match_duration = float(request.POST.get('match_duration'))
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        date_from = datetime.strptime(request.POST.get('date_from'), '%Y-%m-%d')
        date_to = datetime.strptime(request.POST.get('date_to'), '%Y-%m-%d')

       
        start_datetime = datetime.strptime(start_time, '%H:%M')
        end_datetime = datetime.strptime(end_time, '%H:%M')

       
        time_slot_count = int((end_datetime - start_datetime).seconds / (match_duration * 3600))

        
        num_days = (date_to - date_from).days + 1
        
        # Save the time slots for each day within the date range
        for _ in range(num_days):
            current_datetime = start_datetime  # Reset for each new day
            for i in range(time_slot_count):
                TimeSlot.objects.create(
                    added_by=request.user,
                    ground_id=ground_id,
                    date=date_from.date(),
                    start_time=current_datetime.time(),
                    end_time=(current_datetime + timedelta(hours=match_duration)).time()
                )
                current_datetime += timedelta(hours=match_duration)
                
            # Move to the next day and reset start_datetime
            date_from += timedelta(days=1)
            start_datetime = datetime.strptime(start_time, '%H:%M')
        return redirect('success_page_client')
    return render(request, 'client/timeslotpage_client.html', context={})



@login_required
def turf_list_timeslot(request):
    turf = TurfDetails.objects.filter(added_by=request.user)
    return render(request, 'client/turflist_timeslot_client.html', {'turfs': turf})



@login_required
def ground_list(request, turf_id):
    turf = get_object_or_404(TurfDetails, id=turf_id)
    grounds = Ground.objects.filter(turf=turf)
    return render(request, 'client/groundlist_timeslot_client.html', {'turf': turf, 'grounds': grounds})



@login_required
def timeslot_list(request, ground_id):
    ground = get_object_or_404(Ground, id=ground_id)
    all_timeslots = TimeSlot.objects.filter(ground=ground)
    items_per_page = 20
    paginator = Paginator(all_timeslots, items_per_page)
    page_number = request.GET.get('page')
    timeslots = paginator.get_page(page_number)
    
    return render(request, 'client/list_timeslot_client.html', {'ground': ground, 'timeslots': timeslots})


@login_required
def delete_timeslot_client(request, timeslot_id):
    timeslot = get_object_or_404(TimeSlot, pk=timeslot_id)
    ground_id = timeslot.ground.id  

    if request.method == 'POST':
        timeslot.delete()
        return redirect('timeslot_list_client', ground_id=ground_id)
    
    return render(request, 'client/list_timeslot_client.html', {'timeslot': timeslot})




@login_required
def turf_list_reservation(request):
    t = TurfDetails.objects.filter(added_by=request.user)
    return render(request, 'client/turflist_reservation_client.html', {'turfs': t})



@login_required
def ground_list_reservation(request,turf_id):
    turf = get_object_or_404(TurfDetails, id=turf_id)
    grounds = Ground.objects.filter(turf=turf)
    return render(request, 'client/groundlist_reservation_client.html', {'turf': turf, 'grounds': grounds})



@login_required
def select_date_and_reservations(request, ground_id):
    selected_date = request.GET.get('selected_date')

    if selected_date:
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
    ground = get_object_or_404(Ground, id=ground_id)
    reservations = Reservation.objects.filter(ground=ground, time_slot__date=selected_date) if selected_date else []
    return render(request, 'client/ground_reservation_details_client.html', {'ground': ground, 'selected_date': selected_date, 'reservations': reservations})



@login_required
def bookings_client(request):
    logged_in_client = request.user 
    client_bookings = Bookings.objects.filter(turf_added_by=logged_in_client)
    
    context = {
        'client_bookings': client_bookings,
    }
    return render(request, 'client/bookings_client.html', context)



@login_required
def paymentlist_client(request):
    logged_in_client = request.user  
    client = Clients.objects.get(admin=logged_in_client) 
    client_bookings = Bookings.objects.filter(turf_added_by=logged_in_client)
    
    # Calculate the client's amount for each booking
    for booking in client_bookings:
        commission_percentage = client.commission_percentage
        commission = (commission_percentage / 100) * booking.amount
        amount_to_client = booking.amount - commission
        booking.amount_to_client = amount_to_client
    
    context = {
        'client_bookings': client_bookings,
    }
    return render(request, 'client/payment_list_client.html', context)


@login_required
def payment_history(request):
    client_bookings = Bookings.objects.filter(turf_added_by=request.user)
    context = {'client_bookings': client_bookings}
    return render(request, 'client/payment_list_client.html', context)



@login_required
def pending_payments(request):
    client_bookings = Bookings.objects.filter(turf_added_by=request.user, payment_status='pending')
    context = {'client_bookings': client_bookings}
    return render(request, 'client/payment_list_client.html', context)



@login_required
def completed_payments(request):
    client_bookings = Bookings.objects.filter(turf_added_by=request.user, payment_status='completed')
    context = {'client_bookings': client_bookings}
    return render(request, 'client/payment_list_client.html', context)








