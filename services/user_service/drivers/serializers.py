from rest_framework import serializers
from .models import DriverProfile
from authentication.serializers import UserSerializer
import re
from datetime import date

class DriverProfileCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a driver profile"""
    user = UserSerializer(required=True)
    class Meta:
        model = DriverProfile
        fields = [
           'vehicle_type',
           'vehicle_brand',
           'vehicle_model',
           'vehicle_color',
           'license_plate',
           'driver_license_number',
           'drive_license_expiry',
           'vehicle_registration_number',
        ]
    def validate_license_plate(self, value):
        """Validate biển số xe"""
        plate_pattern = r'^\d{2}[A-Z]{1,2}-?\d{4,5}$'
        cleaned_value = value.replace(' ', '').upper()
        
        if not re.match(plate_pattern, cleaned_value):
            raise serializers.ValidationError("Invalid license plate format. Expected format: 59A-12345")
        if DriverProfile.objects.filter(license_plate=cleaned_value).exists():
            raise serializers.ValidationError("License plate already registered")
        
        return cleaned_value
    
    def validate_drive_license_expiry(self, value):
        """Validate ngày hết hạn giấy phép lái xe"""
        if value and value < date.today():
            raise serializers.ValidationError("Driver license has expired")
        return value
    
    def validate_vehicle_type(self, value):
        """Validate loại xe"""
        valid_types = ['bike', 'car_4seats', 'car_7seats']
        if value not in valid_types:
            raise serializers.ValidationError(f"Invalid vehicle type. Must be one of: {', '.join(valid_types)}")
        return value
    
    
class DriverStatsUpdateSerializer(serializers.Serializer):
    """Serializer để cập nhật thống kê của tài xế"""
    total_trips = serializers.IntegerField(required=False, min_value=0)
    total_earnings = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, min_value=0.00)

class DriverProfileSerializer(serializers.ModelSerializer):
    """Serializer để lấy thông tin tài xế"""
    
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = DriverProfile
        fields = [
            'id', 'user', 'vehicle_type', 'vehicle_brand', 'vehicle_model',
            'vehicle_color', 'license_plate', 'driver_license_number',
            'driver_license_expiry', 'vehicle_registration_number',
            'approval_status', 'approval_note', 'approved_at',
            'rating', 'total_trips', 'total_earnings',
            'is_online', 'last_online_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'approval_status', 'approved_at', 'rating',
            'total_trips', 'total_earnings', 'created_at', 'updated_at'
        ]
    
class DriverPublicSerializer(serializers.ModelSerializer):
    """Serializer for driver public details"""
    
    full_name = serializers.CharField(source='user.full_name')
    phone = serializers.CharField(source="user.phone")
    
    class Meta:
        model = DriverProfile
        fields = [
            'id', 'full_name', 'phone', 
            'vehicle_type', 'vehicle_brand', 'vehicle_model', 'vehicle_color',
            'license_plate', 'total_trips'
        ]
        
class DriverStatusUpdateSerializer(serializers.Serializer):
    """Serializer để cập nhật trạng thái online của tài xế"""
    is_online = serializers.BooleanField(required=True)
    latitude = serializers.DecimalField(max_digits=10, decimal_places=8, required=False, allow_null=True)
    longitude = serializers.DecimalField(max_digits=11, decimal_places=8, required=False, allow_null=True)
    def validate(self, attrs):
        """Validate vị trí khi online"""
        if attrs.get('is_online'):
            if not (attrs.get('latitude')) and not (attrs.get('longitude')):
                raise serializers.ValidationError("Vị trí không được để trống khi online")
        return attrs

