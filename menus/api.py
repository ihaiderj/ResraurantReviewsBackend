from ninja import Router, Schema
from typing import List
from django.shortcuts import get_object_or_404
from .models import MenuCategory, PricingTitle, MenuDesign, MenuDesignCategory, MenuDesignPricing, SpiceLevel, DietaryRequirement, ReligiousRestriction, Allergen, PortionSize, MenuItem, MenuItemPortion, MenuItemPrice, MenuItemImage
from django.utils.timezone import datetime
from restaurants.models import Restaurant
from rest_framework.response import Response
from rest_framework import status
from ninja.errors import HttpError
from django.http import JsonResponse

router = Router()

# Schemas
class MenuCategoryOut(Schema):
    id: int
    name: str
    code: str
    description: str | None
    special_notes: str | None
    is_active: bool

class MenuCategoryCreate(Schema):
    name: str
    description: str | None = None
    special_notes: str | None = None
    is_active: bool = True

# Pricing Title Schemas
class PricingTitleOut(Schema):
    id: int
    name: str
    code: str
    description: str | None
    display_order: int
    is_active: bool

class PricingTitleCreate(Schema):
    name: str
    description: str | None = None
    display_order: int = 0
    is_active: bool = True

# Menu Design Schemas
class MenuDesignCategoryBase(Schema):
    category_id: int
    special_notes: str | None = None
    display_order: int = 0

class MenuDesignPricingBase(Schema):
    pricing_title_id: int
    display_order: int = 0

class MenuDesignCreate(Schema):
    restaurant_id: int
    is_multiple_pricing: bool = False
    categories: List[MenuDesignCategoryBase]
    pricing_titles: List[MenuDesignPricingBase] | None = None

class MenuDesignCategoryOut(Schema):
    id: int
    category: MenuCategoryOut
    special_notes: str | None
    display_order: int
    is_custom: bool

class MenuDesignPricingOut(Schema):
    id: int
    pricing_title: PricingTitleOut
    display_order: int
    is_custom: bool

class MenuDesignCategorySimple(Schema):
    id: int
    name: str

class MenuDesignPricingSimple(Schema):
    id: int
    name: str

class MenuDesignOut(Schema):
    id: int
    is_multiple_pricing: bool
    categories: List[MenuDesignCategorySimple]
    pricing_titles: List[MenuDesignPricingSimple]

# Menu Item Related Schemas
class MenuItemPortionBase(Schema):
    portion_size_id: int
    quantity: int
    display_order: int = 0

class MenuItemPriceBase(Schema):
    portion_id: int | None = None
    pricing_title_id: int | None = None
    price: float

class MenuItemCreate(Schema):
    restaurant_id: int
    menu_category_id: int
    name: str
    description: str
    spice_level_id: int | None = None
    dietary_requirement_ids: List[int] | None = None
    religious_restriction_ids: List[int] | None = None
    allergen_ids: List[int] | None = None
    has_multiple_portions: bool = False
    portions: List[MenuItemPortionBase] | None = None
    prices: List[MenuItemPriceBase]
    display_order: int = 0

class MenuItemUpdate(Schema):
    name: str | None = None
    description: str | None = None
    spice_level_id: int | None = None
    dietary_requirement_ids: List[int] | None = None
    religious_restriction_ids: List[int] | None = None
    allergen_ids: List[int] | None = None
    has_multiple_portions: bool | None = None
    display_order: int | None = None
    is_active: bool | None = None

class MenuItemPortionOut(Schema):
    id: int
    portion_size: str
    quantity: int
    display_order: int

class MenuItemPriceOut(Schema):
    id: int
    portion: MenuItemPortionOut | None = None
    pricing_title: str | None = None
    price: float

class MenuItemImageOut(Schema):
    id: int
    image: str
    display_order: int

class MenuItemOut(Schema):
    id: int
    restaurant_id: int
    menu_category: str
    name: str
    description: str
    spice_level: str | None
    dietary_requirements: List[str]
    religious_restrictions: List[str]
    allergens: List[str]
    has_multiple_portions: bool
    portions: List[MenuItemPortionOut]
    prices: List[MenuItemPriceOut]
    images: List[MenuItemImageOut]
    display_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

# API Endpoints
@router.get("/categories/", response=List[MenuCategoryOut])
def list_categories(request):
    """Get all active menu categories"""
    return MenuCategory.objects.filter(is_active=True)

@router.post("/categories/", response=MenuCategoryOut)
def create_category(request, payload: MenuCategoryCreate):
    """Create a new menu category"""
    category = MenuCategory.objects.create(**payload.dict())
    return category

