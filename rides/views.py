# rides/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import RideRequest, RideTracking
from .serializers import RideRequestSerializer, RideHistorySerializer, RideRatingSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync



# ---------------------------------------------
# 1. CREATE RIDE REQUEST (Passenger)
# ---------------------------------------------
class CreateRideRequest(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RideRequestSerializer(data=request.data, context={'request': request})


        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        # Create ride
        ride = serializer.save(passenger=request.user, status="PENDING")

        # Broadcast ride request to ALL online drivers
        channel_layer = get_channel_layer()
        
        async_to_sync(channel_layer.group_send)(
            
        "online_drivers",
        {
            "type": "new_ride_request",
            "ride": {
                "id": ride.id,
                "passenger_name": request.user.username,

                # 👇 EXACT keys Android expects
                "from_location": ride.pickup_text or "Pickup Location",
                "to_location": ride.drop_text or "Drop Location",

                # raw coords
                "pickup_lat": ride.pickup_lat,
                "pickup_lng": ride.pickup_lng,
                "drop_lat": ride.drop_lat,
                "drop_lng": ride.drop_lng,
            }
        }
    )
        print("CREATE_RIDE:",request.user.username,request.data)
        return Response({
            "message": "Ride request created. Waiting for a driver...",
            "ride_id": ride.id
        }, status=201)



# ---------------------------------------------
# 2. DRIVER ACCEPTS RIDE
# ---------------------------------------------
class AcceptRideView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, ride_id):
        try:
            ride = RideRequest.objects.get(id=ride_id)
        except RideRequest.DoesNotExist:
            return Response({"error": "Ride not found"}, status=404)

        # If already taken — deny
        if ride.driver:
            return Response({"error": "Ride already accepted by another driver"}, status=409)

        # Assign driver
        ride.driver = request.user
        ride.status = "ACCEPTED"
        ride.save()

        # create tracking automatically
        RideTracking.objects.create(ride=ride)

        # Notify passenger via WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"ride_{ride.id}",   # ✅ SAME GROUP AS RideRoomConsumer
            {
                "type": "send_update",
                "data": {
                    "status": "ACCEPTED",
                    "driver_name": request.user.username,
                    "driver_id": request.user.id
                    
                }
            }
        )


        return Response({"message": "Ride accepted successfully"}, status=200)



# ---------------------------------------------
# 3. START TRIP
# ---------------------------------------------


class StartRideView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, ride_id):

        try:
            ride = RideRequest.objects.get(id=ride_id)
        except RideRequest.DoesNotExist:
            return Response(
                {"error": "Ride not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # 🔒 Only assigned driver can start
        if ride.driver != request.user:
            return Response(
                {"error": "Not allowed"},
                status=status.HTTP_403_FORBIDDEN
            )
        print("Ride driver:", ride.driver)
        print("Request user:", request.user)
        print("Ride status before:", ride.status) 

    
        # 🚫 Prevent double start
        if ride.status == "STARTED":
            return Response(
                {"message": "Ride already started"},
                status=status.HTTP_200_OK
            )

        # ✅ START RIDE
        ride.status = "STARTED"

        ride.save()
        print("Ride status before:", ride.status)   
 


        # 🔥 Notify passenger via socket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"ride_{ride.id}",
            {
                "type": "send_update",
                "data": {
                    "status": "STARTED"
                }
            }
        )

        return Response(
            {"message": "Ride started"},
            status=status.HTTP_200_OK
        )




# ---------------------------------------------
# 4. END TRIP
# ---------------------------------------------
from .utils import calculate_fare

class EndRideView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, ride_id):
        try:
            ride = RideRequest.objects.get(id=ride_id)
        except RideRequest.DoesNotExist:
            return Response({"error": "Ride not found"}, status=404)

        if ride.driver != request.user:
            return Response({"error": "Not allowed"}, status=403)

        if ride.status != "STARTED":
            return Response({"error": "Ride not started"}, status=400)

        # ✅ END RIDE
        ride.status = "COMPLETED"
        ride.save(update_fields=["status"])
        print("Ride driver:", ride.driver)
        print("Request user:", request.user)
        print("Ride status before:", ride.status) 

        fare = calculate_fare(ride)  # ya simple logic

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"ride_{ride.id}",
            {
                "type": "send_update",
                "data": {
                    "status": "COMPLETED",
                    "fare": fare
                }
            }
        )

        return Response({
            "message": "Ride completed",
            "fare": fare
        }, status=200)



# ---------------------------------------------
# RIDE HISTORY
# ---------------------------------------------
class PassengerRideHistory(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rides = RideRequest.objects.filter(passenger=request.user).order_by('-request_time')
        return Response(RideHistorySerializer(rides, many=True).data, status=200)


class DriverRideHistory(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rides = RideRequest.objects.filter(driver=request.user).order_by('-request_time')
        return Response(RideHistorySerializer(rides, many=True).data, status=200)
# ---------------------------------------------------
# RIDE RATINGS
# ---------------------------------------------------
class RateDriverView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, ride_id):
        try:
            ride = RideRequest.objects.get(id=ride_id, passenger=request.user, status="completed")
        except RideRequest.DoesNotExist:
            return Response({"error": "Ride not found or not eligible"}, status=404)

        rating = request.data.get("rating")

        if rating is None or not (1 <= int(rating) <= 5):
            return Response({"error": "Rating must be between 1–5"}, status=400)

        ride.driver_rating = rating
        ride.save()

        return Response({"message": "Driver rated successfully"}, status=200)


class RatePassengerView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, ride_id):
        try:
            ride = RideRequest.objects.get(id=ride_id, driver=request.user, status="completed")
        except RideRequest.DoesNotExist:
            return Response({"error": "Ride not found or not eligible"}, status=404)

        rating = request.data.get("rating")

        if rating is None or not (1 <= int(rating) <= 5):
            return Response({"error": "Rating must be between 1–5"}, status=400)

        ride.passenger_rating = rating
        ride.save()

        return Response({"message": "Passenger rated successfully"}, status=200)
    
    
# GET /api/rides/<ride_id>/detail/
class RideDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, ride_id):
        try:
            ride = RideRequest.objects.get(id=ride_id)
        except RideRequest.DoesNotExist:
            return Response({"error": "Ride not found"}, status=404)

        return Response({
            "ride_id": ride.id,
            "pickup_lat": ride.pickup_lat,
            "pickup_lng": ride.pickup_lng,
            "drop_lat": ride.drop_lat,
            "drop_lng": ride.drop_lng,
            "status": ride.status
        }, status=200)
