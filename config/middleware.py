"""
ErVeda custom middleware.
"""
from django.http import HttpResponseRedirect


class AdminRedirectMiddleware:
    """
    Redirects staff from legacy /admin/ to the dedicated web Admin Portal /admin-portal/.
    Silently redirects authenticated non-staff students away from admin routes to /dashboard/.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Redirect staff from Django standard admin to the custom web Admin Portal
        if request.path == '/admin/' or request.path.startswith('/admin/login/'):
            if request.user.is_authenticated and request.user.is_staff:
                return HttpResponseRedirect('/admin-portal/')
            elif not request.user.is_authenticated:
                return HttpResponseRedirect('/admin-portal/login/')

        # Block non-staff students from accessing protected admin portal endpoints
        if (
            (request.path.startswith('/admin/') or (request.path.startswith('/admin-portal/') and not request.path.startswith('/admin-portal/login/')))
            and request.user.is_authenticated
            and not request.user.is_staff
        ):
            return HttpResponseRedirect('/dashboard/')

        return self.get_response(request)
