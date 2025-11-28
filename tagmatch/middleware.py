# this file handles middleware, their imports and functions

from django.utils import timezone  # timezone reads the user's timezone for displaying accurate timestamps

class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # If the user has a timezone stored in their profile, activate it
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            tz = getattr(request.user.profile, 'timezone', None)
            if tz:
                timezone.activate(tz)
        else:
            timezone.deactivate()

        return self.get_response(request)
