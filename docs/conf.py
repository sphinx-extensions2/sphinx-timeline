from sphinx_subfigure import __version__

project = "Sphinx Subfigures"
author = "Chris Sewell"
copyright = "2022, Chris Sewell"
version = __version__

extensions = ["myst_parser", "sphinx_subfigure"]

myst_enable_extensions = ["colon_fence"]
numfig = True

suppress_warnings = ["epub.unknown_project_files"]

html_theme = "furo"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
