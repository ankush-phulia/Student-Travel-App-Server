from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django import forms
from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
# from .forms import UserForm
from django.forms.models import inlineformset_factory
from django.core.exceptions import PermissionDenied
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

from material import *
from django_tables2 import RequestConfig
import django_tables2 as tables
from pprint import *
import datetime,json
from dateutil import parser
from geoposition.fields import GeopositionField
from base64 import b64encode
import base64

from django.utils import timezone
import pytz

utc=pytz.UTC
# from mapwidgets.widgets import GooglePointFieldWidget, GoogleStaticOverlayMapWidget
##Custom permisionn won't work if we don't use GenericAPIView based classes. See the django rest_framework
## permissions documentation
# See this for an overview tutorial
# https://www.andreagrandi.it/2016/10/01/creating-a-production-ready-api-with-python-and-django-rest-framework-part-2/
#1) To get token for the user:
# http --json POST http://127.0.0.1:8000/api-token-auth/ username="deepak" password="deepaksaini"
# curl -X POST http://127.0.0.1:8000/api-token-auth/ -d "username=deepak&password=deepaksaini"
#2) username, pass based authentication using BasicAuthentication:
# http -a deepak:deepaksaini GET http://127.0.0.1:8000/journeys/
#3) token based authentication:
# http GET http://127.0.0.1:8000/notifications/ "Authorization: Token 2c2670e251bfcacd19b09dff689447a513edb7db"
# But enabling BasicAuthentication along with token authentication has issues in logout from the REST api web interface. So diable it and use only token
# authentication


# echo '{"checkpoints":[{"location":{"location_name":"IITDelhi","latitude":"","longitude":"","location_type":"JourneyPoint","rating":"2.5"},"transport":"Bus","point_id":"0"}],"participants":[{"id":2,"username":"ankush@gmail.com","first_name":"","last_name":"","email":""}],"start_time":"2018-05-03T20:00:48Z","source":"IITDelhi","destination":"SaraiRohillla","journey_id":"Winter_Vacations"},{"checkpoints":[],"participants":[],"start_time":"2018-05-03T20:00:48Z","source":"IITDelhi","destination":"IITDelhi","journey_id":"Winter_Vacations"}' | http --json POST http://127.0.0.1:8000/single_journey/2/


# Link for the dashboard html
# https://bootsnipp.com/snippets/featured/people-card-with-tabs

def match_journeys(user,jrny):
	return [[x,False] for x in Journey.objects.filter(posted=True,closed=False) if user not in x.participants.all()]


class UserInformation(APIView):
	permission_classes = (permissions.IsAuthenticated,)

	def get(self,request,format=None):
		user_object = UserInfo.objects.filter(user=request.user)
		serializer = UserInfoSerializer(user_object, many=True)
		return Response(serializer.data)

class UserInformationUpdate(APIView):
	permission_classes = (permissions.IsAuthenticated,)

	def post(self,request,format=None):
		validated_data = request.data
		try:
			user = request.user
			ui = UserInfo.objects.get(user=user)

			first_name = validated_data.get("first_name",user.first_name)
			last_name = validated_data.get("last_name",user.last_name)
			email = validated_data.get("email",user.email)

			sex = validated_data.get("gender",ui.sex)
			facebook_link = validated_data.get("facebook_link",ui.facebook_link)
			bio = validated_data.get("bio",ui.bio)
			phone = validated_data.get("phone",ui.phone)

			user.first_name  = first_name
			user.last_name  = last_name
			user.email  = email

			ui.sex = sex
			ui.facebook_link = facebook_link
			ui.bio = bio
			ui.phone = phone
			user.save()
			ui.save()
			return Response(validated_data, status=status.HTTP_201_CREATED)
		except:
			return Response({}, status=status.HTTP_400_BAD_REQUEST)

class JourneyPointsList(APIView):
	permission_classes = (permissions.IsAuthenticated,)

	def get(self,request,format=None):
		locs = LocationPoint.objects.filter(user=request.user,location_type="Journey Point")
		serializer = LocationPointSerializer(locs, many=True)
		return Response(serializer.data)

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

