from sqlalchemy_serializer import SerializerMixin

from app import db
from datetime import datetime
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import sqlalchemy as sa

__basemodel = db.Model


class User(UserMixin, __basemodel):
    __tablename__ = 'users'
    id = sa.Column(sa.Integer, primary_key=True)
    username = sa.Column(sa.String(), index=True, unique=True)
    password_hash = sa.Column(sa.String(128))
    recommendations = sa.Column(sa.String)
    def __repr__(self):
        return 'Пользователь {}'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Video(__basemodel, SerializerMixin):
    __tablename__ = 'videos'
    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String())
    description = sa.Column(sa.String())
    cover = sa.Column(sa.String())
    source = sa.Column(sa.String)
    timestamp = sa.Column(sa.DateTime, index=True, default=datetime.utcnow)
