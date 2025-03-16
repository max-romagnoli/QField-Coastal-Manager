import os
import shutil
import tempfile
import json
import subprocess
import datetime

from django.conf import settings
from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from field_manager.models import ProjectInstance, ProjectInstanceUploadRecord

class ProjectInstanceUploadView(APIView):
    """
    Expects:
      - 'json_data': text part with JSON like {"instance_slug": "..."}
      - 'file': exactly one ZIP file part
    """

    def post(self, request, *args, **kwargs):

        # Parse metadata from text part
        meta_data_raw = request.data.get("json_data")
        
        meta_data = {}
        if meta_data_raw:
            try:
                meta_data = json.loads(meta_data_raw)
            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON in 'json_data'."},
                                status=status.HTTP_400_BAD_REQUEST)

        instance_slug = meta_data.get("instance_slug")
        if not instance_slug:
            return Response({"error": "No 'instance_slug' specified in meta_data."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Get the ZIP file from "file" field
        uploaded_files = request.FILES.getlist("file")
        
        if not uploaded_files:
            return Response({"error": "No file uploaded."},
                            status=status.HTTP_400_BAD_REQUEST)
        if len(uploaded_files) > 1:
            return Response({"error": "Multiple files uploaded, only one ZIP expected."},
                            status=status.HTTP_400_BAD_REQUEST)

        zip_file = uploaded_files[0]
        
        if not zip_file.name.lower().endswith(".zip"):
            return Response({"error": "Uploaded file is not a ZIP archive."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Save ZIP to a temporary location
        tmp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(tmp_dir, zip_file.name)

        with open(zip_path, "wb") as out:
            for chunk in zip_file.chunks():
                out.write(chunk)

        # Figure out final folder to store the unzipped project
        project_folder_rel = os.path.join("project_files", instance_slug)
        project_folder_abs = os.path.join(settings.MEDIA_ROOT, project_folder_rel)

        if os.path.exists(project_folder_abs):
            shutil.rmtree(project_folder_abs)
        os.makedirs(project_folder_abs)

        # Unzip the archive into project_folder_abs
        try:
            shutil.unpack_archive(zip_path, project_folder_abs, "zip")
        except Exception as e:
            shutil.rmtree(tmp_dir)
            return Response({"error": f"Failed to unpack zip: {e}"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Convert layers to GeoJSON for data_viewer
        # geojson_output = os.path.join(project_folder_abs, 'collection', 'layers.geojson')
        # gpkg_files = [f for f in os.listdir(os.path.join(project_folder_abs, 'collection')) if f.endswith('.gpkg')]
        # if gpkg_files:
        #     gpkg_path = os.path.join(project_folder_abs, 'collection', gpkg_files[0])
        #     subprocess.run(["ogr2ogr", "-f", "GeoJSON", geojson_output, gpkg_path], check=True)

        upload_timestamp = datetime.timezone.now().strftime('%Y%m%d_%H%M%S')
        upload_folder_rel = os.path.join('uploads', f"{upload_timestamp}-{instance_slug}")
        upload_folder_abs = os.path.join(settings.MEDIA_ROOT, upload_folder_rel)

        # Create subfolders
        layers_folder = os.path.join(upload_folder_abs, 'layers')
        files_folder = os.path.join(upload_folder_abs, 'files')
        os.makedirs(layers_folder, exist_ok=True)
        os.makedirs(files_folder, exist_ok=True)

        # Convert layers to GeoJSON in the layers_folder
        gpkg_files = [f for f in os.listdir(os.path.join(project_folder_abs, 'collection')) if f.endswith('.gpkg')]
        if gpkg_files:
            gpkg_path = os.path.join(project_folder_abs, 'collection', gpkg_files[0])
            geojson_output = os.path.join(layers_folder, 'layers.geojson')
            subprocess.run(["ogr2ogr", "-f", "GeoJSON", geojson_output, gpkg_path], check=True)

        # Record this upload in the DB
        ProjectInstanceUploadRecord.objects.create(
            project_instance=instance,
            upload_folder=upload_folder_rel
        )

        # Cleanup temp directory
        shutil.rmtree(tmp_dir)

        # Update or create ProjectInstance linking it to the unzipped folder
        try:
            instance = ProjectInstance.objects.get(instance_slug=instance_slug)
            instance.qgis_folder_path = project_folder_rel
            instance.save()
        except ProjectInstance.DoesNotExist:
            return Response(
                {"error": f"No ProjectInstance found with slug {instance_slug}."},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {
                "message": "Project instance unzipped successfully",
                "instance_slug": instance_slug,
                "folder_path": project_folder_rel,
            },
            status=status.HTTP_201_CREATED
        )
 