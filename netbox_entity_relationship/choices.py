""" Choices."""
import django.apps

from utilities.choices import ChoiceSet


class AppChoices(ChoiceSet):
    """Dynamic values for AppChoices."""

    CHOICES = ()

    # Create a list of related Models to include in the graph
    for model in django.apps.apps.get_models():
        app_label = model._meta.app_label  # pylint: disable=protected-access
        if app_label not in str(CHOICES):
            choice = ((app_label, app_label),)
            CHOICES = CHOICES + choice
    CHOICES = sorted(CHOICES)


class OptionsChoices(ChoiceSet):
    """Valid values for Options."""

    TRUE = True
    FALSE = False

    CHOICES = (
        (TRUE, "True"),
        (FALSE, "False"),
    )


class ArrowShapeChoices(ChoiceSet):
    """Valid values for Arrow Shape."""

    BOX = "box"
    CROW = "crow"
    CURVE = "curve"
    DIAMOND = "diamond"
    DOT = "dot"
    ICURVE = "icurve"
    INV = "inv"
    NONE = "none"
    NORMAL = "normal"
    TEE = "tee"
    VEE = "vee"

    CHOICES = (
        (BOX, "Box"),
        (CROW, "Crow"),
        (CURVE, "Curve"),
        (DIAMOND, "Diamond"),
        (DOT, "Dot"),
        (ICURVE, "Icurve"),
        (INV, "Inv"),
        (NONE, "None"),
        (NORMAL, "Normal"),
        (TEE, "Tee"),
        (VEE, "Vee"),
    )


class RankDirChoices(ChoiceSet):
    """Valid values for Rank Dir."""

    TB = "TB"
    LR = "LR"
    BT = "BT"
    RL = "RL"

    CHOICES = (
        (TB, "Top to Bottom"),
        (LR, "Left to Right"),
        (BT, "Bottom to Top"),
        (RL, "Right to Left"),
    )
