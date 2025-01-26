# field_manager/views.py

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
        # 1) Parse the text part (metadata)
        meta_data_raw = request.data.get("json_data")  # "json_data" from your QHttpPart text
        meta_data = {}
        if meta_data_raw:
            try:
                meta_data = json.loads(meta_data_raw)
            except json.JSONDecodeError:
                pass  # or handle error

        # Debug / Log
        print("Received metadata:", meta_data)

        # 2) Process uploaded files
        #    By default, Django Rest Framework will parse them into request.FILES
        #    "file" is the field name used in the QHttpMultiPart (ScssCloudConnection).
        #    If multiple files are appended under the same "file" field, getlist("file") has them all.
        uploaded_files = request.FILES.getlist("file")

        if not uploaded_files:
            return Response(
                {"error": "No files uploaded."},
                status=status.HTTP_400_BAD_REQUEST
            )

        saved_files = []

        for f in uploaded_files:
            # This saves the file to your default storage, e.g. local "MEDIA_ROOT",
            # or S3 if that's configured in settings.
            # default_storage.save() returns the final path, typically.
            saved_path = default_storage.save(f.name, f)
            saved_files.append(saved_path)

        # 3) Return a JSON response
        #    In a production scenario, you might store metadata + file references
        #    in the database, or perform other logic.
        return Response(
            {
                "message": "Files uploaded successfully",
                "saved_files": saved_files,
                "meta_data": meta_data
            },
            status=status.HTTP_201_CREATED
        )
