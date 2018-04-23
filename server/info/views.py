from django.shortcuts import render
# from django.http import HttpResponse, JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from django.http import Http404
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from info.models import *
from info.serializers import *
from info.permissions import IsTo
##Custom permisionn won't work if we don't use GenericAPIView based classes. See the django rest_framework
## permissions documentation
# See this for an overview tutorial
# https://www.andreagrandi.it/2016/10/01/creating-a-production-ready-api-with-python-and-django-rest-framework-part-2/
#1) To get token for the user:
# http --json POST http://127.0.0.1:8000/api-token-auth/ username="deepak" password="deepaksaini"
#2) username, pass based authentication using BasicAuthentication:
# http -a deepak:deepaksaini GET http://127.0.0.1:8000/journeys/
#3) token based authentication:
# http GET http://127.0.0.1:8000/notifications/ "Authorization: Token 2c2670e251bfcacd19b09dff689447a513edb7db"



class NotificationList(APIView):
	permission_classes = (permissions.IsAuthenticated,)
	# authentication_classes = (SessionAuthentication, BasicAuthentication)
	def get(self,request,format=None):
		notifs = Notification.objects.filter(user_to=request.user)
		serializer = NotificationSerializer(notifs, many=True)
		return Response(serializer.data)

	def post(self,request,format=None):
		data = JSONParser().parse(request)
		serializer = NotificationSerializer(data=data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class JourneyList(APIView):
	# authentication_classes = (SessionAuthentication, BasicAuthentication)
	permission_classes = (permissions.IsAuthenticated,)
	def get(self,request,format=None):
		journeys = Journey.objects.filter(participants__in=[request.user])
		serializer = JourneySerializer(journeys, many=True)
		return Response(serializer.data)

	def post(self,request,format=None):
		data = JSONParser().parse(request)
		serializer = JourneySerializer(data=data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @csrf_exempt
# @api_view(["GET","DELETE"])
class UserNotifications(APIView):
	permission_classes = (permissions.IsAuthenticated,)
	def get_user_notifications(self,username):
		try:
			return Notification.objects.filter(user_to__username = username)
		except Snippet.DoesNotExist:
			raise Http404
	def get(self,request,username,format=None):
		notifs = self.get_user_notifications(username)
		serializer = NotificationSerializer(notifs,many=True)
		return Response(serializer.data)

	def delete(self,request,username,format=None):
		notifs = self.get_user_notifications(username)
		notifs.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)
