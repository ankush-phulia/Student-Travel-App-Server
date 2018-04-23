from django.conf.urls import url, include
from info import views
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken import views as auth_views

urlpatterns = [
    url(r'^notifications/$', views.NotificationList.as_view()),
    url(r'^journeys/$', views.JourneyList.as_view()),
    url(r'^notifications/(?P<username>[0-9a-zA-Z_@.-]+)/$', views.UserNotifications.as_view()),
    url(r'^api-auth/', include('rest_framework.urls')),
    url(r'^api-token-auth/', auth_views.obtain_auth_token),
]
urlpatterns = format_suffix_patterns(urlpatterns)
