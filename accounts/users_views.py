from django.shortcuts import render,redirect
from .models import *
from django.http import HttpResponse
from django.contrib import messages
import datetime
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.encoding import force_str
from django.contrib.auth.forms import SetPasswordForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from .forms import PasswordResetForm
from django.contrib.auth import login
from datetime import datetime
import datetime as dt


def home(request):
    return render(request,'user/home.html',locals())


def about(request):
    return render(request,'user/about.html',locals())


def show_register(request):
    return render(request,'register.html')


def add_user_save(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        address = request.POST.get("address")
        email = request.POST.get("email")
        password = request.POST.get("password")
        mobile = request.POST.get("phone")

        if CustomUser.objects.filter(email=email).exists():
            return HttpResponse("Email already taken", status=400)
        elif CustomUser.objects.filter(username=username).exists():
            return HttpResponse("Username already taken", status=400)
        else:
            user = CustomUser.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password,
                user_type=3
            )
            customers, created = Customers.objects.get_or_create(admin=user)
            if not created:
                customers.address = address
                customers.mobile = mobile
                customers.save()
            else:
                customers.mobile = mobile
                customers.address = address
                customers.save()

            login(request, user)
            messages.success(request, "Your account was created successfully")
            return redirect('loginpage') 

    return render(request, 'registration/register.html')


@login_required
def turf_list(request):
    user_selected_place = request.GET.get('place')  
    turfs = TurfDetails.objects.filter(place__place=user_selected_place) if user_selected_place else TurfDetails.objects.all()
    return render(request, 'user/turf_list.html', {'turfs': turfs})
   
@login_required
def turf_details_user(request, turf_id):
    turf = get_object_or_404(TurfDetails, id=turf_id)
    grounds = Ground.objects.filter(turf=turf)
    return render(request, 'user/turf_details_user.html', {'turf': turf, 'grounds': grounds})



@login_required
def available_time_slots(request, ground_id):
    ground = get_object_or_404(Ground, id=ground_id)
    time_slots = TimeSlot.objects.filter(ground=ground)
    return render(request, 'user/list_timeslot_user.html', {'ground': ground, 'time_slots': time_slots})


@login_required
def timeslot_list_user(request):
    selected_date = request.GET.get('selected_date')
    ground_id = request.GET.get('ground_id')

    if selected_date and ground_id:
        selected_date = dt.datetime.strptime(selected_date, '%Y-%m-%d').date()
        ground = get_object_or_404(Ground, id=ground_id)
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

        try:
            ground = Ground.objects.get(pk=ground_id)
        except Ground.DoesNotExist:
            return HttpResponse("error") 

        reservation_details_list = []
        date_formats = ['%b. %d, %Y', '%B %d, %Y']

        selected_date = None
        for date_format in date_formats:
            try:
                selected_date = datetime.strptime(selected_date_str.replace('Sept', 'Sep'), date_format).strftime('%Y-%m-%d')
                break  
            except ValueError as e:
                print(f"Error parsing date with format {date_format}: {e}")
                pass  
        
        if selected_date is None:
            return HttpResponse("Invalid date format")

        for time_slot_id_str in delete_checkbox_values:
            try:
                time_slot_id = int(time_slot_id_str)
                time_slot = TimeSlot.objects.get(pk=time_slot_id)
            except (ValueError, TimeSlot.DoesNotExist):
                continue

            existing_reservation = Reservation.objects.filter(
                customer=customer,
                time_slot=time_slot,
                ground=ground,
                reservation_date=selected_date
            ).exists()

            if not existing_reservation:
                reservation = Reservation.objects.create(
                    customer=customer,
                    ground=ground,
                    time_slot=time_slot,
                    reservation_date=selected_date
                )
                reservation_details = {
                    'turf_name': ground.turf.turf_name,
                    'ground_name': ground.ground_name,
                    'ground_price': ground.price,
                    'time_slot': f'{time_slot.start_time.strftime("%I:%M %p")} - {time_slot.end_time.strftime("%I:%M %p")}',
                    'reserved_date': selected_date_str,
                }
                reservation_details_list.append(reservation_details)

        context = {
            'reservation_details_list': reservation_details_list,
        }
        return redirect('success_page_user') 

    return render(request, 'user/list_timeslot_user.html')



