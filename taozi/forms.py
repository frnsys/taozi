from flask import current_app
from .models import Issue, Media, Author
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.fields.html5 import URLField
from wtforms.validators import InputRequired
from wtforms.fields import TextField, TextAreaField, BooleanField, DateTimeField, FormField
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField, QuerySelectField

ALLOWED_EXTENSIONS = set(Media.extensions)


class AuthorForm(FlaskForm):
    name = TextField('Name', [InputRequired()])

class IssueForm(FlaskForm):
    name = TextField('Name', [InputRequired()])
    published = BooleanField('Published')

class UploadMediaForm(FlaskForm):
    file = FileField('File', [
        FileRequired(),
        FileAllowed(ALLOWED_EXTENSIONS,
            'Supported filetypes: {}'.format(','.join(ALLOWED_EXTENSIONS)))])
    desc = TextField('Description')

class MediaForm(FlaskForm):
    desc = TextField('Description', [InputRequired()])

class PostForm(FlaskForm):
    slug = TextField('Slug')
    title = TextField('Title', [InputRequired()])
    subtitle = TextField('Subtitle')
    desc = TextField('Description', [InputRequired()])
    body = TextAreaField('Body')
    tags = TextField('Tags')
    redirect = URLField('Redirect URL')
    published = BooleanField('Published')
    published_at = DateTimeField('Published At', [InputRequired()], format='%Y-%m-%d %H:%M')
    print_only = BooleanField('Print Only')
    authors = QuerySelectMultipleField('Authors', query_factory=lambda: Author.query.all(),
                                       get_label='name')
    issue = QuerySelectField('Issue', query_factory=lambda: Issue.query.all(),
                             get_label='name')
    image = QuerySelectField('Image', query_factory=lambda: Media.query.all(),
                             get_label='desc')


class EventPostForm(FlaskForm):
    title = TextField('Title', [InputRequired()])
    slug = TextField('Slug')
    desc = TextField('Description', [InputRequired()])
    body = TextAreaField('Body', [InputRequired()])
    tags = TextField('Tags')
    published = BooleanField('Published')
    issue = QuerySelectField('Issue', query_factory=lambda: Issue.query.all(),
                             get_label='name')
    image = QuerySelectField('Image', query_factory=lambda: Media.query.all(),
                             get_label='desc')


class EventForm(FlaskForm):
    start = DateTimeField('Start', [InputRequired()], format='%Y-%m-%d %H:%M')
    end = DateTimeField('End', format='%Y-%m-%d %H:%M')
    ignore_time = BooleanField('Ignore time')
    post = FormField(EventPostForm)


class MetaForm(FlaskForm):
    slug = TextField('Slug', [InputRequired()])
    text = TextAreaField('Text', [InputRequired()])


def append_fields(form_cls, spec):
    for name, typ in spec.items():
        if typ == str:
            field = TextField(name.title())
        elif typ == bool:
            field = BooleanField(name.title())
        setattr(form_cls, name, field)

