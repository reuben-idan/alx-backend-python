from django.apps import AppConfig

class DjangoChatConfig(AppConfig):
    name = 'Django-Chat'

    def ready(self):
        import Django_Chat.signals
