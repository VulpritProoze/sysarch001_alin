from django.shortcuts import render 
from django.utils.functional import SimpleLazyObject
from django.contrib.auth.models import User

# Ensures logged-out user cannot go back to authorized pages
class CacheControlMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response

# Render an error page for status 405 (redirect error)
class MethodNotAllowedMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code == 405:
            return render(request, 'backend/pages/405.html', status=405)
        return response
    
# Prefetch request.user
class UserPrefetchMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.user.is_authenticated:
            user_pk = request.user.pk
            request.user = SimpleLazyObject(lambda: User.objects.select_related(
                'registration',
                'sitinsurvey'
            ).prefetch_related(
                'groups',
                'user_permissions',
            ).get(pk=user_pk))
        return self.get_response(request)