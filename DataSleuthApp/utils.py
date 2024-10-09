from .models import Log, Agent
from django.contrib.auth.models import User


def create_log(agent=None, user=None, action=None, description=""):
    log = Log(agent=agent, user=user, action=action, description=description)
    log.save()
