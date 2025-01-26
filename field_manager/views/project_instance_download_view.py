"""
    field_manager/views/project_instance_download_view.py
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

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
import os
import shutil
import tempfile
from django.http import FileResponse
from django.conf import settings

from field_manager.models import ProjectInstance

class ProjectInstanceDownloadView(APIView):
    """
    GET /field_manager/project-instances/<int:pk>/download/
    Returns the URL to the .qgz file or (optionally) an actual file response (TODO: to be decided).
    """

    def get(self, request, pk):
        instance = get_object_or_404(ProjectInstance, pk=pk)
        if not instance.qgis_folder_path:
            return Response({"error": "No folder assigned"}, status=404)

        folder_path = os.path.join(settings.MEDIA_ROOT, instance.qgis_folder_path)
        if not os.path.exists(folder_path):
            return Response({"error": "Folder not found"}, status=404)

        tmp_dir = tempfile.mkdtemp()
        zip_file_path = os.path.join(tmp_dir, f"{instance.instance_slug}.zip")

        shutil.make_archive(
            base_name=os.path.splitext(zip_file_path)[0],
            format="zip",
            root_dir=folder_path
        )

        return FileResponse(
            open(zip_file_path, "rb"),
            as_attachment=True,
            filename=f"{instance.instance_slug}.zip"
        )
