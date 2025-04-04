import os
import subprocess
import tempfile
import json
import shutil

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from field_manager.models import (
    ProjectInstance,
    ProjectInstanceUploadRecord,
    ProjectInstanceGeoJSONLayer
)

class Command(BaseCommand):
    help = "Convert existing project uploads to GeoJSON and create records."

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
            collection_folder = os.path.join(instance_path, 'collection')
            if not os.path.isdir(collection_folder):
                self.stdout.write(f"Skipping {instance_slug}: No collection folder.")
                continue
            gpkg_files = [f for f in os.listdir(collection_folder) if f.endswith('.gpkg')]
            if not gpkg_files:
                self.stdout.write(f"No GPKG file found for {instance_slug}, skipped.")
                continue
            upload_timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            upload_folder_rel = os.path.join('uploads', f"{upload_timestamp}-{instance_slug}")
            upload_folder_abs = os.path.join(settings.MEDIA_ROOT, upload_folder_rel)
            layers_folder = os.path.join(upload_folder_abs, 'layers')
            files_folder = os.path.join(upload_folder_abs, 'files')
            os.makedirs(layers_folder, exist_ok=True)
            os.makedirs(files_folder, exist_ok=True)
            source_files_folder = os.path.join(instance_path, 'files')
            if os.path.exists(source_files_folder):
                shutil.copytree(source_files_folder, files_folder, dirs_exist_ok=True)
            upload_record = ProjectInstanceUploadRecord.objects.create(
                project_instance=instance,
                upload_folder=upload_folder_rel
            )
            for gpkg_filename in gpkg_files:
                gpkg_path = os.path.join(collection_folder, gpkg_filename)
                with tempfile.TemporaryDirectory() as tmp_dir:
                    tmp_geojson = os.path.join(tmp_dir, f"{gpkg_filename}.geojson")
                    layers_output = subprocess.check_output([
                        "ogrinfo",
                        gpkg_path
                    ], encoding='utf-8')

                    layer_names = [
                        line.strip().split(' ')[1]
                        for line in layers_output.splitlines()
                        if line.strip().startswith('1:') or line.strip().startswith('2:')  # assuming layer listing lines
                    ]

                    for layer_name in layer_names:
                        tmp_geojson = os.path.join(tmp_dir, f"{layer_name}.geojson")
                        subprocess.run([
                            "ogr2ogr",
                            "-f", "GeoJSON",
                            "-t_srs", "EPSG:4326",
                            "-nln", layer_name,
                            tmp_geojson,
                            gpkg_path,
                            layer_name
                        ], check=True)
                        with open(tmp_geojson, "r", encoding="utf-8") as f:
                            raw_data = f.read()
                        parsed_data = json.loads(raw_data)
                        ProjectInstanceGeoJSONLayer.objects.create(
                            upload_record=upload_record,
                            layer_name=layer_name,
                            geojson_data=parsed_data
                        )
            self.stdout.write(f"Processed {instance_slug} successfully.")
        self.stdout.write(self.style.SUCCESS("All existing uploads processed."))