from django.shortcuts import render
from rest_framework import viewsets
from .models import Project
from .serializers import ProjectSerializer
from .tenant_context import get_current_tenant

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    def perform_create(self, serializer):
        serializer.save(
            tenant=get_current_tenant()
        )