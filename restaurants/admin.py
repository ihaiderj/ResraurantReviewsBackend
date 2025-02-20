from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Restaurant, RestaurantImage, OperatingHours, 
    HolidayHours, RestaurantAmenities, VenueType, CuisineType,
    AmenityCategory, Amenity, Holiday
)
from django import forms
from django.db import models
from django.db.models import Count
from django.core.cache import cache
from django.contrib.admin.views.main import ChangeList
from users.models import User  # Import User from users app

# Custom admin site styling
class RestaurantAdminArea(admin.AdminSite):
    site_header = 'Restaurant Reviews Administration'
    site_title = 'Restaurant Reviews Admin Portal'
    index_title = 'Restaurant Management'

restaurant_admin_site = RestaurantAdminArea(name='restaurant_admin')

# Restaurant related inlines
class RestaurantImageInline(admin.TabularInline):
    model = RestaurantImage
    extra = 1

class OperatingHoursInline(admin.TabularInline):
    model = OperatingHours
    extra = 7

class HolidayHoursInline(admin.TabularInline):
    model = HolidayHours
    extra = 1

class RestaurantAmenitiesInline(admin.StackedInline):
    model = RestaurantAmenities
    filter_horizontal = ('selected_amenities',)
    
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "selected_amenities":
            kwargs["queryset"] = Amenity.objects.filter(is_active=True)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Enter additional amenities separated by commas (e.g., Rooftop Garden, Private Chef, Wine Cellar)'
        })},
    }

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('restaurant_name', 'owner', 'city', 'approval_status', 'created_at')
    list_filter = ('is_approved', 'city', 'state', 'venue_types', 'cuisine_styles', 'created_at')
    search_fields = ('name', 'owner__username', 'city')
    filter_horizontal = ('venue_types', 'cuisine_styles')
    inlines = [
        RestaurantImageInline,
        OperatingHoursInline,
        HolidayHoursInline,
        RestaurantAmenitiesInline
    ]
    actions = ['approve_restaurants']
    
    fieldsets = (
        ('Basic Information', {
            'classes': ('wide', 'extrapretty'),
            'fields': ('name', 'owner', 'logo', 'is_approved')
        }),
        ('Contact Details', {
            'fields': ('phone', 'email', 'website')
        }),
        ('Location', {
            'fields': ('country', 'street_address', 'room_number', 'city', 'state', 'postal_code', 'latitude', 'longitude')
        }),
        ('Classifications', {
            'fields': ('venue_types', 'cuisine_styles')
        }),
    )

    def restaurant_name(self, obj):
        return format_html(
            '<div style="font-size: 14px; font-weight: bold; color: #2c3e50;">'
            '{}</div>',
            obj.name
        )
    restaurant_name.short_description = 'Restaurant Name'

    def approval_status(self, obj):
        if obj.is_approved:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Approved</span>'
            )
        return format_html(
            '<span style="color: orange; font-weight: bold;">⌛ Pending</span>'
        )
    approval_status.short_description = 'Status'

    def approve_restaurants(self, request, queryset):
        queryset.update(is_approved=True)
    approve_restaurants.short_description = "Approve selected restaurants"

    class Media:
        css = {
            'all': ('admin/css/restaurant_admin.css',)
        }

# Other model admins (kept simple)
@admin.register(VenueType)
class VenueTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')

@admin.register(CuisineType)
class CuisineTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')

@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')

@admin.register(AmenityCategory)
class AmenityCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'created_at')
    search_fields = ('name', 'code')

@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'code', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'code', 'category__name')

class CustomAdminSite(admin.AdminSite):
    def index(self, request, extra_context=None):
        # Get stats from cache or database
        stats = cache.get('admin_dashboard_stats')
        if not stats:
            stats = {
                'total_restaurants': Restaurant.objects.count(),
                'pending_approvals': Restaurant.objects.filter(is_approved=False).count(),
                'active_users': User.objects.filter(is_active=True).count(),
            }
            cache.set('admin_dashboard_stats', stats, 300)  # Cache for 5 minutes

        extra_context = extra_context or {}
        extra_context.update(stats)
        return super().index(request, extra_context)

# Register your custom admin site
admin_site = CustomAdminSite()
