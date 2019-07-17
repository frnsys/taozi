import json
import random
from .datastore import db
from flask import url_for
from datetime import datetime
from flask_security import UserMixin, RoleMixin

roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


posts_authors = db.Table('posts_authors',
    db.Column('post_id', db.Integer(), db.ForeignKey('post.id'), nullable=False),
    db.Column('author_id', db.Integer(), db.ForeignKey('author.id'), nullable=False),
                       db.PrimaryKeyConstraint('post_id', 'author_id'))


class Role(db.Model, RoleMixin):
    id          = db.Column(db.Integer(), primary_key=True)
    name        = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    id              = db.Column(db.Integer(), primary_key=True)
    email           = db.Column(db.String(255), unique=True)
    active          = db.Column(db.Boolean())
    confirmed_at    = db.Column(db.DateTime())
    created_at      = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_at      = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)
    password        = db.Column(db.String(255))
    roles           = db.relationship('Role', secondary=roles_users,
                                      backref=db.backref('users', lazy='dynamic'))


class HasMeta:
    def set_meta(self, data):
        self.meta = json.dumps(data)

    def get_meta(self):
        return json.loads(self.meta) if self.meta else {}

    def set_meta_from_form(self, form):
        cols = self.__table__.columns.keys()
        meta = self.get_meta()
        for field in form:
            if field.name not in cols and field.name is not 'csrf_token':
                meta[field.name] = field.data
        self.set_meta(meta)


class Post(db.Model, HasMeta):
    __mapper_args__         = {
        'order_by': db.text('created_at DESC')
    }
    __table_args__          = (
        db.UniqueConstraint('slug', 'issue_id', name='_slug_issue_uc'),
    )
    id                      = db.Column(db.Integer(), primary_key=True)
    slug                    = db.Column(db.Unicode())
    body                    = db.Column(db.Unicode())
    desc                    = db.Column(db.Unicode())
    html                    = db.Column(db.Unicode())
    title                   = db.Column(db.Unicode())
    subtitle                = db.Column(db.Unicode())
    tags                    = db.Column(db.Unicode())
    published               = db.Column(db.Boolean(), default=False)
    print_only              = db.Column(db.Boolean(), default=False)
    created_at              = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_at              = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at            = db.Column(db.DateTime(), default=datetime.utcnow)
    authors                 = db.relationship('Author',
                                              secondary=posts_authors,
                                              backref='posts')

    image_id                = db.Column(db.Integer, db.ForeignKey('media.id'))
    image                   = db.relationship('Media',
                                              uselist=False,
                                              backref=db.backref('posts',
                                                                 lazy='dynamic',
                                                                 order_by='desc(Post.created_at)'))

    event_id                = db.Column(db.Integer, db.ForeignKey('event.id'))
    event                   = db.relationship('Event', uselist=False, back_populates='post')

    issue_id                = db.Column(db.Integer, db.ForeignKey('issue.id'))
    issue                   = db.relationship('Issue',
                                              uselist=False,
                                              backref=db.backref('posts',
                                                                 lazy='dynamic',
                                                                 order_by='desc(Post.created_at)'))

    @property
    def byline(self):
        if not self.authors:
            return 'Anonymous'
        return ', '.join(a.name for a in self.authors)

    @property
    def tags_list(self):
        return [t.lower().strip() for t in self.tags.split(',')]

    @staticmethod
    def latest_event():
        now = datetime.utcnow()
        query = Post.query.join(Event)\
            .filter(Post.published==True, Post.event!=None)
        latest = query.filter(Post.event.has(Event.end >= now))\
            .order_by(Event.start.asc()).first()

        # Fallback to most recent event
        if latest is None:
            latest = query.order_by(Event.start.desc()).first()
        return latest


class Media(db.Model):
    __mapper_args__         = {
        'order_by': db.text('created_at DESC')
    }
    id                      = db.Column(db.Integer(), primary_key=True)
    desc                    = db.Column(db.Unicode())
    filename                = db.Column(db.Unicode(), unique=True)
    created_at              = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_at              = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)
    width                   = db.Column(db.Integer())
    height                  = db.Column(db.Integer())

    @property
    def path(self):
        return url_for('front.uploads', filename=self.filename)


class Author(db.Model, HasMeta):
    id                      = db.Column(db.Integer(), primary_key=True)
    slug                    = db.Column(db.Unicode(), unique=True)
    name                    = db.Column(db.Unicode())
    meta                    = db.Column(db.Unicode())


class Issue(db.Model, HasMeta):
    id                      = db.Column(db.Integer(), primary_key=True)
    name                    = db.Column(db.Unicode())
    slug                    = db.Column(db.Unicode(), unique=True)
    meta                    = db.Column(db.Unicode())
    published               = db.Column(db.Boolean, default=False)

    def __repr__(self):
        if self.edition:
            return '{} — {}'.format(self.name, self.edition)
        return self.name

    @property
    def published_posts(self):
        posts = [p for p in self.posts if p.published and p.event is None]
        random.shuffle(posts)
        return posts

    @property
    def published_events(self):
        posts = [p for p in self.posts if p.published and p.event is not None]
        return posts


class Event(db.Model):
    id                      = db.Column(db.Integer(), primary_key=True)
    start                   = db.Column(db.DateTime())
    end                     = db.Column(db.DateTime())
    post                    = db.relationship('Post', uselist=False, back_populates='event')
    ignore_time             = db.Column(db.Boolean(), default=False)

    def __repr__(self):
        if self.ignore_time:
            dtfmt = '%B %-d, %Y'
            suffix = ''
        else:
            dtfmt = '%B %-d, %Y %-I:%M'
            suffix = ' %p'
        if not self.end:
            return self.start.strftime(dtfmt + suffix)
        else:
            if self.start.date() == self.end.date():
                start = self.start.strftime(dtfmt)
                if self.ignore_time:
                    return start
                else:
                    return '{}-{}'.format(start, self.end.strftime('%-I:%M %p'))
            else:
                start = self.start.strftime(dtfmt + suffix)
                return '{} - {}'.format(start, self.end.strftime(dtfmt + suffix))
