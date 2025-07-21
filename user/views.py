from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as django_login
from django.contrib import messages
from django.contrib.auth import logout
from .models import Signup

# Dashboard view (after successful login)
def dashboard(request):
    return render(request, 'dashboard.html')

#Signup view
def signup_view(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']

        if name and email and password:
            Signup.objects.create(name=name, email=email, password=password)
            return redirect('login')

    return render(request, 'signup.html')

# Login view
def login(request):
    if request.method == 'POST':
        chk_pswd = request.POST['password']
        chk_email = request.POST['email']

        try:
            user = Signup.objects.get(email=chk_email)
            if user.password == chk_pswd:
                request.session['email'] = user.email  # optional: to use in dashboard
                return redirect('dashboard')
            else:
                return render(request, 'login.html', {'error': "Invalid password"})
        except Signup.DoesNotExist:
            return render(request, 'login.html', {'error': "User not found"})

    return render(request, 'login.html')

    # if request.method == 'POST':
    #     email = request.POST.get('email')
    #     password = request.POST.get('password')
    #
    #     user = authenticate(request, username=email, password=password)
    #
    #     if user is not None:
    #         # Successful authentication, log the user in
    #         django_login(request, user)
    #         messages.success(request, "Login successful!")  # Optional success message
    #         return redirect('dashboard')  # Redirect to the dashboard after successful login
    #     else:
    #         # Authentication failed
    #         messages.error(request, "Invalid credentials")  # Optional error message
    #         return render(request, 'login.html')  # Render the login page again with error message

    # return render(request, 'login.html')

# Logout view
def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to the login page after logout
