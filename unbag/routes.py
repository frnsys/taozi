import config
from .models import Post
from flask_security import current_user
from flask import Blueprint, send_from_directory, render_template, abort

bp = Blueprint('main', __name__)

@bp.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(config.UPLOAD_FOLDER, filename)

@bp.route('/<slug>')
def post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    if not post.published and not current_user.is_authenticated:
        abort(404)
    return render_template('post.html', post=post)
