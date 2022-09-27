import re
import sqlalchemy as sa
from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy

naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
db = SQLAlchemy(session_options={'autoflush': False}, metadata=MetaData(naming_convention=naming_convention))

def search(item, expr):
    return re.search(expr, item) is not None

def init_db():
    db.configure_mappers()
    db.create_all()

    @sa.event.listens_for(db.engine, 'connect')
    def on_connect(dbapi_connection, connection_record):
        dbapi_connection.create_function('REGEX', 2, search)
