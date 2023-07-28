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


# def show_time_slot_details(request):
#     if request.method == 'GET':
#         selected_date = request.GET.get('selected_date')
#         ground_id = request.GET.get('ground_id')

#         if not selected_date or not ground_id:
#             # Handle the case when required GET parameters are missing
#             return render(request, 'error_template.html', {'error_message': 'Invalid parameters'})

#         # Implement your logic to retrieve time slot details based on the selected date and ground ID
#         # For example, assuming you have a TimeSlot model:
#         try:
#             time_slots = TimeSlot.objects.filter(date=selected_date, ground_id=ground_id)
#         except TimeSlot.DoesNotExist:
#             # Handle the case when no time slots are available for the given date and ground ID
#             return render(request, 'error_template.html', {'error_message': 'Time slots not found'})

#         # Pass the retrieved time_slots and selected_date to the template for rendering
#         return render(request, 'user/list_timeslot_user.html', {'timeslots': time_slots, 'selected_date': selected_date})

#     # Handle the case when the request method is not GET (optional)
#     return render(request, 'error_template.html', {'error_message': 'Invalid request'})

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


# def reserve_timeslots(request):
#     if request.method == 'POST':
#         selected_date = request.POST.get('selected_date')
#         ground_id = request.POST.get('ground_id')
#         delete_checkbox_values = request.POST.getlist('delete_checkbox')

#         if not selected_date or not ground_id:
#             messages.error(request, "Invalid form submission. Please select a date and a ground.")
#             return redirect('timeslot_list_user')

#         try:
#             ground = Ground.objects.get(id=ground_id)
#         except Ground.DoesNotExist:
#             messages.error(request, "Invalid ground selected.")
#             return redirect('timeslot_list_user')

#         # Implement logic to save the selected time slots into the database
#         try:
#             customer = request.user.customer  # Assumes you have the Customer related to the CustomUser
#         except AttributeError:
#             messages.error(request, "You must be logged in as a customer to reserve time slots.")
#             return redirect('timeslot_list_user')

#         # Create reservations for selected time slots
#         reservations_created = 0
#         for timeslot_id in delete_checkbox_values:
#             try:
#                 timeslot = TimeSlot.objects.get(id=timeslot_id)
#             except TimeSlot.DoesNotExist:
#                 continue  # Skip this iteration if the timeslot does not exist

#             # Check if the timeslot is available for reservation (you can add more checks if needed)
#             if not timeslot.is_available_on_date(selected_date):
#                 continue  # Skip this iteration if the timeslot is not available on the selected date

#             # Create the reservation
#             reservation = Reservation.objects.create(
#                 customer=customer,
#                 ground=ground,
#                 time_slot=timeslot,
#                 reservation_date=selected_date,  # Use the selected_date here
#             )
#             reservations_created += 1

#         # Check if any reservations were created
#         if reservations_created == 0:
#             messages.error(request, "No valid time slots were selected or all selected slots are already booked.")
#         else:
#             messages.success(request, f"{reservations_created} time slot(s) reserved successfully.")

#         # Redirect the user to another page or show a success message
#         return redirect('success_page_user')

#     # Handle GET request or invalid form submission (optional)
#     return redirect('timeslot_list_user')


from datetime import datetime
@login_required
def reserve_timeslots(request):
    if request.method == 'POST':
        selected_date_str = request.POST.get('selected_date')
        ground_id = request.POST.get('ground_id')
        delete_checkbox_values = request.POST.getlist('delete_checkbox')

        if not selected_date_str or not ground_id:
            # Handle the case where selected_date or ground_id is missing or not provided
            return HttpResponse("error")  # Replace 'error' with the error response you want to return

        # Assuming the user is authenticated and logged in
        customer = Customers.objects.get(admin=request.user)

        # Assuming you have obtained the 'ground' object based on 'ground_id'
        ground = Ground.objects.get(pk=ground_id)

        # Convert the selected_date to the correct format 'YYYY-MM-DD'
        selected_date = datetime.strptime(selected_date_str, '%B %d, %Y').strftime('%Y-%m-%d')

        # Get a list of TimeSlot objects that match the given date and ground_id
        time_slots = TimeSlot.objects.filter(ground=ground, date=selected_date)

        if not time_slots:
            # Handle the case where no TimeSlot exists for the given date and ground_id
            return HttpResponse("error")  # Replace 'error' with the error response you want to return

        # Select one of the time slots to use for the reservation (you can choose based on your logic)
        time_slot = time_slots.first()

        # Create the Reservation object using the customer, ground, and time_slot
        reservation = Reservation.objects.create(customer=customer, ground=ground, time_slot=time_slot)

        return redirect('success_page_user')  # Assuming 'success_page_user' is the URL name for the success page

    # Handle the case if the view is accessed via a GET request (optional)
    return render(request, 'user/reservation_details_user.html')

    
# from django.utils import timezone
# def reserve_timeslots(request):
#     if request.method == 'POST':
#         selected_date = request.POST.get('selected_date')
#         ground_id = request.POST.get('ground_id')
#         delete_checkbox = request.POST.get('delete_checkbox')

#         ground = Ground.objects.get(id=ground_id)

#         try:
#             customer = Customers.objects.get(user=request.user)
#         except Customers.DoesNotExist:
#             customer = Customers.objects.create(user=request.user)
#             # You can add additional fields to the Customers model here if needed.
#             # For example: customer.name = request.user.username
#             # Make sure to call customer.save() to save the changes.

#         timeslots = TimeSlot.objects.filter(ground=ground, date=selected_date)

#         if delete_checkbox:
#             # Handle the case where the customer wants to cancel a reservation
#             for slot in timeslots:
#                 try:
#                     reservation = Reservation.objects.get(
#                         timeslot=slot, customer=customer
#                     )
#                     reservation.delete()
#                 except Reservation.DoesNotExist:
#                     pass

#             messages.success(request, "Your reservation has been canceled.")
#         else:
#             # Handle the case where the customer wants to make a new reservation
#             for slot in timeslots:
#                 # Check if the timeslot is already reserved
#                 if Reservation.objects.filter(
#                     timeslot=slot, date=selected_date
#                 ).exists():
#                     messages.error(
#                         request,
#                         f"The timeslot {slot.start_time} - {slot.end_time} is already reserved.",
#                     )
#                 else:
#                     # Create a new reservation for the customer and timeslot
#                     Reservation.objects.create(
#                         timeslot=slot,
#                         customer=customer,
#                         date=selected_date,
#                         reserved_at=timezone.now(),
#                     )
#                     messages.success(
#                         request,
#                         f"You have successfully reserved the timeslot {slot.start_time} - {slot.end_time}.",
#                     )

#         return redirect('client-dashboard')  # Redirect to the appropriate URL after processing the reservation

#     # Handle the GET request if needed
#     return render(request, 'user/reservation_details_user.html', context)


def reservation_success_user(request):
    # selected_date = request.GET.get('selected_date')

    # # Fetch reservation details related to the logged-in user
    # customer_reservations = Reservation.objects.filter(customer=request.user.customers)

    # context = {
    #     'customer_reservations': customer_reservations,
    #     'selected_date': selected_date,  # Pass the selected_date to the template
    # }

    return render(request, 'user/reservation_details_user.html')    