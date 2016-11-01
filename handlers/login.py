"""Handlers for login and logout.
"""
from models.user import User
from handlers.blog import BlogHandler

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
