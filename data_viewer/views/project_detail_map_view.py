from django.shortcuts import render, get_object_or_404
from django.views import View
from field_manager.models import Project, ProjectInstanceUploadRecord, ProjectInstance
import json

class ProjectDetailMapView(View):
    template_name = "data_viewer/project_detail_map.html"

    def get(self, request, project_id):
        project = get_object_or_404(Project, project_id=project_id)
        instances = ProjectInstance.objects.filter(project=project)
        instance_info = []
        for instance in instances:
            latest_upload = instance.uploads.order_by('-uploaded_at').first()
            if latest_upload:
                layers = latest_upload.geojson_layers.all()
                geojson_list = []
                for layer in layers:
                    geojson_list.append({
                        "layer_name": layer.layer_name,
                        "geojson_data": layer.geojson_data
                    })
                instance_info.append({
                    "slug": instance.instance_slug,
                    "username": instance.user.username,
                    "geojson_layers": geojson_list,
                    "upload_folder": latest_upload.upload_folder,
                })
        context = {
            "project": project,
            "instances_json": json.dumps(instance_info)
        }
        return render(request, self.template_name, context)