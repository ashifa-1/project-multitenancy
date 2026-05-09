import json
import time
from django.core.management.base import BaseCommand
from django.db import connection
from app.models import Tenant, Project

class Command(BaseCommand):
    help = 'Runs performance benchmarks for RLS vs Schema Isolation'
    def handle(self, *args, **kwargs):
        results = {}
        self.stdout.write('Creating benchmark data...')
        tenants = []
        for i in range(10):
            tenant, _ = Tenant.objects.get_or_create(
                tenant_id=f'benchmark_tenant_{i}',
                defaults={
                    'name': f'Benchmark Tenant {i}',
                    'db_schema': f'benchmark_schema_{i}'
                }
            )
            tenants.append(tenant)

            with connection.cursor() as cursor:

                cursor.execute(
                    f'''
                    CREATE SCHEMA IF NOT EXISTS
                    "{tenant.db_schema}"
                    '''
                )
                
        existing_count = Project.all_objects.count()
        if existing_count < 10000:
            projects = []
            for tenant in tenants:
                for j in range(1000):
                    projects.append(
                        Project(
                            tenant=tenant,
                            name=f'Project {j}',
                            description='Benchmark project'
                        )
                    )
            Project.all_objects.bulk_create(
                projects,
                batch_size=1000
            )
        self.stdout.write('Benchmark data ready.')
        # --- RLS Benchmarking ---
        # 1. Query without composite index
        start = time.perf_counter()
        list(
            Project.all_objects.filter(
                tenant=tenants[0]
            ).order_by('-created_at')[:100]
        )
        end = time.perf_counter()
        results['rls_without_index'] = (
            end - start
        )
        # ---------------------------
        # Create composite index
        # ---------------------------

        with connection.cursor() as cursor:

            cursor.execute(
                '''
                CREATE INDEX IF NOT EXISTS
                idx_project_tenant_created
                ON app_project (tenant_id, created_at);
                '''
            )
        # RLS with composite index
        start = time.perf_counter()
        list(
            Project.all_objects.filter(
                tenant=tenants[0]
            ).order_by('-created_at')[:100]
        )
        end = time.perf_counter()
        results['rls_with_index'] = (
            end - start
        )
        # Schema Isolation Benchmark
        schema_times = []
        with connection.cursor() as cursor:
            for tenant in tenants[:3]:
                schema_name = tenant.db_schema
                cursor.execute(
                    f'''
                    CREATE TABLE IF NOT EXISTS
                    "{schema_name}".benchmark_projects (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255),
                        created_at TIMESTAMP DEFAULT NOW()
                    );
                    '''
                )
                cursor.execute(
                    f'''
                    INSERT INTO "{schema_name}".benchmark_projects (name)
                    SELECT 'Benchmark Project'
                    FROM generate_series(1, 1000)
                    ON CONFLICT DO NOTHING;
                    '''
                )
                start = time.perf_counter()
                cursor.execute(
                    f'''
                    SET search_path TO "{schema_name}";
                    '''
                )
                cursor.execute(
                    '''
                    SELECT *
                    FROM benchmark_projects
                    ORDER BY created_at DESC
                    LIMIT 100;
                    '''
                )
                cursor.fetchall()
                end = time.perf_counter()
                schema_times.append(
                    end - start
                )
            cursor.execute(
                'SET search_path TO public;'
            )
        results['schema_isolation_avg'] = (
            sum(schema_times) / len(schema_times)
        )
        # Measure search_path overhead
        start = time.perf_counter()
        with connection.cursor() as cursor:
            for _ in range(100):
                cursor.execute(
                    'SET search_path TO public'
                )
        end = time.perf_counter()
        results['search_path_overhead'] = (
            end - start
        ) / 100
        # Index size
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT pg_size_pretty(
                    pg_relation_size(
                        'idx_project_tenant_created'
                    )
                );
                """
            )
            index_size = cursor.fetchone()[0]
        results['index_size'] = index_size
        # Save results
        with open(
            'results/benchmarks.json',
            'w'
        ) as file:

            json.dump(
                results,
                file,
                indent=2
            )
        self.stdout.write(
            self.style.SUCCESS(
                'Benchmarks completed.'
            )
        )