from django.db import models
from django.conf import settings


class Tag(models.Model):
    id = models.AutoField(primary_key=True, db_column='tag_id')
    tag_name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'tags'
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['tag_name']

    def __str__(self):
        return self.tag_name


class Folder(models.Model):
    id = models.AutoField(primary_key=True, db_column='folder_id')
    folder_name = models.CharField(max_length=255)
    subject = models.ForeignKey(
        'academics.Subject',
        on_delete=models.CASCADE,
        related_name='folders',
        db_column='subject_id',
    )
    parent_folder = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subfolders',
        db_column='parent_folder_id',
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='created_by',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'folders'
        verbose_name = 'Thư mục'
        verbose_name_plural = 'Thư mục'
        unique_together = [('subject', 'parent_folder', 'folder_name')]

    def __str__(self):
        return self.folder_name


class Document(models.Model):
    PENDING = 'PENDING'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'
    STATUS_CHOICES = [
        (PENDING, 'Chờ duyệt'),
        (APPROVED, 'Đã duyệt'),
        (REJECTED, 'Từ chối'),
    ]

    id = models.AutoField(primary_key=True, db_column='document_id')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    subject = models.ForeignKey(
        'academics.Subject',
        on_delete=models.CASCADE,
        related_name='documents',
        db_column='subject_id',
    )
    folder = models.ForeignKey(
        Folder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents',
        db_column='folder_id',
    )
    uploader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_documents',
        db_column='uploader_id',
    )
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=PENDING)
    is_public = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    download_count = models.PositiveIntegerField(default=0)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_documents',
        db_column='approved_by',
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='documents',
        db_table='document_tags',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'documents'
        verbose_name = 'Tài liệu'
        verbose_name_plural = 'Tài liệu'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def latest_version(self):
        return self.versions.order_by('-version_number').first()


class DocumentVersion(models.Model):
    id = models.AutoField(primary_key=True, db_column='version_id')
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='versions',
        db_column='document_id',
    )
    # Lưu Cloudflare R2 object key hoặc file path
    file = models.CharField(max_length=500, db_column='file_path')
    version_number = models.PositiveIntegerField()
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='updated_by',
    )
    updated_at = models.DateTimeField(auto_now_add=True)
    change_summary = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'document_versions'
        verbose_name = 'Phiên bản tài liệu'
        verbose_name_plural = 'Phiên bản tài liệu'
        unique_together = [('document', 'version_number')]
        ordering = ['-version_number']

    def __str__(self):
        return f'{self.document.title} – v{self.version_number}'

    @property
    def file_path(self):
        return self.file

    @property
    def object_key(self):
        return self.file

    def get_download_url(self, expires_in=3600):
        from .r2_service import r2_service
        return r2_service.generate_download_url(self.object_key, expires_in=expires_in)


class DocumentActivityLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Tạo mới'),
        ('UPDATE', 'Cập nhật'),
        ('DELETE', 'Xóa'),
        ('APPROVE', 'Duyệt'),
        ('REJECT', 'Từ chối'),
        ('VIEW', 'Xem'),
        ('DOWNLOAD', 'Tải xuống'),
        ('CHANGE_PERMISSION', 'Thay đổi quyền'),
        ('ADD_TAG', 'Thêm tag'),
        ('REMOVE_TAG', 'Xóa tag'),
    ]

    id = models.AutoField(primary_key=True, db_column='log_id')
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='activity_logs',
        db_column='document_id',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='user_id',
    )
    action = models.CharField(max_length=100, choices=ACTION_CHOICES)
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'document_activity_logs'
        verbose_name = 'Nhật ký hoạt động'
        verbose_name_plural = 'Nhật ký hoạt động'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.action} – {self.document.title}'
