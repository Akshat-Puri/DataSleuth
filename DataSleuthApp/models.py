from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class Agent(models.Model):
    name = models.CharField(max_length=255)
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

    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)  # Or consider SET_NULL if needed
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    version_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return f"File: {self.file_name}, Agent: {self.agent.name}, Uploaded at: {self.uploaded_at}"


class Log(models.Model):
    ACTION_CHOICES = [
        ('UPLOAD', 'File Upload'),
        ('ASSIGN', 'Agent Assignment'),
        ('UPDATE', 'Data Update'),
        ('DELETE', 'Data Deletion'),
    ]

    agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # Optional: Track which user did the action
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    description = models.TextField()  # Detailed info about the log
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Action: {self.action}, User: {self.user}, Agent: {self.agent}, Time: {self.timestamp}"


class LeakDetectionLog(models.Model):
    file = models.ForeignKey(File, on_delete=models.CASCADE)  # Or consider SET_NULL to preserve the leak log if file is deleted
    detected_at = models.DateTimeField(auto_now_add=True)
    unauthorized_location = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default='unresolved')  # Example field for status

    def __str__(self):
        return f"Leak detected in {self.file.file_name} at {self.unauthorized_location}, Status: {self.status}"
