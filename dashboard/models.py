from django.db import models


class NoticeHistory(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)

    class Meta:
        ordering = ['-created_at']
