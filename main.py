# coding=utf-8

import webapp2
import jinja2

import os


class BlogHandler(webapp2.RequestHandler):
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    jinja_env = jinja2.Environment(
            loader = jinja2.FileSystemLoader(template_dir),
            autoescape = True
            )

    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = self.jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainPage(BlogHandler):
    def get(self):
        self.render('base.html')

app = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)