@router.get("/categories/{category_id}/", response=MenuCategoryOut)
def get_category(request, category_id: int):
    """Get a specific menu category"""
    return get_object_or_404(MenuCategory, id=category_id)

# Pricing Title Endpoints
@router.get("/pricing-titles/", response=List[PricingTitleOut])
def list_pricing_titles(request):
    """Get all active pricing titles"""
    return PricingTitle.objects.filter(is_active=True)

@router.post("/pricing-titles/", response=PricingTitleOut)
def create_pricing_title(request, payload: PricingTitleCreate):
    """Create a new pricing title"""
    pricing_title = PricingTitle.objects.create(**payload.dict())
    return pricing_title

@router.get("/pricing-titles/{title_id}/", response=PricingTitleOut)
def get_pricing_title(request, title_id: int):
    """Get a specific pricing title"""
    return get_object_or_404(PricingTitle, id=title_id)

# Menu Design Endpoints
@router.post("/menu-designs/", response=MenuDesignOut)
def create_menu_design(request, payload: MenuDesignCreate):
    """Create a new menu design for a restaurant"""
    restaurant = get_object_or_404(Restaurant, id=payload.restaurant_id)
    
    # Create menu design
    menu_design = MenuDesign.objects.create(
        restaurant=restaurant,
        is_multiple_pricing=payload.is_multiple_pricing
    )
    
    # Add categories
    for cat in payload.categories:
        category = get_object_or_404(MenuCategory, id=cat.category_id)
        MenuDesignCategory.objects.create(
            menu_design=menu_design,
            category=category,
            special_notes=cat.special_notes,
            display_order=cat.display_order
        )
    
    # Add pricing titles if multiple pricing is enabled
    if payload.is_multiple_pricing and payload.pricing_titles:
        for price in payload.pricing_titles:
            pricing_title = get_object_or_404(PricingTitle, id=price.pricing_title_id)
            MenuDesignPricing.objects.create(
                menu_design=menu_design,
                pricing_title=pricing_title,
                display_order=price.display_order
            )
    
    return menu_design

@router.get("/menu-designs/{restaurant_id}/", response={200: MenuDesignOut, 404: dict, 500: dict})
def get_restaurant_menu_design(request, restaurant_id: int):
    try:
        # Fix the query to use prefetch_related before get()
        design = (MenuDesign.objects
                 .prefetch_related('categories__category', 'pricing_titles__pricing_title')
                 .get(restaurant_id=restaurant_id, is_active=True))
        
        # Add debug logging
        categories = list(design.categories.all())  # Force evaluation to check data
        pricing_titles = list(design.pricing_titles.all())
        
        response_data = {
            "id": design.id,
            "is_multiple_pricing": design.is_multiple_pricing,
            "categories": [],
            "pricing_titles": []
        }
        
        # Safely build categories list
        for category in categories:
            try:
                if category.category:  # Check if category relation exists
                    response_data["categories"].append({
                        "id": category.category.id,
                        "name": category.category.name
                    })
            except Exception as category_error:
                print(f"Error processing category: {category_error}")
        
        # Safely build pricing titles list
        for pricing in pricing_titles:
            try:
                if pricing.pricing_title:  # Check if pricing_title relation exists
                    response_data["pricing_titles"].append({
                        "id": pricing.pricing_title.id,
                        "name": pricing.pricing_title.name
                    })
            except Exception as pricing_error:
                print(f"Error processing pricing: {pricing_error}")
        
        return 200, response_data
        
    except MenuDesign.DoesNotExist:
        return 404, {"detail": "No active menu design found"}
    except Exception as e:
        print(f"Error in get_restaurant_menu_design: {str(e)}")  # Debug log
        return 500, {"detail": f"Server error: {str(e)}"}

@router.put("/menu-designs/{restaurant_id}/categories/order/", response=List[MenuDesignCategoryOut])
def update_category_order(request, restaurant_id: int, payload: List[MenuDesignCategoryBase]):
    """Update the display order of menu categories"""
    menu_design = get_object_or_404(MenuDesign, restaurant_id=restaurant_id)
    
    for cat in payload:
        MenuDesignCategory.objects.filter(
            menu_design=menu_design,
            category_id=cat.category_id
        ).update(display_order=cat.display_order)
    
    return MenuDesignCategory.objects.filter(menu_design=menu_design)

@router.put("/menu-designs/{restaurant_id}/pricing/order/", response=List[MenuDesignPricingOut])
def update_pricing_order(request, restaurant_id: int, payload: List[MenuDesignPricingBase]):
    """Update the display order of pricing titles"""
    menu_design = get_object_or_404(MenuDesign, restaurant_id=restaurant_id)
    
    for price in payload:
        MenuDesignPricing.objects.filter(
            menu_design=menu_design,
            pricing_title_id=price.pricing_title_id
        ).update(display_order=price.display_order)
    
    return MenuDesignPricing.objects.filter(menu_design=menu_design)

