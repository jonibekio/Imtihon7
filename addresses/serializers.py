from rest_framework import serializers
from addresses.models import UserAddress

class UserAddressSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = UserAddress
        fields = "__all__"

    def validate(self, attrs):
        required_text_fields = ("title", "country", "city", "district", "address")
        for field in required_text_fields:
            value = attrs.get(field, getattr(self.instance, field, None))
            if isinstance(value, str) and not value.strip():
                raise serializers.ValidationError({field: "Bu maydon bo'sh bo'lishi mumkin emas"})

        latitude = attrs.get("latitude", getattr(self.instance, "latitude", None))
        longitude = attrs.get("longitude", getattr(self.instance, "longitude", None))

        if latitude is not None and not (-90 <= latitude <= 90):
            raise serializers.ValidationError({"latitude": "Latitude -90 va 90 oralig'ida bo'lishi kerak"})

        if longitude is not None and not (-180 <= longitude <= 180):
            raise serializers.ValidationError({"longitude": "Longitude -180 va 180 oralig'ida bo'lishi kerak"})

        if (latitude is None) != (longitude is None):
            raise serializers.ValidationError("Latitude va longitude birga yuborilishi kerak")

        return attrs
