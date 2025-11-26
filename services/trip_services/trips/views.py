from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Trip
from .serializers import (
    TripCreateSerializer,
    TripDetailSerializer,
    TripStatusUpdateSerializer,
    TripAssignDriverSerializer
)
from .pagination import trips_pagination, available_trips_pagination
import requests
from django.conf import settings


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def trip_list_create(request):
    """
    API endpoint kết hợp:
    - POST /api/trips/ : Tạo trip mới
    - GET /api/trips/  : Lấy danh sách trips của user
    """
    if request.method == 'POST':
        return create_trip(request)
    else:
        return get_user_trips(request)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_trip(request):
    """
    API tạo trip mới - POST /api/trips/

    Passenger tạo trip mới với thông tin pickup/dropoff
    """
    serializer = TripCreateSerializer(data=request.data, context={'request': request})

    if serializer.is_valid():
        trip = serializer.save()
        # Trả về thông tin trip vừa tạo
        response_serializer = TripDetailSerializer(trip)
        return Response({
            'success': True,
            'data': {
                'trip': response_serializer.data
            },
            'message': 'Tạo chuyến đi thành công'
        }, status=status.HTTP_201_CREATED)

    return Response({
        'success': False,
        'error': {
            'code': 'VALIDATION_ERROR',
            'message': 'Dữ liệu không hợp lệ',
            'details': serializer.errors
        }
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_trips(request):
    """
    API lấy danh sách trips của user - GET /api/trips/

    Lấy tất cả trips mà user là passenger hoặc driver
    """
    user_id = request.user.id
    user_role = request.query_params.get('role', 'passenger')  # passenger hoặc driver

    if user_role == 'driver':
        trips = Trip.objects.filter(driver_id=user_id)
    else:
        trips = Trip.objects.filter(passenger_id=user_id)

    # Sử dụng pagination class để phân trang
    paginated_trips, pagination_info = trips_pagination.paginate_queryset(trips, request)
    
    # Serialize dữ liệu đã phân trang
    serializer = TripDetailSerializer(paginated_trips, many=True)

    # Trả về response với format chuẩn
    return trips_pagination.get_paginated_response(
        data=serializer.data,
        pagination_info=pagination_info,
        message='Lấy danh sách chuyến đi thành công',
        items_key='trips'  # Tên key cho danh sách trips
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_trip_detail(request, trip_id):
    """
    API lấy chi tiết trip - GET /api/trips/{trip_id}/

    Lấy thông tin chi tiết của một trip cụ thể
    """
    try:
        # UUID validation
        import uuid
        uuid.UUID(trip_id)  # Kiểm tra format UUID
    except ValueError:
        return Response({
            'success': False,
            'error': {
                'code': 'INVALID_ID',
                'message': 'ID chuyến đi không hợp lệ'
            }
        }, status=status.HTTP_400_BAD_REQUEST)

    trip = get_object_or_404(Trip, id=trip_id)

    # Kiểm tra quyền: chỉ passenger hoặc driver của trip mới xem được
    user_id = request.user.id
    if trip.passenger_id != user_id and trip.driver_id != user_id:
        return Response({
            'success': False,
            'error': {
                'code': 'FORBIDDEN',
                'message': 'Bạn không có quyền xem chuyến đi này'
            }
        }, status=status.HTTP_403_FORBIDDEN)

    serializer = TripDetailSerializer(trip)
    return Response({
        'success': True,
        'data': {
            'trip': serializer.data
        },
        'message': 'Lấy thông tin chuyến đi thành công'
    }, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_trip_status(request, trip_id):
    """
    API cập nhật status trip - PUT /api/trips/{trip_id}/status/

    Cập nhật trạng thái chuyến đi (passenger cancel, driver update status, etc.)
    """
    try:
        import uuid
        uuid.UUID(trip_id)
    except ValueError:
        return Response({
            'success': False,
            'error': {
                'code': 'INVALID_ID',
                'message': 'ID chuyến đi không hợp lệ'
            }
        }, status=status.HTTP_400_BAD_REQUEST)

    trip = get_object_or_404(Trip, id=trip_id)
    user_id = request.user.id

    serializer = TripStatusUpdateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Dữ liệu không hợp lệ',
                'details': serializer.errors
            }
        }, status=status.HTTP_400_BAD_REQUEST)

    new_status = serializer.validated_data['status']

    # Kiểm tra quyền cập nhật status
    if new_status in ['cancelled_by_passenger']:
        # Chỉ passenger mới có thể cancel
        if trip.passenger_id != user_id:
            return Response({
                'success': False,
                'error': {
                    'code': 'FORBIDDEN',
                    'message': 'Chỉ hành khách mới có thể hủy chuyến'
                }
            }, status=status.HTTP_403_FORBIDDEN)

        trip.cancelled_by = user_id
        trip.cancelled_at = timezone.now()
        trip.cancellation_reason = serializer.validated_data.get('cancellation_reason', '')

    elif new_status in ['cancelled_by_driver', 'driver_arriving', 'passenger_picked_up', 'completed']:
        # Chỉ driver mới có thể cập nhật các status này
        if trip.driver_id != user_id:
            return Response({
                'success': False,
                'error': {
                    'code': 'FORBIDDEN',
                    'message': 'Chỉ tài xế mới có thể cập nhật trạng thái này'
                }
            }, status=status.HTTP_403_FORBIDDEN)

        # Cập nhật timestamp tương ứng
        if new_status == 'driver_arriving':
            trip.driver_arrived_at = timezone.now()
        elif new_status == 'passenger_picked_up':
            trip.trip_started_at = timezone.now()
        elif new_status == 'completed':
            trip.trip_completed_at = timezone.now()
        elif new_status == 'cancelled_by_driver':
            trip.cancelled_by = user_id
            trip.cancelled_at = timezone.now()
            trip.cancellation_reason = serializer.validated_data.get('cancellation_reason', '')

    trip.status = new_status
    trip.save()

    response_serializer = TripDetailSerializer(trip)
    return Response({
        'success': True,
        'data': {
            'trip': response_serializer.data
        },
        'message': 'Cập nhật trạng thái chuyến đi thành công'
    }, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def assign_driver_to_trip(request, trip_id):
    """
    API gán driver cho trip - PUT /api/trips/{trip_id}/assign-driver/

    Driver nhận chuyến đi (chỉ dành cho driver service call)
    """
    try:
        import uuid
        uuid.UUID(trip_id)
    except ValueError:
        return Response({
            'success': False,
            'error': {
                'code': 'INVALID_ID',
                'message': 'ID chuyến đi không hợp lệ'
            }
        }, status=status.HTTP_400_BAD_REQUEST)

    trip = get_object_or_404(Trip, id=trip_id)

    # Kiểm tra service token (chỉ driver service mới được gọi API này)
    service_token = request.headers.get('X-Service-Token')
    expected_token = getattr(settings, 'INTERNAL_SERVICE_TOKEN', None)

    if service_token != expected_token:
        return Response({
            'success': False,
            'error': {
                'code': 'UNAUTHORIZED',
                'message': 'Invalid service token'
            }
        }, status=status.HTTP_401_UNAUTHORIZED)

    serializer = TripAssignDriverSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Dữ liệu không hợp lệ',
                'details': serializer.errors
            }
        }, status=status.HTTP_400_BAD_REQUEST)

    # Kiểm tra trip có đang tìm driver không
    if trip.status != 'finding_driver':
        return Response({
            'success': False,
            'error': {
                'code': 'INVALID_STATUS',
                'message': 'Chuyến đi không còn khả dụng'
            }
        }, status=status.HTTP_400_BAD_REQUEST)

    driver_id = serializer.validated_data['driver_id']

    # Gán driver cho trip
    trip.driver_id = driver_id
    trip.status = 'driver_assigned'
    trip.driver_accepted_at = timezone.now()
    trip.save()

    response_serializer = TripDetailSerializer(trip)
    return Response({
        'success': True,
        'data': {
            'trip': response_serializer.data
        },
        'message': 'Gán tài xế cho chuyến đi thành công'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_available_trips(request):
    """
    API lấy danh sách trips đang tìm driver - GET /api/trips/available/

    Driver service gọi để lấy trips khả dụng
    """
    # Kiểm tra service token
    service_token = request.headers.get('X-Service-Token')
    expected_token = getattr(settings, 'INTERNAL_SERVICE_TOKEN', None)

    if service_token != expected_token:
        return Response({
            'success': False,
            'error': {
                'code': 'UNAUTHORIZED',
                'message': 'Invalid service token'
            }
        }, status=status.HTTP_401_UNAUTHORIZED)

    # Lấy trips đang tìm driver
    available_trips = Trip.objects.filter(status='finding_driver')

    # Lọc theo vehicle_type nếu có
    vehicle_type = request.query_params.get('vehicle_type')
    if vehicle_type:
        available_trips = available_trips.filter(vehicle_type=vehicle_type)

    # Sử dụng pagination class để phân trang (page_size mặc định lớn hơn)
    paginated_trips, pagination_info = available_trips_pagination.paginate_queryset(
        available_trips, request
    )
    
    # Serialize dữ liệu đã phân trang
    serializer = TripDetailSerializer(paginated_trips, many=True)

    # Trả về response với format chuẩn
    return available_trips_pagination.get_paginated_response(
        data=serializer.data,
        pagination_info=pagination_info,
        message='Lấy danh sách chuyến đi khả dụng thành công',
        items_key='trips'  # Tên key cho danh sách trips
    )