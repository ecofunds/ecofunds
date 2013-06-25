
from  ecofunds.models import *
from django.contrib.auth.models import User

def notificate(obj,type,user,msg):
    model = obj.__class__
    try:
        type = NotificationType.objects.get(description=type)
    except Notification.DoesNotExist:
        return
    note = Notification(notification_type=type,message=msg)
    receivers = [user]
    if model == Project:
        for org in obj.organization.all():
            for userporg in org.userprofiles.all():
                user = userporg.user
                if not user in receivers:
                    receivers.append(user)
        note.project = obj
    elif model == Organization:
        for userporg in obj.userprofiles.all():
            user = userporg.user
            if not user in receivers:
                receivers.append(user)
        note.organization = obj
    elif model == User:
        for org in obj.organizations:
            for userporg in org.userprofiles.all():
                if userporg.admin:
                    user = userporg.userprofile
                    if not user in receiver:
                        receivers.append(user)
        note.user_updated = obj
    note.receivers = receivers
    note.user = user
    note.save()

def create_notification_type():
    NotificationType(description='create').save()
    NotificationType(description='update').save()
    NotificationType(description='delete').save()

