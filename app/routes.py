from datetime import datetime
import os

from flask import render_template, send_from_directory, url_for, render_template_string, flash, redirect, request
from flask_ckeditor import upload_fail, upload_success

from app import app, morph, db, DataManager, manager

from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Video
from app.forms import LoginForm, RegistrationForm, CreateNewsForm, AddAnimalForm, AddDocumentForm, ConfigForm, \
    AddPartnerForm
from werkzeug.urls import url_parse
from app import login

from urllib.parse import unquote



@login.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.route('/files/<path:filename>')
def uploaded_files(filename):
    return send_from_directory("static/loaded_media", filename)


@app.route('/reload_auth')
def reload_auth_system():
    messages = ["Конфигурационный файл аутентификации пользователей был перезагружен!"]
    if not db.session.query(User).filter_by(username="Admin").first():
        admin = User(username="Admin")
        admin.set_password("admin!6745")
        db.session.add(admin)

        db.session.commit()
        logout_user()


    return render_template("service/Уведомление.html", title="Внимание", messages=messages)


@app.route('/upload', methods=['POST', "GET"])
def upload():
    f = request.files.get('upload')
    # Add more validations here
    save_file(f)

    url = url_for('uploaded_files', filename=f.filename)

    return upload_success(url, filename=f.filename)


def save_file(file, path="/loaded_media", name=None, formates=[]):
    if not file:
        return None
    if name:
        file.filename = name
    extension = file.filename.split('.')[-1].lower()
    if formates and extension not in formates:
        return upload_fail(message='Image only!')

    file.save(f"app/static/{path}/{file.filename}")
    return f"static/{path}/{file.filename}"


@app.route('/')
def index():


    return render_template("index.html", music=manager.get_top())


@app.route('/logout')
def logout():
    logout_user()
    return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect("/")
    form = LoginForm()
    if form.validate_on_submit():

        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect("/login")
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if not current_user.is_authenticated:
        return redirect(url_for("index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        # login_user(user, remember=form.remember_me.data)
        flash('Congratulations, you are now a registered admin!')
        return redirect(url_for('index'))
    return render_template('register.html', title='Register', form=form)




@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404


