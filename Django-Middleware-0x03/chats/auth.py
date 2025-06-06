from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import AnonymousUser

class CustomJWTAuthentication(JWTAuthentication):
    """
    Optional custom authentication class for added flexibility.
    Currently wraps DRF SimpleJWT with room for custom logic (e.g., user activity tracking).
    """

    def authenticate(self, request):
        try:
            user_auth_tuple = super().authenticate(request)
            if user_auth_tuple is None:
                return (AnonymousUser(), None)
            return user_auth_tuple
        except AuthenticationFailed:
            # You can log this event or raise a custom exception
            raise AuthenticationFailed("Invalid or expired token. Please log in again.")
