from django.urls import path
from . import views

# URL patterns cho Trip Service API
# Tất cả endpoints đều có prefix /api/trips/

urlpatterns = [
    # Tạo trip mới (POST) hoặc lấy danh sách trips (GET)
    path('', views.trip_list_create, name='trip_list_create'),

    # Lấy chi tiết trip cụ thể
    path('<uuid:trip_id>/', views.get_trip_detail, name='get_trip_detail'),

    # Cập nhật status trip
    path('<uuid:trip_id>/status/', views.update_trip_status, name='update_trip_status'),

    # Gán driver cho trip (chỉ driver service)
    path('<uuid:trip_id>/assign-driver/', views.assign_driver_to_trip, name='assign_driver'),

    # Lấy trips khả dụng (chỉ driver service)
    path('available/', views.get_available_trips, name='available_trips'),
]
