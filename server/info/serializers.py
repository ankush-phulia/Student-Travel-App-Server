from rest_framework import serializers
from info.models import *
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ('id', 'username','first_name','last_name','email')

class NotificationSerializer(serializers.ModelSerializer):
	user_from = UserSerializer()
	user_to = UserSerializer()

	class Meta:
		model = Notification
		fields = ("user_from","user_to","title","description","notif_type","creation_time",)

	def create(self,validated_data):
		# print(">>>>>>>>>>",validated_data.pop('user_to'))
		user_to = User.objects.get(username=validated_data.pop('user_to')["username"])
		user_from = User.objects.get(username=validated_data.pop('user_from')["username"])
		return Notification.objects.create(user_to=user_to,user_from=user_from,**validated_data)

class JourneyPointSerializer(serializers.ModelSerializer):
	class Meta:
		model = JourneyPoint
		fields = ("location_name","latitude","longitude",)


class UserInfoSerializer(serializers.ModelSerializer):
	user = UserSerializer()
	class Meta:
		model = UserInfo
		fields = ('user','sex','facebook_link')

class JourneySerializer(serializers.ModelSerializer):
	checkpoints = JourneyPointSerializer(many=True)
	participants = UserSerializer(many=True)
	class Meta:
		model = Journey
		fields = ("checkpoints","participants","start_time","source","destination","journey_id")