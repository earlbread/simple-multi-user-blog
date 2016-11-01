"""Handlers for post list.
"""
from models.post import Post

from handlers.blog import BlogHandler


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

        offset = per_page * (page - 1)
        posts = [l.post for l in likes.fetch(limit=per_page, offset=offset)]

        self.render('likeposts.html', posts=posts, page=page,
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

        offset = per_page * (page - 1)
        posts = my_posts.fetch(limit=per_page, offset=offset)

        self.render('main.html', posts=posts, page=page,
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

        offset = per_page * (page - 1)
        posts = posts_all.fetch(limit=per_page, offset=offset)

        self.render('main.html', posts=posts, page=page,
                    total_page=total_page)
