import logging
from datetime import datetime
from django.http import HttpResponseForbidden
import time
from django.http import JsonResponse
from collections import defaultdict

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create file handler
file_handler = logging.FileHandler('requests.log')
file_handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter('%(message)s')
file_handler.setFormatter(formatter)

# Add the handler to the logger (prevent multiple handler duplications)
if not logger.hasHandlers():
    logger.addHandler(file_handler)

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else "Anonymous"
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        logger.info(log_message)
        return self.get_response(request)


class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Restrict access only to chat-related paths
        restricted_paths = ['/api/messages/', '/api/conversations/']
        
        current_time = datetime.now().time()
        start_time = datetime.strptime("18:00", "%H:%M").time()
        end_time = datetime.strptime("21:00", "%H:%M").time()

        # Only apply restriction to chat-related URLs
        if request.path in restricted_paths:
            if not (start_time <= current_time <= end_time):
                return HttpResponseForbidden("Access to chat is restricted to between 6PM and 9PM.")
        
        return self.get_response(request)


class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Store IPs and their POST request timestamps
        self.message_log = defaultdict(list)
        self.TIME_WINDOW = 60  # seconds
        self.MAX_MESSAGES = 5  # per minute

    def __call__(self, request):
        if request.method == "POST" and request.path.startswith("/api/messages"):
            ip = self.get_client_ip(request)
            current_time = time.time()

            # Filter timestamps: keep only those within the time window
            recent_messages = [
                t for t in self.message_log[ip]
                if current_time - t < self.TIME_WINDOW
            ]
            self.message_log[ip] = recent_messages

            if len(recent_messages) >= self.MAX_MESSAGES:
                return JsonResponse(
                    {"error": "Rate limit exceeded. Max 5 messages per minute."},
                    status=429  # Too Many Requests
                )

            # Log the current POST time
            self.message_log[ip].append(current_time)

        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
    

class RolepermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        protected_paths = ["/api/messages/", "/api/conversations/"]

        if request.path.startswith(tuple(protected_paths)):
            user = request.user
            if user.is_authenticated:
                # Check for role-based access
                user_role = getattr(user, 'role', None)
                if user_role not in ['admin', 'moderator']:
                    return JsonResponse(
                        {"error": "Access denied. Admin or moderator role required."},
                        status=403
                    )
            else:
                return JsonResponse(
                    {"error": "Authentication required."},
                    status=403
                )

        return self.get_response(request)
