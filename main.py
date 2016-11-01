"""Main module for blog application.
"""
import webapp2

from handlers.register import RegisterPage
from handlers.login import LoginPage, LogoutPage
from handlers.post import NewPostPage, EditPostPage, DeletePostPage
from handlers.comment import NewCommentPage, EditCommentPage, DeleteCommentPage
from handlers.like import LikePage, UnlikePage
from handlers.postlist import PostPage
from handlers.postlist import LikePostListPage
from handlers.postlist import MyPostListPage
from handlers.postlist import MainPage

class PageNotFoundHandler(webapp2.RequestHandler):
    """ Handler for 404 error
    """
    def get(self):
        """ Redirect to main page if a page doesn't exist.
        """
        self.redirect('/blog')

app = webapp2.WSGIApplication([
    ('/blog/signup/?', RegisterPage),
    ('/blog/login/?', LoginPage),
    ('/blog/logout/?', LogoutPage),
    ('/blog/new_post/?', NewPostPage),
    ('/blog/edit_post/(\d+)/?', EditPostPage),
    ('/blog/delete_post/(\d+)/?', DeletePostPage),
    ('/blog/new_comment/?', NewCommentPage),
    ('/blog/edit_comment/(\d+)/?', EditCommentPage),
    ('/blog/delete_comment/(\d+)/?', DeleteCommentPage),
    ('/blog/like/(\d+)/?', LikePage),
    ('/blog/unlike/(\d+)/?', UnlikePage),
    ('/blog/(\d+)/?', PostPage),
    ('/blog/like_post/?', LikePostListPage),
    ('/blog/my_post/?', MyPostListPage),
    ('/blog/?', MainPage),
    ('/.*', PageNotFoundHandler),
], debug=True)
