"""
    field_manager/views/project_join_view.py
    -----------------------
    begin                : January 2025
    copyright            : (C) 2025 QField Coastal by max-romagnoli
    email                : maxxromagnoli (at) gmail.com
 ******************************************************************************
 *                                                                            *
 *   This program is free software; you can redistribute it and/or modify     *
 *   it under the terms of the GNU General Public License as published by     *
 *   the Free Software Foundation; either version 2 of the License, or        *
 *   (at your option) any later version.                                      *
 *                                                                            *
 ******************************************************************************
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.contrib.auth import authenticate, get_user_model
from django.utils.text import slugify
from django.utils.crypto import get_random_string

from field_manager.models import Project, ProjectInstance
from field_manager.utils.qgis_project_generator import create_project_folder_for_instance


User = get_user_model()

class ProjectJoinView(APIView):
    """
    POST /field_manager/projects/join/
    Allows a participant to join/create an instance of a Project:
      - with username/password, or
      - as a guest (creates a one-off user).
    """

    def post(self, request, *args, **kwargs):
        project_id = request.data.get("project_id")
        username = request.data.get("username")
        password = request.data.get("password")
        guest_flag = request.data.get("guest", False)

        if not project_id:
            return Response({"error": "No project_id provided."},
                            status=status.HTTP_400_BAD_REQUEST)

        # 1) Try to get the Project
        try:
            project = Project.objects.get(project_id=project_id)
        except Project.DoesNotExist:
            return Response({"error": f"Project {project_id} not found."},
                            status=status.HTTP_404_NOT_FOUND)

        # 2) Determine the user (authenticate or create guest)
        if guest_flag:
            user = self._create_guest_user()
        else:
            if not username or not password:
                return Response({"error": "Must provide username/password or use guest flag."},
                                status=status.HTTP_400_BAD_REQUEST)

            user = authenticate(username=username, password=password)
            if not user:
                return Response({"error": "Invalid credentials."},
                                status=status.HTTP_401_UNAUTHORIZED)

        # 3) Create a new ProjectInstance for the user
        instance = ProjectInstance.objects.create(
            project=project,
            user=user,
            instance_slug=self._generate_instance_slug(project, user)
        )

        # template_dir = "field_manager/"      # TODO: Can have many more templates
        template_dir = "field_manager/qgis_templates/ir_general"
        instance_dir = create_project_folder_for_instance(instance, template_dir)

        # 4) Return instance info
        data = {
            "message": "Joined project successfully.",
            "project": {
                "id": project.pk,
                "name": project.name,
                "project_id": project.project_id
            },
            "user": {
                "id": user.pk,
                "username": user.username
            },
            "instance_slug": instance.instance_slug,
            "instance_id": instance.pk,
            "project_folder": instance.qgis_folder_path
        }
        return Response(data, status=status.HTTP_201_CREATED)


    def _create_guest_user(self):
        """
        Creates a one-off guest user with a random username. 
        Ensure it doesn't conflict with real accounts.
        """
        random_str = get_random_string(6)
        guest_username = f"guest_{random_str}"
        guest_user = User.objects.create_user(username=guest_username, password=None)
        return guest_user


    def _generate_instance_slug(self, project, user):
        """
        Creates a unique slug for the user's project instance, 
        e.g. "coastal-001-guest_abc123".
        """
        base_slug = f"{project.project_id}-{user.username}"
        new_slug = slugify(base_slug)
        while ProjectInstance.objects.filter(instance_slug=new_slug).exists():
            new_slug = slugify(base_slug + "-" + get_random_string(4))
        return new_slug
