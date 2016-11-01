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
        username (str): User's name.
        password (str): User's password.
        salt (str): The salt of password already hashed.

    Returns:
        str: Salt with hashed password seperated by comma.
    """
    if salt is None:
        salt = make_salt()

    hashed_password = hashlib.sha256(username + password + salt).hexdigest()
    return '%s,%s' % (salt, hashed_password)

def check_password(username, password, hashed_password):
    """Check if it's the same password with hashed_password.

    Args:
        username (str): User's name for checking.
        password (str): User's password for checking.
        hashed_password (str): Hashed password stored in database.

    Returns:
        bool: True if password correct, False otherwise.
    """
    salt = hashed_password.split(',')[0]
    return hashed_password == make_password_hash(username, password, salt)

class User(db.Model):
    """DB model for User Entity.

    This class models blog's user information.

    Attributes:
        username (str): User's name.
        password (str): User's password.
        email (str): User's email address.
    """
    username = db.StringProperty(required=True)
    password = db.StringProperty(required=True)
    email = db.StringProperty()

    @classmethod
    def by_id(cls, uid):
        """Find user by id and return User instance.

        Args:
            uid (int): User's id for finding.

        Returns:
            User instance if it exists, None otherwise.
        """
        return User.get_by_id(uid)

    @classmethod
    def by_name(cls, username):
        """Find user by name and return User instance.

        Args:
            username (str): User's name for finding.

        Returns:
            User instance if it exists, None otherwise.
        """
        user = User.all().filter('username =', username).get()
        return user

    @classmethod
    def register(cls, username, password, email):
        """Make hashed password and User instance using given information.

        Args:
            username (str): User's name.
            password (str): User's password.
            email (str): User's email address.

        Returns:
            User instance.
        """
        password = make_password_hash(username, password)
        return User(username=username,
                    password=password,
                    email=email)

    @classmethod
    def login(cls, username, password):
        """Find user by name and return it if password is correct.

        Args:
            username (str): User name for logging in.
            password (str): Password for logging in.

        Retruns:
            User instance if login is successful, None otherwise.
        """
        user = cls.by_name(username)
        if user and check_password(username, password, user.password):
            return user
