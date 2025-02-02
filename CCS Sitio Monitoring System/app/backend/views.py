from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as auth_logout 
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Registration

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'backend/login.html', {'error': 'Invalid username or password'})

    return render(request, 'backend/login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        password2 = request.POST['password2']
        if password == password2: 
            user = User.objects.create_user(username=username, password=password)
            Registration.objects.create(
                username=user,
                idno=request.POST['idno'],
                lastname=request.POST['lastname'],
                firstname=request.POST['firstname'],
                middlename=request.POST['middlename'],
                course=request.POST['course'],
                level=request.POST['level'],
                email=request.POST['email'],
            )
            return redirect('/')
        else: 
            return redirect(request, 'backend/register.html', {'error': 'Passwords do not match'})
    
    return render(request, 'backend/register.html')

def logout_view(request):
    auth_logout(request)
    return redirect('/')

def home(request):
    if not request.user.is_authenticated:
        return redirect('/')
    return render(request, 'backend/home.html')