@router.get("/menu-designs/{restaurant_id}/pricing-titles/", response=List[PricingTitleOut])
def get_restaurant_pricing_titles(request, restaurant_id: int):
    """Get pricing titles for a restaurant's active menu design"""
    return PricingTitle.objects.filter(
        menudesignpricing__menu_design__restaurant_id=restaurant_id,
        menudesignpricing__menu_design__is_active=True,
        menudesignpricing__menu_design__is_multiple_pricing=True
    ).distinct()

# Menu Item Endpoints
@router.get("/menu-items/", response=List[MenuItemOut])
def list_menu_items(request, restaurant_id: int | None = None):
    """Get all menu items, optionally filtered by restaurant"""
    queryset = MenuItem.objects.all()
    if restaurant_id:
        queryset = queryset.filter(restaurant_id=restaurant_id)
    return queryset

@router.post("/menu-items/", response=MenuItemOut)
def create_menu_item(request, payload: MenuItemCreate):
    """Create a new menu item"""
    restaurant = get_object_or_404(Restaurant, id=payload.restaurant_id)
    menu_category = get_object_or_404(MenuDesignCategory, id=payload.menu_category_id)
    
    # Create menu item
    menu_item = MenuItem.objects.create(
        restaurant=restaurant,
        menu_category=menu_category,
        name=payload.name,
        description=payload.description,
        spice_level_id=payload.spice_level_id,
        has_multiple_portions=payload.has_multiple_portions,
        display_order=payload.display_order
    )
    
    # Add related fields
    if payload.dietary_requirement_ids:
        menu_item.dietary_requirements.set(payload.dietary_requirement_ids)
    if payload.religious_restriction_ids:
        menu_item.religious_restrictions.set(payload.religious_restriction_ids)
    if payload.allergen_ids:
        menu_item.allergens.set(payload.allergen_ids)
    
    # Add portions if multiple portions enabled
    if payload.has_multiple_portions and payload.portions:
        for portion in payload.portions:
            MenuItemPortion.objects.create(
                menu_item=menu_item,
                portion_size_id=portion.portion_size_id,
                quantity=portion.quantity,
                display_order=portion.display_order
            )
    
    # Add prices
    for price in payload.prices:
        MenuItemPrice.objects.create(
            menu_item=menu_item,
            portion_id=price.portion_id,
            pricing_title_id=price.pricing_title_id,
            price=price.price
        )
    
    return menu_item

@router.get("/menu-items/{item_id}/", response=MenuItemOut)
def get_menu_item(request, item_id: int):
    """Get a specific menu item"""
    return get_object_or_404(MenuItem, id=item_id)

@router.put("/menu-items/{item_id}/", response=MenuItemOut)
def update_menu_item(request, item_id: int, payload: MenuItemUpdate):
    """Update a menu item"""
    menu_item = get_object_or_404(MenuItem, id=item_id)
    
    # Update fields if provided
    for field, value in payload.dict(exclude_unset=True).items():
        if field.endswith('_ids'):
            # Handle many-to-many fields
            field_name = field[:-4]  # Remove '_ids' suffix
            getattr(menu_item, field_name).set(value)
        else:
            setattr(menu_item, field, value)
    
    menu_item.save()
    return menu_item

@router.delete("/menu-items/{item_id}/")
def delete_menu_item(request, item_id: int):
    """Delete a menu item"""
    menu_item = get_object_or_404(MenuItem, id=item_id)
    menu_item.delete()
    return {"success": True}

@router.post("/menu-items/{item_id}/images/")
def upload_menu_item_images(request, item_id: int):
    """Upload images for a menu item"""
    menu_item = get_object_or_404(MenuItem, id=item_id)
    images = request.FILES.getlist('images', [])
    
    uploaded_images = []
    for image in images:
        menu_item_image = MenuItemImage.objects.create(
            menu_item=menu_item,
            image=image
        )
        uploaded_images.append({"id": menu_item_image.id, "image": menu_item_image.image.url})
    
    return uploaded_images

@router.put("/menu-items/{item_id}/order/", response=MenuItemOut)
def update_menu_item_order(request, item_id: int, display_order: int):
    """Update the display order of a menu item"""
    menu_item = get_object_or_404(MenuItem, id=item_id)
    menu_item.display_order = display_order
    menu_item.save()
    return menu_item 