from rest_framework import serializers
from .models import RideRequest, RideTracking, RideFare

# rides/serializers.py
class RideRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RideRequest
        fields = [
            'id','passenger','driver','pickup_lat','pickup_lng','drop_lat','drop_lng',
            'pickup_text','drop_text','ride_type','status','request_time',
            'passenger_rating','driver_rating'
        ]
        read_only_fields = ['id','passenger','driver','status','request_time']


    def create(self, validated_data):
        # Assign logged-in user as passenger
        user = self.context['request'].user
        validated_data['passenger'] = user
        validated_data['status'] = "pending"
        return super().create(validated_data)


class RideTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = RideTracking
        fields = '__all__'


class RideFareSerializer(serializers.ModelSerializer):
    class Meta:
        model = RideFare
        fields = '__all__'

class RideRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = RideRequest
        fields = ['id', 'driver_rating', 'passenger_rating']
        read_only_fields = ['id']
        
class RideHistorySerializer(serializers.ModelSerializer):
    driver_name = serializers.CharField(source='driver.username', read_only=True)
    passenger_name = serializers.CharField(source='passenger.username', read_only=True)
    fare = serializers.SerializerMethodField()

    class Meta:
        model = RideRequest
        fields = ['id', 'pickup_lat', 'pickup_lng', 'drop_lat', 'drop_lng', 'status', 'request_time', 'driver_name', 'passenger_name', 'driver_rating', 'passenger_rating', 'fare']

    def get_fare(self, obj):
        if hasattr(obj, 'fare'):
            return {
                "total_fare": obj.fare.total_fare,
                "distance_km": obj.fare.distance_km,
                "time_minutes": obj.fare.time_minutes
            }
        return None
