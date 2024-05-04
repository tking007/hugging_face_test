from django.apps import AppConfig


class UserConfig(AppConfig):
    name = 'admin'

class MyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mrking_app'
