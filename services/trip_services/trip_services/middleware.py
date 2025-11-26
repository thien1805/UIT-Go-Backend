import jwt
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class JWTAuthMiddleware(MiddlewareMixin):
    """
    Middleware để xác thực JWT token từ User Service

    Trip Service không có user database riêng, nên validate JWT từ User Service
    """

    def process_request(self, request):
        # Lấy token từ header Authorization
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            # Không có token, set user là AnonymousUser
            request.user = AnonymousUser()
            return

        token = auth_header.split(' ')[1]  # Lấy token sau "Bearer "

        try:
            # Decode và validate token
            access_token = AccessToken(token)
            user_id = access_token['user_id']

            # Tạo một mock user object với id từ token
            # Trong thực tế, có thể call User Service để lấy thông tin user
            class MockUser:
                def __init__(self, user_id):
                    self.id = user_id
                    self.is_authenticated = True

                def __str__(self):
                    return f"User {self.id}"

            request.user = MockUser(user_id)

        except (InvalidToken, TokenError, KeyError):
            # Token không hợp lệ
            request.user = AnonymousUser()
            return

