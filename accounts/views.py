from django.shortcuts import render,redirect
from .models import Customers
from django.contrib.auth import login, logout
from django.shortcuts import render
from django.contrib import messages
from django.views.decorators.cache import never_cache


from accounts.EmailBackEnd import EmailBackEnd

# Create your views here.


def blocked_page(request):
    return render(request, 'blocked_page.html')

def success_page(request):
    return render(request,'success.html')
def invalid(request):
    return render(request,'invalid.html')

def ShowLoginPage(request):
    return render(request,"login.html")

def show_register(request):
    return render(request,'register.html')

@never_cache
def doLogin(request):
    if request.method == 'POST':
        user = EmailBackEnd.authenticate(request, username=request.POST.get("email"), password=request.POST.get("password"))
        if user is not None:
            if user.is_blocked:
                # User is blocked, redirect with a message
                messages.error(request, "Your account is blocked.")
                return redirect('dologin')  # Redirect to the login page with a message
            else:
                login(request, user)
                if user.user_type == "1":
                    return redirect('admin_dashborad')
                elif user.user_type == "2":
                    return redirect('client_dashboard')
                elif user.user_type == "3":
                    return redirect('home')
        else:
            # Invalid email or password, redirect with a message
            messages.error(request, "Invalid email or password")
            return redirect('dologin')  # Redirect to the login page with a message

    # For GET requests or when login fails, render the login page
    return render(request, 'login.html') 
    
       
def doLogout(request):
    logout(request)
    return redirect('home')



def customer_list(request):
    customers = Customers.objects.all()
    context = {
        'customers': customers
    }
    return render(request, 'admin/customer_list_admin.html', context)
