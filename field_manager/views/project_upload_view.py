"""
    field_manager/views/project_upload_view.py
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

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json

class ProjectUploadView(APIView):
    """
    A simple view that handles multi-part file uploads.
    Expects:
      - 'json_data': text part with some JSON describing the project
      - 'file': one or more file parts for the actual project files
    """

    def post(self, request, *args, **kwargs):
        # Parse metadata
        meta_data_raw = request.data.get("json_data")
        meta_data = {}
        if meta_data_raw:
            try:
                meta_data = json.loads(meta_data_raw)
            except json.JSONDecodeError:
                pass

        # Process uploaded files
        uploaded_files = request.FILES.getlist("file")
        if not uploaded_files:
            return Response(
                {"error": "No files uploaded."},
                status=status.HTTP_400_BAD_REQUEST
            )

        saved_files = []
        for f in uploaded_files:
            saved_path = default_storage.save(f.name, f)
            saved_files.append(saved_path)

        return Response(
            {
                "message": "Files uploaded successfully",
                "saved_files": saved_files,
                "meta_data": meta_data
            },
            status=status.HTTP_201_CREATED
        )