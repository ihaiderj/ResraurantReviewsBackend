from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.utils.html import format_html
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'gender', 'profile_picture_display', 'is_staff', 'is_superuser')
    list_filter = ('user_type', 'gender', 'is_staff', 'is_superuser')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Additional Info', {
            'fields': ('user_type', 'phone_number', 'about_me', 'gender', 'profile_picture'),
            'classes': ('wide',)
        }),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
        ('Additional Info', {
            'classes': ('wide',),
            'fields': ('user_type', 'phone_number', 'about_me', 'gender', 'profile_picture'),
        }),
    )
    
    def profile_picture_display(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.profile_picture.url)
        return "No Image"
    profile_picture_display.short_description = 'Profile Picture'

    def save_model(self, request, obj, form, change):
        # If creating a new Website Admin, make them staff
        if obj.user_type == 'ADMIN':
            obj.is_staff = True
            
            # Get or create the Website Admins group
            admin_group, created = Group.objects.get_or_create(name='Website Admins')
            
            # If the group was just created, assign permissions
            if created:
                # Get all permissions for our apps
                admin_permissions = Permission.objects.filter(
                    content_type__app_label__in=['users', 'restaurants', 'reviews', 'menus']
                )
                admin_group.permissions.set(admin_permissions)
            
            # Save the user first
            super().save_model(request, obj, form, change)
            
            # Add user to the admin group
            obj.groups.add(admin_group)
        else:
            super().save_model(request, obj, form, change)
