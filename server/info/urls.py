from django.conf.urls import url, include
from info import views
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken import views as auth_views
from django.contrib.auth import views as user_auth_views

urlpatterns = [
    url(r'^user_info/$', views.UserInformation.as_view()),
    url(r'^notifications/$', views.NotificationList.as_view()),
    url(r'^journeys/$', views.JourneyList.as_view()),
    url(r'^single_journey/(?P<journey_id>[ 0-9a-zA-Z_@.-]+)/$', views.JourneySingle.as_view()),
    url(r'^search_journey/$', views.JourneySearch.as_view()),
    url(r'^post_journey/$', views.JourneyPost.as_view()),
    url(r'^close_journey/$', views.JourneyClose.as_view()),

    url(r'^make_request/$', views.MakeRequest.as_view()),
    url(r'^accept_request/$', views.AcceptRequest.as_view()),
    url(r'^reject_request/$', views.RejectRequest.as_view()),

    # user_info_update/
    # make_request
    # accept_request
    # reject_request

    url(r'^notifications/(?P<username>[0-9a-zA-Z_@.-]+)/$', views.UserNotifications.as_view()),
    url(r'^api-auth/', include('rest_framework.urls')),
    url(r'^api-token-auth/', auth_views.obtain_auth_token),

    url(r'^accounts/login/$', user_auth_views.login, {'template_name': 'info/login.html'}, name='login'),
    url(r'^accounts/logout/$', user_auth_views.logout, name='logout'),
    url(r'^$', views.home, name='home'),
    url(r'^dashboard/$', views.Dashboard, name='dashboard'),
    url(r'^accounts/update/$', views.edit_user, name='account_update'),
    url(r'^accounts/register/$', views.user_registration, name='register'),

    url(r'^user_notifications/$', views.user_notifications, name='user_notifications'),
    url(r'^user_notifications/notification_create_handler/$', views.notification_create_handler, name='notification_create_handler'),

    url(r'^user_locations/$', views.user_locations, name='user_locations'),
    url(r'^user_locations/location_create_handler/$', views.location_create_handler, name='location_create_handler'),

    url(r'^user_journeys/$', views.user_journeys, name='user_journeys'),
    url(r'^user_journeys/journey_create_handler1/$', views.journey_creation_handler1, name='journey_create_handler1'),
    url(r'^user_journeys/journey_create_handler2/$', views.journey_creation_handler2, name='journey_create_handler2'),
    url(r'^user_journeys/journey_modify_handler/$', views.journey_modify_handler, name='journey_modify_handler'),
    url(r'^user_journeys/request_add_handler/$', views.request_add_handler, name='request_add_handler'),
    url(r'^user_journeys/request_resolve_handler/$', views.request_resolve_handler, name='request_resolve_handler'),

]
urlpatterns = format_suffix_patterns(urlpatterns)

# API key AIzaSyAZMN4VVZiDsO9SRKISeV20WD9Z47vUReU
# TODO:
# remove rating from journey point list
# make api to edit user info
# introduce id field in notification model
# TODO display only new notification in dashboard
