from info.models import *

from django.utils import timezone
class SetLastVisitMiddleware(object):
	def process_response(self, request, response):
		if request.user.is_authenticated():
			# Update last visit time after request finished processing.
			UserInfo.objects.filter(user=request.user).update(last_visit=timezone.now())
		return response
