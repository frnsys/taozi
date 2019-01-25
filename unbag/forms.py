from .models import Author
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import InputRequired
from wtforms.fields import TextField, TextAreaField, BooleanField
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


class AuthorForm(FlaskForm):
    name = TextField('Name', [InputRequired()])
    twitter = TextField('Twitter')

class UploadMediaForm(FlaskForm):
    file = FileField('Image', [FileRequired(),
                               FileAllowed(ALLOWED_EXTENSIONS, 'Images only')])
    desc = TextField('Description', [InputRequired()])

class MediaForm(FlaskForm):
    desc = TextField('Description', [InputRequired()])

class PostForm(FlaskForm):
    title = TextField('Title', [InputRequired()])
    body = TextAreaField('Body', [InputRequired()])
    tags = TextField('Tags', [InputRequired()])
    published = BooleanField('Published')
    authors = QuerySelectMultipleField('Authors', query_factory=lambda: Author.query.all(),
                                       get_label='name')
