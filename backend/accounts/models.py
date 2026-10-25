from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class Role(models.Model):
    """Bảng roles trong PostgreSQL: ADMIN, LECTURER, STUDENT"""
    ADMIN = 'ADMIN'
    LECTURER = 'LECTURER'
    STUDENT = 'STUDENT'
    ROLE_CHOICES = [
        (ADMIN, 'Quản trị viên'),
        (LECTURER, 'Giảng viên'),
        (STUDENT, 'Sinh viên'),
    ]

    role_id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=50, unique=True, choices=ROLE_CHOICES)

    class Meta:
        managed = False
        db_table = 'roles'
        verbose_name = 'Vai trò'
        verbose_name_plural = 'Vai trò'
        ordering = ['role_id']

    def __str__(self):
        return self.get_role_name_display() or self.role_name


class UserManager(BaseUserManager):
    def create_user(self, username, full_name, role=None, password=None, **extra_fields):
        if not username:
            raise ValueError('Username là bắt buộc')
        if not role:
            role = Role.objects.filter(role_name=Role.STUDENT).first()
        user = self.model(username=username, full_name=full_name, role=role, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, username, full_name, password=None, **extra_fields):
        admin_role, _ = Role.objects.get_or_create(role_name=Role.ADMIN)
        return self.create_user(username, full_name, admin_role, password, **extra_fields)


class User(AbstractBaseUser):
    """
    Ánh xạ bảng users hiện có trong PostgreSQL:
    user_id, username, password_hash, full_name, role_id, department_id, class_id, created_at
    """
    last_login = None  # Không có cột last_login trong PostgreSQL schema

    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=255, db_column='password_hash')
    full_name = models.CharField(max_length=255)

    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        db_column='role_id',
        related_name='users',
    )
    department = models.ForeignKey(
        'academics.Department',
        on_delete=models.SET_NULL,
        db_column='department_id',
        null=True,
        blank=True,
        related_name='users',
    )
    student_class = models.ForeignKey(
        'academics.Class',
        on_delete=models.SET_NULL,
        db_column='class_id',
        null=True,
        blank=True,
        related_name='students',
    )

    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        managed = False
        db_table = 'users'
        verbose_name = 'Người dùng'
        verbose_name_plural = 'Người dùng'
        ordering = ['user_id']

    def __str__(self):
        return f'{self.full_name} (@{self.username})'

    @property
    def id(self):
        return self.user_id

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

    @property
    def is_active(self):
        # Nếu là sinh viên và lớp bị khóa (is_locked=True), tài khoản xem như bị khóa
        if self.is_student and self.student_class and self.student_class.is_locked:
            return False
        return True

    @property
    def is_staff(self):
        return self.is_admin

    @property
    def is_superuser(self):
        return self.is_admin

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin
