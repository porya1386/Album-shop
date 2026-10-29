
"""The 16 base colours a painting can have. Names are translatable."""
from django.utils.translation import gettext_lazy as _

# (code, name, hex)
PALETTE = [
    ("red",    _("Red"),    "#D32F2F"),
    ("orange", _("Orange"), "#F57C00"),
    ("yellow", _("Yellow"), "#FBC02D"),
    ("lime",   _("Lime"),   "#AFB42B"),
    ("green",  _("Green"),  "#388E3C"),
    ("teal",   _("Teal"),   "#00897B"),
    ("cyan",   _("Cyan"),   "#00ACC1"),
    ("blue",   _("Blue"),   "#1976D2"),
    ("navy",   _("Navy"),   "#1A237E"),
    ("purple", _("Purple"), "#7B1FA2"),
    ("pink",   _("Pink"),   "#EC407A"),
    ("brown",  _("Brown"),  "#6D4C41"),
    ("beige",  _("Beige"),  "#D7C4A3"),
    ("gray",   _("Gray"),   "#757575"),
    ("black",  _("Black"),  "#111111"),
    ("white",  _("White"),  "#F5F5F5"),
]

PALETTE_NAMES = {code: name for code, name, _hex in PALETTE}


def seed_colors(sender, **kwargs):
    """post_migrate: make sure the 16 colours exist (never touches ones you edited)."""
    apps = kwargs.get("apps")
    using = kwargs.get("using", "default")
    try:
        Color = apps.get_model("shop", "Color")
    except LookupError:        # e.g. migrating back to zero
        return
    for order, (code, _name, hex_value) in enumerate(PALETTE):
        Color.objects.using(using).get_or_create(
            code=code, defaults={"hex": hex_value, "order": order}
        )
