from django.core.management.base import BaseCommand
from django.db import connection
from app.models import Tenant

class Command(BaseCommand):
    help = 'Create schema for tenant'
    def add_arguments(self, parser):
        parser.add_argument(
            'tenant_id',
            type=str
        )
    def handle(self, *args, **options):
        tenant_id = options['tenant_id']
        try:
            tenant = Tenant.objects.get(
                tenant_id=tenant_id
            )
        except Tenant.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    f'Tenant {tenant_id} not found'
                )
            )
            return
        schema_name = tenant.db_schema
        with connection.cursor() as cursor:
            cursor.execute(
                f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'
            )
        self.stdout.write(
            self.style.SUCCESS(
                f'Schema "{schema_name}" created successfully'
            )
        )