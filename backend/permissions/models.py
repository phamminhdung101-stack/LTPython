from django.db import models


class DocumentPermission(models.Model):
    DEPARTMENT = 'DEPARTMENT'
    CLASS = 'CLASS'
    USER = 'USER'
    PERMISSION_TYPE_CHOICES = [
        (DEPARTMENT, 'Theo khoa'),
        (CLASS, 'Theo lớp'),
        (USER, 'Theo người dùng'),
    ]

    id = models.AutoField(primary_key=True, db_column='permission_id')
    document = models.ForeignKey(
        'documents.Document',
        on_delete=models.CASCADE,
        related_name='permissions',
        db_column='document_id',
    )
    permission_type = models.CharField(max_length=50, choices=PERMISSION_TYPE_CHOICES)

    department = models.ForeignKey(
        'academics.Department',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column='department_id',
    )
    student_class = models.ForeignKey(
        'academics.Class',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column='class_id',
    )
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column='user_id',
    )

    can_view = models.BooleanField(default=True)
    can_download = models.BooleanField(default=True)
    can_edit = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'document_permissions'
        verbose_name = 'Quyền tài liệu'
        verbose_name_plural = 'Quyền tài liệu'

    def __str__(self):
        return f'{self.permission_type} – {self.document.title}'
