import base64
from datetime import datetime
import os

from flask import render_template, send_from_directory, url_for, render_template_string, flash, redirect, request
from flask_ckeditor import upload_fail, upload_success
from werkzeug.datastructures import FileStorage

from app import app, morph, db, DataManager, manager

from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Videos, Studios, Images, VideoPosts
from app.forms import LoginForm, RegistrationForm, AddVideoForm, CreateStudioForm
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
        admin.set_password("admin")
        db.session.add(admin)

        db.session.commit()
        logout_user()

    return render_template("service/Уведомление.html", title="Внимание", messages=messages)


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
            next_page = url_for('top')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/register', methods=['GET', 'POST'])

def register():


    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        # login_user(user, remember=form.remember_me.data)
        flash('Congratulations, you are now a registered admin!')
        return redirect(url_for("/"))
    return render_template('register.html', title='Register', form=form)


@app.route('/upload', methods=['POST', "GET"])
def upload():
    f = request.files.get('upload')
    # Add more validations here
    save_file(f)

    url = url_for('uploaded_files', filename=f.filename)

    return upload_success(url, filename=f.filename)


def save_file(file, path="/media", name=None, formates=[]):
    if not file:
        return None
    format = file.filename.split(".")[-1].lower()
    if name:
        file.filename = name + "." + format

    if formates and format not in formates:
        return upload_fail(message='Image only!')

    file.save(f"app/{path}/{file.filename}")
    return f"/{path}/{file.filename}"


@app.route("/")
@app.route("/Популярное")
def top():
    text = ""
    with open("app/static/loaded_media/123.mp4", "rb") as videoFile:
        text = base64.b64encode(videoFile.read())

    with open("app/static/loaded_media/tt.txt", "wb") as f:
        f.write(text)
    return render_template("index.html", music=manager.get_top())


@app.route('/Рекомендации')
def recommendations():
    return render_template("index.html", music=manager.get_top())


@app.route('/logout')
def logout():
    logout_user()
    return redirect("/")


@login_required
@app.route('/Добавить видео', methods=['GET', 'POST'])
def add_video():
    studio_id = request.args.get("studio_id")
    request_studio = Studios.query.filter_by(id=studio_id).first()
    if not current_user.is_authenticated or request_studio not in current_user.studios:
        return redirect("/")
    form = AddVideoForm()
    if form.validate_on_submit():
        video = Videos(format=form.video.data.filename.split(".")[-1])
        db.session.add(video)
        db.session.commit()
        save_file(form.video.data, "media/videos/", str(video.id))

        cover = Images(format=form.cover.data.filename.split(".")[-1])
        db.session.add(cover)
        db.session.commit()
        save_file(form.cover.data, "media/images/", str(cover.id))
        video_post = VideoPosts()
        video_post.title = form.title.data
        video_post.description = form.description.data
        video_post.cover = cover.id
        video_post.source = video.id
        video_post.studio_id = studio_id
        db.session.add(video_post)
        db.session.commit()

        return redirect("/")
    return render_template('Добавить видео.html', title='Sign In', form=form)


@login_required
@app.route('/Создать студию', methods=['GET', 'POST'])
def create_studio():
    if not current_user.is_authenticated:
        return redirect("/")
    form = CreateStudioForm()
    if form.validate_on_submit():
        cover = Images(format=form.cover.data.filename.split(".")[-1])
        db.session.add(cover)
        db.session.commit()
        save_file(form.cover.data, "media/images/", str(cover.id))

        studio = Studios()
        studio.title = form.title.data
        studio.description = form.description.data
        studio.cover = cover.id
        studio.user_id = current_user.id
        db.session.add(studio)
        db.session.commit()

        return redirect("/")
    return render_template('Создать студию.html', form=form)


#
@login_required
@app.route('/Мои студии')
def my_studios():
    if not current_user.is_authenticated:
        return redirect("/")
    studios = current_user.studios

    print(studios)
    return render_template('Студии.html', studios=studios)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404
