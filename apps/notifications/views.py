from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Notification

@login_required
def notifications_list(request):
    notifications = Notification.objects.filter(destinataire=request.user).order_by('-date_creation')
    return render(request, 'notifications/list.html', {'notifications': notifications})
