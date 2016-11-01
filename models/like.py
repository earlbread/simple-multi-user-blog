"""This module models blog like post information.
"""
from google.appengine.ext import db
from models.user import User
from models.post import Post

class Like(db.Model):
    """DB Model for Like Entity.

    This class models like post information.

    Attributes:
        user (User): User instance which is owner of the post.
        post (Post): Post instance which is the comment belongs.
    """
    user = db.ReferenceProperty(User, collection_name='likes', required=True)
    post = db.ReferenceProperty(Post, collection_name='liked_by', required=True)
