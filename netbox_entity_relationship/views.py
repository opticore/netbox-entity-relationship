"""Classes required in order to render an entity relationship diagram for netbox views."""
from django.apps import apps
from django.shortcuts import render
from django.views.generic import View
from netbox_entity_relationship.diagram import render_entity_relationship_diagram
from netbox_entity_relationship.forms import EntityRelationshipForm
from utilities.views import ViewTab


class EntityRelationshipNetboxView(View):
    """Display Netbox Object Entity Relationship Diagram."""

    tab = ViewTab(
        label="Entity Relationship",
        permission="netbox_entity_relationship.view_render",
        weight=10000,
    )
    template_name = "netbox_entity_relationship/netbox_entity_relationship_netbox.html"

    def get(self, request, **kwargs):
        """Get."""

        xml_str = render_entity_relationship_diagram(kwargs["model"], {})

        return render(
            request,
            self.template_name,
            {
                "object": kwargs["model"].objects.get(pk=kwargs["pk"]),
                "tab": self.tab,
                "xml_str": xml_str,
            },
        )


class EntityRelationshipRenderView(View):
    """Display Plugin Object Entity Relationship Diagram Form."""

    form = EntityRelationshipForm

    def get(self, request):
        """Get."""
        self.form = self.form()
        return render(
            request,
            "netbox_entity_relationship/netbox_entity_relationship_form.html",
            {
                "form": self.form,
                "return_url": "",
            },
        )

    def post(self, request):
        """Post."""
        form = self.form(data=request.POST)
        if form.is_valid():
            model = apps.get_model(
                form.cleaned_data["model_name"].app_label,
                model_name=form.cleaned_data["model_name"].model,
            )
            xml_str = render_entity_relationship_diagram(model, form.cleaned_data)
        else:
            xml_str = ""

        return render(
            request,
            "netbox_entity_relationship/netbox_entity_relationship_render.html",
            {
                "xml_str": xml_str,
            },
        )
