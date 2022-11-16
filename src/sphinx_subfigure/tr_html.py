from __future__ import annotations

from html import escape
from typing import Any

from docutils import nodes
from sphinx.application import Sphinx
from sphinx.transforms.post_transforms import SphinxPostTransform
from sphinx.writers.html import HTMLTranslator

from ._compat import findall


def setup_html(app: Sphinx):
    """Setup the extension for HTML building."""
    app.add_post_transform(SubfigureHtmlTransform)
    app.add_node(
        SubfigureGridHtml, html=(visit_subfigure_grid_html, depart_subfigure_grid_html)
    )
    app.add_node(
        SubfigureGridItemHtml,
        html=(visit_subfigure_grid_item_html, depart_subfigure_grid_item_html),
    )
    app.connect("html-page-context", html_page_context)


def html_page_context(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, Any],
    doctree: nodes.document | None,
) -> None:
    """Add CSS for grid layouts, to HTML pages that require it."""
    if not doctree:
        return
    if "subfig_layouts" not in doctree:
        return

    style = []
    for size, cls_layout in doctree["subfig_layouts"].items():
        if size == "sm":
            style.append("@media (max-width: 576px) {")
        if size == "lg":
            style.append("@media (min-width: 992px) {")
        if size == "xl":
            style.append("@media (min-width: 1200px) {")
        if size == "xxl":
            style.append("@media (min-width: 1400px) {")
        for layout_class, layout in cls_layout.items():
            layout_grid = " ".join(["'" + " ".join(row) + "'" for row in layout])
            style.append(f"  .{layout_class} {{ grid-template-areas: {layout_grid}; }}")
        if size in ["sm", "lg", "xl", "xxl"]:
            style.append("}")

    if style:
        context["body"] = (
            "\n<style>\n" + "\n".join(style) + "\n</style>\n" + context["body"]
        )


class SubfigureGridHtml(nodes.General, nodes.Element):
    """Node for subfigure grid, added only for Html."""


def visit_subfigure_grid_html(self: HTMLTranslator, node: SubfigureGridHtml) -> None:
    """Visit subfigure grid node."""
    classes = " ".join(node["classes"])
    style = "display: grid;"
    if "gap" in node:
        # the grid- prefix is deprecated
        style += f" gap: {node['gap']}; grid-gap: {node['gap']};"
    self.body.append(f'<div class="{classes}" style="{style}">\n')


def depart_subfigure_grid_html(self: HTMLTranslator, node: SubfigureGridHtml) -> None:
    """Depart subfigure grid node."""
    self.body.append("</div>\n")


class SubfigureGridItemHtml(nodes.General, nodes.Element):
    """Node for subfigure grid item, added only for Html."""


def visit_subfigure_grid_item_html(
    self: HTMLTranslator, node: SubfigureGridItemHtml
) -> None:
    """Visit subfigure grid item node."""
    classes = " ".join(node["classes"])
    style = "display: flex; flex-direction: column; justify-content: center; align-items: center;"
    style += f" grid-area: {node['area']};"
    self.body.append(f'<div class="{classes}" style="{style}">\n')
    if "caption" in node and node["caption-align"] == "above":
        self.body.append(f'<span class="caption">{escape(node["caption"])}</span>\n')


def depart_subfigure_grid_item_html(
    self: HTMLTranslator, node: SubfigureGridItemHtml
) -> None:
    """Depart subfigure grid item node."""
    if "caption" in node and node["caption-align"] == "below":
        self.body.append(f'<span class="caption">{escape(node["caption"])}</span>\n')
    self.body.append("</div>\n")


class SubfigureHtmlTransform(SphinxPostTransform):
    """Transform subfigure containers into the HTML specific AST structures."""

    default_priority = 199
    formats = ("html",)

    def run(self) -> None:
        """Run the transform."""

        # docutils <0.18 (traverse) >=0.18 (findall) compatibility
        for fig_node in findall(
            self.document, lambda n: "is_subfigure" in getattr(n, "attributes", {})
        ):

            # initiate figure children
            children = []

            # store layouts
            classes = ["sphinx-subfigure-grid"]
            if "subfig_layouts" not in self.document:
                self.document["subfig_layouts"] = {}
            for size, layout in fig_node["layout"].items():
                layout_class = f"ss-layout-{size}-" + "_".join(
                    ["".join(a.replace(".", "d") for a in row) for row in layout]
                )
                self.document["subfig_layouts"].setdefault(size, {})[
                    layout_class
                ] = layout
                classes.append(layout_class)

            # add grid
            grid_node = SubfigureGridHtml(
                classes=classes + fig_node.get("grid_classes", [])
            )
            if "gap" in fig_node:
                grid_node["gap"] = fig_node["gap"]
            children.append(grid_node)

            # add image items to grid
            caption = None
            area_classes = ["sphinx-subfigure-area"] + fig_node.get("area_classes", [])
            for child in fig_node:
                if isinstance(child, nodes.caption):
                    caption = child
                    continue
                item_node = SubfigureGridItemHtml(classes=area_classes)
                # if fig_node["layout_type"] == "areas":
                item_node["area"] = child["subfigure_area"]
                if fig_node.get("subcaptions") and child.get("alt"):
                    item_node["caption-align"] = fig_node["subcaptions"]
                    item_node["caption"] = child["alt"]
                item_node.append(child)
                grid_node.append(item_node)

            # add caption
            if caption:
                children.append(caption)

            fig_node.children = children