class JourneySingle(APIView):
	permission_classes = (permissions.IsAuthenticated,)
	def get_journey(self,journey_id,user):
		try:
			return Journey.objects.filter(journey_id=journey_id)
		except Journey.DoesNotExist:
			raise Http404
	def get(self,request,journey_id,format=None):
		print("journey_id",journey_id)
		jrny = self.get_journey(journey_id,request.user)
		serializer = JourneySerializer(jrny,many=True)
		return Response(serializer.data)

	def post(self,request,journey_id,format=None):
		print("came here")
		validated_data = request.data
		pprint(validated_data)
		print(request.user)
		try:
			user = request.user
			try:
				journey_date = parser.parse(validated_data.get("start_time"))
			except:
				journey_date = datetime.datetime.now()+datetime.timedelta(hours=5.5)
			print(journey_date)
			cotravel_number = validated_data.get("cotravel_number",2)
			checkpoints = json.loads(validated_data.get("checkpoints"))
			source = validated_data.get("source","")
			destination = validated_data.get("source","")
			print(checkpoints)
			jrny = Journey(journey_id=journey_id,start_time=journey_date,
				source=checkpoints[0]["location"]["location_name"],destination=checkpoints[-1]["location"]["location_name"],
				cotravel_number=cotravel_number)

			jrny.save()
			jrny.participants.add(user)
			for i,x in enumerate(checkpoints):
				loc = LocationPoint.objects.get(location_name=x["location"]["location_name"],user=user)
				JourneyPoint.objects.create(location=loc,transport=x["transport"],point_id = x["point_id"],journey=jrny)
			return Response(validated_data, status=status.HTTP_201_CREATED)
		except:
			return Response({}, status=status.HTTP_400_BAD_REQUEST)

class UserNotifications(APIView):
	permission_classes = (permissions.IsAuthenticated,)
	def get_user_notifications(self,username):
		try:
			return Notification.objects.filter(user_to__username = username)
		except Notification.DoesNotExist:
			raise Http404
	def get(self,request,username,format=None):
		notifs = self.get_user_notifications(username)
		serializer = NotificationSerializer(notifs,many=True)
		return Response(serializer.data)

	def delete(self,request,username,format=None):
		notifs = self.get_user_notifications(username)
		notifs.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)

class LoginForm(forms.Form):
	email = forms.EmailField()
	password = forms.CharField(widget=forms.PasswordInput)
	keep_logged = forms.BooleanField(required=False, label="Keep me logged in")


class MakeRequest(APIView):
	permission_classes = (permissions.IsAuthenticated,)

	def post(self,request,format=None):
		validated_data = request.data
		try:
			user = request.user
			req_users = validated_data.get("users",[])
			title = validated_data.get("title","")
			description = validated_data.get("description","")
			notif_type = validated_data.get("notif_type","Logistics Related")
			for ut in req_users:
				Notification.objects.create(user_to=ut,user_from=user,title=title,description=description,
					notif_type=notif_type,creation_time=datetime.datetime.now()+datetime.timedelta(hours=5.5))
			return Response(validated_data, status=status.HTTP_201_CREATED)
		except:
			return Response({}, status=status.HTTP_400_BAD_REQUEST)

class AcceptRequest(APIView):
	permission_classes = (permissions.IsAuthenticated,)

	def post(self,request,format=None):
		validated_data = request.data
		try:
			id = validated_data.get("id")
			username = request.user.username
			notif = Notification.objects.get(id=id)
			notif.resolved = username+" accepted the request"
			notif.save()
			return Response(validated_data, status=status.HTTP_201_CREATED)
		except:
			return Response({}, status=status.HTTP_400_BAD_REQUEST)

class RejectRequest(APIView):
	permission_classes = (permissions.IsAuthenticated,)

	def post(self,request,format=None):
		validated_data = request.data
		try:
			id = validated_data.get("id")
			username = request.user.username
			notif = Notification.objects.get(id=id)
			notif.resolved = username+" rejected the request"
			notif.save()
			return Response(validated_data, status=status.HTTP_201_CREATED)
		except:
			return Response({}, status=status.HTTP_400_BAD_REQUEST)


