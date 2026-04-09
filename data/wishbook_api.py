import flask
from flask import jsonify, make_response, request
from . import db_session
from .wishbook import WishBook

blueprint = flask.Blueprint(
    'wishbook_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/wishbook', methods=['GET'])
def get_wishbook():
    db_sess = db_session.create_session()
    wishbook = db_sess.query(WishBook).all()
    return jsonify(
        {
            'wishbook':
                [item.to_dict(only=(
                    'id', 'user_id', 'wish_id'))
                    for item in wishbook]
        }
    )


@blueprint.route('/api/wishbook/<int:wishbook_id>', methods=['GET'])
def get_one_wishbook(wishbook_id):
    db_sess = db_session.create_session()
    wishbook = db_sess.get(WishBook, wishbook_id)
    if not wishbook:
        return make_response(jsonify({'error': 'Not found'}), 404)
    return jsonify(
        {
            'wish': wishbook.to_dict(only=(
                'id', 'user_id', 'wish_id'))
        }
    )


@blueprint.route('/api/wishbook', methods=['POST'])
def create_wishbook():
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    elif not all(key in request.json for key in
                 ['user_id', 'wish_id']):
        return make_response(jsonify({'error': 'Bad request'}), 400)
    db_sess = db_session.create_session()
    wishbook = WishBook(
        user_id=request.json['user_id'],
        wish_id=request.json['wish_id']
    )
    db_sess.add(wishbook)
    db_sess.commit()
    return jsonify({'id': wishbook.id})
