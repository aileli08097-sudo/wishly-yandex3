import flask
from flask import jsonify, make_response, request
from . import db_session
from .lists import Lists

blueprint = flask.Blueprint(
    'lists_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/lists', methods=['GET'])
def get_lists():
    db_sess = db_session.create_session()
    lists = db_sess.query(Lists).all()
    return jsonify(
        {
            'lists':
                [item.to_dict(only=(
                    'id', 'feast', 'date', 'time', 'notification', 'user_id', 'token'))
                    for item in lists]
        }
    )


@blueprint.route('/api/lists/<int:lists_id>', methods=['GET'])
def get_one_list(lists_id):
    db_sess = db_session.create_session()
    lists = db_sess.get(Lists, lists_id)
    if not lists:
        return make_response(jsonify({'error': 'Not found'}), 404)
    return jsonify(
        {
            'list': lists.to_dict(only=(
                'id', 'feast', 'date', 'time', 'notification', 'user_id', 'token'))
        }
    )


@blueprint.route('/api/lists', methods=['POST'])
def create_list():
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    elif not all(key in request.json for key in
                 ['feast', 'date', 'time', 'notification', 'user_id', 'token']):
        return make_response(jsonify({'error': 'Bad request'}), 400)
    db_sess = db_session.create_session()
    list = Lists(
        feast=request.json['feast'],
        date=request.json['date'],
        time=request.json['time'],
        notification=request.json['notification'],
        user_id=request.json['user_id'],
        token=request.json['token']
    )
    db_sess.add(list)
    db_sess.commit()
    return jsonify({'id': list.id})
