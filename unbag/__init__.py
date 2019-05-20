import config
import sentry_sdk
from flask import Flask
from flask_migrate import Migrate
from flask_mail import Mail
from flask_security import SQLAlchemyUserDatastore, Security
from .datastore import db
from .models import User, Role, Issue
from .admin import bp as admin_bp
from .routes import bp as main_bp
from sentry_sdk.integrations.flask import FlaskIntegration
from flask_konbini import Konbini


def create_app(package_name=__name__, static_folder='static', template_folder='templates', **config_overrides):
    app = Flask(package_name,
                static_url_path='/assets',
                static_folder=static_folder,
                template_folder=template_folder)
    app.config.from_object(config)

    # Apply overrides
    app.config.update(config_overrides)

    # Initialize the database and declarative Base class
    db.init_app(app)
    Migrate(app, db, render_as_batch=True)
    app.db = db

    # Setup security
    app.user_db = SQLAlchemyUserDatastore(db, User, Role)
    Security(app, app.user_db)
    Mail(app)

    # Create the database tables.
    # Flask-SQLAlchemy needs to know which
    # app context to create the tables in.
    with app.app_context():
        db.configure_mappers()
        db.create_all()

    app.register_blueprint(admin_bp)
    app.register_blueprint(main_bp)

    k = Konbini(app)

    if not app.debug:
        sentry_sdk.init(
            dsn=config.SENTRY_DSN,
            integrations=[FlaskIntegration()]
        )

    @app.context_processor
    def inject_issues():
        """Inject issues into all templates"""
        issues = Issue.query.filter(Issue.name!='Programs', Issue.published).order_by(Issue.id.desc()).all()
        return dict(issues=issues,
                    get_products=app.get_products,
                    get_plans=app.get_plans)

    return app
