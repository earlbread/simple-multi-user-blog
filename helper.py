"""Helper functions.
"""
from functools import wraps

def login_required(function):
    """Decorator function for login required pages.
    """
    @wraps(function)
    def decorated_function(self, *args, **kw):
        """Redirect to main if user is not logged in.
        """
        if self.user is None:
            return self.redirect('/blog/login')
        return function(self, *args, **kw)
    return decorated_function
