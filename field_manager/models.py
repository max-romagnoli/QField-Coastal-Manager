"""
    field_manager/models.py
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

from django.db import models
from django.contrib.gis.db import models as gis_models
from django.contrib.auth.models import User
from django.utils import timezone


class Project(models.Model):
    """
    Represents a coastal survey project. Each project has a unique ID (slug) used 
    by participants to join.
    """
    name = models.CharField(max_length=200)
    project_id = models.SlugField(unique=True, help_text="Unique ID for participants to join.")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name_plural = 'Projects'
        verbose_name = 'Project' 

    def __str__(self):
        return f"{self.name} ({self.project_id})"


class ProjectInstance(models.Model):
    """
    Each user (or guest) joining a Project gets a separate ProjectInstance,
    ensuring multiple participants do not overwrite each other's work.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="instances")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="project_instances")
    created_at = models.DateTimeField(default=timezone.now)

    instance_slug = models.SlugField(null=True, blank=True, unique=True)

    qgis_folder_path = models.CharField(
        max_length=500,
        null=True, blank=True,
        help_text="Path (relative to MEDIA_ROOT) for the project folder."
    )

    class Meta:
        verbose_name_plural = 'Project Instances'
        verbose_name = 'Project Instance' 

    def __str__(self):
        return f"Instance of {self.project} for user {self.user.username}"


class TestGeometry(models.Model):
    point = gis_models.PointField()
    # photo = models.ImageField(upload_to='photos/', null=True, blank=True)
    # photo = models.BinaryField(null=True, blank=True)  # Store the photo as binary data

    class Meta:
        verbose_name_plural = 'Test Geometries'
        verbose_name = 'Test Geometry' 