from django.shortcuts import render,redirect
import datetime
from .models import Customers
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from accounts.EmailBackEnd import EmailBackEnd

# Create your views here.

def success_page(request):
    return render(request,'success.html')

def ShowLoginPage(request):
    return render(request,"login.html")

def show_register(request):
    return render(request,'register.html')

def doLogin(request):
    if request.method=='POST':
        user=EmailBackEnd.authenticate(request,username=request.POST.get("email"),password=request.POST.get("password"))
        if user !=None:
            login(request,user)
            if user.user_type=="1":
                return redirect('adminhome')
            elif user.user_type=="2":
                return redirect('clienthome')
            elif user.user_type=="3":
                return redirect('home')
            else:
                return redirect('dologin')
        else:
            return redirect('dologin')


def doLogout(request):
    logout(request)
    return redirect('home')



def customer_list(request):
    customers = Customers.objects.all()
    context = {
        'customers': customers
    }
    return render(request, 'admin/customer_list_admin.html', context)
