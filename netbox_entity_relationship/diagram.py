"""Classes required in order to render an entity relationship diagram in netbox views."""
import pygraphviz
from django_extensions.management.modelviz import ModelGraph, generate_dot, loader, os


#
# Entity Relationship Render
#


def render_entity_relationship_diagram(model, options):
    """Render to xml."""
    # Create a list of related Models to include in the graph
    include_models = []
    model_name = model._meta.object_name
    include_models.append(model_name)
    for relation in model._meta.related_objects:
        include_models.append(relation.related_model.__name__.capitalize())
    # Create the Model Graph
    args = []
    cli_options = {}

    # Convert string to bool
    for k, v in options.items():  # pylint: disable=invalid-name
        if v == "False":
            options[k] = False
        elif v == "True":
            options[k] = True
    options = {
        "pygraphviz": True,
        "all_applications": True,
        "relations_as_fields": False,
        "include_models": include_models,
        "arrow_shape": "normal",
        "rankdir": "BT",
        **options,
    }
    graph_models = ModelGraph(args, cli_options=cli_options, **options)

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
    xml_str = xml_bytes.decode()

    # Customise for netbox look and feel
    xml_str = xml_str.replace('polygon fill="white"', 'polygon fill="var(--nbx-select-content-bg)"')
    xml_str = xml_str.replace('polygon fill="#1b563f"', 'polygon fill="var(--nbx-sidebar-link-active-bg)"')
    xml_str = xml_str.replace(
        'polygon fill="none"',
        'polygon fill="none" stroke="var(--nbx-cable-termination-border-color)"',
    )
    xml_str = xml_str.replace(
        'polygon fill="black"',
        'polygon fill="var(--nbx-cable-termination-border-color)"',
    )
    xml_str = xml_str.replace('font-family="Roboto"', 'class="--bs-font-sans-serif"')
    xml_str = xml_str.replace('stroke="black"', 'stroke="var(--nbx-cable-termination-border-color)"')
    xml_str = xml_str.replace('fill="#7b7b7b"', "")
    xml_str = xml_str.replace('stroke="transparent"', "")
    xml_str = xml_str.replace('font-size="8.00"', 'font-size="10.00" fill="var(--nbx-body-color)"')
    xml_str = xml_str.replace(
        'font-style="italic" font-size="10.00" fill="white">',
        'font-size="0" fill="transparent">',
    )
    xml_str = xml_str.replace(
        'font-weight="bold" font-size="10.00" fill="white">',
        ' font-weight="bold" font-size="16.00" fill="var(--nbx-body-color)">',
    )
    xml_str = xml_str.replace('stroke="black"', "")

    # Remove garbage from SVG
    xml_str = xml_str.replace("&#160;&#160;&#160;", "")
    xml_str = xml_str.replace("&gt;", "")
    xml_str = xml_str.replace("&lt;", "")
    xml_str = xml_str.replace("&#45;", "")
    xml_str = xml_str.replace("\n", "")

    return xml_str
