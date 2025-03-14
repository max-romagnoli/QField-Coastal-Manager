"""
    data_viewer/views/map_view.py
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

class MapView(TemplateView):
    template_name = "data_viewer/map.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['projects'] = Project.objects.all()
        context['instances'] = ProjectInstance.objects.select_related('project').all()
        return context