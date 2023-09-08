from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import *
from django.contrib import messages
from django.http import HttpResponse,JsonResponse
from django.urls import reverse
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
from django.core.paginator import Paginator
from django.db.models import Sum
from django.db.models.functions import ExtractMonth

def success_page(request):
    return render(request,'admin/admininclude/success_admin.html')



@login_required
def dashboard(request):
    customer_count = Customers.objects.count()
    clients_count = Clients.objects.count()
    grounds_count = Ground.objects.count()

    
    total_booking_amount = Bookings.objects.filter(turf_added_by=request.user).aggregate(Sum('amount'))['amount__sum'] or 0
    total_commission = Bookings.objects.aggregate(Sum('commission'))['commission__sum'] or 0
    total_profit = total_booking_amount + total_commission

    revenue_data = Bookings.objects.filter(
        turf_added_by=request.user,
        payment_status='completed'
    ).annotate(
        month=ExtractMonth('timestamp')
    ).values('month').annotate(
        monthly_revenue=Sum('amount')
    ).order_by('month').values_list('monthly_revenue', flat=True)

    
    bookings_data = Bookings.objects.annotate(
    month=ExtractMonth('timestamp')
    ).values('month').annotate(
    monthly_bookings=Sum(1)
    ).order_by('month').values_list('monthly_bookings', flat=True)

    context = {
        'customer_count': customer_count,
        'clients_count': clients_count,
        'grounds_count': grounds_count,
        'total_profit': total_profit,
          'revenue_data': list(revenue_data),
        'bookings_data': list(bookings_data),
    }
    return render(request, 'admin/admin_dashboard.html', context)

@login_required(login_url='/')
def adminhome(request):
    client=Clients.objects.all()
    context={
        'client':client,
    }
    return render( request,'admin/adminhome.html',context)

@login_required
def add_client(request):
    return render(request,"admin/addclient.html")


def customer_list_admin(request):
    customers = Customers.objects.all()
    context = {
        'customers': customers
    }
    return render(request, 'admin/customer_list_admin.html', context)

@login_required
def delete_customer_admin(request, customer_id):
    customer = get_object_or_404(Customers, id=customer_id)
    user = customer.admin
    customer.delete()
    user.delete()
    return redirect('customer_list_admin')



@login_required
def add_client_save(request):
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    else:
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        address = request.POST.get("address")
        mobile = request.POST.get("mobile")
        commission_percentage = request.POST.get("commission_percentage")
        account_details = request.POST.get("account_details")
        upi_num_or_id = request.POST.get("upi") 

        if CustomUser.objects.filter(email=email).exists():
            messages.warning(request, "Email already taken")
            return redirect('addclient')
        elif CustomUser.objects.filter(username=username).exists():
            messages.warning(request, "Username already taken")
            return redirect('addclient')
        else:
            user = CustomUser.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password,
                user_type=2
            )

            
            client = Clients.objects.filter(admin=user).first()
            if client:
                client.address = address
                client.mobile = mobile
                client.commission_percentage = commission_percentage
                client.account_details = account_details
                client.upi_num_or_id = upi_num_or_id  
                client.save()
            else:
                client = Clients.objects.create(
                    admin=user,
                    address=address,
                    mobile=mobile,
                    commission_percentage=commission_percentage,
                    account_details=account_details,
                    upi_num_or_id=upi_num_or_id 
                )

            return redirect('success_page_admin')

@login_required
def delete_client(request, id):
    client = get_object_or_404(CustomUser, id=id)
    client.delete()
    messages.success(request, "Selected client deleted successfully")
    return redirect('adminhome')


@login_required
def block_client(request, user_id):
    client = get_object_or_404(CustomUser, id=user_id)
    client.is_blocked = True
    client.save()
    messages.success(request, f"{client.username} has been blocked.")
    return redirect('adminhome')



@login_required
def unblock_client(request, user_id):
    client = get_object_or_404(CustomUser, id=user_id)
    client.is_blocked = False
    client.save()
    messages.success(request, f"{client.username} has been unblocked.")
    return redirect('adminhome')



@login_required
def blocked_clients(request):
    blocked_clients = CustomUser.objects.filter(is_blocked=True)
    context = {
        'blocked_clients': blocked_clients
    }
    return render(request, 'admin/blocked_clients.html', context)


