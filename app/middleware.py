from django.http import JsonResponse

from .models import Tenant
from .tenant_context import (
    set_current_tenant,
    clear_current_tenant
)


class TenantMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        tenant_id = request.headers.get('X-Tenant-ID')

        if tenant_id:
            try:
                tenant = Tenant.objects.get(tenant_id=tenant_id)

                set_current_tenant(tenant)

                request.tenant = tenant

            except Tenant.DoesNotExist:

                return JsonResponse(
                    {'error': 'Invalid tenant ID'},
                    status=404
                )

        response = self.get_response(request)

        clear_current_tenant()

        return response