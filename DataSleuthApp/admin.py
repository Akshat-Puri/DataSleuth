from django.contrib import admin
from .models import Agent, File, LeakDetectionLog, Log


class LogAdmin(admin.ModelAdmin):
    list_display = ('action', 'agent', 'user', 'timestamp')
    list_display_links = ('action', 'timestamp')  # Makes these fields clickable
    list_filter = ('action', 'timestamp')
    search_fields = ('description',)
    ordering = ('-timestamp',)  # Orders logs by most recent first


class AgentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at')
    search_fields = ('name', 'email')
    list_filter = ('created_at',)


class FileAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'file_type', 'agent', 'uploaded_at')
    search_fields = ('file_name',)
    list_filter = ('file_type', 'uploaded_at')


class LeakDetectionLogAdmin(admin.ModelAdmin):
    list_display = ('file', 'detected_at', 'unauthorized_location', 'status')
    search_fields = ('unauthorized_location',)
    list_filter = ('detected_at', 'status')


# Register your models here
admin.site.register(Log, LogAdmin)
admin.site.register(Agent, AgentAdmin)
admin.site.register(File, FileAdmin)
admin.site.register(LeakDetectionLog, LeakDetectionLogAdmin)
