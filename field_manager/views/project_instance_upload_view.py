import os
import shutil
import tempfile
import json

from django.conf import settings
from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from field_manager.models import ProjectInstance

class ProjectInstanceUploadView(APIView):
    """
    Expects:
      - 'json_data': text part with JSON like {"instance_slug": "..."}
      - 'file': exactly one ZIP file part
    """

    def post(self, request, *args, **kwargs):
        print("Received upload request.")
        
        # Parse metadata from text part
        meta_data_raw = request.data.get("json_data")
        print(f"Raw metadata: {meta_data_raw}")
        
        meta_data = {}
        if meta_data_raw:
            try:
                meta_data = json.loads(meta_data_raw)
                print(f"Parsed metadata: {meta_data}")
            except json.JSONDecodeError:
                print("Error: Invalid JSON in 'json_data'.")
                return Response({"error": "Invalid JSON in 'json_data'."},
                                status=status.HTTP_400_BAD_REQUEST)

        instance_slug = meta_data.get("instance_slug")
        if not instance_slug:
            print("Error: No 'instance_slug' specified.")
            return Response({"error": "No 'instance_slug' specified in meta_data."},
                            status=status.HTTP_400_BAD_REQUEST)
        print(f"Instance slug: {instance_slug}")

        # Get the ZIP file from "file" field
        uploaded_files = request.FILES.getlist("file")
        print(f"Uploaded files count: {len(uploaded_files)}")
        
        if not uploaded_files:
            print("Error: No file uploaded.")
            return Response({"error": "No file uploaded."},
                            status=status.HTTP_400_BAD_REQUEST)
        if len(uploaded_files) > 1:
            print("Error: Multiple files uploaded, only one ZIP expected.")
            return Response({"error": "Multiple files uploaded, only one ZIP expected."},
                            status=status.HTTP_400_BAD_REQUEST)

        zip_file = uploaded_files[0]
        print(f"Received file: {zip_file.name}")
        
        if not zip_file.name.lower().endswith(".zip"):
            print("Error: Uploaded file is not a ZIP archive.")
            return Response({"error": "Uploaded file is not a ZIP archive."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Save ZIP to a temporary location
        tmp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(tmp_dir, zip_file.name)
        print(f"Temporary directory created: {tmp_dir}")

        with open(zip_path, "wb") as out:
            for chunk in zip_file.chunks():
                out.write(chunk)
        print(f"ZIP file saved to {zip_path}")

        # Figure out final folder to store the unzipped project
        project_folder_rel = os.path.join("project_files", instance_slug)
        project_folder_abs = os.path.join(settings.MEDIA_ROOT, project_folder_rel)
        print(f"Target folder: {project_folder_abs}")

        if os.path.exists(project_folder_abs):
            print(f"Removing existing folder: {project_folder_abs}")
            shutil.rmtree(project_folder_abs)
        os.makedirs(project_folder_abs)
        print(f"Created new folder: {project_folder_abs}")

        # Unzip the archive into project_folder_abs
        try:
            shutil.unpack_archive(zip_path, project_folder_abs, "zip")
            print("Unzipping successful.")
        except Exception as e:
            shutil.rmtree(tmp_dir)
            print(f"Error: Failed to unpack zip: {e}")
            return Response({"error": f"Failed to unpack zip: {e}"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Cleanup temp directory
        shutil.rmtree(tmp_dir)
        print("Temporary directory cleaned up.")

        # Update or create ProjectInstance linking it to the unzipped folder
        try:
            instance = ProjectInstance.objects.get(instance_slug=instance_slug)
            instance.qgis_folder_path = project_folder_rel
            instance.save()
            print(f"Updated ProjectInstance {instance_slug} with new folder path.")
        except ProjectInstance.DoesNotExist:
            print(f"Error: No ProjectInstance found with slug {instance_slug}.")
            return Response(
                {"error": f"No ProjectInstance found with slug {instance_slug}."},
                status=status.HTTP_404_NOT_FOUND
            )

        print("Upload and processing completed successfully.")
        return Response(
            {
                "message": "Project instance unzipped successfully",
                "instance_slug": instance_slug,
                "folder_path": project_folder_rel,
            },
            status=status.HTTP_201_CREATED
        )
