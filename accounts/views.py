from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, UserSerializer, UpdateUserSerializer, DriverProfileSerializer, PassengerProfileSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view, permission_classes
from .tokens import MyTokenObtainPairSerializer
import base64
User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]



class UserDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        serializer = UpdateUserSerializer(self.get_object(), data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(self.get_object()).data)


# Optional: endpoints to update driver/passenger profiles
class DriverProfileUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = DriverProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return DriverProfile.objects.get(user=self.request.user)

class PassengerProfileUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = PassengerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.passenger_profile

# class PassengerProfileUpdateView(generics.RetrieveUpdateAPIView):
#     permission_classes = [permissions.IsAuthenticated]
#     serializer_class = PassengerProfileSerializer

#     def get_object(self):
#         return self.request.user.passenger_profile


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


# accounts/views_location.py
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import DriverProfile

User = get_user_model()


class DriverLocationUpdate(APIView):
    """
    POST { "lat": 24.8607, "lng": 67.0011 }
    Auth required (driver)
    Updates DriverProfile.current_lat/current_lng and notifies channel layer.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if getattr(user, "role", None) != "driver":
            return Response({"detail": "Forbidden: only drivers"}, status=status.HTTP_403_FORBIDDEN)

        lat = request.data.get("lat")
        lng = request.data.get("lng")

        if lat is None or lng is None:
            return Response({"detail": "lat and lng required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            dp = user.driver_profile
        except DriverProfile.DoesNotExist:
            return Response({"detail": "DriverProfile not found"}, status=status.HTTP_404_NOT_FOUND)

        # store coordinates
        dp.current_lat = lat
        dp.current_lng = lng
        dp.save(update_fields=["current_lat", "current_lng"])

        # broadcast to group 'online_drivers'
        channel_layer = get_channel_layer()
        payload = {
            "type": "driver.location",  # handler name in consumer
            "driver": {
                "id": user.id,
                "username": user.username,
                "lat": str(dp.current_lat),
                "lng": str(dp.current_lng),
                "vehicle_model": dp.vehicle_model,
                "vehicle_number": dp.vehicle_number,
                "is_available": dp.is_available,
                "profile_image": base64.b64encode(user.profile_image).decode("utf-8") if user.profile_image else None,
            }
            
        }
        # sync call to channel_layer
        async_to_sync(channel_layer.group_send)("online_drivers", payload)

        return Response({"ok": True})
