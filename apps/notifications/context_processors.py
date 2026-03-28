from apps.notifications.models import Notification


def unread_notifications_count(request):
    if request.user.is_authenticated:
        nb = Notification.objects.filter(destinataire=request.user, est_lue=False).count()
    else:
        nb = 0
    return {'unread_notifications_count': nb}
