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

        # Get the TurfDetails object based on the ground_id
        ground = get_object_or_404(Ground, id=ground_id)

        # Filter the timeslots based on the selected_date and the related ground
        timeslots = TimeSlot.objects.filter(ground=ground, date=selected_date)
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

        return render(request, 'user/reservation_details_user.html', {'reservation_details_list': reservation_details_list})
    
    return render(request, 'user/reservation_details_user.html')
# def reservation_success_user(request):
#     try:
#         customer = Customers.objects.get(admin=request.user)
#         reservations = Reservation.objects.filter(customer=customer)
#     except Customers.DoesNotExist:
#         return HttpResponse("You are not a registered customer.")

#     reservation_details_list = []
#     for reservation in reservations:
#         ground_name = reservation.ground.ground_name
#         ground_price = reservation.ground.price
#         turf_name = reservation.ground.turf.turf_name
#         time_slot = f"{reservation.time_slot.start_time.strftime('%I:%M %p')} - {reservation.time_slot.end_time.strftime('%I:%M %p')}"
#         reserved_date = reservation.reservation_date.strftime('%B %d, %Y')

#         reservation_details_list.append({
#             'turf_name': turf_name,
#             'ground_name': ground_name,
#             'ground_price': ground_price,
#             'time_slot': time_slot,
#             'reserved_date': reserved_date,
#         })

#     # Print the details in the terminal
#     for details in reservation_details_list:
#         print(details)

#     return render(request, 'user/reservation_details_user.html', {'reservation_details_list': reservation_details_list})
