from django.db import models
from django.conf import settings   # <-- FIXED (Best practice)


class RideRequest(models.Model):
    passenger = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ride_passenger"
    )

    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_rides"
    )

    pickup_lat = models.FloatField()
    pickup_lng = models.FloatField()
    drop_lat = models.FloatField()
    drop_lng = models.FloatField()

    pickup_text = models.CharField(max_length=255, blank=True, null=True)
    drop_text   = models.CharField(max_length=255, blank=True, null=True)
    ride_type   = models.CharField(max_length=32, blank=True, null=True)

    status = models.CharField(max_length=20, default="pending")
    request_time = models.DateTimeField(auto_now_add=True)

    driver_rating = models.IntegerField(null=True, blank=True)
    passenger_rating = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Ride {self.id} - {self.passenger}"


class RideTracking(models.Model):
    ride = models.OneToOneField(
        RideRequest,
        on_delete=models.CASCADE,
        related_name="tracking"
    )
    driver_lat = models.FloatField(default=0)
    driver_lng = models.FloatField(default=0)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Tracking for ride {self.ride.id}"


class RideFare(models.Model):
    ride = models.OneToOneField(
        RideRequest,
        on_delete=models.CASCADE,
        related_name="fare"
    )
    base_fare = models.FloatField(default=50)
    distance_km = models.FloatField(default=0)
    time_minutes = models.FloatField(default=0)
    total_fare = models.FloatField(default=0)

    def __str__(self):
        return f"Fare for ride {self.ride.id}"
