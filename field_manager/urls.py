"""
    field_manager/urls.py
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

from django.urls import path
from .views import ProjectJoinView, ProjectListView, ProjectUploadView, ProjectInstanceDownloadView

urlpatterns = [
    path("projects/", ProjectListView.as_view(), name="project-list"),   
    path("projects/join/", ProjectJoinView.as_view(), name="project-join"),         
    path("projects/upload/", ProjectUploadView.as_view(), name="project-upload"),
    path("project-instances/<int:pk>/download/", ProjectInstanceDownloadView.as_view(), name="instance-download"),
]