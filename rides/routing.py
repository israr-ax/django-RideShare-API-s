# rides/routing.py
from django.urls import re_path
from .consumers import OnlineDriversConsumer, RideRoomConsumer, RideTrackingConsumer



websocket_urlpatterns = [
    re_path(r"ws/online-drivers/$", OnlineDriversConsumer.as_asgi()),
    re_path(r"ws/ride/(?P<ride_id>\d+)/$", RideRoomConsumer.as_asgi()),
    re_path(r"ws/ride-tracking/(?P<ride_id>\d+)/$", RideTrackingConsumer.as_asgi()),
]
