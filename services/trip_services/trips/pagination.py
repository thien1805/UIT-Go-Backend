from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from rest_framework.response import Response


class CustomPagination:
    """
    Class phân trang tùy chỉnh cho Trip Service
    
    Xử lý phân trang một cách gọn gàng và dễ hiểu,
    trả về kết quả với format chuẩn của API
    """
    
    def __init__(self, default_page_size=20, max_page_size=100):
        """
        Khởi tạo pagination
        
        Args:
            default_page_size: Số items mặc định mỗi trang (mặc định: 20)
            max_page_size: Số items tối đa mỗi trang (mặc định: 100)
        """
        self.default_page_size = default_page_size
        self.max_page_size = max_page_size
    
    def paginate_queryset(self, queryset, request):
        """
        Phân trang queryset dựa trên request
        
        Args:
            queryset: Django QuerySet cần phân trang
            request: Django request object (chứa query params)
        
        Returns:
            tuple: (paginated_queryset, pagination_info)
                - paginated_queryset: QuerySet đã được phân trang
                - pagination_info: Dict chứa thông tin phân trang
        """
        # Lấy page và page_size từ query params
        try:
            page = int(request.query_params.get('page', 1))
        except (ValueError, TypeError):
            page = 1
        
        try:
            page_size = int(request.query_params.get('page_size', self.default_page_size))
        except (ValueError, TypeError):
            page_size = self.default_page_size
        
        # Giới hạn page_size không vượt quá max
        if page_size > self.max_page_size:
            page_size = self.max_page_size
        
        # Đảm bảo page và page_size là số dương
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = self.default_page_size
        
        # Tính toán vị trí bắt đầu và kết thúc
        start = (page - 1) * page_size
        end = start + page_size
        
        # Lấy tổng số items (trước khi phân trang)
        total = queryset.count()
        
        # Lấy items cho trang hiện tại
        paginated_queryset = queryset[start:end]
        
        # Tính toán thông tin phân trang
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0  # Làm tròn lên
        has_next = page < total_pages
        has_previous = page > 1
        
        # Tạo dict thông tin phân trang
        pagination_info = {
            'page': page,
            'page_size': page_size,
            'total': total,
            'total_pages': total_pages,
            'has_next': has_next,
            'has_previous': has_previous,
        }
        
        return paginated_queryset, pagination_info
    
    def get_paginated_response(self, data, pagination_info, message='Lấy dữ liệu thành công', items_key='items'):
        """
        Tạo response với format chuẩn của API
        
        Args:
            data: Dữ liệu đã được serialize
            pagination_info: Thông tin phân trang từ paginate_queryset
            message: Thông báo thành công
            items_key: Tên key cho dữ liệu (mặc định: 'items', có thể đổi thành 'trips', 'drivers', etc.)
        
        Returns:
            Response: DRF Response object với format chuẩn
        """
        from rest_framework import status
        
        return Response({
            'success': True,
            'data': {
                items_key: data,  # Dữ liệu đã phân trang (tên key có thể tùy chỉnh)
                'pagination': pagination_info  # Thông tin phân trang
            },
            'message': message
        }, status=status.HTTP_200_OK)


# Instance mặc định để sử dụng nhanh
default_pagination = CustomPagination(default_page_size=20, max_page_size=100)

# Instance cho trips (có thể tùy chỉnh)
trips_pagination = CustomPagination(default_page_size=20, max_page_size=100)

# Instance cho available trips (page size lớn hơn)
available_trips_pagination = CustomPagination(default_page_size=50, max_page_size=200)
