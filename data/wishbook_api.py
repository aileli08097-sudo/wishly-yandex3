import flask
from flask import jsonify, make_response, request
from . import db_session
from .wishbook import ListSub

blueprint = flask.Blueprint(
    'listsub_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/listsub', methods=['GET'])
def get_listsub():
    db_sess = db_session.create_session()
    listsub = db_sess.query(ListSub).all()
    return jsonify(
        {
            'listsub':
                [item.to_dict(only=(
                    'id', 'user_id', 'list_id'))
                    for item in listsub]
        }
    )


@blueprint.route('/api/listsub/<int:listsub_id>', methods=['GET'])
def get_one_listsub(listsub_id):
    db_sess = db_session.create_session()
    listsub = db_sess.get(ListSub, listsub_id)
    if not listsub:
        return make_response(jsonify({'error': 'Not found'}), 404)
    return jsonify(
        {
            'wish': listsub.to_dict(only=(
                'id', 'user_id', 'list_id'))
        }
    )


@blueprint.route('/api/listsub', methods=['POST'])
def create_listsub():
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    elif not all(key in request.json for key in
                 ['user_id', 'list_id']):
        return make_response(jsonify({'error': 'Bad request'}), 400)
    db_sess = db_session.create_session()
    listsub = ListSub(
        user_id=request.json['user_id'],
        list_id=request.json['list_id']
    )
    db_sess.add(listsub)
    db_sess.commit()
    return jsonify({'id': listsub.id})
