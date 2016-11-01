"""BlogHandler module for every page.
"""
import os
import hmac

import webapp2

import render

from models.user import User

if os.environ.has_key('SECRET'):
    SECRET = os.environ['SECRET']
else:
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
