import base64
from pathlib import Path
import re

from bs4 import BeautifulSoup
import pytest
from sphinx_pytest.plugin import CreateDoctree

IMAGE_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAHQAAAB0CAYAAABUmhYnAAAEd0lEQVR4Xu2c0ZLjIAwEk///6GzVvZlspWtWksNRnVcwiGmNwHaS5+v1ej38HKPAU6DHsPy3EIGexVOgh/EUqEBPU+Cw9biHCvQwBQ5bjg4V6GEKHLYcHSrQwxQ4bDk6VKCHKXDYcnSoQA9T4LDllB36fD5vlWR9fUvz0+ve9fp0/O7FU7w0n0CXhBSoDiXTRO06FBKKBLLkLvlGgkTp+UvndPzu/ul46Xq7x2/fQ8kR0wtOBaL+1J6uZ+3fPb5Aw0PRtxOWEkigAr3mCJUMuk9cM45uG3ZvJwel8dN4byW8+r1cgWYPVgRaLIlpwqWCT1cgHbr8skOgYUqkgtHwVYfQKZTiTW8rdCgQFWjtt2Pjty3TGdztOB0aHlosuVcHpglJ+h3nUFow7bE6dDOHCjRN2fBty917qEAF+jEHaI+bTlhK0Nsf/aUBpXtYdXy6noDS9dTePf74oYgWRO3dC6b57k6o7vUJFAh3Cz6dMAIV6FWB9FCQlry1f/ejQXLgt9eX6tXu0DSAtL9APysm0OYHI2mCUgVKxxOoQNOcubc/7XnF5yj3LuYPs5Ud+oc5Ry8R6GEpK1CBjlaMuwcvl1xyBC2I8im9T0xva6pPbtL1V+MjPQW6KEQJRAlAggs0vK2oCibQ4g9+LbnXb96THlQBvl5y0yclqYNQAKgAVGIJQHWPpfjf4uv+bUsagECvClCCkL46VIdecyQtKZRhlKGW3OG3LekeQ0DSBOk+1VLCdbdTAqfzlUuuQFPJe/fM9kORQAV6UYBKJslF11NJS0s8xZO2U3zpeO0lNw2g2+HV8dLbKJov1aMKWKDFfyITKKRsegqmjE7H06FpTRHoRwUoQUnu9pJLh4z0EFMdjwRI46ESWwVC8VK7QMN/TRHookDqCB1Knry261AdmmXMdG86xabzd49H83fP1+5QWkB3e7sg4eu06nra46++4K4uqHp9uyACrSKpXS/Q5kMRnUJruN6vnr7Po/VMn9KrepX3UBKgGmD1UVw6P61HoKmi0F+HfhZIhy766NDhU2F66CEgzQXjQRUjjb8aX7tDaYFpwKkgAi0SSAUXaO0Pjkk/HUoKFQ9p0wm/hjcONC2B6W3B24KKv1ZLx0vzgfQoFsyHQJe3LQINHUEZrUNre6wO1aHLw+AvO5QOHdReLbE0/vSeedyhKBWUDh00XpoAAg2/EkIAqD0FlPYXqEDp3Pix/b8/FKUOIMem7fR6j8Yr0fvlYoEWK4JAw0dplOE6dLnrqH5JrCp4NcMFejPQ6h7RnTAUT/eTKkpYiidtH99D04C6bwvS+QX65W8sUMkVaKgAlcRwuLfuNL5Ah/fQKkC6Pi2JKXB6NEjxUTslKF1P7e17KE1YbRfoZwUFuuijQ4v/l5s6VocOOzQFYv9ZBcoldzY8R08VEGiq2Ob9Bbo5oDQ8gaaKbd5foJsDSsMTaKrY5v0FujmgNDyBpopt3l+gmwNKwxNoqtjm/QW6OaA0PIGmim3eX6CbA0rDE2iq2Ob9Bbo5oDS8H8eCMw7yCzx+AAAAAElFTkSuQmCC"  # noqa: E501
)

