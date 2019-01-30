import os
import config
from . import forms
from .datastore import db
from slugify import slugify
from .compile import compile_markdown
from .models import Post, Author, Media, Issue
from flask_security.decorators import roles_required
from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename

bp = Blueprint('admin', __name__, url_prefix='/admin')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in forms.ALLOWED_EXTENSIONS


@bp.route('/')
@roles_required('admin')
def index():
    return redirect(url_for('admin.posts'))


@bp.route('/posts', methods=['GET', 'POST'])
@roles_required('admin')
def posts():
    data = request.args
    page = int(data.get('page', 1))

    form = forms.PostForm()
    if form.validate_on_submit():
        post = Post()
        form.populate_obj(post)
        post.slug = slugify(post.title)
        post.html = compile_markdown(post.body)
        db.session.add(post)
        db.session.commit()
        flash('Post created.')

    paginator = Post.query.paginate(page, per_page=20)
    return render_template('admin/posts.html', posts=paginator.items, paginator=paginator)


@bp.route('/posts/new')
@roles_required('admin')
def new_post():
    form = forms.PostForm()
    return render_template('admin/post.html', form=form,
                           action=url_for('admin.posts'))


@bp.route('/posts/<int:id>', methods=['GET', 'POST', 'DELETE'])
@roles_required('admin')
def post(id):
    post = Post.query.get_or_404(id)

    form = forms.PostForm(obj=post)
    if form.validate_on_submit():
        form.populate_obj(post)
        post.slug = slugify(post.title)
        post.html = compile_markdown(post.body)
        db.session.add(post)
        db.session.commit()
        flash('Post updated.')

    elif request.method == 'DELETE':
        db.session.delete(post)
        flash('Post deleted.')
        return redirect(url_for('admin.posts'))

    return render_template('admin/post.html', post=post, form=form,
                           action=url_for('admin.post', id=post.id))


@bp.route('/authors', methods=['GET', 'POST'])
@roles_required('admin')
def authors():
    data = request.args
    page = int(data.get('page', 1))

    form = forms.AuthorForm()
    if form.validate_on_submit():
        author = Author()
        form.populate_obj(author)
        author.slug = slugify(author.name)
        db.session.add(author)
        db.session.commit()
        flash('Author added.')

    paginator = Author.query.paginate(page, per_page=20)
    return render_template('admin/authors.html', authors=paginator.items, paginator=paginator)


@bp.route('/authors/new')
@roles_required('admin')
def new_author():
    form = forms.AuthorForm()
    return render_template('admin/author.html',
                           form=form, action=url_for('admin.authors'))


@bp.route('/authors/<int:id>', methods=['GET', 'POST', 'DELETE'])
@roles_required('admin')
def author(id):
    author = Author.query.get_or_404(id)

    form = forms.AuthorForm(obj=author)
    if form.validate_on_submit():
        form.populate_obj(author)
        author.slug = slugify(author.name)
        db.session.add(author)
        db.session.commit()
        flash('Author updated.')

    elif request.method == 'DELETE':
        db.session.delete(author)
        flash('Author deleted.')
        return redirect(url_for('admin.authors'))

    return render_template('admin/author.html',
                           form=form, action=url_for('admin.author', id=author.id))


@bp.route('/media', methods=['GET', 'POST'])
@roles_required('admin')
def media():
    data = request.args
    page = int(data.get('page', 1))

    form = forms.UploadMediaForm()
    if form.validate_on_submit():
        file = request.files[form.file.name]
        if file.filename == '':
            flash('No selected file.')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(config.UPLOAD_FOLDER, filename))
            media = Media(filename=filename)
            form.populate_obj(media)
            db.session.add(media)
            db.session.commit()
            flash('Media created.')

    paginator = Media.query.paginate(page, per_page=20)
    return render_template('admin/media.html',
                           media=paginator.items,
                           paginator=paginator,
                           form=form)

@bp.route('/media/new')
@roles_required('admin')
def new_medium():
    form = forms.UploadMediaForm()
    return render_template('admin/medium.html',
                           form=form, action=url_for('admin.media'))

@bp.route('/media/<int:id>', methods=['GET', 'POST', 'DELETE'])
@roles_required('admin')
def medium(id):
    media = Media.query.get_or_404(id)

    form = forms.MediaForm(obj=media)
    if form.validate_on_submit():
        form.populate_obj(media)
        db.session.add(media)
        db.session.commit()
        flash('Media updated.')

    elif request.method == 'DELETE':
        db.session.delete(media)
        flash('Media deleted.')
        return redirect(url_for('admin.media'))

    return render_template('admin/medium.html', media=media,
                           form=form, action=url_for('admin.medium', id=media.id))


@bp.route('/issues', methods=['GET', 'POST'])
@roles_required('admin')
def issues():
    data = request.args
    page = int(data.get('page', 1))

    form = forms.IssueForm()
    if form.validate_on_submit():
        issue = Issue()
        form.populate_obj(issue)
        issue.slug = slugify(issue.title)
        db.session.add(issue)
        db.session.commit()
        flash('Issue created.')

    paginator = Issue.query.paginate(page, per_page=20)
    return render_template('admin/issues.html', issues=paginator.items, paginator=paginator)


@bp.route('/issues/new')
@roles_required('admin')
def new_issue():
    form = forms.IssueForm()
    return render_template('admin/issue.html', form=form,
                           action=url_for('admin.issues'))


@bp.route('/issues/<int:id>', methods=['GET', 'POST', 'DELETE'])
@roles_required('admin')
def issue(id):
    issue = Issue.query.get_or_404(id)

    form = forms.IssueForm(obj=issue)
    if form.validate_on_submit():
        form.populate_obj(issue)
        issue.slug = slugify(issue.title)
        db.session.add(issue)
        db.session.commit()
        flash('Issue updated.')

    elif request.method == 'DELETE':
        db.session.delete(issue)
        flash('Issue deleted.')
        return redirect(url_for('admin.issues'))

    return render_template('admin/issue.html', issue=issue, form=form,
                           action=url_for('admin.issue', id=issue.id))
