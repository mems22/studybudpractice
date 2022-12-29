from django.contrib import admin
from .models import Room, Topic, Message, User
#Allows you to display info on admin panel

admin.site.register(User )
admin.site.register(Room)
admin.site.register(Topic)
admin.site.register(Message)


