"""
Driver Matching Algorithm - Thuật toán tìm driver phù hợp

Module này xử lý logic tìm driver gần nhất và phù hợp nhất
cho một trip dựa trên nhiều yếu tố.
"""

import math
import requests
from django.conf import settings
from typing import List, Dict, Optional


class DriverMatcher:
    """
    Class xử lý logic matching driver cho trip
    
    Thuật toán ưu tiên:
    1. Driver đang online
    2. Driver có vehicle type phù hợp
    3. Driver gần pickup location nhất
    4. Driver có rating cao (nếu có)
    """
    
    def __init__(self):
        self.user_service_url = getattr(settings, 'USER_SERVICE_URL', 'http://localhost:8001')
        self.internal_token = getattr(settings, 'INTERNAL_SERVICE_TOKEN', '')
        self.max_distance_km = 10  # Bán kính tìm kiếm tối đa (km)
    
    def calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """
        Tính khoảng cách giữa 2 điểm theo công thức Haversine
        
        Args:
            lat1, lng1: Tọa độ điểm 1 (pickup)
            lat2, lng2: Tọa độ điểm 2 (driver)
        
        Returns:
            float: Khoảng cách tính bằng km
        """
        # Bán kính trái đất (km)
        R = 6371.0
        
        # Chuyển độ sang radian
        lat1_rad = math.radians(lat1)
        lng1_rad = math.radians(lng1)
        lat2_rad = math.radians(lat2)
        lng2_rad = math.radians(lng2)
        
        # Tính chênh lệch
        dlat = lat2_rad - lat1_rad
        dlng = lng2_rad - lng1_rad
        
        # Công thức Haversine
        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        return round(distance, 2)
    
    def get_online_drivers(self, vehicle_type: str) -> List[Dict]:
        """
        Lấy danh sách drivers đang online từ User Service
        
        Args:
            vehicle_type: Loại xe cần (bike, car_4seats, car_7seats)
        
        Returns:
            List[Dict]: Danh sách drivers với thông tin cơ bản
        """
        try:
            # Gọi API User Service để lấy drivers online
            response = requests.get(
                f'{self.user_service_url}/api/drivers/',
                params={
                    'is_online': 'true',
                    'vehicle_type': vehicle_type,
                    'approval_status': 'approved'
                },
                headers={'X-Service-Token': self.internal_token},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', {}).get('drivers', [])
            else:
                return []
                
        except requests.RequestException as e:
            print(f"Error fetching online drivers: {e}")
            return []
    
    def find_nearest_drivers(
        self, 
        pickup_lat: float, 
        pickup_lng: float, 
        vehicle_type: str,
        limit: int = 5
    ) -> List[Dict]:
        """
        Tìm drivers gần nhất với pickup location
        
        Args:
            pickup_lat: Vĩ độ điểm đón
            pickup_lng: Kinh độ điểm đón
            vehicle_type: Loại xe cần
            limit: Số lượng drivers trả về (mặc định: 5)
        
        Returns:
            List[Dict]: Danh sách drivers gần nhất, sorted theo khoảng cách
                       Mỗi dict chứa: driver_id, distance_km, driver_info
        """
        # Lấy danh sách drivers online
        online_drivers = self.get_online_drivers(vehicle_type)
        
        if not online_drivers:
            return []
        
        # Tính khoảng cách từ mỗi driver đến pickup location
        drivers_with_distance = []
        
        for driver in online_drivers:
            # Giả sử driver_info có current_lat và current_lng
            # Trong thực tế cần có Location model để lưu vị trí real-time
            driver_lat = driver.get('current_lat')
            driver_lng = driver.get('current_lng')
            
            # Nếu chưa có vị trí, skip driver này
            if driver_lat is None or driver_lng is None:
                continue
            
            # Tính khoảng cách
            distance = self.calculate_distance(
                pickup_lat, pickup_lng,
                float(driver_lat), float(driver_lng)
            )
            
            # Chỉ lấy drivers trong bán kính cho phép
            if distance <= self.max_distance_km:
                drivers_with_distance.append({
                    'driver_id': driver.get('id') or driver.get('user_id'),
                    'distance_km': distance,
                    'driver_info': driver
                })
        
        # Sort theo khoảng cách, gần nhất trước
        drivers_with_distance.sort(key=lambda x: x['distance_km'])
        
        # Trả về top N drivers
        return drivers_with_distance[:limit]
    
    def assign_best_driver(
        self,
        pickup_lat: float,
        pickup_lng: float,
        vehicle_type: str
    ) -> Optional[Dict]:
        """
        Tìm và trả về driver tốt nhất cho trip
        
        Args:
            pickup_lat: Vĩ độ điểm đón
            pickup_lng: Kinh độ điểm đón
            vehicle_type: Loại xe cần
        
        Returns:
            Optional[Dict]: Thông tin driver được chọn hoặc None nếu không tìm thấy
        """
        nearest_drivers = self.find_nearest_drivers(
            pickup_lat, pickup_lng, vehicle_type, limit=1
        )
        
        if nearest_drivers:
            return nearest_drivers[0]
        
        return None


# Instance mặc định để sử dụng
default_matcher = DriverMatcher()


def find_drivers_for_trip(pickup_lat: float, pickup_lng: float, vehicle_type: str) -> List[Dict]:
    """
    Helper function để tìm drivers cho trip
    
    Usage:
        drivers = find_drivers_for_trip(10.762622, 106.660172, 'bike')
    """
    return default_matcher.find_nearest_drivers(pickup_lat, pickup_lng, vehicle_type)


def assign_driver_for_trip(pickup_lat: float, pickup_lng: float, vehicle_type: str) -> Optional[str]:
    """
    Helper function để assign driver tốt nhất cho trip
    
    Returns:
        Optional[str]: driver_id hoặc None
    """
    result = default_matcher.assign_best_driver(pickup_lat, pickup_lng, vehicle_type)
    if result:
        return result['driver_id']
    return None
