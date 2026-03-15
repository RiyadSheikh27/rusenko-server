from .models import *
from rest_framework import serializers
from django.conf import settings

def build_absolute_url(request, path):
    """Build absolute media URL."""
    if not path:
        return None
    if request:
        return request.build_absolute_url(f"{settings.MEDIA_URL}{path}")
    return f"{settings.MEDIA_URL}{path}"

# ----Review Serializer-----------------------------------------
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.profile:
            return build_absolute_url(request, obj.profile.name)
        return None
    
# --- Our Results Serializer-----------------------------------------
class OurResultImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = OurResultImages
        fields = ['id', 'image']

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image:
            return build_absolute_url(request, obj.image.name)
        return None

class OurResultSerializer(serializers.ModelSerializer):
    images = OurResultImageSerializer(many=True, read_only=True)

    class Meta:
        model = OurResults
        fields = ['id', 'title', 'subtitle', 'images']

# --- Request Quote Serializer-----------------------------------------
class RequestQuoteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = RequestQuote
        fields = [
            'id',
            'name',
            'profession',
            'email',
            'business_name',
            'location',
            'phone',
            'description',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']