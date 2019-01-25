from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import Required
from wtforms.fields import TextField, TextAreaField, BooleanField

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


class AuthorForm(FlaskForm):
    name = TextField('Name', [Required()])
    twitter = TextField('Twitter')

class MediaForm(FlaskForm):
    file = FileField('Image', [FileRequired(),
                               FileAllowed(ALLOWED_EXTENSIONS, 'Images only')])
    desc = TextField('Description', [Required()])

class PostForm(FlaskForm):
    title = TextField('Title', [Required()])
    body = TextAreaField('Body', [Required()])
    tags = TextField('Tags', [Required()])
    published = BooleanField('Published')
