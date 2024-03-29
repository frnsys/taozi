from flask_security import current_user
from .models import Post, Event, Issue, Meta
from flask import Blueprint, send_from_directory, render_template, request, abort, redirect, current_app

bp = Blueprint('taozi', __name__)

@bp.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@bp.route('/uploads/<filename>')
def uploads(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@bp.route('/')
def posts():
    posts = Post.query.filter(Post.published & Post.visible).all()
    return render_template('posts.html', posts=posts)

@bp.route('/issues')
def issues():
    issues = Issue.query.filter(Issue.published).all()
    return render_template('issues.html', issues=issues)

@bp.route('/<slug>')
def issue(slug):
    issue = Issue.query.filter_by(slug=slug).first_or_404()
    return render_template('issue.html', issue=issue)

@bp.route('/<issue>/<slug>')
def post(issue, slug):
    post = Post.query.filter(Post.slug==slug, Post.issue.has(slug=issue)).first_or_404()
    if not post.published and not current_user.is_authenticated:
        abort(404)
    if post.redirect:
        return redirect(post.redirect)
    return render_template('post.html', post=post, issue=post.issue)

@bp.route('/events')
def events():
    events = [e.post
            for e in Event.query.order_by(Event.end.desc(), Event.start.asc()).all()
            if e.post.published and e.post.visible]
    return render_template('events.html', events=events)

@bp.route('/search')
def search():
    query = request.args.get('query')
    posts = Post.search(query) if query else []
    return render_template('search.html', query=query, posts=posts)

@bp.app_template_global('meta')
def meta(slug):
    meta = Meta.query.filter(Meta.slug==slug).first()
    if meta:
        return meta.html
    return  '[No meta for slug={}]'.format(slug)
