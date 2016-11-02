"""Handlers for like and unlike.
"""

import time

from models.post import Post
from models.like import Like

from handlers.blog import BlogHandler

from helper import login_required

class LikePage(BlogHandler):
    """ Blog like page handler.
    """
    @login_required
    def post(self, post_id):
        """Like post.

        Args:
            post_id (str): Post's id to like.
        """
        post = Post.get_by_id(int(post_id))

        if not(post and self.user.key().id() != post.user.key().id()):
            return self.redirect('/blog')

        if self.user.likes.filter('post = ', post).get():
            return self.redirect('/blog/%s' % post.key().id())

        Like(user=self.user, post=post).put()

        # Delay for DB processing.
        time.sleep(0.1)

        return self.redirect('/blog/%s' % post.key().id())

class UnlikePage(BlogHandler):
    """ Blog unlike page handler.
    """
    @login_required
    def post(self, post_id):
        """Unlike post.

        Args:
            post_id (str): Post's id to unlike.
        """
        post = Post.get_by_id(int(post_id))

        if not(post and self.user.key().id() != post.user.key().id()):
            return self.redirect('/blog')

        like = self.user.likes.filter('post = ', post).get()

        if like:
            like.delete()

            # Delay for DB processing.
            time.sleep(0.1)

        return self.redirect('/blog/%s' % post.key().id())
