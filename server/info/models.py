from django.db import models
from django.contrib.auth.models import User

# Create your models here.
NOTIFICATION_TYPES = [(x,x) for x in ["Logistics Related", "Trip Related", "Journey Related"]]
SEX_TYPES = [(x,x) for x in ["Male","Female","Other"]]

class UserInfo(models.Model):
	user = models.ForeignKey(User,on_delete=models.CASCADE)
	sex = models.CharField(choices=SEX_TYPES,max_length=50)
	facebook_link = models.CharField(max_length=200)

	def __str__(self):
		return self.user.username

class Notification(models.Model):
	user_from = models.ForeignKey(User, related_name="user_from", on_delete=models.CASCADE,null=True)
	user_to = models.ForeignKey(User, related_name="user_to", on_delete=models.CASCADE)
	title = models.TextField()
	description = models.TextField()
	notif_type = models.CharField(choices=NOTIFICATION_TYPES, default="Logistics Related", max_length=100)
	creation_time = models.DateTimeField()
	class Meta:
		ordering = ("creation_time",)
	def __str__(self):
		return self.user_from.username+"->"+self.user_to.username+">>"+str(self.creation_time)

class JourneyPoint(models.Model):
	location_name = models.CharField(max_length=100)
	latitude = models.CharField(max_length=50)
	longitude = models.CharField(max_length=50)
	def __str__(self):
		return self.location_name

class Journey(models.Model):
	journey_id = models.CharField(max_length=50)
	start_time = models.DateTimeField()
	source  = models.CharField(max_length=100)
	destination = models.CharField(max_length=100)
	checkpoints = models.ManyToManyField(JourneyPoint)
	participants = models.ManyToManyField(User)
	def __str__(self):
		return self.journey_id


