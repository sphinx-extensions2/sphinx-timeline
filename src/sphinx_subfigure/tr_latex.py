from __future__ import annotations

import string

from docutils import nodes
from sphinx.application import Sphinx
from sphinx.transforms.post_transforms import SphinxPostTransform
from sphinx.writers.latex import LaTeXTranslator

from ._compat import findall


def setup_latex(app: Sphinx):
    """Setup the extension for LaTeX building."""
    app.add_latex_package("subcaption")
    app.add_post_transform(SubfigureLaTexTransform)
    app.add_node(
        SubfigureEnvLatex,
        latex=(visit_subfigure_grid_latex, depart_subfigure_grid_latex),
    )


class SubfigureEnvLatex(nodes.General, nodes.Element):
    """Node for subfigure grid, added only for LaTeX."""


def visit_subfigure_grid_latex(self: LaTeXTranslator, node: SubfigureEnvLatex) -> None:
    """Visit subfigure grid node."""
    self.body.append("\\begin{subfigure}{" + str(node["width"]) + "\\textwidth}\n")
    self.body.append("\\centering\n")
    if "caption" in node and node["caption-align"] == "above":
        self.body.append("\\caption{" + self.escape(node["caption"]) + "}\n")


def depart_subfigure_grid_latex(self: LaTeXTranslator, node: SubfigureEnvLatex) -> None:
    """Depart subfigure grid node."""
    if "caption" in node and node["caption-align"] == "below":
        self.body.append("\\caption{" + self.escape(node["caption"]) + "}\n")
    self.body.append("\\end{subfigure}\n")
    if node.get("new-row"):
        self.body.append("\n")


class SubfigureLaTexTransform(SphinxPostTransform):
    """Transform subfigure containers into the HTML specific AST structures."""

    default_priority = 199
    formats = ("latex",)

    def run(self) -> None:
        """Run the transform."""

        # docutils <0.18 (traverse) >=0.18 (findall) compatibility
        for fig_node in findall(
            self.document, lambda n: "is_subfigure" in getattr(n, "attributes", {})
        ):
            layout = fig_node["layout"]["default"]
            if not layout:
                continue
            # if the layout is a simple progression of areas,
            # we can use just the subfigure environment to create a grid
            progression = True
            next = (0, "A")
            flattened = []
            for row in layout:
                for idx, area in enumerate(row):
                    if area == ".":
                        pass
                    elif idx != 0 and flattened[-1][0] == area:
                        flattened[-1][1] += 1
                    elif area == next[1]:
                        flattened.append([area, 1, False])
                        next = (next[0] + 1, string.ascii_uppercase[next[0] + 1])
                    else:
                        progression = False
                        break
                if not progression:
                    break
                flattened[-1][2] = True

            flattened[-1][2] = False

            if not progression:
                continue

            width = round(0.99 / len(layout[0]), 3)

            children = []
            subfigs = 0
            for child in fig_node:
                if isinstance(child, nodes.caption):
                    children.append(child)
                else:
                    subcaption_node = SubfigureEnvLatex(
                        width=width * flattened[subfigs][1]
                    )
                    if flattened[subfigs][2]:
                        subcaption_node["new-row"] = True
                    subfigs += 1
                    if fig_node.get("subcaptions") and child.get("alt"):
                        subcaption_node["caption-align"] = fig_node["subcaptions"]
                        subcaption_node["caption"] = child["alt"]
                    subcaption_node += child
                    children.append(subcaption_node)
            fig_node.children = children
