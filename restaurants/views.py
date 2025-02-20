from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from .models import (
    Restaurant, RestaurantImage, OperatingHours, 
    HolidayHours, RestaurantAmenities
)
from .serializers import (
    RestaurantSerializer, RestaurantImageSerializer,
    OperatingHoursSerializer, HolidayHoursSerializer,
    RestaurantAmenitiesSerializer
)
from .permissions import IsRestaurantOwner

# Create your views here.

class RestaurantViewSet(viewsets.ModelViewSet):
    serializer_class = RestaurantSerializer
    parser_classes = (MultiPartParser, FormParser)
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Restaurant.objects.all()
        elif self.request.user.is_authenticated:
            if self.request.user.is_restaurant_owner():
                return Restaurant.objects.filter(owner=self.request.user)
            return Restaurant.objects.filter(is_approved=True)
        return Restaurant.objects.filter(is_approved=True)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsRestaurantOwner]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser])
    def upload_images(self, request, pk=None):
        restaurant = self.get_object()
        
        # Handle multiple images
        images = request.FILES.getlist('images', [])
        video_url = request.data.get('video_url')
        is_video_thumbnail = request.data.get('is_video_thumbnail', False)
        
        created_images = []
        for image in images:
            serializer = RestaurantImageSerializer(data={
                'image': image,
                'video_url': video_url if is_video_thumbnail else None,
                'is_video_thumbnail': is_video_thumbnail
            })
            if serializer.is_valid():
                serializer.save(restaurant=restaurant)
                created_images.append(serializer.data)
            
        return Response(created_images, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def set_hours(self, request, pk=None):
        restaurant = self.get_object()
        
        # Handle operating hours
        operating_hours = request.data.get('operating_hours', [])
        for hours in operating_hours:
            serializer = OperatingHoursSerializer(data=hours)
            if serializer.is_valid():
                serializer.save(restaurant=restaurant)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Handle holiday hours
        holiday_hours = request.data.get('holiday_hours', [])
        for hours in holiday_hours:
            serializer = HolidayHoursSerializer(data=hours)
            if serializer.is_valid():
                serializer.save(restaurant=restaurant)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'message': 'Hours updated successfully'}, 
                       status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def set_amenities(self, request, pk=None):
        restaurant = self.get_object()
        
        serializer = RestaurantAmenitiesSerializer(
            restaurant.amenities if hasattr(restaurant, 'amenities') else None,
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save(restaurant=restaurant)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        if not request.user.is_staff:
            return Response(
                {'error': 'Only staff members can approve restaurants'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        restaurant = self.get_object()
        restaurant.is_approved = True
        restaurant.save()
        
        return Response(
            {'message': 'Restaurant approved successfully'},
            status=status.HTTP_200_OK
        )
