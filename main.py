"""Main module for blog application.
"""
import re
import hmac
import time

import webapp2
from google.appengine.ext import db

from user import User
from post import Post
from comment import Comment
from like import Like
import render

SECRET = 'secret'

def make_secure_val(val):
    """Make hashed value for secure

    Args:
        val (str): Value to make secure.

    Returns:
        str: value with hashed string using secret key seperated by '|'
    """
    return '%s|%s' % (val, hmac.new(SECRET, val).hexdigest())

def check_secure_val(secure_val):
    """Check validity of secure_val

    Args:
        secure_val (str): Secure value for checking

    Returns:
        Return original value if secure_val is valid, None otherwise.
    """
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

class BlogHandler(webapp2.RequestHandler):
    """This class is base handler of blog.

    This class provides fuctions to make blog pages.
    """
    def write(self, *a, **kw):
        """Write to browser using given arguments.

        Write to browser *a if it exists, **kw otherwise.

        Args:
            *a: Arbitrary parameters to render.
            **kw: Arbitrary keyword parameters to render.
        """
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        """Render html using given template and parameters.

        Args:
            template (str): Template name to render.
            **params: Arbitrary parameters to render.

        Returns:
            str: Rendered html string.
        """
        params['user'] = self.user
        return render.render_str(template, **params)

    def render(self, template, **kw):
        """Write to browser rendered string using given template and arguments.

        Args:
            template (str): Template name to render.
            **kw: Arbitrary parameters to render.
        """
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val, remember):
        """Make secure cookie and set it to the browser.

        Args:
            name (str): Cookie name to set.
            val (str): Cookie value to set.
        """
        cookie_val = make_secure_val(val)
        cookie_str = '%s=%s; Path=/;' % (name, cookie_val)

        if remember:
            expires_date = 'expires=Fri, 31 Dec 9999 23:59:59 GMT;'
            cookie_str += expires_date

        self.response.headers.add_header('Set-Cookie', cookie_str)

    def read_secure_cookie(self, name):
        """Read cookie from the browser and check validity.

        Args:
            name (str): Cookie name to read.

        Return:
            Return original cookie value if it is valid, None otherwise.
        """
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user, remember=False):
        """Set 'user_id' cookie to login.

        Args:
            user (User): user instance to login.
        """
        self.set_secure_cookie('user_id', str(user.key().id()), remember)

    def logout(self):
        """Remove cookie to log out.
        """
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        """Set self.user value from 'user_id' cookie if it exists.
        """
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        if uid:
            self.user = User.by_id(int(uid))
        else:
            self.user = None


USERNAME_RE = re.compile(r'^[a-zA-Z ]{3,20}$')
def valid_username(username):
    """Check validity of username.

    Args:
        username (str): Username to register.

    Returns:
        bool: True if username is valid, False otherwise.
    """
    return username and USERNAME_RE.match(username)

PASSWORD_RE = re.compile(r'^.{3,20}$')
def valid_password(password):
    """Check validity of password.

    Args:
        password (str): Password to register.

    Returns:
        bool: True if password is valid, False otherwise.
    """
    return password and PASSWORD_RE.match(password)

EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    """Check validity of email.

    Args:
        email (str): Email to register.

    Returns:
        bool: True if email is valid, False otherwise.
    """
    return not email or EMAIL_RE.match(email)

def validate_userinfo(username, password, confirmation, email):
    """Check validity of user information to register.

    If there is invalid information, set errors to return parameter.

    Args:
        username (str): Username to register.
        password (str): Password to register.
        email (str): Email to register.

    Returns:
        dict: Dict value has username, email and errors if it has.

    """
    params = dict(username=username, email=email)
    has_error = False

    if not valid_username(username):
        has_error = True
        params['error_username'] = "That's not a valid username."
    else:
        user = User.by_name(username)

        if user:
            has_error = True
            params['error_username'] = 'That username already exists.'


    if not valid_email(email):
        has_error = True
        params['error_email'] = "That's not a valid email."
    if not valid_password(password):
        has_error = True
        params['error_password'] = "That's not a valid password"
    elif password != confirmation:
        has_error = True
        params['error_confirmation'] = "Your password didn't match."

    params['has_error'] = has_error

    return params


