import os

import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Entry(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class EntryPage(BlogHandler):
    def get(self, page_id):
        entry = Entry.get_by_id(int(page_id))

        if entry:
            self.render("main.html", entries=[entry])
        else:
            self.redirect("/blog")

class NewPostPage(BlogHandler):
    def render_front(self, subject="", content="", error=""):
        self.render('newpost.html', subject=subject, content=content,
                    error=error)

    def get(self):
        self.render_front()

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            b = Entry(subject=subject, content=content)
            bput = b.put()
            self.redirect("/blog/%s" % bput.id())
        else:
            error = "subject and content are needed"
            self.render_front(subject, content, error)

class MainPage(BlogHandler):
    def get(self):
        entries = db.GqlQuery('SELECT * FROM Entry ORDER BY created DESC')
        self.render('main.html', entries = entries)

app = webapp2.WSGIApplication([
    ('/blog', MainPage),
    ('/blog/(\d+)', EntryPage),
    ('/blog/newpost', NewPostPage),
], debug=True)

