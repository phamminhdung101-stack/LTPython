from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class Role(models.Model):
    ADMIN = 'ADMIN'
    LECTURER = 'LECTURER'
    STUDENT = 'STUDENT'
    ROLE_CHOICES = [
        (ADMIN, 'Quản trị viên'),
        (LECTURER, 'Giảng viên'),
        (STUDENT, 'Sinh viên'),
    ]

    role_name = models.CharField(max_length=50, unique=True, choices=ROLE_CHOICES)

    class Meta:
        db_table = 'roles'
        verbose_name = 'Vai trò'
        verbose_name_plural = 'Vai trò'

    def __str__(self):
        return self.get_role_name_display()


class UserManager(BaseUserManager):
    def create_user(self, username, full_name, role, password=None, **extra_fields):
        if not username:
            raise ValueError('Username là bắt buộc')
        user = self.model(username=username, full_name=full_name, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, full_name, password=None, **extra_fields):
        admin_role, _ = Role.objects.get_or_create(role_name=Role.ADMIN)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, full_name, admin_role, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=100, unique=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, default='')

    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name='users',
        null=True,
        blank=True,
    )
    department = models.ForeignKey(
        'academics.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
    )
    student_class = models.ForeignKey(
        'academics.Class',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        db_table = 'users'
        verbose_name = 'Người dùng'
        verbose_name_plural = 'Người dùng'

    def __str__(self):
        return f'{self.full_name} (@{self.username})'

    @property
    def role_name(self):
        return self.role.role_name if self.role else None

    @property
    def is_admin(self):
        return self.role_name == Role.ADMIN

    @property
    def is_lecturer(self):
        return self.role_name == Role.LECTURER

    @property
    def is_student(self):
        return self.role_name == Role.STUDENT
