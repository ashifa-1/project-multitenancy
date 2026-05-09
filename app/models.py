from django.db import models
from .managers import TenantManager

class Tenant(models.Model):
    name = models.CharField(max_length=255)
    tenant_id = models.CharField(max_length=100, unique=True)
    db_schema = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'tenants'

    def __str__(self):
        return self.name


class Project(models.Model):

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)

    name = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    objects = TenantManager()

    all_objects = models.Manager()

    def __str__(self):
        return self.name