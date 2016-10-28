"""This module models user information for blog.
"""
import hashlib
import random
from string import letters

from google.appengine.ext import db

def make_salt(length=5):
    """Make salt for hashed password.

    Args:
        length (int): Length of salt.

    Returns:
        str: Random salt string.
    """
    return ''.join(random.choice(letters) for x in xrange(length))

def make_password_hash(username, password, salt=None):
    """Make hashed password.

    If salt is given, use the salt for making hashed password.
    If not, make new random salt.

    Args:
        username
    """
    if salt is None:
        salt = make_salt()

    hashed_password = hashlib.sha256(username + password + salt).hexdigest()
    return '%s,%s' % (salt, hashed_password)

def check_password(username, password, hashed_password):
    """Dummy
    """
    salt = hashed_password.split(',')[0]
    return hashed_password == make_password_hash(username, password, salt)

class User(db.Model):
    """Dummy
    """
    username = db.StringProperty(required=True)
    email = db.StringProperty()
    password = db.StringProperty(required=True)

    @classmethod
    def by_id(cls, uid):
        """Dummy
        """
        return User.get_by_id(uid)

    @classmethod
    def by_name(cls, username):
        """Dummy
        """
        user = User.all().filter('username =', username).get()
        return user

    @classmethod
    def register(cls, username, password, email):
        """Dummy
        """
        password = make_password_hash(username, password)
        return User(username=username,
                    password=password,
                    email=email)

    @classmethod
    def login(cls, username, password):
        """Dummy
        """
        user = cls.by_name(username)
        if user and check_password(username, password, user.password):
            return user
