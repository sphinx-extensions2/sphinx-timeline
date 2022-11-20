# sphinx-timeline

[![PyPI][pypi-badge]][pypi-link]

A [sphinx](https://www.sphinx-doc.org) extension to create timelines.

## Usage

Install `sphinx-timeline` with `pip install sphinx-timeline`,
then add `sphinx_timeline` to your `conf.py` file's `extensions` variable:

```python
extensions = ["sphinx_timeline"]

numfig = True  # optional
```

Now add a `timeline` directive to your document:

```restructuredtext
.. timeline::
   - start: 1980-02-03
     name: 1st event
   - start: 1990-02-03
     name: 2nd event
   - start: 2000-02-03
     name: 3rd event
   ---
   **{{e.start|fdtime}}**:
   *{{e.name}}*

   Description ...
```

[pypi-badge]: https://img.shields.io/pypi/v/sphinx_timeline.svg
[pypi-link]: https://pypi.org/project/sphinx_timeline
