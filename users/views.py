from django.shortcuts import render
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer, UserUpdateSerializer
from django.core.exceptions import ValidationError
from django.db import Error as DBError
import logging
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated

User = get_user_model()

logger = logging.getLogger(__name__)

# Create your views here.

class RegisterView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "user": UserSerializer(user).data,
                "message": "User Created Successfully"
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        try:
            serializer = LoginSerializer(data=request.data, context={'request': request})
            
            if not serializer.is_valid():
                logger.error(f"Login validation failed: {serializer.errors}")
                return Response(
                    {'error': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'status': 'success',
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    
    def get(self, request):
        """Get user profile information"""
        serializer = UserSerializer(request.user)
        return Response({
            'status': 'success',
            'user': serializer.data
        })
    
    def patch(self, request):
        """Update user profile information"""
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'message': 'Profile updated successfully',
                'user': UserSerializer(request.user).data
            })
        return Response({
            'status': 'error',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
