from django.apps import AppConfig
#Allows you to connect to main project via settings.py

class BaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'base'
