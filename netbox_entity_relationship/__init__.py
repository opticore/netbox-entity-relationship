"""Plugin for Entity Relationship."""
import django.apps

from netbox.registry import registry
from extras.plugins import PluginConfig

__version__ = "0.1.0"


class EntityRelationshipConfig(PluginConfig):
    """Plugin configuration for netbox_entity_relationship."""

    name = "netbox_entity_relationship"
    verbose_name = "Netbox Entity Relationship"
    version = __version__
    author = "OpticoreIT"
    author_email = "info@opticoreit.com"
    description = "Plugin for Entity Relationship"
    base_url = "netbox_entity_relationship"

    django_apps = ["django_extensions"]

    def ready(self):
        for netbox_model in django.apps.apps.get_models():
            netbox_app_label = netbox_model._meta.app_label
            netbox_model_name = netbox_model._meta.model_name

            if netbox_model_name not in registry["views"][netbox_app_label]:
                registry["views"][netbox_app_label][netbox_model_name] = []

            registry["views"][netbox_app_label][netbox_model_name].append(
                {
                    "name": "netbox_entity_relationship",
                    "view": "netbox_entity_relationship.views.EntityRelationshipNetboxView",
                    "path": "netbox_entity_relationship",
                    "kwargs": {"model": netbox_model},
                }
            )
        return super().ready()


config = EntityRelationshipConfig  # pylint: disable=invalid-name
