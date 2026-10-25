from django.db import models
from django.conf import settings


class Tag(models.Model):
    """Bảng tags trong PostgreSQL"""
    tag_id = models.AutoField(primary_key=True)
    tag_name = models.CharField(max_length=100, unique=True)

    class Meta:
        managed = False
        db_table = 'tags'
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['tag_id']

    def __str__(self):
        return self.tag_name


class Folder(models.Model):
    """Bảng folders trong PostgreSQL"""
    folder_id = models.AutoField(primary_key=True)
    folder_name = models.CharField(max_length=255)
    subject = models.ForeignKey(
        'academics.Subject',
        on_delete=models.CASCADE,
        db_column='subject_id',
        related_name='folders',
    )
    parent_folder = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        db_column='parent_folder_id',
        null=True,
        blank=True,
        related_name='subfolders',
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        db_column='created_by',
        null=True,
        blank=True,
        related_name='created_folders',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'folders'
        verbose_name = 'Thư mục'
        verbose_name_plural = 'Thư mục'
        unique_together = (('subject', 'parent_folder', 'folder_name'),)
        ordering = ['folder_id']

    def __str__(self):
        return self.folder_name


class Document(models.Model):
    """Bảng documents trong PostgreSQL"""
    PENDING = 'PENDING'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'
    STATUS_CHOICES = [
        (PENDING, 'Chờ duyệt'),
        (APPROVED, 'Đã duyệt'),
        (REJECTED, 'Từ chối'),
    ]

    document_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    subject = models.ForeignKey(
        'academics.Subject',
        on_delete=models.CASCADE,
        db_column='subject_id',
        related_name='documents',
    )
    folder = models.ForeignKey(
        Folder,
        on_delete=models.SET_NULL,
        db_column='folder_id',
        null=True,
        blank=True,
        related_name='documents',
    )
    uploader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        db_column='uploader_id',
        null=True,
        blank=True,
        related_name='uploaded_documents',
    )
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=PENDING)
    is_public = models.BooleanField(default=False)
    view_count = models.IntegerField(default=0)
    download_count = models.IntegerField(default=0)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        db_column='approved_by',
        null=True,
        blank=True,
        related_name='approved_documents',
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    tags = models.ManyToManyField(Tag, through='DocumentTag', related_name='documents', blank=True)

    class Meta:
        managed = False
        db_table = 'documents'
        verbose_name = 'Tài liệu'
        verbose_name_plural = 'Tài liệu'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def id(self):
        return self.document_id

    @property
    def latest_version(self):
        return self.versions.order_by('-version_number').first()


class DocumentTag(models.Model):
    """Bảng trung gian document_tags trong PostgreSQL"""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, db_column='document_id', primary_key=True)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, db_column='tag_id')

    class Meta:
        managed = False
        db_table = 'document_tags'
        unique_together = (('document', 'tag'),)


class DocumentVersion(models.Model):
    """Bảng document_versions trong PostgreSQL"""
    version_id = models.AutoField(primary_key=True)
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        db_column='document_id',
        related_name='versions',
    )
    file_path = models.CharField(max_length=500)
    version_number = models.IntegerField()
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        db_column='updated_by',
        null=True,
        blank=True,
        related_name='updated_versions',
    )
    updated_at = models.DateTimeField(auto_now_add=True)
    change_summary = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'document_versions'
        verbose_name = 'Phiên bản tài liệu'
        verbose_name_plural = 'Phiên bản tài liệu'
        unique_together = (('document', 'version_number'),)
        ordering = ['-version_number']

    def __str__(self):
        return f'{self.document.title} – v{self.version_number}'


class DocumentActivityLog(models.Model):
    """Bảng document_activity_logs trong PostgreSQL"""
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

    log_id = models.AutoField(primary_key=True)
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        db_column='document_id',
        related_name='activity_logs',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        db_column='user_id',
        null=True,
        blank=True,
        related_name='activity_logs',
    )
    action = models.CharField(max_length=100, choices=ACTION_CHOICES)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'document_activity_logs'
        verbose_name = 'Nhật ký hoạt động'
        verbose_name_plural = 'Nhật ký hoạt động'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.action} – {self.document.title}'
