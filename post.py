from google.appengine.ext import db
import render
from user import User

class Post(db.Model):
    user = db.ReferenceProperty(User, required = True)
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

    def render(self):
        return render.render_str('post.html', post=self)
