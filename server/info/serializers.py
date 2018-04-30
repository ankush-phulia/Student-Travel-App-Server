from rest_framework import serializers
from info.models import *
from django.contrib.auth.models import User
from dateutil import parser
import datetime

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ('id', 'username','first_name','last_name','email')

class NotificationSerializer(serializers.ModelSerializer):
	user_from = UserSerializer()
	user_to = UserSerializer()
	creation_time = serializers.SerializerMethodField()

	def get_creation_time(self, obj):
		return obj.creation_time.replace(second=0, microsecond=0)
		# return datetime.datetime.strptime(obj.creation_time.strftime("yyyy-MM-dd HH:mm"),"yyyy-MM-dd HH:mm")

	class Meta:
		model = Notification
		fields = ("user_from","user_to","title","description","notif_type","creation_time",)

	def create(self,validated_data):
		# print(">>>>>>>>>>",validated_data.pop('user_to'))
		user_to = User.objects.get(username=validated_data.pop('user_to')["username"])
		user_from = User.objects.get(username=validated_data.pop('user_from')["username"])
		return Notification.objects.create(user_to=user_to,user_from=user_from,**validated_data)

class LocationPointSerializer(serializers.ModelSerializer):
	class Meta:
		model = LocationPoint
		fields = ("location_name","latitude","longitude","location_type","rating")

class JourneyPointSerializer(serializers.ModelSerializer):
	location = LocationPointSerializer()
	class Meta:
		model = JourneyPoint
		fields = ("location","transport","point_id",)


class UserInfoSerializer(serializers.ModelSerializer):
	user = UserSerializer()
	class Meta:
		model = UserInfo
		fields = ('user','sex','facebook_link')

class JourneySerializer(serializers.ModelSerializer):
	checkpoints = JourneyPointSerializer(read_only=True,many=True)
	participants = UserSerializer(many=True)
	start_time = serializers.SerializerMethodField()

	def get_start_time(self, obj):
		return obj.start_time.replace(second=0, microsecond=0)
	class Meta:
		model = Journey
		fields = ("checkpoints","participants","start_time","source","destination","journey_id")

	def create(self, validated_data):
		print("came here /// 999999999999")
		# participants = validated_data.pop('profile')
		# user = User.objects.create(**validated_data)
		# Profile.objects.create(user=user, **profile_data)
		# return user
		user = self.context['request'].user
		journey_name = validated_data.pop('journey_id')
		journey_date = validated_data.pop("start_time")
		# cotravel_number = validated_data.pop("cotravel_number")
		checkpoints = validated_data.pop("checkpoints")
		jrny = Journey(journey_id=journey_name,start_time=parser.parse(journey_date),
			source=checkpoints[0]["location"]["location_name"],destination=checkpoints[-1]["location"]["location_name"])
			# cotravel_number=cotravel_number)
		jrny.save()
		jrny.participants.add(user)

		for i,x in enumerate(checkpoints):
			loc = LocationPoint.objects.get(location_name=x["location"]["location_name"],user=user)
			JourneyPoint.objects.create(location=loc,transport=x["means"],point_id = i,journey=jrny)
		return jrny
