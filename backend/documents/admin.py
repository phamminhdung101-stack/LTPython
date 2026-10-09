from django.contrib import admin
from .models import Tag, Folder, Document, DocumentVersion, DocumentActivityLog


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['tag_name']
    search_fields = ['tag_name']


@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ['folder_name', 'subject', 'parent_folder', 'created_by']
    list_filter = ['subject']
    search_fields = ['folder_name']


class DocumentVersionInline(admin.TabularInline):
    model = DocumentVersion
    extra = 0
    readonly_fields = ['updated_at']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'uploader', 'status', 'is_public', 'download_count', 'created_at']
    list_filter = ['status', 'is_public', 'subject__department']
    search_fields = ['title', 'description']
    filter_horizontal = ['tags']
    inlines = [DocumentVersionInline]
    readonly_fields = ['view_count', 'download_count', 'created_at']


@admin.register(DocumentActivityLog)
class DocumentActivityLogAdmin(admin.ModelAdmin):
    list_display = ['document', 'user', 'action', 'created_at']
    list_filter = ['action']
    readonly_fields = ['created_at']
