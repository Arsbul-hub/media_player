import re

from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField, TextAreaField
from wtforms.widgets import TextArea
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User
from app.validators import video_validator, image_validator


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

    def validate_password(self, password):
        user = User.query.filter_by(username=self.username.data).first()

        if not user or not user.check_password(self.password.data):
            raise ValidationError('Неверное имя пользователя или пароль.')


class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])

    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField('Повтор пароля', validators=[DataRequired(), EqualTo('password')])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()

        if user:
            raise ValidationError('Please use a different username.')


class AddVideoForm(FlaskForm):
    title = StringField("Название видео", validators=[DataRequired()])
    description = TextAreaField("Описание видео", validators=[DataRequired()])
    video = FileField("Видео ресурс", validators=[DataRequired(), video_validator])
    cover = FileField("Обложка", validators=[image_validator])
    submit = SubmitField("Добавить")


class CreateStudioForm(FlaskForm):
    title = StringField("Название студии", validators=[DataRequired()])
    description = TextAreaField("Описание студии", validators=[DataRequired()])
    cover = FileField("Аватарка", validators=[DataRequired(), image_validator])
    submit = SubmitField("Создать")


