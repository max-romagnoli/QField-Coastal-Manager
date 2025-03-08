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

    qgs_filename = _find_qgis_project_file(instance_dir)
    if qgs_filename:
        new_qgs_filename = os.path.join(instance_dir, f"{instance.project.name}.qgs")
        os.rename(qgs_filename, new_qgs_filename)

    relative_path = os.path.relpath(instance_dir, settings.MEDIA_ROOT)
    instance.qgis_folder_path = relative_path
    instance.save()

    return instance_dir


def _find_qgis_project_file(folder_path):
    """
    Helper function to find a .qgz or .qgs file in the given folder.
    """
    for file in os.listdir(folder_path):
        if file.endswith(".qgz") or file.endswith(".qgs"):
            return file  # Return the first found QGIS project file
    return None