"""This module models blog comment information in post.
"""
from google.appengine.ext import db
import render
from models.user import User
from models.post import Post

class Comment(db.Model):
    """DB Model for Comment Entity.

    This class models blog post information.

    Attributes:
        user (User): User instance which is owner of the post.
        post (Post): Post instance which is the comment belongs.
        content (text): Content of the comment.
        created (datetime): Created time of the comment.
    """
    user = db.ReferenceProperty(User, collection_name='comments', required=True)
    post = db.ReferenceProperty(Post, collection_name='comments', required=True)
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

        return render.render_str('comment.html', comment=self, user=user)
