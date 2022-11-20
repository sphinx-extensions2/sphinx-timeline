from __future__ import annotations

import csv
import hashlib
from importlib import resources
from io import StringIO
import json
from pathlib import Path
import re
from typing import Any, Literal, TextIO

from docutils import nodes
from docutils.parsers.rst import directives
from docutils.statemachine import StringList
import jinja2
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective
import yaml

from sphinx_timeline import dtime
from sphinx_timeline import static as static_module


def setup(app: Sphinx) -> None:
    """Setup the extension."""
    from sphinx_timeline import __version__

    app.connect("builder-inited", add_css)
    app.add_directive("timeline", TimelineDirective)
    app.add_node(
        TimelineDiv,
        html=(visit_tl_div, depart_tl_div),
        latex=(visit_depart_null, visit_depart_null),
        text=(visit_depart_null, visit_depart_null),
        man=(visit_depart_null, visit_depart_null),
        texinfo=(visit_depart_null, visit_depart_null),
    )

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }


def add_css(app: Sphinx):
    """Copy the CSS to the build directory."""
    # setup up new static path in output dir
    static_path = (Path(app.outdir) / "_sphinx_timeline_static").absolute()
    static_path.mkdir(exist_ok=True)
    app.config.html_static_path.append(str(static_path))
    # Read the css content and hash it
    content = resources.read_text(static_module, "default.css")
    hash = hashlib.md5(content.encode("utf8")).hexdigest()
    # Write the css file
    css_path = static_path / f"tl_default.{hash}.css"
    app.add_css_file(css_path.name)
    if css_path.exists():
        return
    for path in static_path.glob("*.css"):
        path.unlink()
    css_path.write_text(content, encoding="utf8")


class TimelineDiv(nodes.General, nodes.Element):
    """A div for a timeline."""

    def add_style(self, key, value):
        """Add a style to the div."""
        self.attributes.setdefault("styles", {})
        self["styles"][key] = value


def visit_depart_null(self, node: nodes.Element) -> None:
    """visit/depart passthrough"""


def visit_tl_div(self, node: nodes.Node):
    """visit tl_div"""
    attrs = {}
    if node.get("styles"):
        attrs["style"] = ";".join(
            (f"{key}: {val}" for key, val in node["styles"].items())
        )
    self.body.append(self.starttag(node, "div", CLASS="docutils", **attrs))


def depart_tl_div(self, node: nodes.Node):
    """depart tl_div"""
    self.body.append("</div>\n")


RE_BREAKLINE = re.compile(r"^\s*-{3,}\s*$")