class JourneySearch(APIView):
	permission_classes = (permissions.IsAuthenticated,)

	def post(self,request,format=None):
		validated_data = request.data
		pprint(validated_data)
		try:
			journey_id = validated_data.get("journey_id")
			jrny = Journey.objects.get(journey_id=journey_id)
			matches = match_journeys(user,jrny)
			serializer = JourneySerializer(matches,many=True)
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		except:
			return Response({}, status=status.HTTP_400_BAD_REQUEST)

class JourneyPost(APIView):
	permission_classes = (permissions.IsAuthenticated,)

	def post(self,request,format=None):
		validated_data = request.data
		pprint(validated_data)
		try:
			journey_id = validated_data.get("journey_id")
			jrny = Journey.objects.get(journey_id=journey_id)
			jrny.posted=True
			jrny.save()
			return Response(validated_data, status=status.HTTP_201_CREATED)
		except:
			return Response({}, status=status.HTTP_400_BAD_REQUEST)

class JourneyClose(APIView):
	permission_classes = (permissions.IsAuthenticated,)

	def post(self,request,format=None):
		validated_data = request.data
		pprint(validated_data)
		try:
			journey_id = validated_data.get("journey_id")
			jrny = Journey.objects.get(journey_id=journey_id)
			jrny.closed=True
			jrny.save()
			return Response(validated_data, status=status.HTTP_201_CREATED)
		except:
			return Response({}, status=status.HTTP_400_BAD_REQUEST)

###########################################################################################

def logout(request):
	ui = UserInfo.objects.get(user=request.user)
	ui.last_visit = datetime.datetime.now()+datetime.timedelta(hours=5.5)
	print(ui.last_visit)
	ui.save()
	return redirect("/accounts/internal_logout/")
@login_required
def home(request):
	return redirect("dashboard")

class UserInfoTable(tables.Table):
	Username = tables.Column()
	Email = tables.Column()
	class Meta:
		template_name = "django_tables2/bootstrap.html"

@login_required
def Dashboard(request):
	def take(x):
		if(x==""):
			return "..."
		else:
			return x
	user = request.user
	userinfo = UserInfo.objects.get(user=user)
	data = {"username":"","email":"","first_name":"","last_name":"","gender":"",
			"bio":"","facebook_link":""}
	data["username"] = take(user.username)
	data["email"] = take(user.email)
	data["first_name"] = take(user.first_name)
	data["last_name"] = take(user.last_name)
	data["gender"] = take(userinfo.sex)
	data["bio"] = take(userinfo.bio)
	data["facebook_link"] = take(userinfo.facebook_link)
	data["rating"] = userinfo.rating
	print(userinfo.last_visit)
	last_lg = userinfo.last_visit
	data["notifs"] = Notification.objects.filter(user_to=user,creation_time__gte=last_lg)
	print("Data is ")
	print(last_lg)
	pprint(data)
	# user_info = UserInfo.objects.get(user=user)
	# image = b64encode(user_info.photo)
	data["image"] = userinfo.photo
	# print(user_info.photo.url)
	# table = UserInfoTable(data)
	# RequestConfig(request).configure(table)
	return render(request, "info/dashboard.html",data)


class UserProfileForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ['first_name', 'last_name', 'email']

class ModifyInfoForm(forms.Form):
	email = forms.EmailField(required=False,label="Email Address")
	# password = forms.CharField(widget=forms.PasswordInput,required=False)
	# password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm password",required=False)
	first_name = forms.CharField(required=False,initial="")
	last_name = forms.CharField(required=False,initial="")
	bio = forms.CharField( widget=forms.Textarea, required=False,initial="")
	facebook_link = forms.CharField(required=False,initial="")

	gender = forms.ChoiceField(required=False,choices=((None, ''), ('Female', 'Female'), ('Male', 'Male'), ('Other', 'Other')))
	img = forms.ImageField(required=False,)
	# layout = Layout(Fieldset("Modify your details here.", 'email',
	# 				Row('password', 'password_confirm'),
	# 				Fieldset('Pesonal details',
	# 						 Row('first_name', 'last_name'),
	# 						 'bio','facebook_link','gender','img')))

