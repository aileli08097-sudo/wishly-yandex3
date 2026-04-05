from flask import Flask, render_template, redirect, session, request, flash, abort, url_for
from data import lists_api
from data.wishbook import WishBook
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
    lst = []
    names = []
    aut = False
    if current_user.is_authenticated:
        sub_lists = set()
        for book in db_sess.query(WishBook).filter(WishBook.user_id == current_user.id).all():
            if book is not None:
                sub_lists.add(db_sess.query(Lists).join(
                Wishes, Wishes.list_id == Lists.id).filter(Wishes.id == book.wish_id).first())
        lists = db_sess.query(Lists).filter(Lists.user_id == current_user.id).all()
        lst = list(sub_lists) + lists
        users = db_sess.query(User).all()
        names = {item.id: f'{item.username}' for item in users}
        aut = True
    return render_template('index.html', lists=lst, names=names, aut=aut)


@application.route('/profile')
@login_required
def profile():
    db_sess = db_session.create_session()
    sub_lists = set()
    for book in db_sess.query(WishBook).filter(WishBook.user_id == current_user.id).all():
        if book is not None:
            sub_lists.add(db_sess.query(Lists).join(
            Wishes, Wishes.list_id == Lists.id).filter(Wishes.id == book.wish_id).first())
    lists = db_sess.query(Lists).filter(Lists.user_id == current_user.id).all()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    return render_template('profile.html', sub_lists=list(sub_lists), lists=lists, user=user)


@application.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.username == form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
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
                    return redirect('/')
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
            lst.generate_token()
            db_sess.add(lst)
            db_sess.commit()
            return redirect(f'/list{lst.id}')
        return render_template('add_list.html',
                               message="Введите не прошедшую дату",
                               form=form)
    return render_template('add_list.html', title='Добавление вишлиста',
                           form=form)


@application.route('/list<int:list_id>')
@login_required
def lst(list_id):
    db_sess = db_session.create_session()
    lst = db_sess.get(Lists, list_id)
    for wish in db_sess.query(Wishes).filter(Wishes.list_id == lst.id):
        if db_sess.query(WishBook).filter_by(
                user_id=current_user.id,
                wish_id=wish.id
        ).first():
            return redirect(f'/shared/{lst.token}')
    if lst.user_id == current_user.id:
        wishes = db_sess.query(Wishes).filter_by(list_id=list_id).all()
        is_book = []
        for wish in wishes:
            book = db_sess.query(WishBook).filter_by(wish_id=wish.id).first()
            if book:
                is_book.append((book, True))
            else:
                is_book.append((wish.id, False))
        url = url_for('shared_lst', token=lst.token, _external=True)
        return render_template('list.html', lst=lst, wishes=wishes, url=url, is_shared_view=False, is_book=is_book)
    else:
        flash('Вишлист не найден', 'danger')
        return redirect(request.referrer or '/')


@application.route('/shared/<string:token>')
def shared_lst(token):
    db_sess = db_session.create_session()
    lst = db_sess.query(Lists).filter(Lists.token == token).first()
    if not lst:
        flash('Вишлист не найден', 'danger')
        return redirect(request.referrer or '/')
    if not current_user.is_authenticated or lst.user_id != current_user.id:
        is_book = []
        wishes = db_sess.query(Wishes).filter_by(list_id=lst.id).all()
        for wish in wishes:
            book = db_sess.query(WishBook).filter_by(wish_id=wish.id).first()
            if book:
                is_book.append((book, True))
            else:
                is_book.append((wish.id, False))
        return render_template('list.html', lst=lst, wishes=wishes, is_shared_view=True, is_book=is_book, token=token)
    else:
        return redirect(f'/list{lst.id}')


@application.route('/shared/<string:token>/<int:wish_id>/delete', methods=['POST'])
@login_required
def delete_wish(token, wish_id):
    db_sess = db_session.create_session()
    lst = db_sess.query(Lists).filter(Lists.token == token).first()
    if not lst:
        flash('Вишлист не найден', 'danger')
        return redirect(request.referrer or '/')
    wish = db_sess.get(Wishes, wish_id)
    if not wish or lst.id != wish.list_id:
        flash('Желание не найдено', 'danger')
        return redirect(request.referrer or f'/shared/{token}')
    if lst.user_id != current_user.id:
        flash('Вы не можете удалить это желание', 'danger')
        return redirect(request.referrer or f'/shared/{token}')
    db_sess.delete(wish)
    db_sess.commit()

    flash(f'Желание успешно удалено!', 'success')
    return redirect(request.referrer or f'/shared/{token}')


@application.route('/shared/<string:token>/<int:wish_id>/book', methods=['GET', 'POST'])
def book_lst(token, wish_id):
    db_sess = db_session.create_session()
    lst = db_sess.query(Lists).filter(Lists.token == token).first()
    if not lst:
        flash('Вишлист не найден', 'danger')
        return redirect(request.referrer or '/')
    wish = db_sess.query(Wishes).filter(Wishes.id == wish_id, Wishes.list_id == lst.id).first()
    if not wish:
        flash('Желание не найдено', 'danger')
        return redirect(request.referrer or f'/shared/{token}')
    if not current_user.is_authenticated:
        flash('Сначала войдите в аккаунт!', 'danger')
        return redirect('/login')
    exist = db_sess.query(WishBook).filter_by(
        user_id=current_user.id,
        wish_id=wish.id
    ).first()

    if not exist:
        sub = WishBook(
            user_id=current_user.id,
            wish_id=wish.id
        )
        db_sess.add(sub)
        db_sess.commit()
        flash('Вы забронировали это желание!', 'success')
    else:
        flash('Вы уже забронировали это желание', 'info')

    return redirect(f'/shared/{token}')


@application.route('/shared/<string:token>/<int:wish_id>/unbook', methods=['GET', 'POST'])
def unbook_lst(token, wish_id):
    db_sess = db_session.create_session()
    lst = db_sess.query(Lists).filter(Lists.token == token).first()
    if not lst:
        flash('Вишлист не найден', 'danger')
        return redirect(request.referrer or '/')
    wish = db_sess.query(Wishes).filter(Wishes.id == wish_id, Wishes.list_id == lst.id).first()
    if not wish:
        flash('Желание не найдено', 'danger')
        return redirect(request.referrer or f'/shared/{token}')
    if not current_user.is_authenticated:
        flash('Сначала войдите в аккаунт!', 'danger')
        return redirect('/login')
    exist = db_sess.query(WishBook).filter_by(
        user_id=current_user.id,
        wish_id=wish.id
    ).first()
    if exist:
        sub = db_sess.query(WishBook).filter(WishBook.user_id == current_user.id, WishBook.wish_id == wish.id).first()
        db_sess.delete(sub)
        db_sess.commit()
        flash('Вы отказались от бронирования этого желания!', 'info')
    else:
        flash('Вы не бронировали это желание', 'warning')
    return redirect(f'/shared/{token}')


@application.route('/list<int:list_id>/add_wish', methods=['GET', 'POST'])
@login_required
def add_wish(list_id):
    db_sess = db_session.create_session()
    lst = db_sess.get(Lists, list_id)
    if lst.user_id == current_user.id:
        form = WishForm()
        if form.validate_on_submit():
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
    else:
        return redirect(request.referrer or '/')


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
