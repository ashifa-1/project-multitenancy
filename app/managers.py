from django.db import models

from .tenant_context import get_current_tenant


class TenantManager(models.Manager):

    def get_queryset(self):

        queryset = super().get_queryset()

        tenant = get_current_tenant()

        if tenant:
            return queryset.filter(tenant=tenant)

        return queryset.none()