from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import DriverProfile, PassengerProfile
import base64

User = get_user_model()


def decode_base64(data):
    """Convert base64 string into raw bytes"""
    if not data:
        return None
    try:
        return base64.b64decode(data)
    except Exception:
        return None

class RegisterSerializer(serializers.ModelSerializer):
    vehicle_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    vehicle_model = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    vehicle_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    license_image = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    profile_image = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "phone",
            "password",
            "role",
            "profile_image",
            "vehicle_number",
            "vehicle_model",
            "vehicle_type",
            "license_image",
        )
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        role = validated_data.get("role")

        vehicle_number = validated_data.pop("vehicle_number", None)
        vehicle_model = validated_data.pop("vehicle_model", None)
        vehicle_type = validated_data.pop("vehicle_type", None)
        license_image = validated_data.pop("license_image", None)
        profile_image = validated_data.pop("profile_image", None)

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            phone=validated_data["phone"],
            role=role,
            password=validated_data["password"],
            profile_image=decode_base64(profile_image),
        )

        if role == "driver":
            DriverProfile.objects.update_or_create(
                user=user,
                defaults={
                    "vehicle_number": vehicle_number,
                    "vehicle_model": vehicle_model,
                    "vehicle_type": vehicle_type,
                    "license_image": decode_base64(license_image)
                    if license_image else None,
                }
            )

        if role == "passenger":
            PassengerProfile.objects.get_or_create(user=user)

        return user





class UserSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()
    driver_profile = serializers.SerializerMethodField()
    passenger_profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "phone",
            "role",
            "profile_image",
            "driver_profile",
            "passenger_profile",
        ]

    def get_profile_image(self, obj):
        if obj.profile_image:
            return base64.b64encode(obj.profile_image).decode('utf-8')
        return None

    def get_driver_profile(self, obj):
        if obj.role != "driver":
            return None

        try:
            dp = obj.driver_profile
            return {
                "vehicle_number": dp.vehicle_number,
                "vehicle_model": dp.vehicle_model,
                "vehicle_type": dp.vehicle_type,
                "is_available": dp.is_available,
                "license_image": base64.b64encode(dp.license_image).decode('utf-8') if dp.license_image else None,
            }
        except:
            return None

    def get_passenger_profile(self, obj):
        if obj.role != "passenger":
            return None

        try:
            pp = obj.passenger_profile
            return {
                "default_payment_method": pp.default_payment_method
            }
        except:
            return None



class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "phone"]


class DriverProfileSerializer(serializers.ModelSerializer):
    license_image = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )

    class Meta:
        model = DriverProfile
        fields = [
            "vehicle_number",
            "vehicle_model",
            "vehicle_type",
            "is_available",
            "license_image",
        ]

    def update(self, instance, validated_data):

        # vehicle fields
        for field in ["vehicle_number", "vehicle_model", "vehicle_type"]:
            if field in validated_data:
                value = validated_data.get(field)
                instance.__dict__[field] = value if value != "" else None

        # license image
        license_img = validated_data.get("license_image", None)
        if license_img == "" or license_img is None:
            instance.license_image = None
        elif license_img:
            instance.license_image = base64.b64decode(license_img)

        # availability
        if "is_available" in validated_data:
            instance.is_available = validated_data["is_available"]

        instance.save()
        return instance



class PassengerProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    phone = serializers.CharField(source="user.phone", read_only=True)
    role = serializers.CharField(source="user.role", read_only=True)

    class Meta:
        model = PassengerProfile
        fields = [
            "username",
            "email",
            "phone",
            "role",
        ]