FIXTURE_PATH = Path(__file__).parent.joinpath("fixtures")


@pytest.mark.param_file(FIXTURE_PATH / "posttransform_html.txt")
def test_posttransform_html(file_params, sphinx_doctree: CreateDoctree):
    """Test AST output after post-transforms, when using the HTML builder."""
    sphinx_doctree.set_conf({"extensions": ["sphinx_subfigure"]})
    sphinx_doctree.buildername = "html"
    sphinx_doctree.srcdir.joinpath("image.png").write_bytes(IMAGE_PNG)
    result = sphinx_doctree(file_params.content)
    assert not result.warnings
    file_params.assert_expected(result.get_resolved_pformat(), rstrip_lines=True)


@pytest.mark.param_file(FIXTURE_PATH / "build_html.txt")
def test_build_html(file_params, sphinx_doctree: CreateDoctree):
    """Test HTML build output."""
    sphinx_doctree.set_conf({"extensions": ["sphinx_subfigure"]})
    sphinx_doctree.buildername = "html"
    sphinx_doctree.srcdir.joinpath("image.png").write_bytes(IMAGE_PNG)
    result = sphinx_doctree(file_params.content)
    assert not result.warnings
    html = BeautifulSoup(
        Path(result.builder.outdir).joinpath("index.html").read_text(), "html.parser"
    )
    fig_html = str(html.select_one("figure.sphinx-subfigure"))
    file_params.assert_expected(fig_html, rstrip_lines=True)


@pytest.mark.param_file(FIXTURE_PATH / "posttransform_latex.txt")
def test_posttransform_latex(file_params, sphinx_doctree: CreateDoctree):
    """Test AST output after post-transforms, when using the LaTeX builder."""
    sphinx_doctree.set_conf({"extensions": ["sphinx_subfigure"]})
    sphinx_doctree.buildername = "latex"
    sphinx_doctree.srcdir.joinpath("image.png").write_bytes(IMAGE_PNG)
    result = sphinx_doctree(file_params.content)
    assert not result.warnings
    file_params.assert_expected(result.get_resolved_pformat(), rstrip_lines=True)


@pytest.mark.param_file(FIXTURE_PATH / "build_latex.txt")
def test_build_latex(file_params, sphinx_doctree: CreateDoctree):
    """Test LaTeX build output."""
    sphinx_doctree.set_conf({"extensions": ["sphinx_subfigure"]})
    sphinx_doctree.buildername = "latex"
    sphinx_doctree.srcdir.joinpath("image.png").write_bytes(IMAGE_PNG)
    result = sphinx_doctree(file_params.content)
    assert not result.warnings
    tex = Path(result.builder.outdir).joinpath("python.tex").read_text()
    fig_tex = re.findall(r"\\begin\{figure\}.*\\end\{figure\}", tex, re.DOTALL)[0]
    file_params.assert_expected(fig_tex, rstrip_lines=True)


@pytest.mark.param_file(FIXTURE_PATH / "posttransform_man.txt")
def test_posttransform_man(file_params, sphinx_doctree: CreateDoctree):
    """Test AST output after post-transforms, when using the Man builder."""
    sphinx_doctree.set_conf({"extensions": ["sphinx_subfigure"]})
    sphinx_doctree.buildername = "man"
    sphinx_doctree.srcdir.joinpath("image.png").write_bytes(IMAGE_PNG)
    result = sphinx_doctree(file_params.content)
    assert not result.warnings
    file_params.assert_expected(result.get_resolved_pformat(), rstrip_lines=True)


@pytest.mark.param_file(FIXTURE_PATH / "build_html.txt")
def test_build_man(file_params, sphinx_doctree: CreateDoctree):
    """Test Man build."""
    sphinx_doctree.set_conf({"extensions": ["sphinx_subfigure"]})
    sphinx_doctree.buildername = "man"
    sphinx_doctree.srcdir.joinpath("image.png").write_bytes(IMAGE_PNG)
    result = sphinx_doctree(file_params.content)
    assert not result.warnings
