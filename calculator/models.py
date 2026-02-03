from django.db import models


class Execution(models.Model):
    """Model to store execution history of cashflow calculations."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    input_file = models.FileField(upload_to='inputs/')
    output_file = models.FileField(upload_to='outputs/', null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    input_rows = models.IntegerField(default=0)
    output_rows = models.IntegerField(default=0)

    error_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Execution {self.id} - {self.status} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
