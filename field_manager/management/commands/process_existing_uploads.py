import os
import subprocess
import tempfile
import json
import shutil
import logging

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from field_manager.models import (
    ProjectInstance,
    ProjectInstanceUploadRecord,
    ProjectInstanceGeoJSONLayer
)

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Convert existing project uploads to GeoJSON (all layers) and create records."

    def handle(self, *args, **kwargs):
        base_folder = os.path.join(settings.MEDIA_ROOT, 'project_files')
        
        # Loop over each slug inside project_files
        for instance_slug in os.listdir(base_folder):
            instance_path = os.path.join(base_folder, instance_slug)
            if not os.path.isdir(instance_path):
                continue
            
            # Attempt to find a matching ProjectInstance
            try:
                instance = ProjectInstance.objects.get(instance_slug=instance_slug)
            except ProjectInstance.DoesNotExist:
                self.stdout.write(f"Skipping {instance_slug}: No matching instance.")
                continue
            
            # Must have a 'collection' subfolder
            collection_folder = os.path.join(instance_path, 'collection')
            if not os.path.isdir(collection_folder):
                self.stdout.write(f"Skipping {instance_slug}: No collection folder.")
                continue
            
            gpkg_files = [f for f in os.listdir(collection_folder) if f.endswith('.gpkg')]
            if not gpkg_files:
                self.stdout.write(f"No GPKG file found for {instance_slug}, skipped.")
                continue
            
            # Create a record of this "upload"
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
            
            # Process each GPKG in this folder
            for gpkg_filename in gpkg_files:
                gpkg_path = os.path.join(collection_folder, gpkg_filename)
                
                # -- 1) Get layer names using `ogrinfo`
                try:
                    layer_info = subprocess.run(
                        ["ogrinfo", gpkg_path],
                        capture_output=True, text=True, check=True
                    )
                except subprocess.CalledProcessError as e:
                    # If we can't even read the GPKG, log and skip
                    logger.error("Failed to read %s for instance %s: %s", gpkg_filename, instance_slug, e)
                    continue
                
                # Parse out lines that start with "<number>: <layer_name>"
                # Example line from `ogrinfo` might be: "1: layer_name (Polygon)"
                all_layers = []
                for line in layer_info.stdout.splitlines():
                    line = line.strip()
                    if line and ':' in line and line.split(':')[0].isdigit():
                        # e.g., "1: ardmayle_possible_features (MultiPolygon)"
                        # Extract the portion after "1: "
                        layer_part = line.split(':', 1)[1].strip()
                        # Usually something like "ardmayle_possible_features (MultiPolygon)"
                        # We only need the first token up to space or "("
                        layer_name = layer_part.split('(')[0].strip()
                        all_layers.append(layer_name)
                
                # -- 2) Convert each layer individually
                for layer_name in all_layers:
                    with tempfile.TemporaryDirectory() as tmp_dir:
                        tmp_geojson = os.path.join(tmp_dir, f"{layer_name}.geojson")
                        
                        # Attempt to convert this single layer
                        try:
                            subprocess.run([
                                "ogr2ogr",
                                "-f", "GeoJSON",
                                "-t_srs", "EPSG:4326",
                                tmp_geojson,   # output path
                                gpkg_path,     # input .gpkg
                                layer_name     # specific layer
                            ], check=True)
                        except subprocess.CalledProcessError as e:
                            # Log and continue; do not abort the entire command
                            logger.error(
                                "Failed to convert layer '%s' in '%s' for instance '%s'. Error: %s",
                                layer_name, gpkg_filename, instance_slug, e
                            )
                            continue
                        
                        # If successful, read and store in DB
                        try:
                            with open(tmp_geojson, "r", encoding="utf-8") as f:
                                raw_data = f.read()
                            parsed_data = json.loads(raw_data)
                            
                            # Create a record for each successfully-converted layer
                            ProjectInstanceGeoJSONLayer.objects.create(
                                upload_record=upload_record,
                                layer_name=f"{gpkg_filename}:{layer_name}",
                                geojson_data=parsed_data
                            )
                        except Exception as e:
                            logger.error(
                                "Error reading or storing GeoJSON for layer '%s' in '%s' for instance '%s'. Error: %s",
                                layer_name, gpkg_filename, instance_slug, e
                            )
            
            self.stdout.write(f"Processed {instance_slug} successfully.")
        
        self.stdout.write(self.style.SUCCESS("All existing uploads processed."))