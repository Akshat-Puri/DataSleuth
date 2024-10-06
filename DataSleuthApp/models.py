from django.db import models
import uuid


class Agent(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class File(models.Model):
    FILE_TYPE_CHOICES = [
        ('.txt', 'Text File'),
        ('.pdf', 'PDF File'),
        ('.jpg', 'JPEG Image'),
        ('.bmp', 'Bitmap Image'),
    ]

    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    version_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return self.file_name


class LeakDetectionLog(models.Model):
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    detected_at = models.DateTimeField(auto_now_add=True)
    unauthorized_location = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default='unresolved')  # Example field for status

    def __str__(self):
        return f"Leak for {self.file.file_name} at {self.unauthorized_location}"
