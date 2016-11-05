"""Config variables for getting the database URI."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

username = 'stevula'
password = 'default'
host = 'localhost'
port = 5432
database = 'slackbot'
db_uri = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(username, password, host,
                                                   port, database)

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
