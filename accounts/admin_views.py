from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import *
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect,JsonResponse
from django.urls import reverse
from django.shortcuts import get_object_or_404
# from .utils import add_time
from datetime import datetime, timedelta


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
    # Get the associated CustomUser
    user = customer.admin

    # Delete the Customer and the associated CustomUser
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

            # Check if a Clients instance already exists for the given admin user
            client = Clients.objects.filter(admin=user).first()
            if client:
                client.address = address
                client.mobile = mobile
                client.save()
            else:
                client = Clients.objects.create(
                    admin=user,
                    address=address,
                    mobile=mobile,
                    username=username
                )

            messages.success(request, "Client successfully saved")
            return redirect('addclient')

@login_required
def delete_client(request, id):
    client = get_object_or_404(CustomUser, id=id)
    client.delete()
    messages.success(request, "Selected client deleted successfully")
    return redirect('adminhome')

def block_client(request, user_id):
    client = get_object_or_404(CustomUser, id=user_id)

    # Set is_blocked to True
    client.is_blocked = True
    client.save()

    # Add a custom message when blocking the client
    messages.success(request, f"{client.username} has been blocked.")

    return redirect('adminhome')


def unblock_client(request, user_id):
    client = get_object_or_404(CustomUser, id=user_id)
    client.is_blocked = False
    client.save()
    messages.success(request, f"{client.username} has been unblocked.")
    return redirect('adminhome')

    
def blocked_clients(request):
    blocked_clients = CustomUser.objects.filter(is_blocked=True)
    context = {
        'blocked_clients': blocked_clients
    }
    return render(request, 'admin/blocked_clients.html', context)



def add_turf(request):
    return render(request,'admin/addturf.html')   



@login_required(login_url='/')
def add_turf_save(request):
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

       
        TurfDetails.objects.create(
            added_by=request.user,  
            turf_name=turf_name,
           
            place=place,
            phone=phone,
            
            cafe=cafe,
            first_aid=first_aid,
            locker=locker,
            parking=parking,
            shower=shower,
            image=image,
        )

        return redirect('add_turf_page') 

    else:
        return render(request, 'admin/addturf.html')
    


def list_turf_details(request):
    turfs = TurfDetails.objects.all()
    return render(request, 'admin/list_turf_details.html', {'turfs': turfs})      


def add_ground_page(request):
    turfs = TurfDetails.objects.all()
    return render(request, 'admin/add_ground_admin.html', {'turfs': turfs})



def add_ground_page_admin(request):
    if request.method == 'POST':
        turf_id = request.POST['turf']
        category = request.POST['category']
        ground_name = request.POST['ground_name']
        price = request.POST['price']
        

        # Create a new Ground instance and save it to the database
        ground = Ground(turf_id=turf_id, category=category, ground_name=ground_name, price=price)
        ground.save()

        # Redirect to the page you want to show after the form submission
        return redirect('add_ground_page_admin')  # Change 'some_view_name' to the desired view name

    # If it's not a POST request, render the template as usual
    return render(request, 'admin/add_ground_page_admin.html', {'turfs': TurfDetails.objects.all()})

def ground_details_page(request, turf_id):
    turf = get_object_or_404(TurfDetails, id=turf_id)
    grounds = Ground.objects.filter(turf=turf)

    return render(request, 'admin/ground_list_admin.html', {'turf': turf, 'grounds': grounds})



def delete_ground(request, ground_id):
    ground = get_object_or_404(Ground, id=ground_id)
    if request.method == 'POST':
        # Delete the ground object from the database
        ground.delete()
    return redirect('ground_details_page', turf_id=ground.turf.id)

@login_required
def delete_turf_admin(request, turf_id):
    print("Turf ID to delete:", turf_id)

    try:
        turf = TurfDetails.objects.get(pk=turf_id)
        turf.delete()
    except TurfDetails.DoesNotExist:
        # Handle the case if the turf with the given ID does not exist
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

        # Convert start_time and end_time to datetime objects
        from datetime import datetime
        start_datetime = datetime.strptime(start_time, '%H:%M')
        end_datetime = datetime.strptime(end_time, '%H:%M')

        # Calculate the number of time slots to create
        time_slot_count = int((end_datetime - start_datetime).seconds / (match_duration * 3600))

        # Save the time slots
        for i in range(time_slot_count):
            time_slot = TimeSlot.objects.create(
                added_by=request.user,  # Add the added_by field here with the currently logged-in user
                ground_id=ground_id,
                date=request.POST.get('day'),
                start_time=start_datetime.time(),
                end_time=(start_datetime + timedelta(hours=match_duration)).time()
            )
            start_datetime += timedelta(hours=match_duration)

        # Redirect to a success page after successful data submission
        return redirect('success_page')

    # If the request method is GET, render the form page
    return render(request, 'admin/timeslot_admin.html', context={})




@login_required
def turf_list_timeslot(request):
    t = TurfDetails.objects.all()
    return render(request, 'admin/turflist_timeslot_admin.html', {'turfs': t})


def ground_list(request, turf_id):
    turf = get_object_or_404(TurfDetails, id=turf_id)
    grounds = Ground.objects.filter(turf=turf)
    return render(request, 'admin/groundlist_timeslot_admin.html', {'turf': turf, 'grounds': grounds})


def timeslot_list(request, ground_id):
    ground = get_object_or_404(Ground, id=ground_id)
    timeslots = TimeSlot.objects.filter(ground=ground)
    return render(request, 'admin/list_timeslot_admin.html', {'ground': ground, 'timeslots': timeslots})


def delete_timeslot_admin(request, timeslot_id):
    timeslot = get_object_or_404(TimeSlot, pk=timeslot_id)
    ground_id = timeslot.ground.id  # Assuming Timeslot model has a foreign key to the Ground model

    if request.method == 'POST':
        timeslot.delete()
        return redirect('timeslot_list_admin', ground_id=ground_id)
    
    return render(request, 'admin/list_timeslot_admin.html', {'timeslot': timeslot})


@login_required
def turf_list_reservation(request):
    t = TurfDetails.objects.all()
    return render(request, 'admin/turflist_reservation_admin.html', {'turfs': t})

@login_required
def ground_list_reservation(request,turf_id):
    turf = get_object_or_404(TurfDetails, id=turf_id)
    grounds = Ground.objects.filter(turf=turf)
    return render(request, 'admin/groundlist_reservation_admin.html', {'turf': turf, 'grounds': grounds})


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
    return render(request, 'admin/ground_reservation_details.html', {'ground': ground, 'selected_date': selected_date, 'reservations': reservations})
