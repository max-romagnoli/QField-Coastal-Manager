"""
    data_viewer/urls.py
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

from django.urls import path
from .views import MapView, ProjectsMapView, ProjectDetailMapView

app_name = 'data_viewer'

urlpatterns = [
    path('', ProjectsMapView.as_view(), name='projects-map-view'),
    path('detail/<str:project_id>/', ProjectDetailMapView.as_view(), name='project-detail-map'),
]