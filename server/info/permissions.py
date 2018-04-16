from rest_framework import permissions


class IsTo(permissions.BasePermission):
	def has_object_permission(self, request, view, obj):
		# print(obj.user_to)
		# print(request.user)
		return obj.user_to == request.user