@login_required
def edit_user(request):
	user = request.user
	userinfo = UserInfo.objects.get(user=user)
	if(request.method=="GET"):
		form = ModifyInfoForm(initial={"email":user.email,"password":user.password,
			"first_name":user.first_name,"last_name":user.last_name,"gender":userinfo.sex,
			"bio":userinfo.bio,"facebook_link":userinfo.facebook_link,})
		return render(request, "info/account_update.html",{"form":form,"user":user,"userinfo":userinfo})
		error = ""
	elif(request.method=="POST"):
		print(request.FILES)
		form = ModifyInfoForm(request.POST)
		if form.is_valid():

			email = form.cleaned_data["email"]
			# password = form.cleaned_data["password"]
			# password_confirm = form.cleaned_data["password_confirm"]
			# if(password!=password_confirm):
			# 	error= "Sorry. The passwords don't match!"
			# 	return render(request,'info/account_update.html', locals())

			first_name = form.cleaned_data["first_name"]
			last_name = form.cleaned_data["last_name"]
			gender = form.cleaned_data["gender"]

			bio = form.cleaned_data["bio"]
			facebook_link = form.cleaned_data["facebook_link"]
			try:
				img = request.FILES["img"]
				b64_img = base64.b64encode(img.file.read())
				userinfo.photo = b64_img
			except:
				img  = userinfo.photo
			print(bio)
			print(img)
			# if(img):
			user.first_name = first_name
			user.last_name = last_name
			# user.password = password
			userinfo.sex = gender
			userinfo.bio = bio
			userinfo.facebook_link = facebook_link

			userinfo.save()
			user.save()
			# user = User.objects.create(username=username,email=email,password=password,first_name=first_name,last_name=last_name)
			# UserInfo.objects.create(user=user,sex=gender,bio=bio,facebook_link=facebook_link)
			return redirect("/dashboard/")
		else:
			error = "The form is not valid. Some of the required fields not entered."
			return render(request,'info/account_update.html', locals())


class RegistrationForm(forms.Form):
	username = forms.CharField(required=True)
	email = forms.EmailField(label="Email Address",required=True)
	password = forms.CharField(widget=forms.PasswordInput,required=True)
	password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm password",required=True)
	first_name = forms.CharField(required=False,initial="")
	last_name = forms.CharField(required=False,initial="")
	bio = forms.CharField( widget=forms.Textarea, required=False,initial="")
	facebook_link = forms.CharField(required=False,initial="")

	gender = forms.ChoiceField(choices=((None, ''), ('Female', 'Female'), ('Male', 'Male'), ('Other', 'Other')))
	agree_toc = forms.BooleanField(required=True, label='I agree with the Terms and Conditions')

	layout = Layout(Fieldset("Provide your details here",'username', 'email',
					Row('password', 'password_confirm'),
					Fieldset('Pesonal details',
							 Row('first_name', 'last_name'),
							 'bio','facebook_link','gender', 'agree_toc')))


def user_registration(request):
	print("came into func")
	if(request.method=="GET"):
		form = RegistrationForm()
		return render(request, "info/register.html",{"form":form})
		error = ""
	elif(request.method=="POST"):
		form = RegistrationForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data["username"]
			if(User.objects.filter(username=username).exists()):
				error= "Sorry. This username is already taken!"
				return render(request,'info/register.html', locals())
			email = form.cleaned_data["email"]
			password = form.cleaned_data["password"]
			password_confirm = form.cleaned_data["password_confirm"]
			if(password!=password_confirm):
				error= "Sorry. The passwords don't match!"
				return render(request,'info/register.html', locals())

			first_name = form.cleaned_data["first_name"]
			last_name = form.cleaned_data["first_name"]
			gender = form.cleaned_data["first_name"]
			agree_toc = form.cleaned_data["agree_toc"]
			bio = form.cleaned_data["bio"]
			facebook_link = form.cleaned_data["facebook_link"]
			user = User.objects.create(username=username,email=email,password=password,first_name=first_name,last_name=last_name)
			UserInfo.objects.create(user=user,sex=gender,bio=bio,facebook_link=facebook_link)
			return redirect("/accounts/login/")
		else:
			error = "The form is not valid. Some of the required fields not entered."
			return render(request,'info/register.html', locals())

