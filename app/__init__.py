import locale
from flask import Flask, Blueprint
from flask_ckeditor import CKEditor
from flask_restful import Api

from app.DataManager import DataManager

from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, AnonymousUserMixin

import pymorphy3
class Anonymous(AnonymousUserMixin):
    username = "Guest"
    recommendations = ""
    is_authenticated = True

app = Flask(__name__)
app.config.from_object(Config)

ckeditor = CKEditor(app)
blueprint = Blueprint('app_api', __name__, template_folder='templates')

db = SQLAlchemy(app)
migrate = Migrate(app, db, render_as_batch=True)
login = LoginManager(app)
login.login_view = 'login'

morph = pymorphy3.MorphAnalyzer()
locale.setlocale(
    category=locale.LC_ALL,
    locale="Russian"
)
manager = DataManager()

from app import routes, models
