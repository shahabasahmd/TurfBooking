from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import *
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.contrib.auth import update_session_auth_hash,authenticate
from datetime import datetime, timedelta

@login_required(login_url='/')
def clienthome(request ):
    user = request.user
    client = Clients.objects.filter(admin=user).first()

    # Pass the client object to the template context
    return render(request, 'client/clienthome.html', {'client': client})


@login_required
def change_password_view(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')

        # Get the currently authenticated user from the request
        user = request.user
        print(current_password,new_password,user)

        # Check if the current password is valid for the user
        if user.check_password(current_password):
            # Use the set_password method to change the password
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)  # Update the session to prevent auto logout
            messages.success(request, 'Your password has been changed successfully.')
            return redirect('change_password')  # Replace 'change_password' with the URL name for this view
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
    return render(request,'client/addturf_client.html')
  
@login_required
def add_turf_save_client(request):
    if request.method == 'POST':
        turf_name = request.POST.get('turf_name')
        place = request.POST.get('place')
        phone = request.POST.get('mobile')
        cafe = request.POST.get('cafe') == 'cafe_yes'
        first_aid = request.POST.get('firstaid') == 'firstaid_yes'
        locker = request.POST.get('locker') == 'locker_yes'
        parking = request.POST.get('parking') == 'parking_yes'
        shower = request.POST.get('shower') == 'shower_yes'
        image = request.FILES.get('turf_image')

        added_by = request.user
        #Create a new Turf object and save the data
        turf = TurfDetails(
            added_by=added_by,
            image=image,
            turf_name=turf_name,
            place=place,
            phone=phone,
            cafe=cafe,
            first_aid=first_aid,
            locker=locker,
            parking=parking,
            shower=shower
        )
        turf.save()
        return redirect('add_turf_client') 

    else:
        return render(request, 'client/addturf_client.html')



@login_required
def client_turf_list(request):
    user = request.user
    turf_details = TurfDetails.objects.filter(added_by=user)
    return render(request, 'client/list_turf_client.html', {'turf_details': turf_details})


@login_required
def add_ground_client(request):
    # Fetch turf names uploaded by the logged-in client
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
        
        # Get the logged-in user's ID
        user_id = request.user.id

        # Create a new GroundDetails object and save the data
        ground = Ground(
            turf_id=turf_id,
            category=category,
            ground_name=ground_name,
            price=price,
            
            
        )
        ground.save()

        # Redirect to a success page or back to the form page
        return redirect('success_page')  # Replace 'success_page' with the URL name for your success page

    else:
        # Render the form page
        turfs = TurfDetails.objects.filter(added_by=request.user)
        return render(request, 'client/add_ground_client.html', {'turfs': turfs})



def ground_list_by_turf(request, turf_id):
    # Get the list of grounds associated with the selected turf
    grounds = Ground.objects.filter(turf_id=turf_id)
    
    # Pass the ground objects to the template
    return render(request, 'client/list_ground_client.html', {'grounds': grounds})



@login_required
def delete_ground(request, ground_id):
    # Get the ground object based on the provided ground_id
    try:
        ground = Ground.objects.get(id=ground_id)
    except Ground.DoesNotExist:
        # Handle if the ground with the given ID doesn't exist
        return redirect('ground_list_by_turf')  # Replace 'ground_list' with the URL name for your ground list page

    # Check if the ground belongs to the logged-in user
    if ground.turf.added_by == request.user:
        # Delete the ground
        ground.delete()
    
    # Get the turf_id of the deleted ground
    turf_id = ground.turf.id

    # Redirect back to the ground list page with the turf_id parameter
    return redirect('ground_list_by_turf', turf_id=turf_id)

@login_required
def delete_turf_confirmation_page(request, turf_id):  # Correct the function name here
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

        # Convert start_time and end_time to datetime objects
        start_datetime = datetime.strptime(start_time, '%H:%M')
        end_datetime = datetime.strptime(end_time, '%H:%M')

        # Calculate the number of time slots to create
        time_slot_count = int((end_datetime - start_datetime).seconds / (match_duration * 3600))

        # Calculate the number of days in the date range
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

        # Redirect to a success page after successful data submission
        return redirect('success_page')

    # If the request method is GET, render the form page
    return render(request, 'client/timeslotpage_client.html', context={})

@login_required
def turf_list_timeslot(request):
    turf = TurfDetails.objects.filter(added_by=request.user)
    return render(request, 'client/turflist_timeslot_client.html', {'turfs': turf})


def ground_list(request, turf_id):
    turf = get_object_or_404(TurfDetails, id=turf_id)
    grounds = Ground.objects.filter(turf=turf)
    return render(request, 'client/groundlist_timeslot_client.html', {'turf': turf, 'grounds': grounds})


def timeslot_list(request, ground_id):
    ground = get_object_or_404(Ground, id=ground_id)
    timeslots = TimeSlot.objects.filter(ground=ground)
    return render(request, 'client/list_timeslot_client.html', {'ground': ground, 'timeslots': timeslots})



def delete_timeslot_client(request, timeslot_id):
    timeslot = get_object_or_404(TimeSlot, pk=timeslot_id)
    ground_id = timeslot.ground.id  # Assuming Timeslot model has a foreign key to the Ground model

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


def select_date_and_reservations(request, ground_id):
    selected_date = request.GET.get('selected_date')

    # Convert the selected_date to a Python datetime object if it exists
    if selected_date:
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()

    # Get the specific ground based on the ground_id
    ground = get_object_or_404(Ground, id=ground_id)

    # Filter reservations for the selected date and ground
    reservations = Reservation.objects.filter(ground=ground, time_slot__date=selected_date) if selected_date else []

    # Render the template with the necessary context
    return render(request, 'client/ground_reservation_details_client.html', {'ground': ground, 'selected_date': selected_date, 'reservations': reservations})
# def timeslot_page_client(request):
#     if request.method == 'POST':
#         turf_id = request.POST.get('turf_name')
#         day = request.POST.get('day')
#         start_time = request.POST.get('start_time')
#         end_time = request.POST.get('end_time')

#         # Assuming you have the turf object corresponding to the selected turf_id
#         turf = TurfDetails.objects.get(id=turf_id)

#         # Create and save the time slot
#         time_slot = TimeSlot.objects.create(
#             turf_name=turf,
#             added_by=request.user,
#             day=day,
#             start_time=start_time,
#             end_time=end_time
#         )
#         time_slot.save()
#         return redirect('timeslot_page_client')

#     # Fetch user's turfs for the dropdown
#     user_turfs = TurfDetails.objects.filter(added_by=request.user)

#     context = {
#         'user_turfs': user_turfs
#     }
#     return render(request, 'client/timeslotpage_client.html', context)


# @login_required
# def timeslot_list_client(request, turf_id):
#     turf = get_object_or_404(TurfDetails, id=turf_id, added_by=request.user)
#     timeslots = TimeSlot.objects.filter(turf_name=turf)
#     return render(request, 'client/list_timeslot_client.html', {'turf': turf, 'timeslots': timeslots})



# @login_required
# def delete_timeslot_client(request, turf_id, timeslot_id):
#     # Retrieve the time slot object to be deleted
#     timeslot = get_object_or_404(TimeSlot, id=timeslot_id, turf_name__id=turf_id, added_by=request.user)

#     if request.method == 'POST':
#         # Delete the time slot
#         timeslot.delete()
    
#     # Redirect back to the time slot list page
#     return redirect('timeslot_list_client', turf_id=turf_id)
