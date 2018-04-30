from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
# from mezzanine.core.fields import FileField
from django.db.models.signals import post_save
from django.db.models.signals import post_save
from dateutil import parser
import datetime
# Create your models here.
NOTIFICATION_TYPES = [(x,x) for x in ["Logistics Related", "Trip Related", "Journey Related"]]
SEX_TYPES = [(x,x) for x in ["Male","Female","Other"]]
LOCATION_TYPES = [(x,x) for x in ["Journey Point","Trip Point"]]
TRANSPORT_TYPES = [(x,x) for x in ["Bus","AC1 Train","AC2 Train"]]
# class UserProfile(models.Model):
# 	user = models.OneToOneField(User, related_name='user')
# 	# photo = FileField(verbose_name=_("Profile Picture"),
# 	# 				  upload_to=upload_to("main.UserProfile.photo", "profiles"),
# 	# 				  format="Image", max_length=255, null=True, blank=True)
# 	website = models.URLField(default='', blank=True)
# 	bio = models.TextField(default='', blank=True)
# 	phone = models.CharField(max_length=20, blank=True, default='')
# 	city = models.CharField(max_length=100, default='', blank=True)
# 	country = models.CharField(max_length=100, default='', blank=True)
# 	organization = models.CharField(max_length=100, default='', blank=True)

	# def create_profile(sender, **kwargs):
	# 	user = kwargs["instance"]
	# 	if kwargs["created"]:
	# 		user_profile = UserProfile(user=user)
	# 		user_profile.save()
	# post_save.connect(create_profile, sender=User)

# class MyDateTimeField(models.DateTimeField):

# 	def get_prep_value(self, value):
# 		return datetime.datetime.strptime(value.strftime("yyyy-MM-dd HH:mm"),"yyyy-MM-dd HH:mm")

class UserInfo(models.Model):
	user = models.ForeignKey(User,on_delete=models.CASCADE)
	sex = models.CharField(choices=SEX_TYPES,max_length=50)
	facebook_link = models.CharField(max_length=200)
	bio = models.TextField(default='', blank=True)
	phone = models.CharField(max_length=20, blank=True, default='')
	def __str__(self):
		return self.user.username

class Notification(models.Model):
	user_from = models.ForeignKey(User, related_name="user_from", on_delete=models.CASCADE,null=True)
	user_to = models.ForeignKey(User, related_name="user_to", on_delete=models.CASCADE)
	title = models.TextField()
	description = models.TextField()
	notif_type = models.CharField(choices=NOTIFICATION_TYPES, default="Logistics Related", max_length=100)
	creation_time = models.DateTimeField()
	resolved = models.CharField(default="No",max_length=50)
	class Meta:
		ordering = ("creation_time",)
	def __str__(self):
		return self.user_from.username+"->"+self.user_to.username+">>"+str(self.creation_time)

class LocationPoint(models.Model):
	user = models.ForeignKey(User)
	location_name = models.CharField(max_length=100)
	latitude = models.CharField(max_length=50)
	longitude = models.CharField(max_length=50)
	location_type = models.CharField(choices=LOCATION_TYPES,default="Journey Point",max_length=50)
	rating = models.CharField(max_length=10,default="2.5")
	def __str__(self):
		return self.location_name



class Journey(models.Model):
	journey_id = models.CharField(max_length=50)
	start_time = models.DateTimeField()
	source  = models.CharField(max_length=100)
	destination = models.CharField(max_length=100)
	cotravel_number = models.CharField(max_length=10,default="1")
	participants = models.ManyToManyField(User)
	posted = models.BooleanField(default=False)
	closed = models.BooleanField(default=False)

	def __str__(self):
		return self.journey_id

class JourneyPoint(models.Model):
	location = models.ForeignKey(LocationPoint)
	transport = models.CharField(choices=TRANSPORT_TYPES, default="BUS", max_length=100)
	point_id = models.CharField(max_length=50)
	journey = models.ForeignKey(Journey,related_name="checkpoints")
	def __str__(self):
		return self.location.location_name

