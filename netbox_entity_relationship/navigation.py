"""Navigation."""
from extras.plugins import PluginMenuItem

item = (
    PluginMenuItem(
        link="plugins:netbox_entity_relationship:entityrelationship_render",
        link_text="Generate",
        permissions=["netbox_entity_relationship.entityrelationship_render"],
    ),
)

menu_items = item
