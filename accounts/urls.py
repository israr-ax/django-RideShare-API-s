# accounts/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from .tokens import MyTokenObtainPairSerializer
from .views import RegisterView, UserDetailView, DriverProfileUpdateView, PassengerProfileUpdateView
from django.urls import path
from .views import MyTokenObtainPairView


# create a view class that uses your custom serializer
# class MyTokenObtainPairView(TokenObtainPairView):
#     serializer_class = MyTokenObtainPairSerializer

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path("login/", MyTokenObtainPairView.as_view(), name="login"),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', UserDetailView.as_view(), name='me'),
    path('driver/profile/', DriverProfileUpdateView.as_view(), name='driver_profile'),
    path('passenger/profile/', PassengerProfileUpdateView.as_view(), name='passenger_profile'),
]
# accounts/urls.py (add this import + path)
from .views import DriverLocationUpdate

urlpatterns += [
    path('driver/location/', DriverLocationUpdate.as_view(), name='driver_location'),
]
