from rest_framework import serializers
from .models import Trip
import uuid


class TripCreateSerializer(serializers.ModelSerializer):
    """
    Serializer để tạo trip mới - chỉ cần thông tin cơ bản
    """
    class Meta:
        model = Trip
        fields = [
            'pickup_lat', 'pickup_lng', 'pickup_address', 'pickup_note',
            'dropoff_lat', 'dropoff_lng', 'dropoff_address', 'dropoff_note',
            'vehicle_type', 'estimated_fare'
        ]

    def create(self, validated_data):
        # Lấy passenger_id từ context (từ request.user)
        passenger_id = self.context['request'].user.id
        validated_data['passenger_id'] = passenger_id
        return super().create(validated_data)


class TripDetailSerializer(serializers.ModelSerializer):
    """
    Serializer để trả về chi tiết trip đầy đủ
    """
    class Meta:
        model = Trip
        fields = [
            'id', 'passenger_id', 'driver_id', 'status',
            'pickup_lat', 'pickup_lng', 'pickup_address', 'pickup_note',
            'dropoff_lat', 'dropoff_lng', 'dropoff_address', 'dropoff_note',
            'vehicle_type', 'distance_km', 'estimated_fare', 'actual_fare',
            'payment_method', 'payment_status', 'created_at', 'trip_started_at',
            'trip_completed_at', 'cancelled_at', 'cancelled_by', 'cancellation_reason'
        ]
        read_only_fields = ['id', 'passenger_id', 'driver_id', 'status', 'created_at',
                          'trip_started_at', 'trip_completed_at', 'cancelled_at']


class TripStatusUpdateSerializer(serializers.Serializer):
    """
    Serializer để cập nhật status trip
    """
    status = serializers.ChoiceField(choices=Trip.STATUS_CHOICES, required=True)
    cancellation_reason = serializers.CharField(required=False, allow_blank=True)


class TripAssignDriverSerializer(serializers.Serializer):
    """
    Serializer để gán driver cho trip
    """
    driver_id = serializers.UUIDField(required=True)
