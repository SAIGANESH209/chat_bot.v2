from django.db import models

class Document(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    text = models.TextField(blank=True, null=True)  # Extracted text
    summary = models.TextField(blank=True, null=True)  # Summarized text

    def __str__(self):
        return self.file.name
