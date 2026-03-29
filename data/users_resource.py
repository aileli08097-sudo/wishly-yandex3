from flask_restful import reqparse, abort, Resource
from flask import jsonify
from data import db_session
from data.users import User
from werkzeug.security import generate_password_hash
import datetime

parser = reqparse.RequestParser()
parser.add_argument('username', required=True)
parser.add_argument('email', required=True)
parser.add_argument('hashed_password', required=True)
parser.add_argument('modified_date')


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")


def set_password(password):
    return generate_password_hash(password)


class UserResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.get(User, user_id)
        return jsonify({'user': user.to_dict(
            only=('username', 'email', 'hashed_password', 'modified_date'))})

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.get(User, user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})


class UserListResource(Resource):
    def get(self):
        session = db_session.create_session()
        user = session.query(User).all()
        return jsonify({'users': [item.to_dict(
            only=('username', 'email', 'hashed_password',
                  'modified_date')) for item in user]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        user = User(
            name=args['username'],
            email=args['email'],
            hashed_password=set_password(args['hashed_password']),
            modified_date=datetime.datetime.now()
        )
        session.add(user)
        session.commit()
        return jsonify({'id': user.id})
