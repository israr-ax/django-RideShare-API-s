from django.urls import path
from .views import (
    CreateRideRequest,
    StartRideView,
    EndRideView,
    PassengerRideHistory,
    DriverRideHistory,
    RateDriverView,
    RatePassengerView,
    AcceptRideView,
    RideDetailView   
)

urlpatterns = [
    # Ride flow
    path('create/', CreateRideRequest.as_view(), name='create-ride'),
    path('start/<int:ride_id>/', StartRideView.as_view(), name='start-ride'),
    path('end/<int:ride_id>/', EndRideView.as_view(), name='end-ride'),
    path('<int:ride_id>/detail/', RideDetailView.as_view()),

    # History
    path('history/passenger/', PassengerRideHistory.as_view(), name='passenger-history'),
    path('history/driver/', DriverRideHistory.as_view(), name='driver-history'),

    # Ratings
    path('rate/driver/<int:ride_id>/', RateDriverView.as_view(), name='rate-driver'),
    path('rate/passenger/<int:ride_id>/', RatePassengerView.as_view(), name='rate-passenger'),
    path('accept/<int:ride_id>/', AcceptRideView.as_view(), name='accept-ride'),

]

