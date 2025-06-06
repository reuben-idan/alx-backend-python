# chats/middleware.py

from datetime import datetime
from django.utils.deprecation import MiddlewareMixin

class RequestLoggingMiddleware(MiddlewareMixin):
    def __call__(self, request):
        user = request.user if request.user.is_authenticated else 'Anonymous'
        log_entry = f"{datetime.now()} - User: {user} - Path: {request.path}\n"

        with open('requests.log', 'a') as log_file:
            log_file.write(log_entry)

        response = self.get_response(request)
        return response
