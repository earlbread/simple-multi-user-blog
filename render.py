"""Render jinja2 template to html.

This module render jinja2 template to html.
"""
import os
import jinja2

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
JINJA_ENV = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
                               autoescape=True)

def render_str(template, **params):
    """Render jinja2 template with parameters to html string.

    Args:
        template (str): Template name to render.
        **params: Arbitrary parameters to render.

    Returns:
        str: Rendered html string.
    """
    jinja_template = JINJA_ENV.get_template(template)
    return jinja_template.render(params)
