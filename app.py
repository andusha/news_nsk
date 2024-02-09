import os
from pathlib import Path
from webpack_boilerplate.config import setup_jinja2_ext
import sqlite3
from flask import Flask, render_template, request, g, flash, abort, redirect, url_for, make_response
from api.FDataBase import FDataBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from api.UserLogin import UserLogin
from api.forms import LoginForm, RegisterForm, addPostForm
from flask_uploads import configure_uploads, patch_request_class
from api.config import photos, DATABASE, SECRET_KEY, MAX_CONTENT_LENGTH
import random



BASE_DIR = Path(__file__).parent
app = Flask(__name__, static_folder="frontend/build", static_url_path="/static/")
app.config.update({
    'WEBPACK_LOADER': {
        'MANIFEST_FILE': BASE_DIR / "frontend/build/manifest.json",
    }
})

app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path,'news_nsk.db'),
                       SECRET_KEY = SECRET_KEY
))

app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(app.root_path, 'frontend/vendors/images')
configure_uploads(app, photos)
# максимальный размер файла, по умолчанию 16MB
patch_request_class(app) 

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Авторизуйтесь для доступа к закрытым страницам"
login_manager.login_message_category = "success"

setup_jinja2_ext(app)


@app.cli.command("webpack_init")
def webpack_init():
    from cookiecutter.main import cookiecutter
    import webpack_boilerplate
    pkg_path = os.path.dirname(webpack_boilerplate.__file__)
    cookiecutter(pkg_path, directory="frontend_template")


@login_manager.user_loader
def load_user(user_id):
    print("load_user")
    return UserLogin().fromDB(user_id, dbase)


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def create_db():
    """Вспомогательная функция для создания таблиц БД"""
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()

def get_db():
    '''Соединение с БД, если оно еще не установлено'''
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


dbase = None
@app.before_request
def before_request():
    """Установление соединения с БД перед выполнением запроса"""
    global dbase
    db = get_db()
    dbase = FDataBase(db)


@app.teardown_appcontext
def close_db(error):
    '''Закрываем соединение с БД, если оно было установлено'''
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.route("/")
def index():
    carousel_posts = dbase.get_caroules_posts()
    top_posts = dbase.get_top_posts()
    all_posts = dbase.get_all_posts()

    filtred_posts = {'first_col': [], 'second_col': [], 'third_col': []}
    img_posts = []
    simple_posts = []
    for post in all_posts:
        if post['img_path']:
            img_posts.append(post)
        else:
            simple_posts.append(post)
    simple_posts_len = int(len(simple_posts)/3)
    img_posts_len = int(len(img_posts)/3)
    start_simple = 0
    start_img = 0
    for index,col in enumerate(filtred_posts, start=1):
        if start_img*index == img_posts_len*index or start_simple*index == simple_posts_len*index:
            filtred_posts[col] = img_posts[(start_img*index)-img_posts_len:img_posts_len*index] + simple_posts[(start_simple*index)-simple_posts_len:simple_posts_len*index]
        else:
            filtred_posts[col] = img_posts[start_img*index:img_posts_len*index] + simple_posts[start_simple*index:simple_posts_len*index]
        if start_simple == 0 or start_img == 0:
            start_simple = simple_posts_len
            start_img = img_posts_len
        random.shuffle(filtred_posts[col])
        print(col,(img_posts_len*index, start_img*index, img_posts_len), (start_simple*index,simple_posts_len*index, simple_posts_len))

    return render_template('index.html', menu=dbase.getMenu(),
                            is_auth = current_user.is_authenticated,
                            carousel=carousel_posts,
                            all_posts = filtred_posts,
                            top = top_posts)

@app.route("/add_post", methods=["POST", "GET"])
@login_required
def addPost():
    form = addPostForm()
    if form.validate_on_submit():
        if form.photo.data:
            filename = photos.save(form.photo.data)
            file_url = photos.url(filename)
            dbase.addPost(form.title.data, form.text.data, current_user.get_id(), file_url)
        else:
            dbase.addPost(form.title.data, form.text.data, current_user.get_id())

    return render_template('add_post.html', menu = dbase.getMenu(), title="Добавление статьи", is_auth = current_user.is_authenticated, form=form)


@app.route("/post/<int:id>")
def show_post(id):
    title, post, time, author = dbase.getPost(id)
    if not title:
        abort(404)

    return render_template('post.html', menu=dbase.getMenu(),
                            is_auth = current_user.is_authenticated,
                            title=title,
                            post=post,
                            time=time,
                            author=author)


@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = dbase.getUserByEmail(form.email.data)
        if user and check_password_hash(user['psw'], form.psw.data):
            userlogin = UserLogin().create(user)
            rm = form.remember.data
            login_user(userlogin, remember=rm)
            return redirect(request.args.get("next") or url_for("index"))

        flash("Неверная пара логин/пароль", "error")

    return render_template("login.html", menu=dbase.getMenu(), title="Авторизация", is_auth = current_user.is_authenticated, form=form)


@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
            hash = generate_password_hash(request.form['psw'])
            res = dbase.addUser(form.name.data, form.email.data, hash)
            if res:
                flash("Вы успешно зарегистрированы", "success")
                return redirect(url_for('login'))
            else:
                flash("Ошибка при добавлении в БД", "error")

    return render_template("register.html", menu=dbase.getMenu(), title="Регистрация", is_auth = current_user.is_authenticated, form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('index'))

if __name__ == "__main__":
   app.run()