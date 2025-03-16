from django.core.management.base import BaseCommand
from django.conf import settings
from field_manager.models import ProjectInstance, ProjectInstanceUploadRecord
import os
import subprocess
from django.utils import timezone

class Command(BaseCommand):
    help = "Convert existing project uploads to GeoJSON and create ProjectInstanceUpload entries."

    def handle(self, *args, **kwargs):
        base_folder = os.path.join(settings.MEDIA_ROOT, 'project_files')

        for instance_slug in os.listdir(base_folder):
            instance_path = os.path.join(base_folder, instance_slug)
            if not os.path.isdir(instance_path):
                continue

            try:
                instance = ProjectInstance.objects.get(instance_slug=instance_slug)
            except ProjectInstance.DoesNotExist:
                self.stdout.write(f"Skipping {instance_slug}: No matching instance.")
                continue

            upload_timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            upload_folder_rel = os.path.join('uploads', f"{upload_timestamp}-{instance_slug}")
            upload_folder_abs = os.path.join(settings.MEDIA_ROOT, upload_folder_rel)

            layers_folder = os.path.join(upload_folder_abs, 'layers')
            files_folder = os.path.join(upload_folder_abs, 'files')
            os.makedirs(layers_folder, exist_ok=True)
            os.makedirs(files_folder, exist_ok=True)

            # Convert to GeoJSON
            collection_folder = os.path.join(instance_path, 'collection')
            gpkg_files = [f for f in os.listdir(collection_folder) if f.endswith('.gpkg')]

            if gpkg_files:
                gpkg_path = os.path.join(collection_folder, gpkg_files[0])
                geojson_output = os.path.join(layers_folder, 'layers.geojson')
                subprocess.run(["ogr2ogr", "-f", "GeoJSON", geojson_output, gpkg_path], check=True)
                self.stdout.write(f"Processed {instance_slug} successfully.")
            else:
                self.stdout.write(f"No GPKG file found for {instance_slug}, skipped GeoJSON conversion.")
                continue

            ProjectInstanceUploadRecord.objects.create(
                project_instance=instance,
                upload_folder=upload_folder_rel
            )

        self.stdout.write(self.style.SUCCESS("Existing uploads processed successfully."))