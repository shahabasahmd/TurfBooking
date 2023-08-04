from django.http import HttpResponseForbidden

class BlockMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if user.is_authenticated and user.is_blocked:
            return HttpResponseForbidden("Your access has been blocked by the administrator.")
        return self.get_response(request)