from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from .models import User

class UserSerializer(serializers.ModelSerializer):
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                 'user_type', 'phone_number', 'profile_picture', 
                 'about_me', 'gender', 'gender_display')
        read_only_fields = ('id',)

    def to_representation(self, instance):
        # Return empty dict if user is anonymous
        if not instance.is_authenticated:
            return {}
        return super().to_representation(instance)

class LoginSerializer(serializers.Serializer):
    email_or_username = serializers.CharField(
        required=True,
        error_messages={
            'required': 'Please provide email or username.',
            'blank': 'Email or username cannot be blank.'
        }
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        error_messages={
            'required': 'Please provide password.',
            'blank': 'Password cannot be blank.'
        }
    )

    def validate(self, attrs):
        email_or_username = attrs.get('email_or_username', '').strip()
        password = attrs.get('password', '').strip()

        if not email_or_username or not password:
            raise serializers.ValidationError({
                'error': 'Both email/username and password are required.'
            })

        # Check if input is an email
        if '@' in email_or_username:
            try:
                user = User.objects.get(email=email_or_username)
                username = user.username
            except User.DoesNotExist:
                raise serializers.ValidationError({
                    'error': f'No account found with email: {email_or_username}'
                })
        else:
            username = email_or_username
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise serializers.ValidationError({
                    'error': f'No account found with username: {username}'
                })

        # Try to authenticate
        user = authenticate(
            request=self.context.get('request'),
            username=username,
            password=password
        )

        if not user:
            raise serializers.ValidationError({
                'error': 'Invalid credentials. Please check your email/username and password.'
            })
        
        if not user.is_active:
            raise serializers.ValidationError({
                'error': 'This account is inactive or has been disabled.'
            })

        attrs['user'] = user
        return attrs

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    confirm_password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'confirm_password', 
                 'user_type', 'phone_number', 'about_me', 'gender')
        extra_kwargs = {
            'user_type': {'required': True},
            'phone_number': {'required': False},
            'about_me': {'required': False},
            'gender': {'required': False}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('confirm_password'):
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        # Validate user type
        if attrs['user_type'] not in [choice[0] for choice in User.USER_TYPE_CHOICES]:
            raise serializers.ValidationError({"user_type": "Invalid user type selected."})
        
        # Validate email is unique
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "User with this email already exists."})
        
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            user_type=validated_data['user_type'],
            phone_number=validated_data.get('phone_number', ''),
            about_me=validated_data.get('about_me', ''),
            gender=validated_data.get('gender', '')
        )
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=False, allow_null=True)
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone_number', 'about_me', 'gender', 'profile_picture')
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'phone_number': {'required': False},
            'about_me': {'required': False},
            'gender': {'required': False},
            'profile_picture': {'required': False}
        }

    def validate_gender(self, value):
        if value and value not in [choice[0] for choice in User.GENDER_CHOICES]:
            raise serializers.ValidationError("Invalid gender selected.")
        return value

    def update(self, instance, validated_data):
        # Handle profile picture update/deletion
        if 'profile_picture' in validated_data:
            if instance.profile_picture:
                # Delete old picture if it exists
                instance.profile_picture.delete(save=False)
            
            if validated_data['profile_picture'] is None:
                # If explicitly set to None, remove the profile picture
                instance.profile_picture = None
        
        return super().update(instance, validated_data) 