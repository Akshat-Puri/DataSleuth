from django.contrib import admin
from .models import Agent, File, LeakDetectionLog

admin.site.register(Agent)
admin.site.register(File)
admin.site.register(LeakDetectionLog)
