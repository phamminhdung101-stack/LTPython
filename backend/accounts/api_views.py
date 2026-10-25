from django.contrib.auth import authenticate, login, logout
from django.db import connection
from django.db.models import Q
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import User, Role
from .serializers import (
    UserSerializer,
    LoginSerializer,
    ChangePasswordSerializer,
    UserCreateUpdateSerializer,
    RoleSerializer,
)
from permissions.rest_permissions import (
    IsAuthenticatedCustom,
    IsAdminUserRole,
    IsOwnerOrAdmin,
)


class HealthCheckAPIView(APIView):
    """
    GET /api/health/
    Kiểm tra tình trạng backend Django và kết nối trực tiếp đến PostgreSQL
    """
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            connection.ensure_connection()
            db_name = connection.settings_dict.get('NAME', 'unknown')
            db_vendor = connection.vendor
            return Response({
                'status': 'healthy',
                'backend': 'Django REST Framework',
                'database': {
                    'connected': True,
                    'name': db_name,
                    'vendor': db_vendor,
                    'status': 'active',
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': 'unhealthy',
                'backend': 'Django REST Framework',
                'database': {
                    'connected': False,
                    'error': str(e),
                }
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class LoginAPIView(APIView):
    """
    POST /api/auth/login/
    Xác thực đăng nhập người dùng và tạo session
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'status': 'error',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response({
                'status': 'error',
                'message': 'Tên đăng nhập hoặc mật khẩu không chính xác.',
            }, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({
                'status': 'error',
                'message': 'Tài khoản của bạn hiện đang bị khóa hoặc chưa được kích hoạt.',
            }, status=status.HTTP_403_FORBIDDEN)

        # Lưu thông tin phiên đăng nhập
        login(request, user)

        user_data = UserSerializer(user).data
        return Response({
            'status': 'success',
            'message': f'Xin chào {user.full_name}, đăng nhập thành công!',
            'user': user_data,
        }, status=status.HTTP_200_OK)


class LogoutAPIView(APIView):
    """
    POST /api/auth/logout/
    Đăng xuất và hủy session hiện tại
    """
    permission_classes = [AllowAny]

    def post(self, request):
        if request.user.is_authenticated:
            logout(request)
        return Response({
            'status': 'success',
            'message': 'Đã đăng xuất thành công khỏi hệ thống.',
        }, status=status.HTTP_200_OK)


class CurrentUserAPIView(APIView):
    """
    GET /api/auth/me/
    Lấy thông tin người dùng đang đăng nhập
    """
    permission_classes = [IsAuthenticatedCustom]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response({
            'status': 'success',
            'user': serializer.data,
        }, status=status.HTTP_200_OK)


class AuthStatusAPIView(APIView):
    """
    GET /api/auth/status/
    Kiểm tra trạng thái đăng nhập
    """
    permission_classes = [AllowAny]

    def get(self, request):
        is_auth = bool(request.user and request.user.is_authenticated)
        user_data = UserSerializer(request.user).data if is_auth else None
        return Response({
            'is_authenticated': is_auth,
            'user': user_data,
        }, status=status.HTTP_200_OK)


class ChangePasswordAPIView(APIView):
    """
    POST /api/auth/change-password/
    Đổi mật khẩu cho tài khoản đang đăng nhập
    """
    permission_classes = [IsAuthenticatedCustom]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'status': 'error',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        old_pwd = serializer.validated_data['old_password']
        new_pwd = serializer.validated_data['new_password']

        # Kiểm tra mật khẩu cũ
        if not user.check_password(old_pwd):
            return Response({
                'status': 'error',
                'message': 'Mật khẩu hiện tại không chính xác.',
            }, status=status.HTTP_400_BAD_REQUEST)

        # Lưu mật khẩu mới được băm bằng PBKDF2 của Django
        user.set_password(new_pwd)
        user.save(update_fields=['password'])

        return Response({
            'status': 'success',
            'message': 'Đổi mật khẩu thành công. Vui lòng sử dụng mật khẩu mới cho các lần đăng nhập tiếp theo.',
        }, status=status.HTTP_200_OK)


class UserListCreateAPIView(APIView):
    """
    GET /api/users/ (Admin xem danh sách có lọc & tìm kiếm)
    POST /api/users/ (Admin tạo người dùng mới)
    """
    permission_classes = [IsAdminUserRole]

    def get(self, request):
        qs = User.objects.select_related('role', 'department', 'student_class').order_by('user_id')

        q = request.GET.get('q', '').strip()
        role_filter = request.GET.get('role', '').strip()
        dept_filter = request.GET.get('department', '').strip()
        class_filter = request.GET.get('class', '').strip()

        if q:
            qs = qs.filter(
                Q(full_name__icontains=q) |
                Q(username__icontains=q)
            )
        if role_filter and role_filter != 'ALL':
            qs = qs.filter(role__role_name=role_filter)
        if dept_filter and dept_filter != 'ALL':
            if dept_filter.isdigit():
                qs = qs.filter(department_id=int(dept_filter))
            else:
                qs = qs.filter(department__department_name__icontains=dept_filter)
        if class_filter and class_filter != 'ALL':
            if class_filter.isdigit():
                qs = qs.filter(student_class_id=int(class_filter))
            else:
                qs = qs.filter(student_class__class_name__icontains=class_filter)

        serializer = UserSerializer(qs, many=True)
        return Response({
            'status': 'success',
            'total': qs.count(),
            'users': serializer.data,
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = UserCreateUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'status': 'error',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        new_user = serializer.save()
        return Response({
            'status': 'success',
            'message': f'Đã tạo người dùng {new_user.full_name} thành công.',
            'user': UserSerializer(new_user).data,
        }, status=status.HTTP_201_CREATED)


class UserDetailAPIView(APIView):
    """
    GET /api/users/<pk>/
    PUT/PATCH /api/users/<pk>/
    DELETE /api/users/<pk>/
    """
    permission_classes = [IsAuthenticatedCustom]

    def get_object(self, pk):
        try:
            return User.objects.select_related('role', 'department', 'student_class').get(pk=pk)
        except User.DoesNotExist:
            return None

    def get(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response({'status': 'error', 'message': 'Không tìm thấy người dùng.'}, status=status.HTTP_404_NOT_FOUND)

        # Chỉ Admin hoặc chính người dùng đó mới xem được
        if not (request.user.is_admin or request.user.user_id == user.user_id):
            return Response({'status': 'error', 'message': 'Bạn không có quyền xem thông tin người dùng này.'}, status=status.HTTP_403_FORBIDDEN)

        return Response({
            'status': 'success',
            'user': UserSerializer(user).data,
        }, status=status.HTTP_200_OK)

    def put(self, request, pk):
        return self.patch(request, pk)

    def patch(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response({'status': 'error', 'message': 'Không tìm thấy người dùng.'}, status=status.HTTP_404_NOT_FOUND)

        # Kiểm tra quyền: Admin hoặc chính chủ
        is_self = request.user.user_id == user.user_id
        if not (request.user.is_admin or is_self):
            return Response({'status': 'error', 'message': 'Bạn không có quyền chỉnh sửa thông tin này.'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()

        # Ngăn người dùng thông thường tự ý đổi role hoặc phòng ban
        if not request.user.is_admin:
            data.pop('role_id', None)
            data.pop('role', None)
            data.pop('department_id', None)
            data.pop('class_id', None)

        serializer = UserCreateUpdateSerializer(user, data=data, partial=True)
        if not serializer.is_valid():
            return Response({'status': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        updated_user = serializer.save()
        return Response({
            'status': 'success',
            'message': 'Cập nhật thông tin thành công.',
            'user': UserSerializer(updated_user).data,
        }, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        if not request.user.is_admin:
            return Response({'status': 'error', 'message': 'Chỉ Quản trị viên mới có quyền xóa người dùng.'}, status=status.HTTP_403_FORBIDDEN)

        user = self.get_object(pk)
        if not user:
            return Response({'status': 'error', 'message': 'Không tìm thấy người dùng.'}, status=status.HTTP_404_NOT_FOUND)

        if user.user_id == request.user.user_id:
            return Response({'status': 'error', 'message': 'Bạn không thể tự xóa tài khoản đang đăng nhập của chính mình.'}, status=status.HTTP_400_BAD_REQUEST)

        name = user.full_name
        user.delete()
        return Response({
            'status': 'success',
            'message': f'Đã xóa tài khoản {name} thành công.',
        }, status=status.HTTP_200_OK)


class RoleListAPIView(APIView):
    """
    GET /api/roles/
    Lấy danh sách các vai trò hệ thống
    """
    permission_classes = [AllowAny]

    def get(self, request):
        roles = Role.objects.all().order_by('role_id')
        serializer = RoleSerializer(roles, many=True)
        return Response({
            'status': 'success',
            'roles': serializer.data,
        }, status=status.HTTP_200_OK)

