from __future__ import annotations

import math
import string

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective

from .tr_html import setup_html
from .tr_latex import setup_latex


def setup(app: Sphinx) -> None:
    """Setup the extension."""
    app.add_directive("subfigure", SubfigureDirective)
    setup_html(app)
    setup_latex(app)


class SubfigureDirective(SphinxDirective):
    """A sphinx directive to create sub-figures."""

    has_content = True
    required_arguments = 0
    optional_arguments = 1  # the subfigure layout (defaults to 1)
    final_argument_whitespace = True
    option_spec = {
        "layout-sm": directives.unchanged,
        "layout-lg": directives.unchanged,
        "layout-xl": directives.unchanged,
        "layout-xxl": directives.unchanged,
        "subcaptions": lambda x: directives.choice(x, ("above", "below")),
        "width": directives.length_or_percentage_or_unitless,
        "align": lambda x: directives.choice(x, ("left", "center", "right")),
        "gap": directives.length_or_percentage_or_unitless,
        "name": directives.unchanged,
        "class": directives.class_option,
        "class-grid": directives.class_option,
        "class-area": directives.class_option,
    }

    def run(self) -> list[nodes.Element]:
        """Run the directive."""
        self.assert_has_content()
        figure_node = nodes.figure(
            is_subfigure=True,
            classes=["sphinx-subfigure"] + self.options.get("class", []),
            grid_classes=self.options.get("class-grid", []),
            area_classes=self.options.get("class-area", []),
        )
        self.set_source_info(figure_node)
        for attribute_name in ("align", "width", "gap", "subcaptions"):
            if attribute_name in self.options:
                figure_node.attributes[attribute_name] = self.options[attribute_name]
        self.add_name(figure_node)
        self.state.nested_parse(self.content, self.content_offset, figure_node)

        number_of_images = 0
        has_caption = False
        for idx, child in enumerate(list(figure_node)):
            if isinstance(child, nodes.image):
                child["subfigure_area"] = string.ascii_uppercase[number_of_images]
                number_of_images += 1
            elif (
                isinstance(child, nodes.paragraph)
                and child.children
                and isinstance(child[0], nodes.image)
            ):
                images = []
                for sub in child:
                    if not isinstance(sub, nodes.image):
                        continue
                    images.append(sub)
                    sub["subfigure_area"] = string.ascii_uppercase[number_of_images]
                    number_of_images += 1
                child.replace_self(images)
            elif isinstance(child, nodes.paragraph):
                if has_caption:
                    raise self.error("Invalid subfigure content (multiple captions)")
                child.replace_self(nodes.caption(child.rawsource, *child.children))
                has_caption = True
            else:
                raise self.error(
                    "Invalid subfigure content; must contain only images and single caption, "
                    f"item {idx + 1} is neither (line {child.line})"
                )

        print(number_of_images)
        layout_string = self.arguments[0] if self.arguments else 1
        figure_node["layout"] = {}
        figure_node["layout"]["default"] = self.generate_layout(
            layout_string, number_of_images
        )
        for size in ("sm", "lg", "xl", "xxl"):
            layout_opt = f"layout-{size}"
            if self.options.get(layout_opt):
                figure_node["layout"][size] = self.generate_layout(
                    self.options.get(layout_opt), number_of_images, ltype=layout_opt
                )

        return [figure_node]

    def generate_layout(
        self, string: str, items: int, ltype: str = "layout", validate: bool = True
    ) -> list[list[str]]:
        """Generate a layout from a string."""
        layout = self._generate_layout(string, items)
        if validate:
            self._validate_layout(layout, items, ltype)
        return layout

    def _validate_layout(
        self, layout: list[list[str]], items: int, ltype="layout"
    ) -> None:
        """Validate a layout.

        Validated according to https://www.w3.org/TR/css3-grid-layout/#grid-template-areas-property:
        - All areas must be named A-Z.
        - All areas must form a single filled-in rectangle
        """

        prefix = f"Invalid subfigure {ltype}"

        area_indices: dict[str, list[tuple[int, int]]] = {}

        # check all rows have the same number of columns, and retrieve indices of each area
        if not layout:
            raise self.error(f"{prefix} (empty)")
        for rid, row in enumerate(layout):
            if not row:
                raise self.error(f"{prefix} (empty row)")
            if len(row) != len(layout[0]):
                raise self.error(f"{prefix} (row length mismatch)")
            for cid, area in enumerate(row):
                if area != ".":
                    area_indices.setdefault(area, set()).add((rid, cid))

        available_areas = {string.ascii_uppercase[i] for i in range(items)}
        used_areas = set(area_indices)

        # check all areas are used in the layout
        missing_areas = available_areas - used_areas
        if missing_areas:
            raise self.error(f"{prefix} (missing areas {missing_areas})")

        # check all areas correspond to an item
        additional_areas = used_areas - available_areas
        if additional_areas:
            raise self.error(f"{prefix} (invalid areas {additional_areas})")

        # Check that all area_indices form single filled-in rectangles
        for area, indices in area_indices.items():
            if len(indices) == 1:
                continue
            x0, y0 = min(x for x, _ in indices), min(y for _, y in indices)
            x1, y1 = max(x for x, _ in indices), max(y for _, y in indices)
            expected_indices = {
                (x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)
            }
            if expected_indices != indices:
                raise self.error(f"{prefix} (area {area} is not a single rectangular)")

    def _generate_layout(self, layout_string: str, items: int) -> list[list[str]]:
        """Generate a figure layout from a string."""
        layout = []

        # if an integer is given, generate a layout with this many columns
        # this is similar to the CSS: grid-template-columns: repeat(columns, 1fr)
        try:
            layout_columns = int(layout_string)
        except ValueError:
            pass
        else:
            for row in range(math.ceil(items / layout_columns)):
                layout.append([])
                for col in range(layout_columns):
                    if (row * layout_columns) + col > items - 1:
                        area = "."
                    else:
                        area = string.ascii_uppercase[(row * layout_columns) + col]
                    layout[row].append(area)
            return layout

        # if a string is given, parse it as a grid layout, with columns delimited by "|",
        # ignore spaces, named areas A-Z and empty areas are filled with "."
        for row_string in layout_string.split("|"):
            row = []
            for col in row_string:
                if not col:
                    continue  # ignore spaces
                row.append(col)
            layout.append(row)
        return layout
