# frontend/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('passenger/dashboard/', views.passenger_dashboard, name='passenger_dashboard'),
    path('driver/dashboard/', views.driver_dashboard, name='driver_dashboard'),
    path('track/<int:ride_id>/', views.ride_tracking, name='ride_tracking'),
    path('available_drivers/', views.available_drivers, name='available_drivers'),
    path('ride-status/', views.ride_status, name='ride_status'),
    path('live-tracking/', views.live_tracking, name='live_tracking'),
    path('driver/requests/', views.driver_requests, name='driver_requests'),
    path('bookride/', views.book_ride, name='book_ride'),
    path('profile/', views.profile, name='profile'),

]

