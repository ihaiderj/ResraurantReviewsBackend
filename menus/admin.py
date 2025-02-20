from django.contrib import admin
from .models import MenuCategory, PricingTitle, MenuDesign, MenuDesignCategory, MenuDesignPricing, SpiceLevel, DietaryRequirement, ReligiousRestriction, Allergen, PortionSize, MenuItem, MenuItemPortion, MenuItemPrice, MenuItemImage

@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'is_default', 'created_at')
    list_filter = ('is_active', 'is_default')
    search_fields = ('name', 'code', 'description')
    prepopulated_fields = {'code': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'description')
        }),
        ('Category Details', {
            'fields': ('special_notes', 'is_active', 'is_default')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(PricingTitle)
class PricingTitleAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'display_order', 'is_active', 'is_default')
    list_filter = ('is_active', 'is_default')
    search_fields = ('name', 'code', 'description')
    prepopulated_fields = {'code': ('name',)}
    ordering = ['display_order', 'name']

class MenuDesignCategoryInline(admin.TabularInline):
    model = MenuDesignCategory
    extra = 1

class MenuDesignPricingInline(admin.TabularInline):
    model = MenuDesignPricing
    extra = 1

@admin.register(MenuDesign)
class MenuDesignAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'is_active', 'is_multiple_pricing', 'created_at')
    list_editable = ('is_active',)
    list_filter = ('is_active', 'is_multiple_pricing', 'created_at')
    inlines = [MenuDesignCategoryInline, MenuDesignPricingInline]
    fieldsets = (
        (None, {
            'fields': ('restaurant', 'is_active', 'is_multiple_pricing')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    search_fields = ('restaurant__name',)

    def get_inline_instances(self, request, obj=None):
        """Control the order of inline forms and pricing section"""
        inline_instances = [MenuDesignCategoryInline(self.model, self.admin_site)]
        
        show_pricing = (
            (obj and obj.is_multiple_pricing) or
            (request.method == 'POST' and request.POST.get('is_multiple_pricing')) or
            (request.method == 'GET' and request.GET.get('is_multiple_pricing'))
        )
        
        if show_pricing:
            inline_instances.append(MenuDesignPricingInline(self.model, self.admin_site))
        
        return inline_instances

    class Media:
        css = {
            'all': ('admin/css/menu_design.css',)
        }
        js = ('admin/js/menu_design.js',)

@admin.register(SpiceLevel)
class SpiceLevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'display_order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')
    prepopulated_fields = {'code': ('name',)}

@admin.register(DietaryRequirement)
class DietaryRequirementAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'display_order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')
    prepopulated_fields = {'code': ('name',)}

@admin.register(ReligiousRestriction)
class ReligiousRestrictionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')
    prepopulated_fields = {'code': ('name',)}

@admin.register(Allergen)
class AllergenAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')
    prepopulated_fields = {'code': ('name',)}

@admin.register(PortionSize)
class PortionSizeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'display_order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')
    prepopulated_fields = {'code': ('name',)}

class MenuItemPriceInline(admin.TabularInline):
    model = MenuItemPrice
    extra = 1

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "pricing_title":
            # Get restaurant from parent object
            obj = getattr(request, '_obj', None)
            restaurant_id = obj.restaurant_id if obj else request.GET.get('restaurant')
            
            if restaurant_id:
                kwargs["queryset"] = PricingTitle.objects.filter(
                    menudesignpricing__menu_design__restaurant_id=restaurant_id,
                    menudesignpricing__menu_design__is_active=True
                ).distinct()
            else:
                kwargs["queryset"] = PricingTitle.objects.none()
                
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class MenuItemPortionInline(admin.TabularInline):
    model = MenuItemPortion
    extra = 1

class MenuItemImageInline(admin.TabularInline):
    model = MenuItemImage
    extra = 1

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'menu_category', 'is_active')
    list_filter = ('restaurant', 'menu_category', 'is_active')
    search_fields = ('name', 'description')
    inlines = [MenuItemPortionInline, MenuItemPriceInline, MenuItemImageInline]
    filter_horizontal = ('dietary_requirements', 'religious_restrictions', 'allergens')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('restaurant', 'menu_category', 'name', 'description')
        }),
        ('Dietary Information', {
            'fields': ('spice_level', 'dietary_requirements', 'religious_restrictions', 'allergens')
        }),
        
        ('Display Settings', {
            'fields': ('display_order', 'is_active')
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        # Store the object reference in the request for inlines to access
        request._obj = obj
        return super().get_form(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "menu_category":
            restaurant_id = None
            
            # Get restaurant ID from either existing object or URL parameters
            if request.resolver_match.kwargs.get('object_id'):
                obj = self.get_object(request, request.resolver_match.kwargs['object_id'])
                restaurant_id = obj.restaurant_id if obj else None
            else:
                restaurant_id = request.GET.get('restaurant')

            if restaurant_id:
                # Get categories through the active menu design
                kwargs["queryset"] = MenuCategory.objects.filter(
                    menudesigncategory__menu_design__restaurant_id=restaurant_id,
                    menudesigncategory__menu_design__is_active=True
                ).distinct().prefetch_related('menudesigncategory_set')
            else:
                kwargs["queryset"] = MenuCategory.objects.none()
                
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        restaurant_id = request.GET.get('restaurant') or (obj.restaurant_id if obj else None)
        
        if restaurant_id:
            try:
                menu_design = MenuDesign.objects.get(
                    restaurant_id=restaurant_id,
                    is_active=True
                )
                form.base_fields['has_multiple_prices'].initial = menu_design.is_multiple_pricing
                form.base_fields['has_multiple_prices'].disabled = True  # Make read-only
            except MenuDesign.DoesNotExist:
                pass
                
        return form

    class Media:
        js = ('admin/js/menu_item.js',)
