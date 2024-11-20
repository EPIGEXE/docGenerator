from django.db import models

# Create your models here.
class Document(models.Model):
    DOCUMENT_TYPES = (
        ('ppt', 'PowerPoint'),
        ('excel', 'Excel'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )

    spec_content = models.TextField(verbose_name='명세서 내용')
    doc_type = models.CharField(max_length=10, choices=DOCUMENT_TYPES, verbose_name='문서 유형')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='상태')
    file = models.FileField(upload_to='documents/%Y/%m/%d/', null=True, blank=True, verbose_name='생성된 파일')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    error_message = models.TextField(null=True, blank=True, verbose_name='에러 메시지')

    class Meta:
        ordering = ['-created_at']