class NotificationForm(forms.Form):
	to_user = forms.CharField(required=True)
	notification_type = forms.ChoiceField(choices=((None, ''), ('Logistics Related', 'Logistics Related'), ('Trip Related', 'Trip Related'), ('Journey Related', 'Journey Related')))
	title = forms.CharField(required=True)
	description = forms.CharField( widget=forms.Textarea, required=False,initial="")
	layout = Layout(Fieldset("Provide the notification here",'to_user', 'notification_type',"title","description"))

@login_required
def user_notifications(request):
	notifs = Notification.objects.filter(user_to=request.user)
	notifs_sent = Notification.objects.filter(user_from=request.user)
	form = NotificationForm()
	return render(request,'info/notifications.html', {"notifs":notifs,"notifs_sent":notifs_sent,"form":form})

@login_required
def notification_create_handler(request):
	form = NotificationForm(request.POST)
	pprint(form)
	error = ""
	if form.is_valid():
		user_to = form.cleaned_data["to_user"]
		if(not(User.objects.filter(username=user_to).exists())):
			# print("99999999999999999999999999",user_to)
			error= "Sorry. The user to whom you are trying to send, doesn't exist!"
			return render(request,'info/notifications.html', locals())
		notif_type = form.cleaned_data["notification_type"]
		title = form.cleaned_data["title"]
		description = form.cleaned_data["description"]

		user = Notification.objects.create(user_from=request.user,user_to=User.objects.get(username=user_to),
			notif_type=notif_type,title=title,description=description,creation_time=datetime.datetime.now()+datetime.timedelta(hours=5.5))
		return redirect("/user_notifications/")
	else:
		error = "The form is not valid. Some of the required fields not entered."
		return render(request,'info/notifications.html', locals())
	return redirect("/user_notifications/")




class LocationForm(forms.Form):
	# location_name = forms.CharField(required=True)
	# location_name = forms.PointField(widget=GooglePointFieldWidget)
	location_type = forms.ChoiceField(choices=((None, ''),('Trip Point', 'Trip Point'), ('Journey Point', 'Journey Point')))
	# layout = Layout(Fieldset('location_type'))

class LocationForm2(forms.Form):
	location_name = GeopositionField()

@login_required
def user_locations(request):
	locs = LocationPoint.objects.filter(user=request.user)
	locations = [x.location_name for x in locs]
	form = LocationForm()
	form2 = LocationForm2()
	return render(request,'info/locations.html', {"loc_form":form,"locs":locs,"locations":locations,"loc_form2":form2})

@login_required
def location_create_handler(request):
	pprint(request.POST)
	pprint(request.FILES)
	form = LocationForm(request.POST)
	pprint(form)
	error = ""
	if form.is_valid():
		location_name = request.POST["location_name"]
		location_type = form.cleaned_data["location_type"]
		LocationPoint.objects.create(user=request.user,location_name=location_name,location_type=location_type)
	else:
		error = "The form is not valid. Some of the required fields not entered."
		return render(request,'info/locations.html', locals())
	return redirect("/user_locations/")

##########################################################################################################################################
class JourneyCreationForm1(forms.Form):
	travel_type = forms.ChoiceField(choices=(('Bus', 'Bus'), ('AC1 Train', 'AC1 Train'), ('AC2 Train', 'AC2 Train')),required=True)
	def __init__(self, user, *args, **kwargs):
		super(JourneyCreationForm1, self).__init__(*args, **kwargs)
		jloc = LocationPoint.objects.filter(user=user,location_type="Journey Point")
		self.fields["location_1"] = forms.ChoiceField(choices=((x.location_name,x.location_name) for x in jloc))
		self.fields["location_2"] = forms.ChoiceField(choices=((x.location_name,x.location_name) for x in jloc))
		self.layout = Layout(Fieldset("Provide the journey checkpoints here",Row("location_1","travel_type","location_2")))

