from django.db import models
import uuid

# Trip Model - Model chính để lưu trữ thông tin chuyến đi
# Sử dụng UUID làm primary key để tránh conflict khi scale


class Trip(models.Model):
    """
    Trip Model - Lưu trữ toàn bộ thông tin của một chuyến đi

    Chuyến đi bao gồm: thông tin hành khách, tài xế, vị trí,
    giá cả, trạng thái, phương thức thanh toán, v.v.
    """
    
    STATUS_CHOICES = [
        ('finding_driver', 'Finding Driver'),
        ('driver_assigned', 'Driver Assigned'),
        ('driver_arriving', 'Driver Arriving'),
        ('passenger_picked_up', 'Passenger Picked Up'),
        ('completed', 'Completed'),
        ('cancelled_by_passenger', 'Cancelled by Passenger'),
        ('cancelled_by_driver', 'Cancelled by Driver'),
        ('cancelled_by_system', 'Cancelled by System'),
    ]
    
    VEHICLE_TYPE_CHOICES = [
        ('bike', 'Bike'),
        ('car_4seats', 'Car 4 Seats'),
        ('car_7seats', 'Car 7 Seats'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('wallet', 'Wallet'),
        ('card', 'Card'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]
    
    # Primary key - sử dụng UUID thay vì auto-increment ID
    # Tốt cho microservices và tránh conflict khi merge databases
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Thông tin người tham gia - lưu UUID từ User Service
    # Không lưu foreign key trực tiếp để tránh tight coupling
    passenger_id = models.UUIDField()  # ID của hành khách
    driver_id = models.UUIDField(null=True, blank=True)  # ID của tài xế (có thể null ban đầu)
    
    #Ví trí đón khách
    pickup_lat = models.DecimalField(max_digits=10, decimal_places=8)
    pickup_lng = models.DecimalField(max_digits=11, decimal_places=8)
    pickup_address = models.TextField()
    pickup_note = models.TextField(blank=True)
    
    ##Vị trí trả khách
    dropoff_lat = models.DecimalField(max_digits=10, decimal_places=8)
    dropoff_lng = models.DecimalField(max_digits=11, decimal_places=8)
    dropoff_address = models.TextField()
    dropoff_note = models.TextField(blank=True)
    
    #Chi tiết chuyến đi
    vehicle_type = models.CharField(max_length=50, choices=VEHICLE_TYPE_CHOICES)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='finding_driver')
    
    # Thông tin giá cả và thanh toán
    # Pricing breakdown để tính toán và hiển thị chi tiết cho user
    distance_km = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)  # Khoảng cách tính bằng km
    base_fare = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)   # Phí cơ bản (không phụ thuộc quãng đường)
    distance_fare = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) # Phí theo quãng đường
    time_fare = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)   # Phí theo thời gian (nếu có)
    estimated_fare = models.DecimalField(max_digits=10, decimal_places=2)                     # Tổng phí dự kiến (hiển thị cho user)
    actual_fare = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) # Tổng phí thực tế (sau khi hoàn thành)

    # Thông tin thanh toán
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True)  # Phương thức thanh toán
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')     # Trạng thái thanh toán
    
    #Cancellation
    cancelled_by = models.UUIDField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)
    
    #Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    driver_accepted_at = models.DateTimeField(null=True, blank=True)
    driver_arrived_at = models.DateTimeField(null=True, blank=True)
    trip_started_at = models.DateTimeField(null=True, blank=True)
    trip_completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        # Cấu hình database table
        db_table = 'trips'  # Tên table trong database

        # Database indexes để tối ưu performance query
        indexes = [
            models.Index(fields=["passenger_id"]),      # Query trips của một passenger
            models.Index(fields=["driver_id"]),          # Query trips của một driver
            models.Index(fields=["status"]),             # Filter theo status
            models.Index(fields=["-created_at"])         # Sort theo thời gian tạo (mới nhất trước)
        ]

        # Mặc định sort theo thời gian tạo, mới nhất trước
        ordering = ['-created_at']
        
    def __str__(self):
        # Hiển thị thông tin trip khi debug hoặc admin
        return f"Trip {self.id} - {self.status}"
        
        
