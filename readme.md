# taozi

![](shot.png)

A simple Flask-based CMS.

`taozi` is currently powering [pinko](https://pinko.online/) and [unbag](https://unbag.net/).

You write `Posts` which are associated with `Issues`, have one or more `Authors` and have associated `Media`. You can also create `Events` that are also linked to `Issues`. `Posts`, `Authors`, and `Issues` also support arbitrary metadata; see below.

In combination with [`konbini`](https://github.com/frnsys/konbini) you can handle print subscriptions (plus other merch) as well.

There is no paywall support.

## Setup

First, setup your project directory, e.g. `my_blog`.

### Installation

Development is still happening sporadically, and this isn't available on `pip` yet, so you'll need to install from git:

    pip install -U git+https://github.com/frnsys/taozi

### Configuration

Create your config file, `my_blog/config.py`, according to the following template:

```
SECRET_KEY = 'something-secret'

SQLALCHEMY_DATABASE_URI = 'sqlite:////home/ftseng/myblog/myblog.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

SECURITY_PASSWORD_HASH = 'bcrypt'
SECURITY_PASSWORD_SALT = 'another-secret'
SECURITY_CHANGEABLE = True
SECURITY_RECOVERABLE = True
SECURITY_EMAIL_SENDER = 'foo@foo.co'

MAIL_SERVER = 'smtp.mailgun.org'
MAIL_USERNAME = 'postmaster@foo.mailgun.org'
MAIL_PASSWORD = 'your-password'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_DEBUG = True
MAIL_DEFAULT_SENDER = 'foo@foo.co'

# Don't forget to create this folder
UPLOAD_FOLDER = '/home/ftseng/myblog/uploads/'
MAX_CONTENT_LENGTH = 10 * 1024 * 1024 # 8MB

# Optional
ISSUE_META = {
    'edition': str,
    'color': str,
    'store_url': str
}

# Optional
AUTHOR_META = {
    'twitter': str,
    'nice': bool
}

# Optional
POST_META = {
    'moon_phase': str
}
```

### Setup your application

Create an app script, `myblog/app.py`, with at least the following:

```python
import config
from taozi import create_app
app = create_app(config, name='myblog')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
```

Here you can add additional Flask extensions, configure Sentry, add your own blueprints, and so on. An example of the latter:

```python
import config
from taozi import create_app
from taozi.models import Post
from flask import Blueprint, render_template

bp = Blueprint('myblog', __name__)
@bp.route('/')
def index():
    posts = Post.filter_by_tag('hello').all()
    return render_template('helloworld.html', posts=posts)

app = create_app(config, name='myblog', blueprints=[bp])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
```

User-supplied blueprints take priority, so you can override default routes.

Setup your own templates and static files in `static` and `templates` (by default).

To access pre-defined routes, use the blueprint name `taozi`, e.g. `url_for('taozi.post', issue=post.issue.slug, slug=post.slug)`.

#### All pre-defined routes

- `taozi.posts`
    - endpoint: `/`
    - template: `posts.html`
    - template data:
        - `posts`: a list of all published and visible/listed posts
- `taozi.issues`
    - endpoint: `/issues`
    - template: `issues.html`
    - template data:
        - `issues`: a list of all published issues
- `taozi.issue(slug)`
    - endpoint: `/<slug>`
    - template: `issue.html`
    - template data:
        - `issue`: the issue matching `slug`
- `taozi.post(issue, slug)`
    - endpoint: `/<issue>/<slug>`
    - template: `post.html`
    - template data:
        - `issue`: the issue matching `issue`
        - `post`: the post matching `slug`
            - the post may have an associated event
- `taozi.events`
    - endpoint: `/events`
    - template: `events.html`
    - template data:
        - `events`: all published and visible/listed events
- `taozi.search`
    - endpoint: `/search`
    - template: `search.html`
    - template data:
        - `query`: the current search query, if any
        - `posts`: posts matching the search query

#### Querying tips

When creating your own routes, you will mostly be querying data to send to your templates.

`taozi` uses `flask-sqlalchemy` so [brush up on how their querying works](https://flask-sqlalchemy.palletsprojects.com/en/2.x/queries/#querying-records).

That being said there are some helper methods to make certain queries easier:

- `Post`
    - `Post.search(query)`: gives posts where any of the title, subtitle, description, body, tags, or authors include the query.
    - `Post.filter_by_tag(tag)`: returns a query object that will filter posts that have the provided tag
        - Since this returns a query object, you have to finish it to actually get results, e.g. `Post.filter_by_tag('foo').all()`
- `Meta`
    - `Meta.get_by_slug(slug)`: returns the meta object for the provided slug, if any
- `Event`
    - `Event.latest()`: returns the latest event in the future, if any

#### Creating arbitrary (non-post) pages

If you want to create standalone pages with content editable by the CMS you can use `Meta` objects.

The basic procedure is as follows:

1. Define your `Meta` content in the admin backend.
    - Let's say we create two, with the slugs `about` and `team`.
2. Create your route:

```python
# ...

@bp.route('/about')
def about():
    about = Meta.get_by_slug('about')
    team = Meta.get_by_slug('team')
    return render_tempalte('about.html', about=about, team=team)

# ...
```

3. Then define your template (e.g. `templates/about.html`):

```jinja
{% extends 'layout.html' %}

{% block content %}
<div id="about">
    <h2>About Us</h2>
    {{ about.html|safe }}

    <h2>Our Team</h2>
    {{ team.html|safe }}
</div>
{% endblock %}
```

### Create an admin

To create the admin role:

    flask roles create admin

To create a user and make them an admin:

    flask users create <EMAIL>
    flask users activate <EMAIL>
    flask roles add <EMAIL> admin

Then login at `/login` and access the admin backend at `/admin`.

### Before your first post

Before your first post you need to do a bit of preparation:

- Create an "Issue"
- Create an "Author"
- Upload an image ("Media")

## Demo

To run a demo application, follow the setup instructions above, then run `python app.py`
