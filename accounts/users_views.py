from django.shortcuts import render,redirect
from .models import *
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.views.decorators.csrf import csrf_protect

def home(request):
    return render(request,'user/home.html',locals())


def about(request):
    return render(request,'user/about.html',locals())

def show_register(request):
    return render(request,'register.html')

def add_user_save(request):
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    else:
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        address = request.POST.get("address")
        email = request.POST.get("email")
        password = request.POST.get("password")
        mobile = request.POST.get("phone")

        if CustomUser.objects.filter(email=email).exists():
            messages.warning(request, "Email already taken")
            return redirect('showregisterpage')
        elif CustomUser.objects.filter(username=username).exists():
            messages.warning(request, "Username already taken")
            return redirect('showregisterpage')
        else:
            user = CustomUser.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password,
                user_type=3
            )

            # Check if a Clients instance already exists for the given admin user
            customers = Customers.objects.filter(admin=user).first()
            if customers:
                customers.address = address
                customers.mobile = mobile
                customers.save()
            else:
                customers = Customers.objects.create(
                    admin=user,
                    address=address,
                    mobile=mobile,
                    username=username
                )

            messages.success(request, "your account created successfuly")
            return redirect('loginpage')
        


def turf_list(request):
    turfs = TurfDetails.objects.all()
    return render(request, 'user/turf_list.html', {'turfs': turfs})
def get_places(request):
    search_query = request.GET.get('q', '')
    places = TurfDetails.objects.filter(place__icontains=search_query).values_list('place', flat=True).distinct()
    return JsonResponse(list(places), safe=False)
   

def turf_details_user(request, turf_id):
    turf = get_object_or_404(TurfDetails, id=turf_id)
    grounds = Ground.objects.filter(turf=turf)
    return render(request, 'user/turf_details_user.html', {'turf': turf, 'grounds': grounds})


def available_time_slots(request, ground_id):
    ground = get_object_or_404(Ground, id=ground_id)
    time_slots = TimeSlot.objects.filter(ground=ground)

    # You can do any additional processing or filtering here if needed

    return render(request, 'user/list_timeslot_user.html', {'ground': ground, 'time_slots': time_slots})



def timeslot_list_user(request):
    selected_date = request.GET.get('selected_date')
    ground_id = request.GET.get('ground_id')

    if selected_date and ground_id:
        # Convert the selected_date to a Python datetime object
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()

        # Get the Ground object based on the ground_id
        ground = get_object_or_404(Ground, id=ground_id)

        # Filter the timeslots based on the selected_date and the related ground
        # and also filter by is_available
        timeslots = TimeSlot.objects.filter(ground=ground, date=selected_date, is_available=True)
    else:
        ground = None
        timeslots = TimeSlot.objects.none()

    return render(request, 'user/list_timeslot_user.html', {'ground': ground, 'timeslots': timeslots, 'selected_date': selected_date})



@login_required
def reserve_timeslots(request):
    if request.method == 'POST':
        selected_date_str = request.POST.get('selected_date')
        ground_id = request.POST.get('ground_id')
        delete_checkbox_values = request.POST.getlist('delete_checkbox')

        if not selected_date_str or not ground_id:
            return HttpResponse("error") 

        try:
            customer = Customers.objects.get(admin=request.user)
        except Customers.DoesNotExist:
            return HttpResponse("error") 
         
        ground = Ground.objects.get(pk=ground_id)
        reservation_details_list = []

        # Convert the selected_date_str to the correct format (YYYY-MM-DD)
        selected_date = datetime.strptime(selected_date_str, '%b. %d, %Y').strftime('%Y-%m-%d')


        # Loop through the selected time slot IDs and create a Reservation object for each one
        for time_slot_id_str in delete_checkbox_values:
            try:
                time_slot_id = int(time_slot_id_str)
            except ValueError:
                # Handle the case where the time_slot_id_str is not a valid integer
                continue

            try:
                time_slot = TimeSlot.objects.get(pk=time_slot_id)
            except TimeSlot.DoesNotExist:
                continue

            # Check if the timeslot is already reserved by the current customer on the selected date
            if Reservation.objects.filter(customer=customer, time_slot=time_slot, reservation_date=selected_date).exists():
                # Skip this timeslot as it's already reserved
                continue

            # Create the reservation and add details to the list
            reservation = Reservation.objects.create(customer=customer, ground=ground, time_slot=time_slot, reservation_date=selected_date)
            reservation_details = {
                'turf_name': ground.turf.turf_name,
                'ground_name': ground.ground_name,
                'ground_price': ground.price,
                'time_slot': f'{time_slot.start_time.strftime("%I:%M %p")} - {time_slot.end_time.strftime("%I:%M %p")}',
                'reserved_date': selected_date_str,
            }
            reservation_details_list.append(reservation_details)

        return redirect('success_page_user') 
    
    return render(request, 'user/list_timeslot_user.html')




