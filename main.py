from flask import Flask, render_template, redirect
from data import lists_api
from forms.login_form import LoginForm
from data.lists import Lists
from data.users_resource import *
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import Api
from forms.registr_form import RegistrForm
from forms.list_form import ListForm

application = Flask(__name__)
application.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(application)

api = Api(application)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@application.route('/')
def index():
    db_sess = db_session.create_session()
    lists = db_sess.query(Lists).all()
    users = db_sess.query(User).all()
    names = {item.id: f'{item.username}' for item in users}
    return render_template('index.html', lists=lists, names=names)


@application.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.username == form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@application.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegistrForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = User()
        user.username = form.username.data
        user.email = form.email.data
        if form.password1.data == form.password2.data:
            user.hashed_password = form.password1.data
            user.set_password(user.hashed_password)
            db_sess.add(user)
            db_sess.commit()
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('registr.html',
                               message="Пароли не совпадают",
                               form=form)
    return render_template('registr.html', title='Регистрация',
                           form=form)


@application.route('/add_list', methods=['GET', 'POST'])
@login_required
def add_list():
    form = ListForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        list = Lists()
        list.feast = form.feast.data
        list.date = form.date.data
        list.time = form.time.data
        list.notification = form.notification.data
        list.user_id = current_user.id
        db_sess.add(list)
        db_sess.commit()
        return redirect('/')
    return render_template('add_list.html', title='Добавление вишлиста',
                           form=form)


@application.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def main():
    db_session.global_init('db/wishly.db')
    db_sess = db_session.create_session()
    application.register_blueprint(lists_api.blueprint)
    api.add_resource(UserListResource, '/api/v2/users')
    api.add_resource(UserResource, '/api/v2/users/<int:user_id>')
    application.run()


if __name__ == '__main__':
    main()
