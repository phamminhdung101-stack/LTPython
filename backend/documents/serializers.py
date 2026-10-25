from rest_framework import serializers
from .models import Tag, Folder, Document, DocumentVersion, DocumentActivityLog
from academics.serializers import SubjectSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['tag_id', 'tag_name']


class FolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = ['folder_id', 'folder_name', 'subject_id', 'parent_folder_id', 'created_by_id', 'created_at']


class DocumentVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentVersion
        fields = ['version_id', 'document_id', 'file_path', 'version_number', 'updated_by_id', 'updated_at', 'change_summary']


class DocumentSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    uploader_name = serializers.CharField(source='uploader.full_name', read_only=True, default='')
    approved_by_name = serializers.CharField(source='approved_by.full_name', read_only=True, default='')
    latest_version_path = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'document_id',
            'title',
            'description',
            'subject',
            'folder_id',
            'uploader_id',
            'uploader_name',
            'status',
            'is_public',
            'view_count',
            'download_count',
            'approved_by_id',
            'approved_by_name',
            'approved_at',
            'created_at',
            'tags',
            'latest_version_path',
        ]

    def get_latest_version_path(self, obj):
        latest = obj.latest_version
        return latest.file_path if latest else ''


class DocumentCreateSerializer(serializers.ModelSerializer):
    subject_id = serializers.IntegerField(required=True)
    folder_id = serializers.IntegerField(required=False, allow_null=True)
    is_public = serializers.BooleanField(default=False)

    class Meta:
        model = Document
        fields = [
            'document_id',
            'title',
            'description',
            'subject_id',
            'folder_id',
            'is_public',
        ]

