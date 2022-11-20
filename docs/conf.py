from datetime import datetime
import os

from sphinx_timeline import __version__

project = "Sphinx Timeline"
author = "Chris Sewell"
copyright = f"{datetime.now().year}, Chris Sewell"
version = __version__

extensions = ["myst_parser", "sphinx_timeline"]

myst_enable_extensions = ["deflist"]

suppress_warnings = ["epub.unknown_project_files"]

# get environment variables
html_theme = os.environ.get("HTML_THEME", "furo")
html_static_path = ["_static"]
html_css_files = ["custom.css"]
