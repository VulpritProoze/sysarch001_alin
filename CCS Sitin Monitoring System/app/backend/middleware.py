from django.shortcuts import render 
from django.http import HttpResponseNotAllowed

class CacheControlMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response

class MethodNotAllowedMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code == 405:
            return render(request, 'backend/pages/405.html', status=405)
        return response