import os
from . import forms
from .datastore import db
from slugify import slugify
from datetime import datetime
from .models import Post, Author, Media, Issue, Event, Meta
from flask_security.decorators import roles_required
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify
from werkzeug.utils import secure_filename
from sqlalchemy.exc import IntegrityError
from PIL import Image

bp = Blueprint('admin', __name__, url_prefix='/admin',
               template_folder='templates',
               static_folder='static')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in forms.ALLOWED_EXTENSIONS


@bp.route('/')
@roles_required('admin')
def index():
    return redirect(url_for('admin.posts'))


@bp.route('/help')
@roles_required('admin')
def help():
    return render_template('admin/help.html')


@bp.route('/posts')
@roles_required('admin')
def posts():
    data = request.args
    page = int(data.get('page', 1))

    paginator = Post.query.filter_by(event=None).paginate(page, per_page=20)
    return render_template('admin/posts.html', posts=paginator.items, paginator=paginator)


@bp.route('/posts/new', methods=['GET', 'POST'])
@roles_required('admin')
def new_post():
    form = forms.PostForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            post = Post()
            form.populate_obj(post)
            if not post.slug:
                post.slug = slugify(post.title)
            else:
                post.slug = slugify(post.slug)
            post.set_meta_from_form(form)
            db.session.add(post)
            try:
                db.session.commit()
                flash('Post created.')
                return redirect(url_for('admin.post', id=post.id))
            except IntegrityError:
                db.session.rollback()
                flash('There is already a post with this slug, please use a different one.', 'error')
        else:
            flash('There is one or more issues with the post.', 'error')

    return render_template('admin/post.html', form=form,
                           action=url_for('admin.new_post'))

@bp.route('/posts/<int:id>', methods=['GET', 'POST', 'DELETE'])
@roles_required('admin')
def post(id):
    post = Post.query.get_or_404(id)

    if request.method == 'DELETE':
        db.session.delete(post)
        db.session.commit()
        return jsonify(success=True)

    else:
        form = forms.PostForm(obj=post, **post.get_meta())
        if request.method == 'POST':
            if form.validate_on_submit():
                already_published = post.published
                form.populate_obj(post)
                if not post.slug:
                    post.slug = slugify(post.title)
                else:
                    post.slug = slugify(post.slug)

                if not already_published and post.published:
                    post.published_at = datetime.utcnow()
                post.set_meta_from_form(form)
                db.session.add(post)
                try:
                    db.session.commit()
                    flash('Post updated.')
                except IntegrityError:
                    db.session.rollback()
                    flash('There is already a post with this slug, please use a different one.', 'error')
            else:
                flash('There is one or more issues with the post.', 'error')

        return render_template('admin/post.html', post=post, form=form,
                            action=url_for('admin.post', id=post.id))

@bp.route('/posts/<slug>')
def post_by_slug(slug):
    post = Post.get_by_slug(slug)
    if post:
        return jsonify(id=post.id)
    else:
        return jsonify(id=None)

@bp.route('/events', methods=['GET', 'POST'])
@roles_required('admin')
def events():
    data = request.args
    page = int(data.get('page', 1))

    form = forms.EventForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            event = Event()
            event.post = Post()
            form.populate_obj(event)
            if not event.post.slug:
                event.post.slug = slugify(event.post.title)
            else:
                event.post.slug = slugify(event.post.slug)
            db.session.add(event)
            db.session.commit()
            flash('Event created.')
            return redirect(url_for('admin.event', id=event.post.id))
        else:
            flash('There is one or more issues with the event.', 'error')

    paginator = Post.query.filter(Post.event != None).paginate(page, per_page=20)
    return render_template('admin/events.html', posts=paginator.items, paginator=paginator)


@bp.route('/events/new')
@roles_required('admin')
def new_event():
    form = forms.EventForm()
    return render_template('admin/event.html', form=form,
                           action=url_for('admin.events'))


