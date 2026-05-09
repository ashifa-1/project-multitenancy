import threading
from django.http import JsonResponse
from .models import Tenant

_thread_locals = threading.local()

def get_current_tenant():
    return getattr(_thread_locals, 'tenant', None)

class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        tenant_id = request.headers.get('X-Tenant-ID')
        if tenant_id:
            try:
                tenant = Tenant.objects.get(tenant_id=tenant_id)
                _thread_locals.tenant = tenant
                request.tenant = tenant
            except Tenant.DoesNotExist:
                return JsonResponse(
                    {'error': 'Invalid tenant ID'},
                    status=404
                )
        response = self.get_response(request)
        if hasattr(_thread_locals, 'tenant'):
            del _thread_locals.tenant
        return response