class JourneyCreationForm2(forms.Form):
	journey_name = forms.CharField(required=True)
	travel_date = forms.DateTimeField(required=True)
	cotravel_number = forms.IntegerField()
	layout = Layout(Fieldset("Provide the journey information here","journey_name",Row("travel_date","cotravel_number")))

class JourneyModifyForm(forms.Form):
	def __init__(self, user, *args, **kwargs):
		super(JourneyModifyForm, self).__init__(*args, **kwargs)
		jour = Journey.objects.filter(participants__in=[user],posted=False)
		self.fields["journey_name"] = forms.ChoiceField(choices=((x,x.journey_id) for x in jour))
		self.layout = Layout(Fieldset("Provide the journey here and select one of the options","journey_name"))

# display1 = False
display2 = False
checkpoints = []
matching_jlist = []

@login_required
def user_journeys(request):
	# global display1
	# global display2
	global checkpoints
	global matching_jlist
	jform1 = JourneyCreationForm1(request.user)
	jform2 = JourneyCreationForm2()
	jmform = JourneyModifyForm(request.user)
	lis = []
	for o,dis in matching_jlist:
		d = {}
		d["journey_name"] = o.journey_id
		d["journey_date"] = o.start_time
		d["journey_participants"] = [x.username for x in o.participants.all()]
		d["disable"] = dis
		lis.append(d)
	req_lis = Notification.objects.filter(user_to=request.user,notif_type="Journey Related",resolved="No")
	display1 = len(checkpoints)!=0
	display2 = len(lis)!=0
	jlist = Journey.objects.filter(participants__in=[request.user])
	for j in jlist:
		# and (datetime.datetime.now()+datetime.timedelta(hours=5.5)-j.start_time.replace(tzinfo=utc)).days>10)
		if(j.start_time<(datetime.datetime.now()+datetime.timedelta(hours=5.5)).replace(tzinfo=utc)):
			if(j.posted):
				j.closed = True
				j.save()
	# cjlist = Journey.objects.filter(participants__in=[request.user],closed=True)
	return render(request,'info/journeys.html', {"jform1":jform1,"jform2":jform2,"jmform":jmform,"display1":display1,"display2":display2,"lis":lis,
		"checkpoints":checkpoints,"req_lis":req_lis,"jlist":jlist})

def journey_creation_handler1(request):
	global checkpoints
	if("add_checkpoint" in request.POST):
		pprint(request.POST)
		# form = JourneyCreationForm1(request.POST)
		# if form.is_valid():
		d = {}
		d["checkpointA"] = request.POST.get("location_1")
		d["checkpointB"] = request.POST.get("location_2")
		d["means"] = request.POST.get("travel_type")
		checkpoints.append(d)
		# else:
		# 	error = "The form is not valid. Some of the required fields not entered."
		# 	return render(request,'info/journeys.html', locals())
	return redirect("/user_journeys/")

def journey_creation_handler2(request):
	global checkpoints
	# form = JourneyCreationForm1(request.POST)
	# if form.is_valid():
	pprint(checkpoints)
	pprint(request.POST)
	journey_name = request.POST.get("journey_name")
	journey_date = request.POST.get("travel_date")
	cotravel_number = request.POST.get("cotravel_number")
	jrny = Journey(journey_id=journey_name,start_time=parser.parse(journey_date),
		source=checkpoints[0]["checkpointA"],destination=checkpoints[-1]["checkpointB"],
		cotravel_number=cotravel_number)
	jrny.save()
	jrny.participants.add(request.user)

	for i,x in enumerate(checkpoints):
		loc = LocationPoint.objects.get(location_name=x["checkpointA"],user=request.user)
		JourneyPoint.objects.create(location=loc,transport=x["means"],point_id = i,journey=jrny)
	checkpoints = []
	return redirect("/user_journeys/")


