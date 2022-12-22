from django.contrib import admin
from .models import Room, Topic, Message
#Allows you to display info on admin panel

admin.site.register(Room)
admin.site.register(Topic)
admin.site.register(Message)


