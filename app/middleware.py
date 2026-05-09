from django.http import JsonResponse
from django.db import connection

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

        if not tenant_id:

            self.set_public_schema()

            return self.get_response(request)

        try:

            tenant = Tenant.objects.get(
                tenant_id=tenant_id
            )

            request.tenant = tenant

            set_current_tenant(tenant)

            self.set_tenant_schema(
                tenant.db_schema
            )

        except Tenant.DoesNotExist:

            self.set_public_schema()

            return JsonResponse(
                {'error': 'Invalid tenant ID'},
                status=404
            )

        response = self.get_response(request)

        self.set_public_schema()

        clear_current_tenant()

        return response

    def set_tenant_schema(self, schema_name):

        with connection.cursor() as cursor:

            cursor.execute(
                f'SET search_path TO "{schema_name}"'
            )

    def set_public_schema(self):

        with connection.cursor() as cursor:

            cursor.execute(
                'SET search_path TO public'
            )