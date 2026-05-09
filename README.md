# Production-Ready Multi-Tenant Django Application with PostgreSQL

## Overview

This project implements and benchmarks two major multi-tenancy strategies used in modern SaaS architectures:

1. Row-Level Security (RLS)
2. Schema-per-Tenant Isolation

The system was built using Django, PostgreSQL, Docker, and Redis. It demonstrates tenant-aware request handling, schema switching, benchmarking, indexing analysis, and performance comparisons between isolation strategies.

---

# Objective

The objective of this project is to:

* Understand multi-tenancy architecture in backend systems
* Implement tenant-aware data isolation strategies
* Benchmark and compare performance trade-offs
* Explore database-level isolation techniques in PostgreSQL
* Analyze indexing impact on tenant-scoped queries

---

# Tech Stack

| Technology            | Purpose                       |
| --------------------- | ----------------------------- |
| Django                | Backend framework             |
| Django REST Framework | API development               |
| PostgreSQL            | Relational database           |
| Redis                 | Caching service               |
| Docker                | Containerization              |
| Docker Compose        | Multi-container orchestration |
| Python                | Core programming language     |

---

# Project Architecture

The project implements two tenant isolation approaches:

## 1. Row-Level Security (RLS)

All tenants share the same database tables.
Tenant data isolation is enforced through:

* Tenant-aware middleware
* Thread-local tenant context
* Custom Django model managers
* Automatic queryset filtering

### Example

A query such as:

```python
Project.objects.all()
```

automatically becomes:

```sql
SELECT * FROM app_project
WHERE tenant_id = current_tenant;
```

---

## 2. Schema-per-Tenant Isolation

Each tenant receives a separate PostgreSQL schema.

Example:

```text
public
schema_tenant_a
schema_tenant_b
```

Tenant isolation is achieved using:

```sql
SET search_path TO tenant_schema;
```

This causes PostgreSQL to automatically query tenant-specific tables.

---

# Features Implemented

## Part A - Row-Level Security

### Implemented Features

* Tenant model
* Project model
* Tenant middleware
* Thread-local tenant context
* Tenant-aware custom manager
* Automatic queryset filtering
* Tenant-scoped REST APIs
* Request header based tenant resolution

### Header-Based Tenant Resolution

Example:

```http
X-Tenant-ID: tenant_a
```

---

## Part B - Schema Isolation

### Implemented Features

* PostgreSQL schema provisioning
* Tenant schema creation command
* Database router
* Dynamic schema switching middleware
* PostgreSQL search_path based isolation

### Schema Provisioning Command

```bash
python manage.py provision_tenant tenant_a
```

Creates:

```text
schema_tenant_a
```

inside PostgreSQL.

---

## Part C - Benchmarking

### Benchmarks Performed

* RLS without indexing
* RLS with composite indexing
* Schema isolation query benchmarking
* search_path overhead measurement
* PostgreSQL index size analysis

---

# Benchmark Results

## Final Results

```json
{
  "rls_without_index": 0.006873132999317022,
  "rls_with_index": 0.00314734700077679,
  "schema_isolation_avg": 0.019940409333988402,
  "search_path_overhead": 0.00031619347999367164,
  "index_size": "328 kB"
}
```

---

# Benchmark Analysis

## RLS Without Index

The query performance was slower because PostgreSQL needed to scan a larger portion of the shared table.

---

## RLS With Composite Index

Adding a composite index on:

```text
(tenant_id, created_at)
```

significantly improved query performance.

This demonstrates the importance of indexing in shared-table multi-tenant architectures.

---

## Schema Isolation

Schema isolation introduced a small overhead because each benchmark cycle included:

* schema switching using SET search_path
* namespace resolution
* query execution

Although schema isolation is generally expected to perform very well due to smaller tenant-specific tables, the indexed RLS implementation performed faster in this benchmark because:

* the RLS model used a composite index
* schema benchmark tables did not use equivalent indexing
* search_path switching overhead was included in timing

---

## search_path Overhead

The overhead of:

```sql
SET search_path
```

was extremely small.

This shows that schema switching is lightweight and practical for many SaaS systems.

---

## Index Size

The composite index consumed additional storage:

```text
328 kB
```

This reflects the common database trade-off:

```text
More storage -> Faster query performance
```

---

# Trade-Off Comparison

| Strategy           | Advantages                                                | Disadvantages                           |
| ------------------ | --------------------------------------------------------- | --------------------------------------- |
| Row-Level Security | Simpler management, centralized schema, easier migrations | Requires careful indexing and filtering |
| Schema Isolation   | Strong tenant separation, smaller tenant-specific tables  | More operational complexity             |

---

# When to Choose Each Strategy

## Choose Row-Level Security When:

* tenant count is very high
* centralized schema management is preferred
* operational simplicity is important
* application-level filtering is sufficient

---

## Choose Schema Isolation When:

* strong tenant isolation is required
* enterprise customers demand separation
* tenant-specific customizations are needed
* security boundaries are critical

---

# Challenges Faced During Development

## Circular Imports

Resolved by extracting thread-local tenant logic into:

```text
tenant_context.py
```

---

## Migration Conflicts

Handled migration reconciliation between:

* seeded database tables
* Django migration state
* unmanaged models

---

## Schema Switching

Implemented manual PostgreSQL:

```sql
SET search_path
```

because Django does not provide built-in schema switching methods.

---

## Docker Networking & Startup Dependencies

Configured:

* PostgreSQL startup synchronization
* Redis container communication
* Docker networking

---

# How to Run the Project

## Clone Repository

```bash
git clone https://github.com/ashifa-1/project-multitenancy
cd project-multitenancy
```

---

## Start Containers

```bash
docker-compose up --build
```

---

## Apply Migrations

```bash
docker-compose exec app python manage.py migrate
```

---

## Run Server

```bash
docker-compose exec app python manage.py runserver 0.0.0.0:8000
```

---

## Provision Tenant Schemas

```bash
docker-compose exec app python manage.py provision_tenant tenant_a
```

---

## Run Benchmarks

```bash
docker-compose exec app python manage.py run_benchmarks
```

---

# Outcome

This project successfully demonstrates:

* practical multi-tenancy implementation
* tenant-aware request handling
* PostgreSQL schema isolation
* benchmarking and indexing analysis
* SaaS backend architecture design
* performance trade-off evaluation

The implementation provides hands-on understanding of how modern scalable SaaS systems manage tenant isolation and query optimization.

---

# Conclusion

This project explored two major multi-tenancy strategies used in production-grade SaaS systems.

The benchmarking results demonstrated that indexing plays a critical role in the performance of shared-table architectures. The project also showed that PostgreSQL schema switching introduces minimal overhead while providing stronger tenant separation.

Both approaches have valid use cases depending on scalability requirements, operational complexity, and security expectations.

Through this implementation, important backend engineering concepts such as request-scoped tenant context, schema isolation, indexing strategies, migration reconciliation, and benchmarking were successfully explored and implemented.
