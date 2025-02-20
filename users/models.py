from django.contrib.auth.models import AbstractUser
from django.db import models
import os

# Create your models here.

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('CUSTOMER', 'Customer'),
        ('OWNER', 'Restaurant Owner'),
        ('ADMIN', 'Website Admin'),
    )
    
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('N', 'Prefer not to say')
    )
    
    # Add related_name to avoid clashes
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to.',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.',
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    about_me = models.TextField(blank=True)
    gender = models.CharField(
        max_length=1, 
        choices=GENDER_CHOICES, 
        default='N',
        blank=True
    )
    
    
    def is_restaurant_owner(self):
        return self.user_type == 'OWNER'
        
    def is_website_admin(self):
        return self.user_type == 'ADMIN'
        
    def is_customer(self):
        return self.user_type == 'CUSTOMER'

    def save(self, *args, **kwargs):
        # If this is an update and there's a new profile picture
        if self.pk:
            try:
                old_instance = User.objects.get(pk=self.pk)
                if old_instance.profile_picture and self.profile_picture != old_instance.profile_picture:
                    # Delete the old profile picture
                    if os.path.isfile(old_instance.profile_picture.path):
                        os.remove(old_instance.profile_picture.path)
            except User.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Delete the profile picture file when the user is deleted
        if self.profile_picture:
            if os.path.isfile(self.profile_picture.path):
                os.remove(self.profile_picture.path)
        super().delete(*args, **kwargs)