def add_place(request):
    if request.method == 'POST':
        place_name = request.POST['place_name']
        Places.objects.create(place=place_name)

    all_places = Places.objects.all()
    places_per_page = 20
    paginator = Paginator(all_places, places_per_page)
    page_number = request.GET.get('page')
    places = paginator.get_page(page_number)
    return render(request, 'admin/addplace.html', {'places': places})

def delete_place(request, place_id):
    try:
        place = Places.objects.get(id=place_id)
        place.delete()
    except Places.DoesNotExist:
        pass
    
    return redirect('add_place')


@login_required
def add_turf(request):
    places_list = Places.objects.all() 
    context = {
        'places': places_list
    }
    return render(request, 'admin/addturf.html', context)


@login_required(login_url='/')
def add_turf_save(request):
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

            return redirect('success_page_admin') 
        else:
            messages.error(request, 'Invalid place name. Please select a valid place.')
            return render(request, 'admin/addturf.html')

    else:
        return render(request, 'admin/addturf.html')




@login_required
def list_turf_details(request):
    turfs = TurfDetails.objects.all()
    return render(request, 'admin/list_turf_details.html', {'turfs': turfs})      



@login_required
def add_ground_page(request):
    turfs = TurfDetails.objects.all()
    return render(request, 'admin/add_ground_admin.html', {'turfs': turfs})




@login_required
def add_ground_page_admin(request):
    if request.method == 'POST':
        turf_id = request.POST['turf']
        category = request.POST['category']
        ground_name = request.POST['ground_name']
        price = request.POST['price']
        
        ground = Ground(turf_id=turf_id, category=category, ground_name=ground_name, price=price)
        ground.save()
        return redirect('success_page_admin')  
    
    return render(request, 'admin/add_ground_page_admin.html', {'turfs': TurfDetails.objects.all()})




@login_required
def ground_details_page(request, turf_id):
    turf = get_object_or_404(TurfDetails, id=turf_id)
    grounds = Ground.objects.filter(turf=turf)

    return render(request, 'admin/ground_list_admin.html', {'turf': turf, 'grounds': grounds})


@login_required
def delete_ground(request, ground_id):
    ground = get_object_or_404(Ground, id=ground_id)
    if request.method == 'POST':
        ground.delete()

    return redirect('ground_details_page', turf_id=ground.turf.id)



@login_required
def delete_turf_admin(request, turf_id):
    print("Turf ID to delete:", turf_id)

    try:
        turf = TurfDetails.objects.get(pk=turf_id)
        turf.delete()
    except TurfDetails.DoesNotExist:
        pass

    return redirect('list_turf_details')


def add_time_slot(request):
    turfs = TurfDetails.objects.all()
    context = {
        'turfs': turfs,
    }
    return render(request, 'admin/timeslot_admin.html', context)




def get_ground_names(request, turf_id):
    try:
        turf = TurfDetails.objects.get(pk=turf_id)
        grounds = Ground.objects.filter(turf=turf)
        ground_names = [{'id': ground.id, 'ground_name': ground.ground_name} for ground in grounds]
        return JsonResponse({'grounds': ground_names})
    except TurfDetails.DoesNotExist:
        return JsonResponse({'grounds': []})
    
    
@login_required
def add_time_slot_admin(request):
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

        # Calculate the number of time slots to create
        time_slot_count = int((end_datetime - start_datetime).seconds / (match_duration * 3600))

        # Calculate the number of days in the date range
        num_days = (date_to - date_from).days + 1
        
        
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

        return redirect('success_page_admin')

    return render(request, 'admin/timeslot_admin.html', context={})



@login_required
def turf_list_timeslot(request):
    t = TurfDetails.objects.all()
    return render(request, 'admin/turflist_timeslot_admin.html', {'turfs': t})



@login_required
def ground_list(request, turf_id):
    turf = get_object_or_404(TurfDetails, id=turf_id)
    grounds = Ground.objects.filter(turf=turf)
    return render(request, 'admin/groundlist_timeslot_admin.html', {'turf': turf, 'grounds': grounds})



@login_required
def timeslot_list(request, ground_id):
    ground = get_object_or_404(Ground, id=ground_id)
    timeslots = TimeSlot.objects.filter(ground=ground)

    items_per_page = 20
    paginator = Paginator(timeslots, items_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'admin/list_timeslot_admin.html', {'ground': ground, 'page_obj': page_obj})



