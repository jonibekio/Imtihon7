from rest_framework import serializers

from django.utils import timezone

from profiles.models import Profile, ProfileRole


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"
        read_only_fields = ("user", "is_verified_seller")

    def validate_birth_date(self, value):
        if value and value > timezone.localdate():
            raise serializers.ValidationError("Tug'ilgan sana kelajakda bo'lishi mumkin emas")
        return value

    def validate_preferred_language(self, value):
        allowed_languages = {"uz", "ru", "en"}
        if value not in allowed_languages:
            raise serializers.ValidationError("Til faqat uz, ru yoki en bo'lishi mumkin")
        return value

    def validate(self, attrs):
        role = attrs.get("role", getattr(self.instance, "role", ProfileRole.BUYER))
        shop_name = attrs.get("shop_name", getattr(self.instance, "shop_name", ""))

        if role == ProfileRole.SELLER and not str(shop_name).strip():
            raise serializers.ValidationError({"shop_name": "Seller profil uchun shop_name majburiy"})

        return attrs
