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
import datetime
from dateutil import parser
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

# Link for the dashboard html
# https://bootsnipp.com/snippets/featured/people-card-with-tabs

def match_journeys(jrny):
	return [[x,False] for x in Journey.objects.all()]

class UserInformation(APIView):
	permission_classes = (permissions.IsAuthenticated,)

	def get(self,request,format=None):
		user_object = UserInfo.objects.filter(user=request.user)
		serializer = UserInfoSerializer(user_object, many=True)
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

class LoginForm(forms.Form):
	email = forms.EmailField()
	password = forms.CharField(widget=forms.PasswordInput)
	keep_logged = forms.BooleanField(required=False, label="Keep me logged in")

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
	data["notifs"] = Notification.objects.filter(user_to=user)
	print("Data is ")
	pprint(data)
	table = UserInfoTable(data)
	RequestConfig(request).configure(table)
	return render(request, "info/dashboard.html",data)


class UserProfileForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ['first_name', 'last_name', 'email']

class ModifyInfoForm(forms.Form):
	email = forms.EmailField(label="Email Address",required=True)
	password = forms.CharField(widget=forms.PasswordInput,required=True)
	password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm password",required=True)
	first_name = forms.CharField(required=False,initial="")
	last_name = forms.CharField(required=False,initial="")
	bio = forms.CharField( widget=forms.Textarea, required=False,initial="")
	facebook_link = forms.CharField(required=False,initial="")

	gender = forms.ChoiceField(choices=((None, ''), ('F', 'Female'), ('M', 'Male'), ('O', 'Other')))

	layout = Layout(Fieldset("Modify your details here.", 'email',
					Row('password', 'password_confirm'),
					Fieldset('Pesonal details',
							 Row('first_name', 'last_name'),
							 'bio','facebook_link','gender')))

@login_required
def edit_user(request):
	user = request.user
	userinfo = UserInfo.objects.get(user=user)
	if(request.method=="GET"):
		form = ModifyInfoForm(initial={"email":user.email,"password":user.password,
			"first_name":user.first_name,"last_name":user.last_name,"gender":userinfo.sex,
			"bio":userinfo.bio,"facebook_link":userinfo.facebook_link})
		return render(request, "info/account_update.html",{"form":form})
		error = ""
	elif(request.method=="POST"):
		form = RegistrationForm(request.POST)
		if form.is_valid():

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
			# user = User.objects.create(username=username,email=email,password=password,first_name=first_name,last_name=last_name)
			# UserInfo.objects.create(user=user,sex=gender,bio=bio,facebook_link=facebook_link)
			return redirect("/dashboard/")
		else:
			error = "The form is not valid. Some of the required fields not entered."
			return render(request,'info/register.html', locals())


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

		user = Notification.objects.create(user_from=request.user,user_to=User.objects.get(username=user_to),notif_type=notif_type,title=title,description=description,creation_time=datetime.datetime.now())
		return redirect("/user_notifications/")
	else:
		error = "The form is not valid. Some of the required fields not entered."
		return render(request,'info/notifications.html', locals())
	return redirect("/user_notifications/")




class LocationForm(forms.Form):
	location_name = forms.CharField(required=True)
	location_type = forms.ChoiceField(choices=((None, ''),('Trip Point', 'Trip Point'), ('Journey Point', 'Journey Point')))
	layout = Layout(Fieldset("Provide the location information here",'location_name', 'location_type'))

@login_required
def user_locations(request):
	locs = LocationPoint.objects.filter(user=request.user)
	form = LocationForm()
	return render(request,'info/locations.html', {"loc_form":form,"locs":locs})

@login_required
def location_create_handler(request):
	form = LocationForm(request.POST)
	pprint(form)
	error = ""
	if form.is_valid():
		location_name = form.cleaned_data["location_name"]
		location_type = form.cleaned_data["location_type"]
		LocationPoint.objects.create(user=request.user,location_name=location_name,location_type=location_type)
	else:
		error = "The form is not valid. Some of the required fields not entered."
		return render(request,'info/locations.html', locals())
	return redirect("/user_locations/")

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
	display1 = len(checkpoints)!=0
	display2 = len(lis)!=0

	return render(request,'info/journeys.html', {"jform1":jform1,"jform2":jform2,"jmform":jmform,"display1":display1,"display2":display2,"lis":lis,"checkpoints":checkpoints})

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
		matching_jlist = match_journeys(jrny)
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
			notif_type="Journey Related",creation_time=datetime.datetime.now())
	matching_jlist[index][1] = True
	return redirect("/user_journeys/")
