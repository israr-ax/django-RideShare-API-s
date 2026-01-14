# from channels.generic.websocket import AsyncWebsocketConsumer
# import json

# class OnlineDriversConsumer(AsyncWebsocketConsumer):

#     async def connect(self):
#         await self.channel_layer.group_add("online_drivers", self.channel_name)
#         await self.accept()

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard("online_drivers", self.channel_name)

#     # When backend calls group_send("online_drivers")
#     async def new_ride_request(self, event):
#         await self.send(text_data=json.dumps({
#             "type": "new_ride_request",
#             "ride": event["ride"]   # send ride object
#         }))
