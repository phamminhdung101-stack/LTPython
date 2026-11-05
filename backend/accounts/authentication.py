import jwt
from datetime import datetime, timedelta, timezone
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import User


def generate_jwt_token(user, expires_in_days=7) -> str:
    """
    Sinh JWT token an toàn chứa thông tin định danh và vai trò người dùng.
    """
    now = datetime.now(timezone.utc)
    role_name = user.role.role_name if user.role else 'STUDENT'
    payload = {
        'user_id': user.user_id,
        'username': user.username,
        'role': role_name,
        'department_id': getattr(user, 'department_id', None),
        'class_id': getattr(user, 'student_class_id', None) or getattr(user, 'class_id', None),
        'iat': int(now.timestamp()),
        'exp': int((now + timedelta(days=expires_in_days)).timestamp()),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')


def decode_jwt_token(token: str) -> dict:
    """
    Giải mã và kiểm tra tính hợp lệ của JWT token.
    """
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Phiên làm việc JWT đã hết hạn. Vui lòng đăng nhập lại.')
    except jwt.InvalidTokenError:
        raise AuthenticationFailed('Token xác thực không hợp lệ.')


class JWTAuthentication(BaseAuthentication):
    """
    Custom DRF Authentication hỗ trợ:
    1. Header: Authorization: Bearer <token>
    2. Query param: ?token=<token> (phục vụ tải file trực tiếp trên trình duyệt)
    """

    def authenticate_header(self, request):
        return 'Bearer'

    def authenticate(self, request):
        token = None

        # 1. Kiểm tra header Authorization
        auth_header = request.headers.get('Authorization') or request.META.get('HTTP_AUTHORIZATION')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ', 1)[1].strip()

        # 2. Hỗ trợ query parameter 'token' cho download request
        if not token and hasattr(request, 'query_params') and 'token' in request.query_params:
            token = request.query_params.get('token')
        elif not token and hasattr(request, 'GET') and 'token' in request.GET:
            token = request.GET.get('token')

        if not token:
            return None

        payload = decode_jwt_token(token)
        user_id = payload.get('user_id')
        if not user_id:
            raise AuthenticationFailed('Token không chứa user_id hợp lệ.')

        try:
            user = User.objects.select_related('role', 'department', 'student_class').get(pk=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed('Người dùng trong token không tồn tại.')

        if not user.is_active:
            raise AuthenticationFailed('Tài khoản của bạn hiện đang bị khóa hoặc chưa được kích hoạt.')

        return (user, token)
