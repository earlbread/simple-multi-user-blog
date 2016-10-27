import re
import hmac
import time

import webapp2

from user import User
from post import Post
import render

secret = 'secret'

def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        return render.render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
                'Set-Cookie',
                '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        if uid:
            self.user = User.by_id(int(uid))
        else:
            self.user = None

USERNAME_RE = re.compile(r'^[a-zA-Z ]{3,20}$')
def valid_username(username):
    return username and USERNAME_RE.match(username)

PASSWORD_RE = re.compile(r'^.{3,20}$')
def valid_password(password):
    return password and PASSWORD_RE.match(password)

EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)

def validate_userinfo(username, password, confirmation, email):
    params = dict(username = username, email = email)
    has_error = False

    if not valid_username(username):
        has_error = True
        params['error_username'] = "That's not a valid username."
    else:
        u = User.by_name(username)

        if u:
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


class SignupPage(BlogHandler):
    def get(self):
        self.render('signup.html')

    def post(self):
        username = self.request.get('username')
        email = self.request.get('email')
        password = self.request.get('password')
        confirmation = self.request.get('confirmation')

        params = validate_userinfo(username, password, confirmation, email)

        if params['has_error']:
            self.render('signup.html', **params)
        else:
            u = User.register(username, password, email)
            u.put()

            self.login(u)
            self.redirect('/blog')


class Login(BlogHandler):
    def get(self):
        self.render('login.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        u = User.login(username, password)

        if u:
            self.login(u)
            self.redirect('/blog')
        else:
            msg = 'Invalid username or password'
            self.render('login.html', error = msg)

class Logout(BlogHandler):
    def get(self):
        self.logout()
        self.redirect('/blog')

class PostPage(BlogHandler):
    def get(self, post_id):
        post = Post.get_by_id(int(post_id))

        if post:
            self.render('permalink.html', post=post)
        else:
            self.redirect('/blog')

class AboutPage(BlogHandler):
    def get(self):
        self.render('about.html')

class NewPostPage(BlogHandler):
    def render_front(self, subject='', content='', error=''):
        self.render('newpost.html', subject=subject, content=content,
                    error=error)

    def get(self):
        if self.user is None:
            self.redirect('/blog/login')

        self.render_front()

    def post(self):
        if self.user is None:
            self.redirect('/blog/login')

        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            b = Post(user = self.user, subject=subject, content=content)
            bput = b.put()
            self.redirect('/blog/%s' % bput.id())
        else:
            error = 'Subject and Content are needed'
            self.render_front(subject, content, error)

class DeletePostPage(BlogHandler):
    def post(self, post_id):
        if self.user is None:
            self.redirect('/blog/login')
        post = Post.get_by_id(int(post_id))

        if post:
            post.delete()
            time.sleep(0.1)

        self.redirect('/blog')

class MainPage(BlogHandler):
    def get(self):
        per_page = 5
        page = self.request.get('page')

        if page:
            page = int(page)
        else:
            page = 1

        posts = Post.all().order('-created')
        nr_posts = posts.count()
        total_page = nr_posts / per_page

        if nr_posts % per_page:
            total_page += 1

        posts = posts.fetch(limit = per_page, offset = page - 1)

        self.render('main.html', posts = posts, page = page,
                total_page = total_page)

app = webapp2.WSGIApplication([
    ('/blog', MainPage),
    ('/blog/(\d+)', PostPage),
    ('/blog/about', AboutPage),
    ('/blog/newpost', NewPostPage),
    ('/blog/delete_post/(\d+)', DeletePostPage),
    ('/blog/signup', SignupPage),
    ('/blog/login', Login),
    ('/blog/logout', Logout),
], debug=True)

