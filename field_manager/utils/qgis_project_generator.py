import os
import shutil
from django.conf import settings

def create_project_folder_for_instance(instance, template_dir):
    """
    Copies the entire template directory (e.g. ir_general) for the given
    ProjectInstance, if not already assigned. Returns the path to the instance folder.
    """

    if instance.qgis_folder_path:
        # Already has a folder assigned
        return instance.qgis_folder_path

    #   MEDIA_ROOT/project_files/<instance_slug>/
    instance_dir = os.path.join(
        settings.MEDIA_ROOT,
        "project_files",
        instance.instance_slug or f"instance_{instance.pk}"
    )

    # Copy tree from template_dir to instance_dir
    shutil.copytree(template_dir, instance_dir)

    relative_path = os.path.relpath(instance_dir, settings.MEDIA_ROOT)
    instance.qgis_folder_path = relative_path
    instance.save()

    return instance_dir