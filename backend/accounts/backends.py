from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password, make_password
from .models import User, Role


class PostgresAuthBackend(BaseBackend):
    """
    Custom authentication backend cho bảng users trong PostgreSQL:
    1. Kiểm tra mật khẩu theo thuật toán hash của Django.
    2. Hỗ trợ dữ liệu hạt giống ban đầu (hash_admin, hash_gv, hash_sv)
       và tự động nâng cấp sang Django hash an toàn (PBKDF2) sau lần đăng nhập đầu tiên.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        try:
            user = User.objects.select_related('role', 'department', 'student_class').get(username=username)
        except User.DoesNotExist:
            return None

        # 1. Kiểm tra mật khẩu bằng thuật toán chuẩn Django
        if check_password(password, user.password):
            return user

        # 2. Xử lý các hash mẫu khởi tạo từ schema.sql
        is_seed_match = False
        stored_hash = user.password or ''

        if stored_hash == 'hash_admin' and password in ('admin', 'admin123', 'hash_admin', '123456'):
            is_seed_match = True
        elif stored_hash == 'hash_gv' and password in ('gv', 'gv123', 'hash_gv', '123456'):
            is_seed_match = True
        elif stored_hash == 'hash_sv' and password in ('sv', 'sv123', 'hash_sv', '123456'):
            is_seed_match = True
        elif stored_hash == password:
            is_seed_match = True

        if is_seed_match:
            # Tự động nâng cấp mật khẩu sang Django PBKDF2 hash chuẩn
            user.set_password(password)
            user.save(update_fields=['password'])
            return user

        return None

    def get_user(self, user_id):
        try:
            return User.objects.select_related('role', 'department', 'student_class').get(pk=user_id)
        except User.DoesNotExist:
            return None

