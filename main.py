from flask import Flask, render_template, redirect, session, request, flash
from data import lists_api
from data.wishes import Wishes
from forms.code_registr_form import CodeRegistrForm
from forms.login_form import LoginForm
from data.lists import Lists
from data.users_resource import *
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import Api
from forms.registr_form import RegistrForm
from forms.list_form import ListForm
from forms.wish_form import WishForm
from dotenv import load_dotenv
from email_validator import validate_email
from datetime import *
import os
from flask_mail import Mail

load_dotenv()

application = Flask(__name__)
application.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

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

@application.route('/profile')
@login_required
def profile():
    db_sess = db_session.create_session()
    lists = db_sess.query(Lists).filter(Lists.user_id == current_user.id).all()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    return render_template('profile.html', lists=lists, user=user)


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
        try:
            valid = validate_email(form.email.data, check_deliverability=True)
            normal_email = valid.normalized
        except Exception:
            return render_template('registr.html',
                                   message="Введите существующую почту",
                                   form=form)
        exist = db_sess.query(User).filter((User.email == normal_email) | (User.username == form.username.data)).first()
        if not exist:
            user = User()
            user.username = form.username.data
            user.email = normal_email
            if len(form.password1.data) >= 8:
                if form.password1.data == form.password2.data:
                    user.set_password(form.password1.data)
                    db_sess.add(user)
                    db_sess.commit()
                    login_user(user, remember=form.remember_me.data)
                    return redirect("/")
                return render_template('registr.html',
                                       message="Пароли не совпадают",
                                       form=form)
            return render_template('registr.html',
                                   message="Пароль должен быть не менее 8 символов длиной",
                                   form=form)
        elif exist.email == form.email.data:
            return render_template('registr.html',
                                   message="Эта почта уже зарегистрирована",
                                   form=form)
        elif exist.username == form.username.data:
            return render_template('registr.html',
                                   message="Это имя пользователя уже занято",
                                   form=form)
    return render_template('registr.html', title='Регистрация',
                           form=form)


@application.route('/code_registration', methods=['GET', 'POST'])
def code_registration():
    form = CodeRegistrForm()
    if 'pending_user_id' not in session:
        return redirect('/registration')
    if form.validate_on_submit():
        code = request.form.get('code')
        user_id = session.get('pending_user_id')
        db_sess = db_session.create_session()
        user = db_sess.get(User, user_id)

        if not user:
            flash('Пользователь не найден', 'danger')
            return redirect('/registration')

        if user.code == code:
            time = user.time + timedelta(minutes=10)
            if datetime.now() > time:
                flash('Время действия кода подтверждения истекло', 'danger')
                db_sess.delete(user)
                db_sess.commit()
                session.pop('pending_user_id', None)
                return redirect('/registration')
            user.confirmed = True
            user.code = None
            db_sess.commit()
            login_user(user, remember=user.remember_me)
            session.pop('pending_user_id', None)

            flash('Почта успешно подтверждена!', 'success')
            return redirect('/')
        else:
            flash('Неверный код подтверждения', 'danger')
            return render_template('code_registr.html')


@application.route('/add_list', methods=['GET', 'POST'])
@login_required
def add_list():
    form = ListForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        lst = Lists()
        lst.feast = form.feast.data
        if (date.today() - form.date.data).days < 0:
            lst.date = form.date.data
            lst.time = form.time.data
            lst.notification = form.notification.data
            lst.user_id = current_user.id
            db_sess.add(lst)
            db_sess.commit()
            return redirect(f'/list{lst.id}')
        return render_template('add_list.html',
                               message="Введите не прошедшую дату",
                               form=form)
    return render_template('add_list.html', title='Добавление вишлиста',
                           form=form)


@application.route('/list<int:list_id>')
def lst(list_id):
    db_sess = db_session.create_session()
    lst = db_sess.get(Lists, list_id)
    wishes = db_sess.query(Wishes).filter_by(list_id=list_id).all()
    return render_template('list.html', lst=lst, wishes=wishes)


@application.route('/list<int:list_id>/add_wish', methods=['GET', 'POST'])
@login_required
def add_wish(list_id):
    form = WishForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        wish = Wishes()
        wish.name = form.name.data
        wish.bio = form.bio.data
        wish.url = form.url.data
        wish.list_id = list_id
        db_sess.add(wish)
        db_sess.commit()
        return redirect(f'/list{list_id}')
    return render_template('add_wish.html', title='Добавление желания',
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
    application.run(debug=True)


if __name__ == '__main__':
    main()