@bp.route('/events/<int:id>', methods=['GET', 'POST', 'DELETE'])
@roles_required('admin')
def event(id):
    post = Post.query.get_or_404(id)
    event = post.event

    form = forms.EventForm(obj=event)
    if request.method == 'POST':
        if form.validate_on_submit():
            already_published = post.published
            form.populate_obj(event)
            if not post.slug:
                post.slug = slugify(post.title)
            else:
                post.slug = slugify(post.slug)
            if not already_published and post.published:
                post.published_at = datetime.utcnow()
            db.session.add(event)
            db.session.commit()
            flash('Event updated.')
        else:
            flash('There is one or more issues with the event.', 'error')

    elif request.method == 'DELETE':
        db.session.delete(post)
        db.session.delete(event)
        flash('Event deleted.')
        return redirect(url_for('admin.events'))

    return render_template('admin/event.html', post=post, form=form,
                           action=url_for('admin.event', id=post.id))


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
        author.set_meta_from_form(form)
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

    form = forms.AuthorForm(obj=author, **author.get_meta())
    if form.validate_on_submit():
        form.populate_obj(author)
        author.slug = slugify(author.name)
        author.set_meta_from_form(form)
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
    is_json = request.headers.get('Accept') == 'application/json'

    form = forms.UploadMediaForm()
    if form.validate_on_submit():
        file = request.files[form.file.name]
        if file.filename == '':
            flash('No selected file.', 'error')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if Media.exists(filename):
                filename = '{}_{}'.format(datetime.utcnow().timestamp(), filename)
            savepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(savepath)
            media = Media(filename=filename)
            form.populate_obj(media)

            try:
                img = Image.open(savepath)
                media.width, media.height = img.size

                # Create a thumbnail
                thumbpath = os.path.join(current_app.config['UPLOAD_FOLDER'], media.thumb)
                img.thumbnail((192, 192))
                img.convert('RGB').save(thumbpath)
            except OSError:
                # Not an image, ignore
                pass

            db.session.add(media)

            try:
                db.session.commit()
                if is_json:
                    return jsonify(success=True, id=media.id, thumb=media.thumburl, url=media.path)
                else:
                    flash('Media created.')
            except IntegrityError:
                db.session.rollback()
                err = 'Something went wrong while saving.'
                if is_json:
                    return jsonify(success=False, error=err)
                else:
                    flash(err, 'error')

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
    if request.method == 'DELETE':
        db.session.delete(media)
        db.session.commit()
        flash('Media deleted.')
        return jsonify(success=True, url=url_for('admin.media'))
    else:
        is_json = request.headers.get('Accept') == 'application/json'
        form = forms.MediaForm(obj=media)
        if form.validate_on_submit():
            form.populate_obj(media)
            db.session.add(media)
            db.session.commit()

            if is_json:
                return jsonify(success=True)
            else:
                flash('Media updated.')

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
        issue.slug = slugify(issue.name)
        issue.set_meta_from_form(form)
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

    form = forms.IssueForm(obj=issue, **issue.get_meta())
    if form.validate_on_submit():
        form.populate_obj(issue)
        issue.slug = slugify(issue.name)
        issue.set_meta_from_form(form)
        db.session.add(issue)
        db.session.commit()
        flash('Issue updated.')

    elif request.method == 'DELETE':
        db.session.delete(issue)
        flash('Issue deleted.')
        return redirect(url_for('admin.issues'))

    return render_template('admin/issue.html', issue=issue, form=form,
                           action=url_for('admin.issue', id=issue.id))


@bp.route('/meta', methods=['GET', 'POST'])
@roles_required('admin')
def meta():
    data = request.args
    page = int(data.get('page', 1))

    form = forms.MetaForm()
    if form.validate_on_submit():
        meta = Meta()
        form.populate_obj(meta)
        meta.slug = slugify(meta.slug)
        db.session.add(meta)
        db.session.commit()
        flash('Meta created.')
        return redirect(url_for('admin.meta', id=meta.id))

    paginator = Meta.query.paginate(page, per_page=20)
    return render_template('admin/meta.html', meta=paginator.items, paginator=paginator)


@bp.route('/meta/new')
@roles_required('admin')
def new_metum():
    form = forms.MetaForm()
    return render_template('admin/metum.html', form=form,
                           action=url_for('admin.meta'))


@bp.route('/meta/<int:id>', methods=['GET', 'POST', 'DELETE'])
@roles_required('admin')
def metum(id):
    meta = Meta.query.get_or_404(id)

    form = forms.MetaForm(obj=meta)
    if form.validate_on_submit():
        form.populate_obj(meta)
        meta.slug = slugify(meta.slug)
        db.session.add(meta)
        db.session.commit()
        flash('Meta updated.')

    elif request.method == 'DELETE':
        db.session.delete(meta)
        flash('Meta deleted.')
        return redirect(url_for('admin.meta'))

    return render_template('admin/metum.html', post=post, form=form,
                           action=url_for('admin.metum', id=meta.id))
