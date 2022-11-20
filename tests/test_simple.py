import json
from pathlib import Path

# from bs4 import BeautifulSoup
import pytest
from sphinx_pytest.plugin import CreateDoctree
import yaml

FIXTURE_PATH = Path(__file__).parent.joinpath("fixtures")


@pytest.mark.param_file(FIXTURE_PATH / "posttransform_html.txt")
def test_posttransform_html(file_params, sphinx_doctree: CreateDoctree):
    """Test AST output after post-transforms, when using the HTML builder."""
    sphinx_doctree.set_conf({"extensions": ["sphinx_timeline"]})
    sphinx_doctree.buildername = "html"
    example_data = [{"start": "2021-02-03", "name": "1st draft"}]
    sphinx_doctree.srcdir.joinpath("data.yaml").write_text(yaml.dump(example_data))
    sphinx_doctree.srcdir.joinpath("data.json").write_text(json.dumps(example_data))
    sphinx_doctree.srcdir.joinpath("template.txt").write_text(
        "{{dtrange}} - {{e.name}}"
    )
    result = sphinx_doctree(file_params.content)
    assert not result.warnings
    file_params.assert_expected(result.get_resolved_pformat(), rstrip_lines=True)


# @pytest.mark.param_file(FIXTURE_PATH / "build_html.txt")
# def test_doctree(file_params, sphinx_doctree: CreateDoctree):
#     """Test HTML build output."""
#     sphinx_doctree.set_conf({"extensions": ["sphinx_timeline"]})
#     sphinx_doctree.buildername = "html"
#     result = sphinx_doctree(file_params.content)
#     assert not result.warnings
#     html = BeautifulSoup(
#         Path(result.builder.outdir).joinpath("index.html").read_text(), "html.parser"
#     )
#     fig_html = str(html.select_one("figure.sphinx-subfigure"))
#     file_params.assert_expected(fig_html, rstrip_lines=True)
