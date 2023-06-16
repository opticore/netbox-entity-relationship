"""Urls required in order to render an entity relationship diagram for netbox views."""
from django.urls import path

from .views import (
    EntityRelationshipRenderView,
)


urlpatterns = [
    path("", EntityRelationshipRenderView.as_view(), name="entityrelationship_render"),
]
