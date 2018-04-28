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

	class Meta:
		template_name = "django_tables2/bootstrap.html"

@login_required
def Dashboard(request):
	user = request.user
	userinfo = UserInfo.objects.get(user=user)
	data = {"email":user.email,"first_name":user.first_name,"last_name":user.last_name,"gender":userinfo.sex,
			"bio":userinfo.bio,"facebook_link":userinfo.facebook_link}
	print("Data is ")
	print(data)
	table = UserInfoTable(data)
	RequestConfig(request).configure(table)
	return render(request, "info/dashboard.html",{"table":table})


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

	gender = forms.ChoiceField(choices=((None, ''), ('F', 'Female'), ('M', 'Male'), ('O', 'Other')))
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

