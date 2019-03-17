import os
import json
import shutil
import config
from slugify import slugify
from datetime import datetime
from unbag import create_app, db
from unbag.models import Issue, Post, Author, Media

app = create_app()

exported = json.load(open('../importer/converted.json'))

with app.app_context():
    print('Creating issues...')
    issues = ['Metis', 'End', 'Reverie']
    for name in issues:
        issue = Issue(name=name)
        issue.slug = slugify(issue.name)
        db.session.add(issue)
        db.session.commit()

    for fname, data in exported.items():
        try:
            issue = next(i for i in issues if i.lower() in fname)
            issue = Issue.query.filter_by(name=issue).first()
        except StopIteration:
            print('Skipping:', fname)
            continue

        for _, m in data['media'].items():
            fname = m.split('/')[-1]
            media = Media.query.filter_by(filename=fname).first()
            if media is not None:
                continue

            # B/c of the multisite system,
            # we don't actually know which site the image was
            # from originally. so just brute-force
            # search until we find it.
            to = os.path.join(config.UPLOAD_FOLDER, fname)
            for site in os.listdir('../importer/wp_dumps/uploads/sites'):
                frm = os.path.join('../importer/wp_dumps/uploads/sites', site, m)
                try:
                    shutil.copy(frm, to)
                except FileNotFoundError:
                    continue
                break
            else:
                print('Could not find:', m)
            media = Media()
            media.desc = m
            media.filename = fname
            db.session.add(media)
            db.session.commit()

        for p in data['posts']:
            post = Post()
            post.title = p['title']
            post.slug = p['slug']
            post.published_at = datetime.fromtimestamp(p['published_at'])
            post.html = p['body']
            post.body = post.html
            post.desc = p['desc']
            post.issue = issue

            if p['image'] is not None:
                fname = p['image'].split('/')[-1]
                media = Media.query.filter_by(filename=fname).first()
                if media is None: print('Missing media')
                post.image = media

            authors = []
            for name in p['authors']:
                author = Author.query.filter_by(name=name).first()
                if author is None:
                    author = Author(name=name)
                    author.slug = slugify(author.name)
                    db.session.add(author)
                    db.session.commit()
                authors.append(author)
            post.authors = authors

            db.session.add(post)
            db.session.commit()