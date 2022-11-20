# sphinx-timeline

A [sphinx](https://www.sphinx-doc.org) extension to create timelines.

A scrolling horizontal timeline is created for HTML output, and other formats degrade gracefully to a simple ordered list.

```{timeline}
:height: 350px

- start: 1980-02-03
  name: 1st event
- start: 1990-02-03
  name: 2nd event
- start: 2000-02-03
  name: 3rd event
- start: 2010-02-03
  name: 4th event
- start: 2020-02-04
  name: 5th event
- start: 2021-02-04
  name: 6th event
---
**{{dtrange}}**

*{{e.name}}*

Description ...
```

## Quick-start

Install `sphinx-timeline` with `pip install sphinx-timeline`,
then add `sphinx_timeline` to your `conf.py` file's `extensions` variable:

```python
extensions = ["sphinx_timeline"]
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
   **{{dtrange}}**

   *{{e.name}}*

   Description ...
```

## Usage

A timeline contains two critical pieces:

1. A list of events (in the form of a YAML list, JSON list, or CSV).

   - Each event must have at least `start` key, in [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) date(time) format, which can also have a suffix [time zone](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) in parenthesise, e.g. `2020-02-03 12:34:56 (europe/zurich)`.
   - Each event can have an optional `duration` key, to specify the delta from the `start`.
     This is in the format e.g. `30 minutes 4 hours 1 day 2 months 3 years`.
     All units are optional and can be in any order, e.g. `4 hours 30 minutes` is the same as `30 minutes 4 hours 0 day 0 months 0 years`.

2. A template for the event items content (in the form of a [Jinja2](https://jinja.palletsprojects.com) template)

Each can be supplied *via* an external file, or directly in the directive content.
If both are in the directive content, then they are split by a line with `---`.

For example, to use external files:

```restructuredtext
.. timeline::
   :events: events.yaml
   :template: template.txt
```

## Jinja templates

The template is a [Jinja2](https://jinja.palletsprojects.com) template, which is rendered for each event.
The event dictionary is available as the `e` variable, and the following additional variables are available:

**dtrange**
: The event's `start` and `duration` formatted as a date range, e.g. `Wed 3rd Feb 2021, 10:00 PM - 11:01 PM (UTC)`.
  If the event has no `duration`, then only the `start` is used.
  This can also be parsed arguments to control the formatting

  ```restructuredtext
  .. timeline::
      :style: none

      - start: 2022-02-03 22:00
      - start: 2021-02-03 22:00
        duration: 1 hour 30 minutes
      - start: 2020-02-03
        duration: 1 day
      ---
      - {{dtrange}}
      - {{dtrange(day_name=False)}}
      - {{dtrange(short_date=True)}}
      - {{dtrange(clock12=True)}}
      - {{dtrange(abbr=False)}}
  ```

  ```{timeline}
  :style: none

  - start: 2022-02-03 22:00
  - start: 2021-02-03 22:00 (europe/zurich)
    duration: 1 hour 30 minutes
  - start: 2020-02-03
    duration: 1 day
  ---
  - {{dtrange}}
  - {{dtrange(day_name=False)}}
  - {{dtrange(short_date=True, short_delim="/")}}
  - {{dtrange(clock12=True)}}
  - {{dtrange(abbr=False)}}
  ```

**dt**
: The same as `dtrange`, but `duration` is not included.

## Directive options

events
: Path to the timeline data file, otherwise the data is read from the content.

events-format
: The format of the events. Can be `json`, `yaml`, or `csv`. Defaults to `yaml`.

template
: Path to the template file, otherwise the template is read from the content.

max-items
: The maximum number of items to show. Defaults to all.

reversed
: Whether to reverse the order of the item sorting.

style
: The style of the timeline. Can be `default` or `none`.

height
: The height of the timeline (for default style). Defaults to `300px`.

width-item
: The width of each item (for default style). Defaults to `280px`.

class
: Classes to add to the timeline list.

class-item
: Classes to add to each item.

## CSS Variables

The following CSS variables can be used to customize the appearance of the timeline:

```css
:root {
    --tl-height: 300px;
    --tl-item-outline-color: black;
    --tl-item-outline-width: 1px;
    --tl-item-border-radius: 10px;
    --tl-item-padding: 15px;
    --tl-item-width: 280px;
    --tl-item-gap-x: 8px;
    --tl-item-gap-y: 16px;
    --tl-item-tail-height: 10px;
    --tl-item-tail-color: #383838;
    --tl-item-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);
    --tl-line-color: #686868;
    --tl-line-width: 3px;
    --tl-dot-color: black;
    --tl-dot-diameter: 12px;
}
```

For example, for [furo](https://github.com/pradyunsg/furo) and [pydata-sphinx-theme](https://github.com/pydata/pydata-sphinx-theme), which have dark/light themes, you can add the following to your `conf.py`:

```python
html_static_path = ["_static"]
html_css_files = ["custom.css"]
```

Then create the CSS `_static/custom.css`:

```css
body[data-theme="dark"] {
    --tl-dot-color: #9a9a9a;
    --tl-item-outline-color: #383838;
    --tl-item-tail-color: #747474;
    --tl-item-shadow: 0 4px 8px 0 rgba(100, 100, 100, 0.2), 0 6px 10px 0 rgba(100, 100, 100, 0.19);
}

@media (prefers-color-scheme: dark) {
    body:not([data-theme="light"]) {
        --tl-dot-color: #9a9a9a;
        --tl-item-outline-color: #383838;
        --tl-item-tail-color: #747474;
        --tl-item-shadow: 0 4px 8px 0 rgba(100, 100, 100, 0.2), 0 6px 10px 0 rgba(100, 100, 100, 0.19);
    }
}
```