class TimelineDirective(SphinxDirective):
    """A sphinx directive to create timelines."""

    has_content = True
    required_arguments = 0
    optional_arguments = 0
    option_spec = {
        "events": directives.path,
        "template": directives.path,
        "events-format": lambda val: directives.choice(val, ["yaml", "json", "csv"]),
        "max-items": directives.nonnegative_int,
        "reversed": directives.flag,
        "height": directives.length_or_unitless,
        "width-item": directives.length_or_percentage_or_unitless,
        "style": lambda val: directives.choice(val, ["default", "none"]),
        "class": directives.class_option,
        "class-item": directives.class_option,
    }

    def run(self) -> list[nodes.Element]:
        """Run the directive."""
        data: list[dict[str, Any]]
        template_lines: list[str]

        # get data
        if "events" in self.options:
            input_file = self.options["events"]
            # get file path relative to the document
            _, abs_path = self.env.relfn2path(input_file, self.env.docname)
            if not Path(abs_path).exists():
                raise self.error(f"'data' path does not exist: {abs_path}")
            # read file
            with Path(abs_path).open("r", encoding="utf8") as handle:
                try:
                    data = read_events(
                        handle, self.options.get("events-format", "yaml")
                    )
                except Exception as exc:
                    raise self.error(f"Error parsing data: {exc}")
            # add input file to dependencies
            self.env.note_dependency(input_file)

            template_lines = list(self.content)
        else:
            # split lines by first occurrence of line break
            data_lines = []
            template_lines = []
            in_template = False
            for line in self.content:
                if not in_template and RE_BREAKLINE.match(line):
                    in_template = True
                elif in_template:
                    template_lines.append(line)
                else:
                    data_lines.append(line)

                try:
                    data = read_events(
                        StringIO("\n".join(data_lines)),
                        self.options.get("events-format", "yaml"),
                    )
                except Exception as exc:
                    raise self.error(f"Error parsing data: {exc}")

        if "template" in self.options:
            # get template from file
            input_file = self.options["template"]
            # get file path relative to the document
            _, abs_path = self.env.relfn2path(input_file)
            if not Path(abs_path).exists():
                raise self.error(f"'template' path does not exist: {abs_path}")
            # read file
            with Path(abs_path).open() as handle:
                template_lines = handle.readlines()
            # add input file to dependencies
            self.env.note_dependency(input_file)

        # validate data
        if not isinstance(data, list):
            raise self.error("Data must be a list")
        if not data:
            raise self.error("Data must not be empty")

        for idx, item in enumerate(data):
            if not isinstance(item, dict):
                raise self.error(f"item {idx}: each data item must be a dictionary")

            if "start" not in item:
                raise self.error(f"item {idx}: each data item must contain 'start' key")
            try:
                item["start"] = dtime.to_datetime(item["start"])
            except Exception as exc:
                raise self.error(
                    f"item {idx}: error parsing 'start' value: {exc}"
                ) from exc

            if "duration" in item:
                try:
                    item["duration"] = dtime.parse_duration(item["duration"])
                except Exception as exc:
                    raise self.error(
                        f"item {idx}: error parsing 'duration' value: {exc}"
                    ) from exc

        # validate template
        if not [line for line in template_lines if line.strip()]:
            raise self.error("Template cannot be empty")

        env = jinja2.Environment()
        # env.filters["fdtime"] = _format_datetime
        template = env.from_string("\n".join(template_lines))

        container = TimelineDiv()
        if "height" in self.options:
            container.add_style("--tl-height", self.options["height"])
        if "width-item" in self.options:
            container.add_style("--tl-item-width", self.options["width-item"])

        list_node = nodes.enumerated_list(
            classes=[f"timeline-{self.options.get('style', 'default')}"]
            + self.options.get("class", [])
        )
        self.set_source_info(list_node)
        container.append(list_node)

        for idx, item in enumerate(
            sorted(
                data, key=lambda x: x["start"], reverse=("reversed" not in self.options)
            )
        ):
            if self.options.get("max-items") and idx >= self.options["max-items"]:
                break
            rendered = template.render(
                e=item,
                dt=dtime.DtRangeStr(item["start"]),
                duration=dtime.fmt_delta(item.get("duration")),
                dtrange=dtime.DtRangeStr(item["start"], item.get("duration")),
            )
            item_node = nodes.list_item(
                classes=(["timeline"] + self.options.get("class-item", []))
            )
            self.set_source_info(item_node)
            list_node.append(item_node)
            item_container = TimelineDiv(classes=["tl-item"])
            item_content = TimelineDiv(classes=["tl-item-content"])
            item_container.append(item_content)
            # item_container.append(nodes.Text(rendered))
            self.state.nested_parse(
                StringList(rendered.splitlines(), self.state.document.current_source),
                self.content_offset,
                item_content,
            )
            item_node.append(item_container)

        return [container]


def read_events(
    stream: TextIO, fmt: Literal["yaml", "json", "csv"]
) -> list[dict[str, Any]]:
    """Read events from a stream."""
    if fmt == "yaml":
        return yaml.safe_load(stream)
    if fmt == "json":
        return json.load(stream)
    if fmt == "csv":
        return list(csv.DictReader(stream))

    raise ValueError(f"Unknown format: {fmt}")
