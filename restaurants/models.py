from django.db import models
from django.core.validators import URLValidator, RegexValidator
from users.models import User

class VenueType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class CuisineType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class AmenityCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Amenity Categories"
        ordering = ['name']

class Amenity(models.Model):
    category = models.ForeignKey(AmenityCategory, on_delete=models.CASCADE, related_name='amenities')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.category.name} - {self.name}"

    class Meta:
        verbose_name_plural = "Amenities"
        ordering = ['category', 'name']
        unique_together = ['category', 'code']

class Restaurant(models.Model):
    VENUE_TYPES = [
        ('FINE', 'Fine Dining'),
        ('CASUAL', 'Casual Dining'),
        ('FAMILY', 'Family Friendly'),
        ('HEALTHY', 'Healthy Food Options'),
        ('FAST', 'Fast Food'),
        ('TAKEAWAY', 'Take-away & Delivery'),
        ('CAFE', 'Cafés & Coffee Shops'),
        ('CATERING', 'Catering Services'),
    ]

    CUISINE_STYLES = [
        ('MIXED', 'Mixed Cuisines'),
        ('ITALIAN', 'Italian'),
        ('CHINESE', 'Chinese'),
        ('AUSTRALIAN', 'Australian'),
        ('INDIAN', 'Indian'),
        ('THAI', 'Thai'),
        ('JAPANESE', 'Japanese'),
        ('MEXICAN', 'Mexican'),
        ('MIDDLE_EASTERN', 'Middle Eastern'),
        ('GREEK', 'Greek'),
        ('AMERICAN', 'American'),
        ('SPANISH', 'Spanish'),
        ('FRENCH', 'French'),
        ('INDONESIAN', 'Indonesian'),
        ('ENGLISH', 'English'),
        ('PHILIPPINES', 'Philippines'),
        ('SINGAPORE', 'Singapore'),
        ('VIETNAMESE', 'Vietnamese'),
    ]

    # Basic Details
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='restaurants')
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    website = models.URLField(blank=True, validators=[URLValidator()])
    email = models.EmailField()
    
    # Address
    country = models.CharField(max_length=100)
    street_address = models.CharField(max_length=255)
    room_number = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Venue Type and Cuisine
    venue_types = models.ManyToManyField(VenueType, related_name='restaurants')
    cuisine_styles = models.ManyToManyField(CuisineType, related_name='restaurants')

    # Media
    logo = models.ImageField(upload_to='restaurant_logos/', null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class RestaurantImage(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='restaurant_images/')
    is_video_thumbnail = models.BooleanField(default=False)
    video_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class OperatingHours(models.Model):
    DAYS_OF_WEEK = [
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
        ('SAT', 'Saturday'),
        ('SUN', 'Sunday'),
    ]

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='operating_hours')
    day = models.CharField(max_length=3, choices=DAYS_OF_WEEK)
    open_time = models.TimeField()
    close_time = models.TimeField()
    is_closed = models.BooleanField(default=False)

class Holiday(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class HolidayHours(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='holiday_hours')
    holiday = models.ForeignKey(Holiday, on_delete=models.CASCADE, related_name='restaurant_hours')
    open_time = models.TimeField(null=True, blank=True)
    close_time = models.TimeField(null=True, blank=True)
    is_closed = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.restaurant.name} - {self.holiday.name}"

    class Meta:
        unique_together = ['restaurant', 'holiday']
        ordering = ['holiday__name']

class RestaurantAmenities(models.Model):
    restaurant = models.OneToOneField(Restaurant, on_delete=models.CASCADE, related_name='amenities')
    selected_amenities = models.ManyToManyField(Amenity, related_name='restaurants')
    additional_amenities = models.TextField(blank=True, help_text="Enter additional amenities separated by commas")

    def get_additional_amenities_list(self):
        if not self.additional_amenities:
            return []
        return [amenity.strip() for amenity in self.additional_amenities.split(',') if amenity.strip()]

    def __str__(self):
        return f"Amenities for {self.restaurant.name}"
