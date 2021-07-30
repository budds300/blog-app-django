from django.contrib import admin
from .models import Profile, Blog, Like, Subscribers, Comment, Follow

# Register your models here.
admin.site.register(Profile)
admin.site.register(Blog)
admin.site.register(Like)
admin.site.register(Subscribers)
admin.site.register(Comment)
admin.site.register(Follow)

