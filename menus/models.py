from django.db import models
from django.utils.text import slugify
from restaurants.models import Restaurant
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class MenuCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    special_notes = models.TextField(blank=True, help_text="Add any special notes for this category (e.g., 'Breakfast served 6am - 10:30am')")
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False, help_text="If true, this is a pre-defined category")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Menu Category"
        verbose_name_plural = "Menu Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = slugify(self.name)
        super().save(*args, **kwargs)

class PricingTitle(models.Model):
    name = models.CharField(max_length=50, unique=True)
    code = models.SlugField(max_length=50, unique=True, blank=True)
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False, help_text="If true, this is a pre-defined pricing title")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pricing Title"
        verbose_name_plural = "Pricing Titles"
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = slugify(self.name)
        super().save(*args, **kwargs)

class MenuDesign(models.Model):
    restaurant = models.OneToOneField(
        'restaurants.Restaurant',
        on_delete=models.CASCADE,
        related_name='menu_design'
    )
    is_multiple_pricing = models.BooleanField(
        default=False,
        help_text='If true, menu will show multiple pricing options'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Menu Design for {self.restaurant.name}"

class MenuDesignCategory(models.Model):
    menu_design = models.ForeignKey(MenuDesign, on_delete=models.CASCADE, related_name='categories')
    category = models.ForeignKey(MenuCategory, on_delete=models.PROTECT, related_name='menu_designs')
    special_notes = models.TextField(blank=True, help_text="Special notes specific to this category for this restaurant")
    display_order = models.PositiveIntegerField(default=0)
    is_custom = models.BooleanField(default=False, help_text="If true, this is a custom category for this restaurant only")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order']
        verbose_name = "Menu Design Category"
        verbose_name_plural = "Menu Design Categories"

    def __str__(self):
        try:
            return f"{self.category.name} - {self.menu_design.restaurant.name}"
        except MenuCategory.DoesNotExist:
            return f"Unknown Category - {self.menu_design.restaurant.name}"

class MenuDesignPricing(models.Model):
    menu_design = models.ForeignKey(MenuDesign, on_delete=models.CASCADE, related_name='pricing_titles')
    pricing_title = models.ForeignKey(PricingTitle, on_delete=models.PROTECT, related_name='menu_designs')
    display_order = models.PositiveIntegerField(default=0)
    is_custom = models.BooleanField(default=False, help_text="If true, this is a custom pricing title for this restaurant only")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order']
        verbose_name = "Menu Design Pricing"
        verbose_name_plural = "Menu Design Pricing Options"

    def __str__(self):
        return f"{self.pricing_title.name} - {self.menu_design.restaurant.name}"

class SpiceLevel(models.Model):
    name = models.CharField(max_length=50, unique=True)
    code = models.SlugField(max_length=50, unique=True, blank=True)
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = slugify(self.name)
        super().save(*args, **kwargs)

class DietaryRequirement(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.SlugField(max_length=50, unique=True, blank=True)
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'name']

    def __str__(self):
        return f"{self.name} ({self.code})"

class ReligiousRestriction(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.SlugField(max_length=50, unique=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"

class Allergen(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.SlugField(max_length=50, unique=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class PortionSize(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.SlugField(max_length=50, unique=True, blank=True)
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    restaurant = models.ForeignKey('restaurants.Restaurant', on_delete=models.CASCADE)
    menu_category = models.ForeignKey(MenuCategory, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    has_multiple_prices = models.BooleanField(default=False)
    spice_level = models.ForeignKey(SpiceLevel, on_delete=models.SET_NULL, null=True, blank=True)
    dietary_requirements = models.ManyToManyField(DietaryRequirement, blank=True)
    religious_restrictions = models.ManyToManyField(ReligiousRestriction, blank=True)
    allergens = models.ManyToManyField(Allergen, blank=True)
    has_multiple_portions = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['menu_category', 'display_order', 'name']
        verbose_name = "Menu Item"
        verbose_name_plural = "Menu Items"

    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"

class MenuItemPortion(models.Model):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='portions')
    portion_size = models.ForeignKey(PortionSize, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(2), MaxValueValidator(100)])
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order']
        unique_together = ['menu_item', 'portion_size']

class MenuItemPrice(models.Model):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='prices')
    portion = models.ForeignKey(MenuItemPortion, on_delete=models.CASCADE, null=True, blank=True)
    pricing_title = models.ForeignKey(PricingTitle, on_delete=models.PROTECT, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ['menu_item', 'portion', 'pricing_title']

class MenuItemImage(models.Model):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='menu_items/')
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order']
