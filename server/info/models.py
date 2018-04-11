from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class UserInfo(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    facebook_link = models.CharField(max_length=200)

##TODO : keep color coded notification for logistics, journey, trip
class Notification(models.Model):
    user_from = models.OneToOneField(User, on_delete=models.CASCADE,null=True)
    user_to = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    # type

class Snippet(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=True, default='')
    code = models.TextField()
    linenos = models.BooleanField(default=False)
    language = models.CharField(choices=LANGUAGE_CHOICES, default='python', max_length=100)
    style = models.CharField(choices=STYLE_CHOICES, default='friendly', max_length=100)

    class Meta:
        ordering = ('created',)
