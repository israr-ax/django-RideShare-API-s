import json
from channels.generic.websocket import AsyncWebsocketConsumer, AsyncJsonWebsocketConsumer

# ===============================
# 1️⃣ RIDE ROOM (status updates)
# ws/ride/<ride_id>/
# ===============================

class RideRoomConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.ride_id = self.scope["url_route"]["kwargs"]["ride_id"]
        self.group_name = f"ride_{self.ride_id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

        print("✅ RIDE ROOM CONNECTED:", self.group_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # ONLY ride status updates come here
    async def send_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))


# ===============================
# 2️⃣ LIVE TRACKING
# ws/ride-tracking/<ride_id>/
# ===============================

class RideTrackingConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.ride_id = self.scope["url_route"]["kwargs"]["ride_id"]
        self.group_name = f"ride_tracking_{self.ride_id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

        print("🟢 TRACKING SOCKET CONNECTED:", self.group_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Driver sends location
    async def receive_json(self, content):

        print("📥 SERVER RECEIVED:", content)

        if "lat" not in content or "lng" not in content:
            return

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "broadcast_location",
                "lat": content["lat"],
                "lng": content["lng"],
            }
        )

    # Passenger receives location
    async def broadcast_location(self, event):
        await self.send_json({
            "type": "driver_location",
            "driver_lat": event["lat"],
            "driver_lng": event["lng"],
        })


# ===============================
# 3️⃣ ONLINE DRIVERS
# ws/online-drivers/
# ===============================

class OnlineDriversConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.channel_layer.group_add(
            "online_drivers",
            self.channel_name
        )
        await self.accept()

        print("🚗 DRIVER ONLINE")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            "online_drivers",
            self.channel_name
        )

    async def new_ride_request(self, event):
        await self.send(text_data=json.dumps(event["ride"]))
