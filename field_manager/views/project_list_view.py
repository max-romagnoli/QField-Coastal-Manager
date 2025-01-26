"""
    field_manager/views/project_list_view.py
    -----------------------
    begin                : January 2025
    copyright            : (C) 2025 QField Coastal by max-romagnoli
    email                : maxxromagnoli (at) gmail.com
 ******************************************************************************
 *                                                                            *
 *   This program is free software; you can redistribute it and/or modify     *
 *   it under the terms of the GNU General Public License as published by     *
 *   the Free Software Foundation; either version 2 of the License, or        *
 *   (at your option) any later version.                                      *
 *                                                                            *
 ******************************************************************************
"""

from rest_framework.generics import ListAPIView
from rest_framework import serializers

from field_manager.models import Project


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "name", "project_id", "created_at"]


class ProjectListView(ListAPIView):
    """
    GET /field_manager/projects/
    Returns a list of all available projects (basic example).
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer