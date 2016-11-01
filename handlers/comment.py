"""Handlers for new, edit and delete comments.
"""
import time

from models.post import Post
from models.comment import Comment

from handlers.blog import BlogHandler

class NewCommentPage(BlogHandler):
    """New comment page handler
    """
    def post(self):
        """Check if content is not empty and register it.

        If content is empty, render post page with error.
        """
        if self.user is None:
            return self.redirect('/blog/login')

        content = self.request.get('content')
        post_id = self.request.get('post_id')

        if post_id:
            try:
                post = Post.get_by_id(int(post_id))
            except ValueError:
                return self.redirect('/blog')

        if content:
            comment = Comment(user=self.user, post=post, content=content)
            comment.put()

            # Delay for DB processing.
            time.sleep(0.1)

            return self.redirect('/blog/%s' % post.key().id())
        else:
            error = 'Comment is needed'
            self.render('permalink.html', post=post, error=error)


class EditCommentPage(BlogHandler):
    """Edit comment page handler.
    """
    def post(self, comment_id):
        """Edit comment. If content is empty, just return.

        If logged out user attempt to access, redirect to login page.

        Args:
            comment_id (str): Comment's id to edit.
        """
        if self.user is None:
            return self.redirect('/blog/login')

        comment = Comment.get_by_id(int(comment_id))

        if not(comment and self.user.key().id() == comment.user.key().id()):
            return self.redirect('/blog')

        content = self.request.get('content-%s' % comment_id)

        if content:
            comment.content = content
            comment.put()

            # Delay for DB processing.
            time.sleep(0.1)

            return self.redirect('/blog/%s' % comment.post.key().id())
        else:
            return self.redirect('/blog/%s' % comment.post.key().id())


class DeleteCommentPage(BlogHandler):
    """Delete comment page handler
    """
    def post(self, comment_id):
        """Delete comment if given post_id exists.

        If logged out user attempt to access, redirect to login page.

        Args:
            comment_id (str): Comment's id to edit.
        """
        if self.user is None:
            return self.redirect('/blog/login')

        comment = Comment.get_by_id(int(comment_id))

        if comment and self.user.key().id() == comment.user.key().id():
            comment.delete()

            # Delay for DB processing.
            time.sleep(0.1)

        return self.redirect('/blog/%s' % comment.post.key().id())
