"""This module models blog post information.
"""
from google.appengine.ext import db
import render
from user import User

class Post(db.Model):
    """DB Model for Post Entity.

    This class models blog post information.

    Attributes:
        user (User): User instance what is owner of the post.
        subject (str): Subject of the post.
        content (text): Content of the post.
        created (datetime): Created time of the post.
    """
    user = db.ReferenceProperty(User, required=True)
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

    def render(self, user):
        """Renders the post itself.

        Args:
            user (User): user instance for rendering post.

        Returns:
            str: Rendered html string.
        """
        return render.render_str('post.html', post=self, user=user)