from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
@login_required
def reservation_success_user(request):
    customer = Customers.objects.get(admin=request.user)
    reservations = Reservation.objects.filter(customer=customer)

    reservation_details_list = []
    total_amount = 0

    for reservation in reservations:
        if reservation.time_slot.is_available:  # Check availability
            reservation_details = {
                'id': reservation.id,
                'turf_name': reservation.ground.turf.turf_name,
                'ground_name': reservation.ground.ground_name,
                'reserved_date': reservation.reservation_date.strftime('%B %d, %Y'),
                'ground_price': reservation.ground.price,
                'time_slot': f"{reservation.time_slot.start_time.strftime('%I:%M %p')} - {reservation.time_slot.end_time.strftime('%I:%M %p')}",
                'booked_date': reservation.time_slot.date.strftime('%B %d, %Y'),
            }
            reservation_details_list.append(reservation_details)

            if reservation_details['ground_price']:
                total_amount += float(reservation_details['ground_price'])

    razoramount = int(total_amount * 100)  # Calculate outside the loop

    context = {
        'reservation_details_list': reservation_details_list,
        'total_amount': total_amount,
        'razoramount': razoramount,
    }

    return render(request, 'user/reservation_details_user.html', context)


@csrf_exempt
def save_payment(request):
    if request.method == 'POST':
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        amount = request.POST.get('amount')
        reservation_id = request.POST.get('reservation_id')

        if razorpay_payment_id and amount and reservation_id:
            try:
                reservation = Reservation.objects.get(id=reservation_id)
            except Reservation.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Reservation not found'})

            customer = request.user.customer

            payment = Bookings.objects.create(
                customer=customer,
                reservation=reservation,
                razorpay_payment_id=razorpay_payment_id,
                amount=amount
            )

            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Payment ID, amount, or Reservation ID missing'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def payment_done(request):
    if request.method == 'GET':
        payment_id = request.GET.get('payment_id')
        reservation_ids = request.GET.get('reservation_ids')  # Change to 'reservation_ids' plural

        if not payment_id:
            return JsonResponse({'status': 'error', 'message': 'Payment ID is missing'})

        if not reservation_ids:
            return JsonResponse({'status': 'error', 'message': 'Reservation IDs are missing'})

        try:
            customer = Customers.objects.get(admin=request.user)

            # Split the reservation_ids string into a list of integers
            reservation_id_list = [int(reservation_id) for reservation_id in reservation_ids.split(',')]

            # Get the total amount based on the selected reservations
            total_amount = 0
            for reservation_id in reservation_id_list:
                try:
                    reservation = Reservation.objects.get(id=reservation_id)
                    total_amount += reservation.ground.price
                    # Create a booking for each selected reservation
                    payment = Bookings.objects.create(
                        customer=customer,
                        reservation=reservation,
                        razorpay_payment_id=payment_id,
                        amount=reservation.ground.price  # Assuming you want to save the amount for each reservation
                    )
                    
                    # Mark the associated time slot as not available
                    time_slot = reservation.time_slot
                    time_slot.is_available = False
                    time_slot.save()
                except Reservation.DoesNotExist:
                    pass  # Ignore non-existent reservations

            print("Payment Details Saved Successfully")
            return redirect('booking_history')
        except Exception as e:
            print("Error:", e)
            return JsonResponse({'status': 'error', 'message': 'An error occurred while saving payment details'})

    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})





@login_required
def booking_history(request):
    # Fetch the bookings for the logged-in customer
    customer = request.user.customers
    bookings = Bookings.objects.filter(customer=customer)

    context = {
        'bookings': bookings
    }

    return render(request, 'user/booking_history.html', context)