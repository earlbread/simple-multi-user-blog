from google.appengine.ext import db

import hashlib
import random
from string import letters

def make_salt(length = 5):
    return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(name, pw, salt = None):
    if salt is None:
        salt = make_salt()

    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)

def check_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)

def users_key(group = 'default'):
    return db.Key.from_path('users', group)

class User(db.Model):
    username = db.StringProperty(required = True)
    email = db.StringProperty()
    password = db.StringProperty(required = True)

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent = users_key())

    @classmethod
    def by_name(cls, name):
        u = User.all().filter('username =', name).get()
        return u

    @classmethod
    def register(cls, name, pw, email):
        pw = make_pw_hash(name, pw)
        return User(parent = users_key(),
                    username = name,
                    password = pw,
                    email = email)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        print u
        if u and check_pw(name, pw, u.password):
            return u
