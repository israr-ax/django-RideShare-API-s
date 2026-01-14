import math
from django.contrib.auth import get_user_model

User = get_user_model()

def distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def find_nearest_driver(pickup_lat, pickup_lng):
    drivers = User.objects.filter(is_driver=True, is_available=True)

    nearest_driver = None
    min_distance = 999999

    for d in drivers:
        dist = distance(pickup_lat, pickup_lng, d.current_lat, d.current_lng)
        if dist < min_distance:
            min_distance = dist
            nearest_driver = d

    return nearest_driver
def calculate_fare(ride):
    """
    Simplified fare:
    total_fare = base_fare + (distance_km * per_km_rate) + (time_minutes * per_min_rate)
    For demo, distance/time are fixed or random.
    """
    base_fare = 50
    per_km_rate = 10
    per_min_rate = 2

    # if you want, you can calculate distance from pickup/drop coordinates using haversine
    distance_km = 10  # example static value
    time_minutes = 20  # example static value

    total_fare = base_fare + (distance_km * per_km_rate) + (time_minutes * per_min_rate)

    # Save fare object
    from .models import RideFare
    fare_obj, created = RideFare.objects.get_or_create(ride=ride)
    fare_obj.base_fare = base_fare
    fare_obj.distance_km = distance_km
    fare_obj.time_minutes = time_minutes
    fare_obj.total_fare = total_fare
    fare_obj.save()

    return {
        "base_fare": base_fare,
        "distance_km": distance_km,
        "time_minutes": time_minutes,
        "total_fare": total_fare
    }
