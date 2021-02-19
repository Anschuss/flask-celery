import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

from celery_turn import make_celery



app = Flask(__name__)
app.config["SECRET_KEY"] = "4e90b165e5e5380b"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres+psycopg2://user:password@0.0.0.0:5432/medicin"
app.config.update(
    CELERY_BROKER_URL='redis://0.0.0.0:6379',
    CELERY_RESULT_BACKEND='redis://0.0.0.0:6379',
    CELERY_ACCEPT_CONTENT=['application/json'],
    CELERY_TASK_SERIALIZER='json',
    CELERY_RESULT_SERIALIZER='json',
)

### Mail Connfig
app.config["MAIL_DRIVER"] = "smtp"
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.environ.get("EMAIL_USER")
app.config["MAIL_PASSWORD"] = os.environ.get("EMAIL_PASS")
mail = Mail(app)

client = make_celery(app)
client.conf.update(app.config)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

migrate = Migrate(app, db)

login = LoginManager(app)
login.login_view = "login"
login.login_message_category = "info"

from views import routes
