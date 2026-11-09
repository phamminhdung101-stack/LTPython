from rest_framework import serializers
from .models import User, Role
from academics.models import Department, Class
from academics.serializers import DepartmentSerializer, ClassSerializer


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['role_id', 'role_name']


class UserSerializer(serializers.ModelSerializer):
    """Serializer lấy thông tin người dùng (an toàn - không bao giờ trả về password/hash)"""
    role = RoleSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    student_class = ClassSerializer(read_only=True)
    role_name = serializers.CharField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = [
            'user_id',
            'username',
            'full_name',
            'role',
            'role_name',
            'department',
            'student_class',
            'is_active',
            'created_at',
        ]
        read_only_fields = ['user_id', 'created_at']


class LoginSerializer(serializers.Serializer):
    """Dữ liệu đầu vào đăng nhập"""
    username = serializers.CharField(max_length=100, required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})


class ChangePasswordSerializer(serializers.Serializer):
    """Đổi mật khẩu an toàn"""
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, min_length=6, write_only=True)
    confirm_password = serializers.CharField(required=True, min_length=6, write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'Xác nhận mật khẩu mới không khớp.'})
        return data


class UserCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer cho Admin tạo hoặc cập nhật tài khoản người dùng"""
    password = serializers.CharField(write_only=True, required=False, min_length=6)
    role_id = serializers.IntegerField(required=False)
    department_id = serializers.IntegerField(required=False, allow_null=True)
    class_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            'user_id',
            'username',
            'password',
            'full_name',
            'role_id',
            'department_id',
            'class_id',
            'created_at',
        ]
        read_only_fields = ['user_id', 'created_at']

    def validate_username(self, value):
        user_id = self.instance.user_id if self.instance else None
        if User.objects.filter(username=value).exclude(pk=user_id).exists():
            raise serializers.ValidationError('Tên đăng nhập đã tồn tại trong hệ thống.')
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        role_id = validated_data.pop('role_id', None)
        dept_id = validated_data.pop('department_id', None)
        cls_id = validated_data.pop('class_id', None)

        role = Role.objects.get(pk=role_id) if role_id else Role.objects.get(role_name=Role.STUDENT)
        dept = Department.objects.get(pk=dept_id) if dept_id else None
        cls = Class.objects.get(pk=cls_id) if cls_id else None

        user = User(
            role=role,
            department=dept,
            student_class=cls,
            **validated_data
        )
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        role_id = validated_data.pop('role_id', None)
        dept_id = validated_data.pop('department_id', None)
        cls_id = validated_data.pop('class_id', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if role_id is not None:
            instance.role = Role.objects.get(pk=role_id)
        if dept_id is not None:
            instance.department = Department.objects.get(pk=dept_id) if dept_id else None
        if cls_id is not None:
            instance.student_class = Class.objects.get(pk=cls_id) if cls_id else None

        if password:
            instance.set_password(password)

        instance.save()
        return instance