def journey_modify_handler(request):
	global matching_jlist
	pprint(request.POST)
	jrny = Journey.objects.get(participants__in=[request.user],journey_id=request.POST.get("journey_name"))
	if("search" in request.POST):
		matching_jlist = match_journeys(request.user,jrny)
	elif("post" in request.POST):
		jrny.posted=True
		jrny.save()
		matching_jlist = []
	elif("delete" in request.POST):
		jrny.delete()
		matching_jlist = []
	return redirect("/user_journeys/")

def request_add_handler(request):
	pprint(request.POST)
	global matching_jlist
	n = len(matching_jlist)
	user = request.user
	print(n)
	index = 0
	for i in range(n):
		if("submit"+str(i) in request.POST):
			index = i
	print("index",index)
	jrny = matching_jlist[index][0]
	description = "User "+user.username+" wants to be added to the "+jrny.journey_id+" in which you are a participant."
	title = "Journey Add request"
	for ut in jrny.participants.all():
		Notification.objects.create(user_to=ut,user_from=user,title=title,description=description,
			notif_type="Journey Related",creation_time=datetime.datetime.now()+datetime.timedelta(hours=5.5),
			travel_id=jrny.journey_id)
	matching_jlist[index][1] = True
	return redirect("/user_journeys/")

def request_resolve_handler(request):
	req_lis = Notification.objects.filter(user_to=request.user,notif_type="Journey Related",resolved="No")
	print(request.POST)
	index = 0
	typ = 0
	for i in range(len(req_lis)):
		if("accept"+str(i) in request.POST):
			index = i
			typ = 1
		elif("reject"+str(i) in request.POST):
			index = i
			typ = 0
	print(index,typ)
	req = req_lis[index]
	if(typ==0):
		req.resolved = "Request rejected by "+request.user.username
		# req.creation_time = datetime.datetime.now()+datetime.timedelta(hours=5.5)
		jrny_id = req.travel_id
		print(jrny_id)
		jrny = Journey.objects.get(participants__in=[request.user],journey_id=jrny_id)

		desc = request.user.username+" rejected the request by "+req.user_from.username
		for par in jrny.participants.all():
			Notification.objects.create(user_to=par,user_from=request.user,title="Journey add request rejected",description=desc,
					notif_type="Journey Related",creation_time=datetime.datetime.now()+datetime.timedelta(hours=5.5))
		Notification.objects.create(user_to=req.user_from,user_from=request.user,title="Journey add request rejected",description=desc,
			notif_type="Journey Related",creation_time=datetime.datetime.now()+datetime.timedelta(hours=5.5),
			resolved="Yes")
	if(typ==1):
		req.resolved = "Request accepted by "+request.user.username
		# req.creation_time = datetime.datetime.now()+datetime.timedelta(hours=5.5)
		print(req.description.split())
		jrny_id = req.travel_id
		print(jrny_id)
		jrny = Journey.objects.get(participants__in=[request.user],journey_id=jrny_id)

		jrny.participants.add(req.user_from)
		desc = request.user.username+" accepted the request by "+req.user_from.username
		for par in jrny.participants.all():
			Notification.objects.create(user_to=par,user_from=request.user,title="Journey add request accepted",description=desc,
					notif_type="Journey Related",creation_time=datetime.datetime.now()+datetime.timedelta(hours=5.5),
					resolved="Yes")
	req.save()
	return redirect("/user_journeys/")


##########################################################################################################################################
class TripCreationForm1(forms.Form):
	# travel_type = forms.ChoiceField(choices=(('Bus', 'Bus'), ('AC1 Train', 'AC1 Train'), ('AC2 Train', 'AC2 Train')),required=True)
	def __init__(self, user, *args, **kwargs):
		super(TripCreationForm1, self).__init__(*args, **kwargs)
		tloc = LocationPoint.objects.filter(user=user,location_type="Trip Point")
		self.fields["location"] = forms.ChoiceField(choices=((x.location_name,x.location_name) for x in tloc))
		# self.fields["location_2"] = forms.ChoiceField(choices=((x.location_name,x.location_name) for x in jloc))
		self.layout = Layout(Fieldset("Provide the trip locations here",Row("location")))