@login_required
def delete_timeslot_admin(request, timeslot_id):
    timeslot = get_object_or_404(TimeSlot, pk=timeslot_id)
    ground_id = timeslot.ground.id 

    if request.method == 'POST':
        timeslot.delete()
        return redirect('timeslot_list_admin', ground_id=ground_id)
    
    return render(request, 'admin/list_timeslot_admin.html', {'timeslot': timeslot})



@login_required
def block_timeslot(request, timeslot_id):
    timeslot = get_object_or_404(TimeSlot, id=timeslot_id)
    timeslot.is_available = False
    timeslot.save()
    return redirect('timeslot_list_admin', ground_id=timeslot.ground.id)



@login_required
def unblock_timeslot(request, timeslot_id):
    timeslot = get_object_or_404(TimeSlot, id=timeslot_id)
    timeslot.is_available = True
    timeslot.save()
    return redirect('timeslot_list_admin', ground_id=timeslot.ground.id)


@login_required
def turf_list_reservation(request):
    t = TurfDetails.objects.all()
    return render(request, 'admin/turflist_reservation_admin.html', {'turfs': t})



@login_required
def ground_list_reservation(request,turf_id):
    turf = get_object_or_404(TurfDetails, id=turf_id)
    grounds = Ground.objects.filter(turf=turf)
    return render(request, 'admin/groundlist_reservation_admin.html', {'turf': turf, 'grounds': grounds})



@login_required
def select_date_and_reservations(request, ground_id):
    selected_date = request.GET.get('selected_date')
    if selected_date:
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()

    ground = get_object_or_404(Ground, id=ground_id)
    reservations = Reservation.objects.filter(ground=ground, time_slot__date=selected_date) if selected_date else []
    return render(request, 'admin/ground_reservation_details.html', {'ground': ground, 'selected_date': selected_date, 'reservations': reservations})




@login_required
def booking_page(request):
    all_bookings = Bookings.objects.all().order_by('-timestamp')
    
    context = {
        'all_bookings': all_bookings
    }
    return render(request, 'admin/bookings_admin.html', context)


def sort_by_turf(request):
    sorted_bookings = Bookings.objects.order_by('reservation__ground__turf__turf_name')
    context = {
        'sorted_bookings': sorted_bookings
    }
    return render(request, 'admin/sorted_by_turf.html', context)

def sort_by_date(request):
    sorted_bookings = Bookings.objects.order_by('reservation__time_slot__date')
    context = {
        'sorted_bookings': sorted_bookings
    }
    return render(request, 'admin/sorted_by_date.html', context)


@login_required
def payments_admin(request):
    all_bookings = Bookings.objects.exclude(reservation__ground__turf__added_by__user_type=1).order_by('-timestamp')
    paginator = Paginator(all_bookings, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    for booking in page:
        try:
            reservation = booking.reservation
            ground = reservation.ground
            turf = ground.turf
            added_by = turf.added_by

            if hasattr(added_by, 'clients'):
                commission_percentage = added_by.clients.commission_percentage
                commission = (commission_percentage / 100) * booking.amount
                amount_to_client = booking.amount - commission
                booking.commission = commission
                booking.amount_to_client = amount_to_client
                booking.save()

            else:
                pass

        except (Bookings.DoesNotExist, Clients.DoesNotExist):
            pass

    context = {
        'page': page,  
        'all_bookings':all_bookings
    }

    return render(request, 'admin/paymentspage_admin.html', context)


@login_required
def admins_only_payments(request):
    admin_bookings =Bookings.objects.exclude(reservation__ground__turf__added_by__user_type=2).order_by('-timestamp')

    context = {
        'admin_bookings': admin_bookings,
    }

    return render(request, 'admin/adminsonly_payments.html', context)


@login_required
def update_payment_status(request):
    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        new_status = request.POST.get('new_status')
        
        try:
            booking = Bookings.objects.get(pk=booking_id)
            booking.payment_status = new_status
            booking.save()
            
            return JsonResponse({'message': 'Payment status updated successfully.'})
        except Bookings.DoesNotExist:
            return JsonResponse({'error': 'Booking not found.'})
    else:
        return JsonResponse({'error': 'Invalid request method.'})
   
@login_required
def enquiry_list(request):
    enquiries = Enquiry.objects.all().order_by('-timestamp_enquiry')  # Order by timestamp in descending order
    return render(request, 'admin/enquiry.html', {'enquiries': enquiries})


@login_required
def delete_enquiry(request, pk):
    enquiry = get_object_or_404(Enquiry, pk=pk)
    if request.method == 'POST':
        enquiry.delete()
    return redirect('enquiry_list')