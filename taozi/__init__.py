from flask import Flask
from flask_mail import Mail
from flask_migrate import Migrate
from flask_security import SQLAlchemyUserDatastore, Security
from flask_wtf.csrf import CSRFProtect
from .forms import PostForm, IssueForm, AuthorForm, append_fields
from .datastore import db, init_db
from .models import User, Role, Issue, Post
from .admin import bp as admin_bp
from .routes import bp as front_bp

def create_app(config, blueprints=None, name=__name__, static_folder='static', template_folder='templates'):
    app = Flask(name,
                static_url_path='/assets',
                static_folder=static_folder,
                template_folder=template_folder)
    app.config.from_object(config)

    # Initialize the database and declarative Base class
    db.init_app(app)
    Migrate(app, db, render_as_batch=True)
    app.db = db

    # Setup security
    app.user_db = SQLAlchemyUserDatastore(db, User, Role)
    Security(app, app.user_db)
    Mail(app)
    CSRFProtect(app)

    # Create the database tables.
    # Flask-SQLAlchemy needs to know which
    # app context to create the tables in.
    with app.app_context():
        init_db()

    blueprints = blueprints or []
    for bp in blueprints:
        app.register_blueprint(bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(front_bp)

    # Setup additional fields on forms
    append_fields(PostForm, app.config.get('POST_META', {}))
    append_fields(IssueForm, app.config.get('ISSUE_META', {}))
    append_fields(AuthorForm, app.config.get('AUTHOR_META', {}))

    # Expose additional data to templates
    app.add_template_global(name='Post', f=Post)

    return app
