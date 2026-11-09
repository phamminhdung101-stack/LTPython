from rest_framework import serializers
from .models import AIQuery, AIQuerySource, DocumentEmbedding
from documents.serializers import DocumentSerializer


class DocumentEmbeddingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentEmbedding
        fields = ['embedding_id', 'document_id', 'chunk_index', 'chunk_text', 'created_at']


class AIQuerySourceSerializer(serializers.ModelSerializer):
    document = DocumentSerializer(read_only=True)
    embedding = DocumentEmbeddingSerializer(read_only=True)

    class Meta:
        model = AIQuerySource
        fields = ['query_id', 'document', 'embedding']


class AIQuerySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True, default='')

    class Meta:
        model = AIQuery
        fields = ['query_id', 'user_id', 'user_name', 'query_text', 'ai_response', 'created_at']
        read_only_fields = ['query_id', 'user_id', 'created_at']

