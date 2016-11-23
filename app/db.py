"""Database initialization settings and logic."""
from flask_sqlalchemy import SQLAlchemy


def connect_db(**kwargs):
    """Link the app database to a postgres db with the supplied info."""
    db_uri = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(kwargs.get('username'),
                                                       kwargs.get('password'),
                                                       kwargs.get('host'),
                                                       kwargs.get('port'),
                                                       kwargs.get('database'))
    app = kwargs.get('app')
    db = SQLAlchemy(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    return db
