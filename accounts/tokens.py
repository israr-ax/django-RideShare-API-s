import base64
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role        # JWT claim
        token["username"] = user.username
        return token

    def validate(self, attrs):
        # 🔥 PROOF
        print("🔥🔥🔥 MY TOKEN SERIALIZER HIT 🔥🔥🔥")

        # 1️⃣ Get default token response
        data = super().validate(attrs)

        # 2️⃣ Logged-in user
        user = self.user

        # 3️⃣ Profile image (safe)
        profile_image_b64 = None
        img = getattr(user, "profile_image", None)
        if isinstance(img, (bytes, bytearray)):
            profile_image_b64 = base64.b64encode(img).decode("utf-8")

        # 4️⃣ ADD EXTRA DATA TO SAME `data`
        data["role"] = user.role
        data["user"] = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "phone": getattr(user, "phone", None),
            "role": user.role,
            "profile_image": profile_image_b64,
        }

        # 5️⃣ RETURN MODIFIED DATA (THIS WAS MISSING / WRONG)
        return data
