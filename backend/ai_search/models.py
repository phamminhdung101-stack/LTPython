from django.db import models
from django.conf import settings


class AIQuery(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ai_queries',
    )
    query_text = models.TextField()
    ai_response = models.TextField(blank=True, default='')
    source_documents = models.ManyToManyField(
        'documents.Document',
        blank=True,
        related_name='ai_queries',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_queries'
        verbose_name = 'Câu hỏi AI'
        verbose_name_plural = 'Câu hỏi AI'
        ordering = ['-created_at']

    def __str__(self):
        return self.query_text[:80]
