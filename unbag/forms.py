from .models import Issue, Media, Author
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import InputRequired
from wtforms.fields import TextField, TextAreaField, BooleanField, DateTimeField, FormField
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField, QuerySelectField

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


class AuthorForm(FlaskForm):
    name = TextField('Name', [InputRequired()])
    twitter = TextField('Twitter')

class IssueForm(FlaskForm):
    name = TextField('Name', [InputRequired()])
    edition = TextField('Edition')
    color = TextField('Color', [InputRequired()])

class UploadMediaForm(FlaskForm):
    file = FileField('Image', [FileRequired(),
                               FileAllowed(ALLOWED_EXTENSIONS, 'Images only')])
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
    published = BooleanField('Published')
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
    post = FormField(EventPostForm)
