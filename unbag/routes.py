import config
from .models import Post, Issue
from flask_security import current_user
from flask import Blueprint, send_from_directory, render_template, request, abort

bp = Blueprint('main', __name__)

@bp.context_processor
def current_issue():
    issue = Issue.query.order_by(Issue.id.desc()).first()
    return dict(current_issue=issue)

@bp.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@bp.route('/')
def index():
    issues = Issue.query.order_by(Issue.id.desc()).all()
    return render_template('index.html', issues=issues)

@bp.route('/uploads/<filename>')
def uploads(filename):
    return send_from_directory(config.UPLOAD_FOLDER, filename)

@bp.route('/<slug>')
def post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    return render_template('post.html', post=post, current_post=post)
    if not post.published and not current_user.is_authenticated:
        abort(404)
    return render_template('post.html', post=post, current='foobar')

@bp.route('/events')
def events():
    return 'TODO'

@bp.route('/donate')
def donate():
    return 'TODO'

@bp.route('/shop')
def shop():
    return 'TODO'