@login_required
def reservation_success_user(request):
    customer = Customers.objects.get(admin=request.user)
    reservations = Reservation.objects.filter(customer=customer)
    reservation_details_list = []
    total_amount = 0

    for reservation in reservations:
        if reservation.time_slot.is_available: 
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

    razoramount = int(total_amount * 100)  
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


@login_required
def payment_done(request):
    if request.method == 'GET':
        payment_id = request.GET.get('payment_id')
        reservation_ids = request.GET.get('reservation_ids')

        if not payment_id:
            return JsonResponse({'status': 'error', 'message': 'Payment ID is missing'})

        if not reservation_ids:
            return JsonResponse({'status': 'error', 'message': 'Reservation IDs are missing'})

        try:
            customer = Customers.objects.get(admin=request.user)
            reservation_id_list = [int(reservation_id) for reservation_id in reservation_ids.split(',')]
            with transaction.atomic():
                total_amount = 0
                for reservation_id in reservation_id_list:
                    try:
                        reservation = Reservation.objects.get(id=reservation_id)
                        total_amount += reservation.ground.price
                        payment = Bookings.objects.create(
                            customer=customer,
                            reservation=reservation,
                            razorpay_payment_id=payment_id,
                            amount=reservation.ground.price,
                            turf_added_by=reservation.ground.turf.added_by,  
                            payment_status='pending', 
                        )
                        time_slot = reservation.time_slot
                        time_slot.is_available = False
                        time_slot.save()
                    except Reservation.DoesNotExist:
                        pass  

            
            return redirect('booking_history')
        except Exception as e:
            print("Error:", e)
            return JsonResponse({'status': 'error', 'message': 'An error occurred while saving payment details'})

    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})






@login_required
def booking_history(request):
    customer = request.user.customers
    bookings = Bookings.objects.filter(customer=customer).order_by('-timestamp')
    context = {
        'bookings': bookings
    }
    return render(request, 'user/booking_history.html', context)



def enquiry_view(request):
    if request.method == 'POST':
        name = request.POST.get('name') 
        place = request.POST.get('place')  
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        enquiry = Enquiry(name=name, place=place, email=email, phone=phone, message=message)
        enquiry.save()
        messages.success(request, "Your information has been received. Our team will contact you soon.")
        return render(request, 'user/home.html')    
    return render(request, 'user/home.html')


@login_required
def profile(request):
    return render(request, 'user/profile.html')




def change_password(request):
    if request.method == 'POST':
        old_password = request.POST['old_password']
        new_password1 = request.POST['new_password1']
        new_password2 = request.POST['new_password2']

        if not request.user.check_password(old_password):
            messages.error(request, 'Incorrect old password. Please try again.')
        elif new_password1 != new_password2:
            messages.error(request, 'New passwords do not match. Please try again.')
        else:
            request.user.set_password(new_password1)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Your password was successfully changed!')
            return redirect('profile') 
    
    return render(request, 'user/change_password.html')





def send_reset_link(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)

            
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = f"http://localhost:8000/reset-password/{uid}/{token}/"
            subject = "Reset Your Password"
            message = render_to_string('password_reset_email.html', {
                'user': user,
                'reset_link': reset_link,
            })
            send_mail(subject, message, 'from@example.com', [email])

            return render(request, 'user/forgot_password.html', {'email_sent': True})

    else:
        form = PasswordResetForm()

    return render(request, 'user/forgot_password.html', {'form': form})


def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your password has been reset successfully.')
                return redirect('dologin') 
        else:
            form = SetPasswordForm(user)
        return render(request, 'user/reset_password.html', {'form': form})
    else:
        messages.error(request, 'The password reset link is invalid or has expired.')
        return redirect('dologin')