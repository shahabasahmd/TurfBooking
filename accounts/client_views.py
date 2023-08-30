from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import *
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth import update_session_auth_hash,authenticate
from datetime import datetime, timedelta
from django.core.paginator import Paginator

@login_required
def success_page_client(request):
    return render(request,'client/clientinclude/success_client.html')

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
            return redirect('success_page_client')  # Replace 'change_password' with the URL name for this view
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
def add_place_client(request):
    if request.method == 'POST':
        place_name = request.POST['place_name']
        Places.objects.create(place=place_name)

    # Fetch all places from the database
    all_places = Places.objects.all()

    # Set the number of places per page
    places_per_page = 20
    paginator = Paginator(all_places, places_per_page)

    # Get the current page number from the request's GET parameters
    page_number = request.GET.get('page')
    places = paginator.get_page(page_number)

    return render(request, 'client/addplace_client.html', {'places': places})
  
@login_required
def add_turf_save_client(request):
    if request.method == 'POST':
        turf_name = request.POST.get('turf_name')
        place_name = request.POST.get('place')  # Get the place name from the form
        phone = request.POST.get('mobile')
        cafe = request.POST.get('cafe')
        first_aid = request.POST.get('firstaid')
        locker = request.POST.get('locker')
        parking = request.POST.get('parking')
        shower = request.POST.get('shower')
        image = request.FILES.get('turf_image')

        # Look up the place by name
        try:
            place = Places.objects.get(place=place_name)
        except Places.DoesNotExist:
            place = None

        # Check if place is not null before creating TurfDetails instance
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
        return redirect('success_page_client')  # Replace 'success_page' with the URL name for your success page

    else:
        # Render the form page
        turfs = TurfDetails.objects.filter(added_by=request.user)
        return render(request, 'client/add_ground_client.html', {'turfs': turfs})


@login_required
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
        return redirect('client_turf_list')  # Redirect to the turf list page after deletion
    
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
        return redirect('success_page_client')

    # If the request method is GET, render the form page
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
    
    # Set the number of items to display per page
    items_per_page = 20
    
    # Create a Paginator object
    paginator = Paginator(all_timeslots, items_per_page)
    
    # Get the requested page number from the URL parameter
    page_number = request.GET.get('page')
    
    # Get the Page object for the requested page number
    timeslots = paginator.get_page(page_number)
    
    return render(request, 'client/list_timeslot_client.html', {'ground': ground, 'timeslots': timeslots})


@login_required
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



@login_required
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



@login_required
def bookings_client(request):
    logged_in_client = request.user  # Assuming the logged-in user is a CustomUser
    client_bookings = Bookings.objects.filter(turf_added_by=logged_in_client)
    
    context = {
        'client_bookings': client_bookings,
    }
    return render(request, 'client/bookings_client.html', context)



@login_required
def paymentlist_client(request):
    logged_in_client = request.user  # Assuming the logged-in user is a CustomUser
    client_bookings = Bookings.objects.filter(turf_added_by=logged_in_client)
    
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