# frontend/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'index.html')

def login_page(request):
    return render(request, 'login.html')

def register_page(request):
    return render(request, 'register.html')

def passenger_dashboard(request):
    return render(request, 'passenger_dashboard.html')

def driver_dashboard(request):
    return render(request, 'driver_dashboard.html')

def ride_tracking(request, ride_id):
    return render(request, 'live_tracking.html', {'ride_id': ride_id})

def available_drivers(request):
    # optional: pass context from query params or session
    return render(request, 'available_drivers.html')

def ride_status(request):
    return render(request, 'ride_status.html')

def live_tracking(request):
    return render(request, 'live_tracking.html')

def driver_requests(request):
    return render(request, 'driver_requests.html')

def book_ride(request):
    return render(request,'book_ride.html')
    
def profile(request):
    return render(request, 'profile.html')
