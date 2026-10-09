from django.db import models
from django.conf import settings


class Tag(models.Model):
    tag_name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'tags'
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['tag_name']

    def __str__(self):
        return self.tag_name


class Folder(models.Model):
    folder_name = models.CharField(max_length=255)
    subject = models.ForeignKey(
        'academics.Subject',
        on_delete=models.CASCADE,
        related_name='folders',
    )
    parent_folder = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subfolders',
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
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

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    subject = models.ForeignKey(
        'academics.Subject',
        on_delete=models.CASCADE,
        related_name='documents',
    )
    folder = models.ForeignKey(
        Folder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents',
    )
    uploader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_documents',
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
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name='documents')
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
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='versions',
    )
    file = models.FileField(upload_to='documents/')
    version_number = models.PositiveIntegerField()
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
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

    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='activity_logs',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
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
