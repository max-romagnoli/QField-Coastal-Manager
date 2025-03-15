from django.shortcuts import render, get_object_or_404
from django.views import View
from field_manager.models import Project, ProjectInstance
import json

class ProjectDetailMapView(View):

    template_name = "data_viewer/project_detail_map.html"

    def get(self, request, project_id):
        project = get_object_or_404(Project, project_id=project_id)

        instances = ProjectInstance.objects.filter(project=project).exclude(qgis_folder_path__isnull=True)

        instance_info = []
        for instance in instances:
            instance_info.append({
                "slug": instance.instance_slug,
                "folder_path": instance.qgis_folder_path,
                "username": instance.user.username
            })

        context = {
            "project": project,
            "instances_json": json.dumps(instance_info),
        }
        return render(request, self.template_name, context)