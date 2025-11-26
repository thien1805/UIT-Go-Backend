"""
Pricing Calculator - Tính giá cước cho trip

Module này xử lý logic tính giá dựa trên:
- Khoảng cách (distance)
- Loại xe (vehicle_type)
- Thời gian (time-based surge pricing)
- Các yếu tố khác (weather, demand, etc.)
"""

from decimal import Decimal
from datetime import datetime
from typing import Dict, Tuple
import math


class PricingCalculator:
    """
    Class tính toán giá cước cho trip
    
    Công thức cơ bản:
        Total = Base Fare + (Distance × Distance Rate) + Time Fare + Surge
    """
    
    # Cấu hình giá cơ bản theo loại xe (VNĐ)
    BASE_FARES = {
        'bike': Decimal('10000'),           # 10,000 VNĐ
        'car_4seats': Decimal('20000'),     # 20,000 VNĐ
        'car_7seats': Decimal('30000'),     # 30,000 VNĐ
    }
    
    # Giá mỗi km theo loại xe (VNĐ/km)
    DISTANCE_RATES = {
        'bike': Decimal('3000'),            # 3,000 VNĐ/km
        'car_4seats': Decimal('8000'),      # 8,000 VNĐ/km
        'car_7seats': Decimal('12000'),     # 12,000 VNĐ/km
    }
    
    # Giá mỗi phút (VNĐ/phút) - áp dụng khi tắc đường
    TIME_RATES = {
        'bike': Decimal('500'),             # 500 VNĐ/phút
        'car_4seats': Decimal('1000'),      # 1,000 VNĐ/phút
        'car_7seats': Decimal('1500'),      # 1,500 VNĐ/phút
    }
    
    # Khoảng cách tối thiểu (km) - dưới này vẫn tính theo base fare
    MIN_DISTANCE = Decimal('2.0')
    
    # Rush hour multiplier (nhân thêm theo giờ cao điểm)
    RUSH_HOUR_MULTIPLIER = Decimal('1.5')  # Tăng 50%
    
    # Giờ cao điểm (24h format)
    RUSH_HOURS = [
        (7, 9),   # Sáng: 7h-9h
        (17, 19), # Chiều: 17h-19h
    ]
    
    def __init__(self):
        self.earth_radius_km = 6371.0  # Bán kính trái đất (km)
    
    def calculate_distance(
        self,
        pickup_lat: float,
        pickup_lng: float,
        dropoff_lat: float,
        dropoff_lng: float
    ) -> Decimal:
        """
        Tính khoảng cách giữa 2 điểm theo công thức Haversine
        
        Returns:
            Decimal: Khoảng cách tính bằng km
        """
        # Chuyển độ sang radian
        lat1_rad = math.radians(pickup_lat)
        lng1_rad = math.radians(pickup_lng)
        lat2_rad = math.radians(dropoff_lat)
        lng2_rad = math.radians(dropoff_lng)
        
        # Tính chênh lệch
        dlat = lat2_rad - lat1_rad
        dlng = lng2_rad - lng1_rad
        
        # Công thức Haversine
        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = self.earth_radius_km * c
        return Decimal(str(round(distance, 2)))
    
    def is_rush_hour(self, check_time: datetime = None) -> bool:
        """
        Kiểm tra có phải giờ cao điểm không
        
        Args:
            check_time: Thời điểm cần check (mặc định: hiện tại)
        
        Returns:
            bool: True nếu là giờ cao điểm
        """
        if check_time is None:
            check_time = datetime.now()
        
        current_hour = check_time.hour
        
        for start_hour, end_hour in self.RUSH_HOURS:
            if start_hour <= current_hour < end_hour:
                return True
        
        return False
    
    def calculate_base_fare(self, vehicle_type: str) -> Decimal:
        """
        Lấy base fare theo loại xe
        
        Args:
            vehicle_type: Loại xe (bike, car_4seats, car_7seats)
        
        Returns:
            Decimal: Base fare
        """
        return self.BASE_FARES.get(vehicle_type, self.BASE_FARES['bike'])
    
    def calculate_distance_fare(self, distance_km: Decimal, vehicle_type: str) -> Decimal:
        """
        Tính phí theo khoảng cách
        
        Args:
            distance_km: Khoảng cách (km)
            vehicle_type: Loại xe
        
        Returns:
            Decimal: Distance fare
        """
        rate = self.DISTANCE_RATES.get(vehicle_type, self.DISTANCE_RATES['bike'])
        
        # Nếu khoảng cách dưới MIN_DISTANCE, không tính thêm
        if distance_km <= self.MIN_DISTANCE:
            return Decimal('0')
        
        # Tính phí cho khoảng cách vượt MIN_DISTANCE
        billable_distance = distance_km - self.MIN_DISTANCE
        return billable_distance * rate
    
    def calculate_time_fare(
        self,
        estimated_minutes: int,
        vehicle_type: str
    ) -> Decimal:
        """
        Tính phí theo thời gian (khi tắc đường)
        
        Args:
            estimated_minutes: Thời gian dự kiến (phút)
            vehicle_type: Loại xe
        
        Returns:
            Decimal: Time fare
        """
        rate = self.TIME_RATES.get(vehicle_type, self.TIME_RATES['bike'])
        
        # Chỉ tính phí thời gian khi > 10 phút
        if estimated_minutes <= 10:
            return Decimal('0')
        
        billable_minutes = estimated_minutes - 10
        return Decimal(str(billable_minutes)) * rate
    
    def calculate_surge(
        self,
        base_amount: Decimal,
        check_time: datetime = None
    ) -> Decimal:
        """
        Tính surge pricing (giờ cao điểm)
        
        Args:
            base_amount: Tổng tiền trước surge
            check_time: Thời điểm check
        
        Returns:
            Decimal: Surge amount
        """
        if self.is_rush_hour(check_time):
            # Tăng thêm % theo rush hour multiplier
            surge = base_amount * (self.RUSH_HOUR_MULTIPLIER - Decimal('1'))
            return surge.quantize(Decimal('1'))  # Làm tròn
        
        return Decimal('0')
    
    def calculate_fare(
        self,
        pickup_lat: float,
        pickup_lng: float,
        dropoff_lat: float,
        dropoff_lng: float,
        vehicle_type: str,
        estimated_minutes: int = 0,
        check_time: datetime = None
    ) -> Dict:
        """
        Tính toán tổng giá cước cho trip
        
        Args:
            pickup_lat, pickup_lng: Tọa độ điểm đón
            dropoff_lat, dropoff_lng: Tọa độ điểm trả
            vehicle_type: Loại xe
            estimated_minutes: Thời gian dự kiến (phút)
            check_time: Thời điểm tính giá
        
        Returns:
            Dict: {
                'distance_km': Khoảng cách,
                'base_fare': Phí cơ bản,
                'distance_fare': Phí theo km,
                'time_fare': Phí theo thời gian,
                'surge_fare': Phí tăng cao điểm,
                'subtotal': Tổng trước surge,
                'total_fare': Tổng tiền cuối cùng,
                'is_rush_hour': Có phải giờ cao điểm
            }
        """
        # 1. Tính khoảng cách
        distance_km = self.calculate_distance(
            pickup_lat, pickup_lng,
            dropoff_lat, dropoff_lng
        )
        
        # 2. Tính các loại phí
        base_fare = self.calculate_base_fare(vehicle_type)
        distance_fare = self.calculate_distance_fare(distance_km, vehicle_type)
        time_fare = self.calculate_time_fare(estimated_minutes, vehicle_type)
        
        # 3. Tổng trước surge
        subtotal = base_fare + distance_fare + time_fare
        
        # 4. Tính surge (giờ cao điểm)
        surge_fare = self.calculate_surge(subtotal, check_time)
        
        # 5. Tổng cuối cùng
        total_fare = subtotal + surge_fare
        
        # 6. Làm tròn đến hàng nghìn (VNĐ)
        total_fare = (total_fare / 1000).quantize(Decimal('1')) * 1000
        
        return {
            'distance_km': float(distance_km),
            'base_fare': float(base_fare),
            'distance_fare': float(distance_fare),
            'time_fare': float(time_fare),
            'surge_fare': float(surge_fare),
            'subtotal': float(subtotal),
            'total_fare': float(total_fare),
            'is_rush_hour': self.is_rush_hour(check_time)
        }
    
    def estimate_trip_time(self, distance_km: Decimal) -> int:
        """
        Ước tính thời gian di chuyển (phút) dựa trên khoảng cách
        
        Giả định tốc độ trung bình: 30 km/h trong thành phố
        
        Args:
            distance_km: Khoảng cách (km)
        
        Returns:
            int: Thời gian dự kiến (phút)
        """
        avg_speed_kmh = Decimal('30')  # 30 km/h
        hours = distance_km / avg_speed_kmh
        minutes = hours * 60
        return int(minutes.quantize(Decimal('1')))


# Instance mặc định
default_calculator = PricingCalculator()


def calculate_trip_fare(
    pickup_lat: float,
    pickup_lng: float,
    dropoff_lat: float,
    dropoff_lng: float,
    vehicle_type: str
) -> Dict:
    """
    Helper function để tính giá trip
    
    Usage:
        fare_info = calculate_trip_fare(
            10.762622, 106.660172,
            10.771513, 106.698660,
            'bike'
        )
    
    Returns:
        Dict: Thông tin chi tiết về giá cước
    """
    return default_calculator.calculate_fare(
        pickup_lat, pickup_lng,
        dropoff_lat, dropoff_lng,
        vehicle_type
    )
