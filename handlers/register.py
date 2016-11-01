"""Handler for register user.
"""
import re

from models.user import User
from handlers.blog import BlogHandler

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
