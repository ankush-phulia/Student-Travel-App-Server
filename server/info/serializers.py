from rest_framework import serializers
from info.models import *

class NotificationSerializer(serializers.ModelSerializer):
	user_from = serializers.CharField(source="user_from.username")
	user_to = serializers.CharField(source="user_to.username")

	class Meta:
		model = Notification
		fields = ("user_from","user_to","text","notif_type","creation_time",)