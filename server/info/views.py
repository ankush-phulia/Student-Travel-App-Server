from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

from info.models import *
from info.serializers import *


@csrf_exempt
def notification_list(request):
    if request.method == 'GET':
        notifs = Notification.objects.all()
        serializer = NotificationSerializer(notifs, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = NotificationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)


@csrf_exempt
def user_notifications(request, username):
    try:
        notifs = Notification.objects.filter(user_to__username = username)
    except Snippet.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == "GET":
        serializer = NotificationSerializer(notifs,many=True)
        return JsonResponse(serializer.data,safe=False)

    elif request.method == "DELETE":
        notifs.delete()
        return HttpResponse(status=204)