class RegisterPage(BlogHandler):
    """User registration handler.
    """
    def get(self):
        """Render signup page.
        """
        self.render('signup.html')

    def post(self):
        """Check validtion of user information and register it.

        If registration is successful, login with the user.
        Otherwise, render signup page with errors.
        """
        username = self.request.get('username')
        email = self.request.get('email')
        password = self.request.get('password')
        confirmation = self.request.get('confirmation')

        params = validate_userinfo(username, password, confirmation, email)

        if params['has_error']:
            self.render('signup.html', **params)
        else:
            user = User.register(username, password, email)
            user.put()

            self.login(user)
            return self.redirect('/blog')


class LoginPage(BlogHandler):
    """User login handler.
    """
    def get(self):
        """Render login page
        """
        self.render('login.html')

    def post(self):
        """Check validation of username and password and login with the user.
        """
        username = self.request.get('username')
        password = self.request.get('password')
        remember = self.request.get('remember')

        user = User.login(username, password)

        remember = True if remember else False

        if user:
            self.login(user, remember)
            return self.redirect('/blog')
        else:
            msg = 'Invalid username or password'
            self.render('login.html', error=msg)


class LogoutPage(BlogHandler):
    """User logout handler.
    """
    def get(self):
        """Do logout.
        """
        self.logout()
        return self.redirect('/blog')


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


class LikePage(BlogHandler):
    """ Blog like page handler.
    """
    def post(self, post_id):
        """Like post.

        Args:
            post_id (str): Post's id to like.
        """
        if self.user is None:
            return self.redirect('/blog/login')

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
    def post(self, post_id):
        """Unlike post.

        Args:
            post_id (str): Post's id to unlike.
        """
        if self.user is None:
            return self.redirect('/blog/login')

        post = Post.get_by_id(int(post_id))

        if not(post and self.user.key().id() != post.user.key().id()):
            return self.redirect('/blog')

        like = self.user.likes.filter('post = ', post).get()

        if like:
            like.delete()

            # Delay for DB processing.
            time.sleep(0.1)

        return self.redirect('/blog/%s' % post.key().id())


class PostPage(BlogHandler):
    """Post handler.
    """
    def get(self, post_id):
        """Get post with given post_id and render it.

        Args:
            post_id (str): Post's id to render.
        """
        post = Post.get_by_id(int(post_id))

        if post:
            self.render('permalink.html', post=post)
        else:
            return self.redirect('/blog')



class LikePostListPage(BlogHandler):
    """My post page handler.
    """
    def get(self):
        """Get logged in user posts from DB and render it.
        """
        if self.user is None:
            return self.redirect('/blog/login')

        per_page = 5
        page = self.request.get('page')

        if page:
            page = int(page)
        else:
            page = 1

        likes = self.user.likes
        nr_posts = likes.count()
        total_page = nr_posts / per_page

        if nr_posts % per_page:
            total_page += 1

        posts = [l.post for l in likes.fetch(limit=per_page, offset=page - 1)]

        self.render('postlist.html', posts=posts, page=page,
                    total_page=total_page)


class MyPostListPage(BlogHandler):
    """My post page handler.
    """
    def get(self):
        """Get logged in user posts from DB and render it.
        """
        if self.user is None:
            return self.redirect('/blog/login')

        per_page = 5
        page = self.request.get('page')

        if page:
            page = int(page)
        else:
            page = 1

        post_all = Post.all().order('-created')
        my_posts = post_all.filter('user =', self.user)
        nr_posts = my_posts.count()
        total_page = nr_posts / per_page

        if nr_posts % per_page:
            total_page += 1

        posts = my_posts.fetch(limit=per_page, offset=page - 1)

        self.render('postlist.html', posts=posts, page=page,
                    total_page=total_page)


class MainPage(BlogHandler):
    """Blog main page handler.
    """
    def get(self):
        """Get posts from DB and render it.
        """
        per_page = 5
        page = self.request.get('page')

        if page:
            page = int(page)
        else:
            page = 1

        posts_all = Post.all().order('-created')
        nr_posts = posts_all.count()
        total_page = nr_posts / per_page

        if nr_posts % per_page:
            total_page += 1

        posts = posts_all.fetch(limit=per_page, offset=page - 1)

        self.render('postlist.html', posts=posts, page=page,
                    total_page=total_page)


class PageNotFoundHandler(webapp2.RequestHandler):
    def get(self):
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
