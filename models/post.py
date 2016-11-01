"""This module models blog post information.
"""
from google.appengine.ext import db
import render
from models.user import User

class Post(db.Model):
    """DB Model for Post Entity.

    This class models blog post information.

    Attributes:
        user (User): User instance what is owner of the post.
        subject (str): Subject of the post.
        content (text): Content of the post.
        created (datetime): Created time of the post.
    """
    user = db.ReferenceProperty(User, collection_name='posts', required=True)
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

    def render(self, user):
        """Renders the post itself.

        Args:
            user (User): User instance logged in.

        Returns:
            str: Rendered html string.
        """
        # This is needed to render post properly.
        self._render_text = self.content.replace('\n', '<br>')

        return render.render_str('post.html', post=self, user=user)
