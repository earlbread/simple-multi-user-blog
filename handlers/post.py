""" Handlers for new, edit and delete post.
"""
import time

from google.appengine.ext import db

from models.post import Post
from models.like import Like

from handlers.blog import BlogHandler

class NewPostPage(BlogHandler):
    """New post page handler.
    """
    def render_front(self, subject='', content='', error=''):
        """Render new post page with given arguments.

        subject (str): Post subject.
        content (str): Post content.
        error (str): Error message to display.
        """
        self.render('newpost.html', subject=subject, content=content,
                    error=error)

    def get(self):
        """Render new post page.

        If logged out user attempt to access, redirect to login page.
        """
        if self.user is None:
            return self.redirect('/blog/login')

        self.render_front()

    def post(self):
        """Check if subject and content are not empty and register it.

        If subject or content is empty, render new post page with error.
        """
        if self.user is None:
            return self.redirect('/blog/login')

        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            post = Post(user=self.user, subject=subject, content=content)

            post.put()

            # Delay for DB processing.
            time.sleep(0.1)

            return self.redirect('/blog/%s' % post.key().id())
        else:
            error = 'Subject and Content are needed'
            self.render_front(subject, content, error)


class EditPostPage(BlogHandler):
    """Edit post page handler.
    """
    def get(self, post_id):
        """Render post page if given post_id exists.

        Otherwise redirect to main.

        Args:
            post_id (str): Post's id.
        """
        if self.user is None:
            return self.redirect('/blog/login')

        post = Post.get_by_id(int(post_id))

        if post and self.user.key().id() == post.user.key().id():
            self.render('editpost.html', subject=post.subject,
                        content=post.content, error='', post=post)
        else:
            return self.redirect('/blog')

    def post(self, post_id):
        """Check if subject and content are not empty and register it.

        If subject or content is empty, render new post page with error.
        If logged out user attempt to access, redirect to login page.

        Args:
            post_id (str): Post's id to edit.
        """
        if self.user is None:
            return self.redirect('/blog/login')

        post = Post.get_by_id(int(post_id))

        if not(post and self.user.key().id() == post.user.key().id()):
            return self.redirect('/blog')

        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            post.subject = subject
            post.content = content
            post.put()

            # Delay for DB processing.
            time.sleep(0.1)

            return self.redirect('/blog/%s' % post.key().id())
        else:
            error = 'Subject and Content are needed'
            self.render('editpost.html', subject=post.subject,
                        content=post.content, error=error, post=post)


        return self.redirect('/blog')


class DeletePostPage(BlogHandler):
    """Delete post page handler
    """
    def post(self, post_id):
        """Delete post if given post_id exists.

        If logged out user attempt to access, redirect to login page.

        Args:
            post_id (str): Post's id to edit.
        """
        if self.user is None:
            return self.redirect('/blog/login')
        post = Post.get_by_id(int(post_id))

        if post and self.user.key().id() == post.user.key().id():
            post.delete()

            db.delete(Like.all().filter('post = ', post))

            # Delay for DB processing.
            time.sleep(0.1)

        return self.redirect('/blog')
