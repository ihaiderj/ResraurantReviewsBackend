from rest_framework import serializers
from .models import (
    Restaurant, RestaurantImage, OperatingHours, 
    HolidayHours, RestaurantAmenities, VenueType, CuisineType, Amenity, Holiday
)

class RestaurantImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantImage
        fields = ['id', 'image', 'is_video_thumbnail', 'video_url', 'created_at']

class OperatingHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperatingHours
        fields = ['id', 'day', 'open_time', 'close_time', 'is_closed']

class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = ['id', 'name', 'code', 'description', 'is_active']

class HolidayHoursSerializer(serializers.ModelSerializer):
    holiday_name = serializers.CharField(source='holiday.name', read_only=True)
    holiday_code = serializers.CharField(source='holiday.code', read_only=True)
    
    class Meta:
        model = HolidayHours
        fields = ['id', 'holiday', 'holiday_name', 'holiday_code', 'open_time', 'close_time', 'is_closed']

class AmenitySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Amenity
        fields = ['id', 'category', 'category_name', 'name', 'code', 'description', 'is_active']

class RestaurantAmenitiesSerializer(serializers.ModelSerializer):
    selected_amenities = AmenitySerializer(many=True, read_only=True)
    selected_amenity_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Amenity.objects.filter(is_active=True),
        source='selected_amenities'
    )
    additional_amenities_list = serializers.SerializerMethodField()

    class Meta:
        model = RestaurantAmenities
        fields = ['selected_amenities', 'selected_amenity_ids', 'additional_amenities', 'additional_amenities_list']

    def get_additional_amenities_list(self, obj):
        return obj.get_additional_amenities_list()

    def validate_additional_amenities(self, value):
        if value:
            # Remove any extra whitespace and ensure proper comma separation
            amenities = [item.strip() for item in value.split(',')]
            return ', '.join(filter(None, amenities))
        return value

class VenueTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VenueType
        fields = ['id', 'name', 'code', 'description']

class CuisineTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuisineType
        fields = ['id', 'name', 'code', 'description']

class RestaurantSerializer(serializers.ModelSerializer):
    images = RestaurantImageSerializer(many=True, read_only=True)
    operating_hours = OperatingHoursSerializer(many=True, read_only=True)
    holiday_hours = HolidayHoursSerializer(many=True, read_only=True)
    amenities = RestaurantAmenitiesSerializer(read_only=True)
    venue_types = VenueTypeSerializer(many=True, read_only=True)
    cuisine_styles = CuisineTypeSerializer(many=True, read_only=True)
    venue_type_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, queryset=VenueType.objects.filter(is_active=True),
        source='venue_types'
    )
    cuisine_style_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, queryset=CuisineType.objects.filter(is_active=True),
        source='cuisine_styles'
    )

    class Meta:
        model = Restaurant
        fields = '__all__'
        read_only_fields = ['owner', 'is_approved', 'created_at', 'updated_at']

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['owner'] = request.user
        return super().create(validated_data) 