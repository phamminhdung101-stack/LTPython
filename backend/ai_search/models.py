from django.db import models
from django.conf import settings


class DocumentEmbedding(models.Model):
    """Bảng document_embeddings trong PostgreSQL"""
    embedding_id = models.AutoField(primary_key=True)
    document = models.ForeignKey(
        'documents.Document',
        on_delete=models.CASCADE,
        db_column='document_id',
        related_name='embeddings',
    )
    chunk_index = models.IntegerField()
    chunk_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'document_embeddings'
        unique_together = (('document', 'chunk_index'),)
        verbose_name = 'Embedding tài liệu'
        verbose_name_plural = 'Embeddings tài liệu'

    def __str__(self):
        return f'{self.document.title} - chunk #{self.chunk_index}'


class AIQuery(models.Model):
    """Bảng ai_queries trong PostgreSQL"""
    query_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        db_column='user_id',
        null=True,
        blank=True,
        related_name='ai_queries',
    )
    query_text = models.TextField()
    ai_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    source_documents = models.ManyToManyField(
        'documents.Document',
        through='AIQuerySource',
        related_name='referenced_ai_queries',
        blank=True,
    )

    class Meta:
        managed = False
        db_table = 'ai_queries'
        verbose_name = 'Câu hỏi AI'
        verbose_name_plural = 'Câu hỏi AI'
        ordering = ['-created_at']

    def __str__(self):
        return self.query_text[:80]


class AIQuerySource(models.Model):
    """Bảng ai_query_sources trong PostgreSQL"""
    query = models.ForeignKey(
        AIQuery,
        on_delete=models.CASCADE,
        db_column='query_id',
        primary_key=True,
    )
    document = models.ForeignKey(
        'documents.Document',
        on_delete=models.CASCADE,
        db_column='document_id',
    )
    embedding = models.ForeignKey(
        DocumentEmbedding,
        on_delete=models.SET_NULL,
        db_column='embedding_id',
        null=True,
        blank=True,
    )

    class Meta:
        managed = False
        db_table = 'ai_query_sources'
        unique_together = (('query', 'document', 'embedding'),)
        verbose_name = 'Nguồn câu trả lời AI'
        verbose_name_plural = 'Nguồn câu trả lời AI'
