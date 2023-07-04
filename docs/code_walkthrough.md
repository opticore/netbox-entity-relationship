## Code Walkthrough
Full code is available in the [Opticore github repo](https://github.com/opticore).

### Dependencies
Python Poetry is a tool for managing dependencies and packaging in Python projects. Once installed, I added the dependencies that are specific to this plugin.

```
[plugins/netbox_entity_relationship/pyproject.toml]

python = "^3.8"
django-extensions = "^3.2.1"
pygraphviz = "^1.10"
```

and also installed these repos.
```
apt-get update
apt-get install -y graphviz libgraphviz-dev
```

### __init__
A standard netbox initialization file but with the required django_extensions package added to netbox installed apps and a loop that searches all Django apps and then adds them to the netbox app registry.
```
 [plugins/netbox_entity_relationship/netbox_entity_relationship/__init__.py]

    ...
    django_apps = ["django_extensions"]
    ...
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
```
Now that the apps are registered, netbox can inject the Tab into the view for all models that are viewed from the netbox navigation pane.

![Entity Relationship Tab](images/entity-relationship-tab.png)

### Diagram
This is the core of the plugin.

Graphviz is an open-source graph visualization software that uses DOT language to generate diagrams and representations of graphs and networks. PyGraphviz is  the Python interface to the Graphviz that is used here.

In Django, related_objects is a backward relation added to a model that allows accessing related objects in a more efficient and generic way. related_objects is used to create a list of the NetBox models related to the model that is selected with app and model by the user. This gives the selected model and its single tiered relations.
```
 [plugins/netbox_entity_relationship/netbox_entity_relationship/diagram.py]

  for relation in model._meta.related_objects
      include_models.append(relation.related_model.__name__.capitalize()):
```
These models and the options that are passed as kwargs to the function are processed by PyGraphviz and modules from django_extensions.management.modelviz, ModelGraph, generate dot and loader.
```
[plugins/netbox_entity_relationship/netbox_entity_relationship/diagram.py]

graph_models = ModelGraph(args, cli_options=cli_options, **options

# Create the dot file
graph_models.generate_graph_data()
graph_data = graph_models.get_graph_data(as_json=False)
theme = "django2018"
template_name = os.path.join("django_extensions", "graph_models", theme, "digraph.dot")
template = loader.get_template(template_name)
dotdata = generate_dot(graph_data, template=template)

# Create the xml for display
graph = pygraphviz.AGraph(dotdata)
graph.layout(prog="dot")
xml_bytes = graph.draw(format="svg")
xml_str = xml_bytes.decode())
```
The resultant XML string XML_STR is customised for netbox's look and feel by adding the light and darkmode CSS to the SVG images within the XML.

### Choices
Django choices allow you to define a set of options or choices for a field in your Django model and restrict the input to those options. These are statically defined in this file, except for the App Choices which are dynamically created when netbox starts.
```

[plugins/netbox_entity_relationship/netbox_entity_relationship/choices.py]

class AppChoices(ChoiceSet)
    """Dynamic values for AppChoices."""


    CHOICES = ()


    # Create a list of related Models to include in the graph
    for model in django.apps.apps.get_models():


        app_label = model._meta.app_label  # pylint: disable=protected-access
        if app_label not in str(CHOICES):
            choice = ((app_label, app_label),)
            CHOICES = CHOICES + choice
    CHOICES = sorted(CHOICES):
```
### Forms
Django forms provide an easy way to generate and handle HTML forms, including data validation, and make it easy to handle user input on the server side. This is the form used to collect the options from the user.
```
[plugins/netbox_entity_relationship/netbox_entity_relationship/forms.py]

class EntityRelationshipForm(forms.Form)
    """Form."""


    app_label = forms.ChoiceField(
        choices=add_blank_choice(APPCHOICES), required=False, help_text="Select an App", widget=StaticSelect()
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
        widget=StaticSelect(),:
...
```
The Model Name uses the netbox APISelect widget in order to dynamically populate the items in the list by passing the App Label.

### Views
I am using a Django class-based view to processes a request, handle user input, and return an HTTP response. There are two required, one is used when viewing netbox models in the navigation pane and the other facilitates the collection of the Models and Options.
```

[plugins/netbox_entity_relationship/netbox_entity_relationship/views.py]

class EntityRelationshipNetboxView(View)
    """Display Netbox Object Entity Relationship Diagram."""


    tab = ViewTab(label="Entity Relationship", permission="netbox_entity_relationship.view_render", weight=10000)
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
        ):
...
```
### Navigation
A simple menu item is created in the netbox navigation pane.
```

[plugins/netbox_entity_relationship/netbox_entity_relationship/navigation.py]

"""Navigation.""
from extras.plugins import PluginMenuItem


item = (
    PluginMenuItem(
        link="plugins:netbox_entity_relationship:entityrelationship_render",
        link_text="Generate",
        permissions=["netbox_entity_relationship.entityrelationship_render"],
    ),
)


menu_items = item"
```
### Template
Django template is a text-based markup language used by the Django web framework to define the structure and presentation of HTML documents.

In the snippet below we see that HTML is dynamically created in order to display the form data.
```
[plugins/netbox_entity_relationship/netbox_entity_relationship/templates/netbox_entity_relationship/netbox_entity_relationship_form.html]
...
            {# Render grouped fields according to Form #
            {% for group, fields in form.fieldsets %}
              <div class="field-group mb-5">
                {% if group %}
                  <div class="row mb-2">
                    <h5 class="offset-sm-3">{{ group }}</h5>
                  </div>
                {% endif %}
                {% for name in fields %}
                  {% with field=form|getfield:name %}
                    {% if not field.field.widget.is_hidden %}
                      {% render_field field %}
                    {% endif %}
                  {% endwith %}
                {% endfor %}
              </div>
            {% endfor %}}
...
```
Three forms are required, one is used when viewing netbox models in the navigation pane, one facilitates the collection of the Models and Options and the third displays the entity relationship diagram render.
```
[plugins/netbox_entity_relationship/netbox_entity_relationship/templates/netbox_entity_relationship/netbox_entity_relationship_render.html]

{% block content-wrapper %
<form>
    <style>
        #graph0 > polygon:nth-child(2) {fill: var(--nbx-select-content-bg)}
        .node > text:nth-child(5) {transform: translateY(+8px) translateX(-5px);}
    </style>
    <div class="tab-content">
        <div class="tab-pane show active" id="edit-form" role="tabpanel" aria-labelledby="object-list-tab">
            <div class="card">
                <div class="card-body overflow-visible d-flex flex-wrap justify-content-between py-3">
                    <div class="col col-12">
                        {% csrf_token %}
                        {{ xml_str | safe }}
                    </div>
                </div>
            </div>
        </div>
    </div>
</form>
{% endblock content-wrapper %}}
```
When a template is rendered, any variables enclosed within {{ }} are replaced with their corresponding values. In this case, the XML string, with some CSS that predicatively modifies the look and feel to the standard netbox theme.

Reading the code, the Graphviz provided HTML is modified for the nth-child(2) polygon after the element with an ID of 'graph0'. The fill is changed to '--nbx-select-content-bg' which gives the blue coloured box at the top of the models that is dynamically modified when the user selects dark or light mode.
