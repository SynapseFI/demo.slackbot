"""Config variables for getting the database URI."""
username = 'stevula'
password = 'default'
host = 'localhost'
port = 5432
database = 'slackbot'
db_uri = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(username, password, host,
                                                   port, database)
