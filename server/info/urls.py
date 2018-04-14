from django.conf.urls import url
from info import views

urlpatterns = [
    url(r'^notifications/$', views.notification_list),
    url(r'^notifications/(?P<username>[0-9a-zA-Z_@.-]+)/$', views.user_notifications),
]