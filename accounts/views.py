from django.shortcuts import render,redirect
from .models import Customers
from django.contrib.auth import login, logout
from django.shortcuts import render


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

def doLogin(request):
    if request.method=='POST':
        user=EmailBackEnd.authenticate(request,username=request.POST.get("email"),password=request.POST.get("password"))
        if user is not None:
            if user.is_blocked:  # Check if the user is blocked
                # Add a message to indicate that the user is blocked
                return redirect('dologin')  # Redirect to the login page
            else:
                login(request, user)
                if user.user_type == "1":
                    return redirect('admin_dashborad')
                elif user.user_type == "2":
                    return redirect('clienthome')
                elif user.user_type == "3":
                    return redirect('home')
                else:
                    return redirect('invalid_page')
        else:
            return redirect('invalid_page')
    else:
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
