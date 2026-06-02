from rest_framework import serializers
from accounts.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "phone_number", "avatar", "bio")

    def validate_email(self, value):
        if value and User.objects.exclude(id=getattr(self.instance, "id", None)).filter(email=value).exists():
            raise serializers.ValidationError("Bu email bilan foydalanuvchi mavjud")
        return value

    def validate_phone_number(self, value):
        if value and User.objects.exclude(id=getattr(self.instance, "id", None)).filter(phone_number=value).exists():
            raise serializers.ValidationError("Bu phone number bilan foydalanuvchi mavjud")
        return value

    def validate_avatar(self, avatar):
        if avatar and avatar.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Avatar hajmi 5MB dan oshmasligi kerak")
        return avatar

    def validate(self, attrs):
        email = attrs.get("email", getattr(self.instance, "email", None))
        phone_number = attrs.get("phone_number", getattr(self.instance, "phone_number", None))
        if not email and not phone_number:
            raise serializers.ValidationError("Email yoki phone numberdan kamida bittasi bo'lishi kerak")
        return attrs

    def update(self, instance, validated_data):
        if "email" in validated_data and validated_data["email"] != instance.email:
            instance.is_email_verified = False
        if "phone_number" in validated_data and validated_data["phone_number"] != instance.phone_number:
            instance.is_phone_verified = False
        return super().update(instance, validated_data)
