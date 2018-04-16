from rest_framework import serializers
from info.models import *
from django.contrib.auth.models import User

class NotificationSerializer(serializers.ModelSerializer):
	user_from = serializers.CharField(source="user_from.username")
	user_to = serializers.CharField(source="user_to.username")

	class Meta:
		model = Notification
		fields = ("user_from","user_to","text","notif_type","creation_time",)

	def create(self,validated_data):
		# print(">>>>>>>>>>",validated_data.pop('user_to'))
		user_to = User.objects.get(username=validated_data.pop('user_to')["username"])
		user_from = User.objects.get(username=validated_data.pop('user_from')["username"])
		return Notification.objects.create(user_to=user_to,user_from=user_from,**validated_data)