class TripCreationForm2(forms.Form):
	trip_name = forms.CharField(required=True)
	travel_date = forms.DateTimeField(required=True)
	cotravel_number = forms.IntegerField()
	source = forms.CharField(required=True)
	duration = forms.CharField(required=False)
	expected_budget = forms.CharField(required=False)
	trip_info = forms.CharField( widget=forms.Textarea, required=False)

	layout = Layout(Fieldset("Provide the trip details here","trip_name","source",Row("travel_date","cotravel_number"),Row("duration","expected_budget"),"trip_info"))

class TripModifyForm(forms.Form):
	def __init__(self, user, *args, **kwargs):
		super(TripModifyForm, self).__init__(*args, **kwargs)
		trips = Trip.objects.filter(participants__in=[user],posted=False)
		self.fields["trip_name"] = forms.ChoiceField(choices=((x,x.trip_id) for x in trips))
		self.layout = Layout(Fieldset("Provide the trip here and select one of the options","trip_name"))

# display1 = False
display2 = False
locations = []
matching_tlist = []

@login_required
def user_trips(request):
	# global display1
	# global display2
	global locations
	global matching_tlist
	tform1 = TripCreationForm1(request.user)
	tform2 = TripCreationForm2()
	tmform = TripModifyForm(request.user)
	lis = []
	for o,dis in matching_tlist:
		d = {}
		d["trip_name"] = o.trip_id
		d["trip_date"] = o.start_time
		d["trip_participants"] = [x.username for x in o.participants.all()]
		d["disable"] = dis
		lis.append(d)
	req_lis = Notification.objects.filter(user_to=request.user,notif_type="Trip Related",resolved="No")
	display1 = len(locations)!=0
	display2 = len(lis)!=0

	return render(request,'info/trips.html', {"tform1":tform1,"tform2":tform2,"tmform":tmform,"display1":display1,"display2":display2,"lis":lis,"locations":locations,"req_lis":req_lis})

def trip_creation_handler1(request):
	global locations
	if("add_checkpoint" in request.POST):
		pprint(request.POST)
		# form = JourneyCreationForm1(request.POST)
		# if form.is_valid():
		d = {}
		d["location"] = request.POST.get("location")
		# d["checkpointB"] = request.POST.get("location_2")
		# d["means"] = request.POST.get("travel_type")
		locations.append(d)
		# else:
		# 	error = "The form is not valid. Some of the required fields not entered."
		# 	return render(request,'info/journeys.html', locals())
	return redirect("/user_trips/")

def trip_creation_handler2(request):
	global locations
	# form = JourneyCreationForm1(request.POST)
	# if form.is_valid():
	pprint(locations)
	pprint(request.POST)
	trip_name = request.POST.get("trip_name")
	trip_date = request.POST.get("travel_date")
	cotravel_number = request.POST.get("cotravel_number")
	source = request.POST.get("source")
	duration = request.POST.get("duration")
	expected_budget = request.POST.get("expected_budget")
	trip_info = request.POST.get("trip_info")

	trp = Trip(trip_id=trip_name,start_time=parser.parse(trip_date),
		source=source,cotravel_number=cotravel_number,duration=duration,expected_budget=expected_budget,trip_info=trip_info)
	trp.save()
	trp.participants.add(request.user)

	for i,x in enumerate(locations):
		loc = LocationPoint.objects.get(location_name=x["location"],user=request.user)
		TripPoint.objects.create(location=loc,trip=trp)
	locations = []
	return redirect("/user_trips/")


def trip_modify_handler(request):
	global matching_tlist
	pprint(request.POST)
	trp = Trip.objects.get(participants__in=[request.user],trip_id=request.POST.get("trip_name"))
	if("search" in request.POST):
		matching_tlist = match_trips(request.user,trp)
	elif("post" in request.POST):
		trp.posted=True
		trp.save()
		matching_tlist = []
	elif("delete" in request.POST):
		trp.delete()
		matching_tlist = []
	return redirect("/user_trips/")

