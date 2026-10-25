from django.db import models
from django.conf import settings


class DocumentPermission(models.Model):
    """Bảng document_permissions trong PostgreSQL"""
    DEPARTMENT = 'DEPARTMENT'
    CLASS = 'CLASS'
    USER = 'USER'
    PERMISSION_TYPE_CHOICES = [
        (DEPARTMENT, 'Theo khoa'),
        (CLASS, 'Theo lớp'),
        (USER, 'Theo người dùng'),
    ]

    permission_id = models.AutoField(primary_key=True)
    document = models.ForeignKey(
        'documents.Document',
        on_delete=models.CASCADE,
        db_column='document_id',
        related_name='permissions',
    )
    permission_type = models.CharField(max_length=50, choices=PERMISSION_TYPE_CHOICES)

    department = models.ForeignKey(
        'academics.Department',
        on_delete=models.CASCADE,
        db_column='department_id',
        null=True,
        blank=True,
        related_name='document_permissions',
    )
    student_class = models.ForeignKey(
        'academics.Class',
        on_delete=models.CASCADE,
        db_column='class_id',
        null=True,
        blank=True,
        related_name='document_permissions',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        db_column='user_id',
        null=True,
        blank=True,
        related_name='document_permissions',
    )

    can_view = models.BooleanField(default=True)
    can_download = models.BooleanField(default=True)
    can_edit = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'document_permissions'
        verbose_name = 'Quyền tài liệu'
        verbose_name_plural = 'Quyền tài liệu'

    def __str__(self):
        return f'{self.permission_type} – {self.document.title}'
