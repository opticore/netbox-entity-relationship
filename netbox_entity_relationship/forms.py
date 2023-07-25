""" Form. """
from django import forms
from django.contrib.contenttypes.models import ContentType
from netbox_entity_relationship.choices import AppChoices as APPCHOICES
from netbox_entity_relationship.choices import ArrowShapeChoices as ARROWSHAPECHOICES
from netbox_entity_relationship.choices import OptionsChoices as OPTIONSCHOICES
from netbox_entity_relationship.choices import RankDirChoices as RANKDIROPTIONSCHOICES
from utilities.forms import add_blank_choice
from utilities.forms.fields import DynamicModelChoiceField
from utilities.forms.widgets import APISelect


class EntityRelationshipForm(forms.Form):
    """Form."""

    app_label = forms.ChoiceField(
        choices=add_blank_choice(APPCHOICES),
        required=False,
        help_text="Select an App",
        widget=forms.Select(),
    )
    model_name = DynamicModelChoiceField(
        queryset=ContentType.objects.all(),
        query_params={"app_label": "$app_label"},
        help_text="Select a Model",
        widget=APISelect(
            api_url="/api/extras/content-types/",
        ),
    )
    arrow_shape = forms.ChoiceField(
        choices=ARROWSHAPECHOICES,
        initial=ARROWSHAPECHOICES.NORMAL,
        required=False,
        help_text="Arrow shape to use for relations",
        widget=forms.Select(),
    )
    color_code_deletions = forms.ChoiceField(
        choices=OPTIONSCHOICES,
        initial=OPTIONSCHOICES.FALSE,
        required=False,
        help_text="Color the relations according to their on_delete setting, where it it applicable. The colors are: red (CASCADE), orange (SET_NULL), green (SET_DEFAULT), yellow (SET), blue (PROTECT), grey (DO_NOTHING) and purple ",
        widget=forms.Select(),
    )
    hide_edge_labels = forms.ChoiceField(
        choices=OPTIONSCHOICES,
        initial=OPTIONSCHOICES.FALSE,
        required=False,
        help_text="Do not show relations labels in the graph",
        widget=forms.Select(),
    )
    rankdir = forms.ChoiceField(
        choices=RANKDIROPTIONSCHOICES,
        initial=RANKDIROPTIONSCHOICES.BT,
        required=False,
        help_text="Set direction of graph layout",
        widget=forms.Select(),
    )
    relation_fields_only = forms.ChoiceField(
        choices=OPTIONSCHOICES,
        initial=OPTIONSCHOICES.FALSE,
        required=False,
        help_text="Only display fields that are relevant for relations",
        widget=forms.Select(),
    )

    fieldsets = (
        ("Model", ("app_label", "model_name")),
        (
            "Options",
            (
                "arrow_shape",
                "color_code_deletions",
                "hide_edge_labels",
                "rankdir",
                "relation_fields_only",
            ),
        ),
    )
