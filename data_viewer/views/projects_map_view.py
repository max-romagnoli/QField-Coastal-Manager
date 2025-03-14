"""
    data_viewer/views/projects_map_view.py
    -----------------------
    begin                : March 2025
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

from django.views.generic import TemplateView
from field_manager.models import Project, ProjectInstance
from django.core.serializers import serialize
import json

class ProjectsMapView(TemplateView):
    template_name = "data_viewer/projects_map.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        projects = Project.objects.exclude(location__isnull=True)
        context["projects_json"] = json.dumps([
            {
                "id": project.id,
                "name": project.name,
                "location": {"lat": project.location.y, "lon": project.location.x},
            }
            for project in projects
        ])
        return context