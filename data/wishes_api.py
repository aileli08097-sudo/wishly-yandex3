import flask
from flask import jsonify, make_response, request
from . import db_session
from .wishes import Wishes

blueprint = flask.Blueprint(
    'wishes_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/wishes', methods=['GET'])
def get_wishes():
    db_sess = db_session.create_session()
    wishes = db_sess.query(Wishes).all()
    return jsonify(
        {
            'wishes':
                [item.to_dict(only=(
                    'id', 'name', 'bio', 'url', 'list_id'))
                    for item in wishes]
        }
    )


@blueprint.route('/api/wishes/<int:wishes_id>', methods=['GET'])
def get_one_wish(wishes_id):
    db_sess = db_session.create_session()
    wishes = db_sess.get(Wishes, wishes_id)
    if not wishes:
        return make_response(jsonify({'error': 'Not found'}), 404)
    return jsonify(
        {
            'wish': wishes.to_dict(only=(
                'id', 'name', 'bio', 'url', 'list_id'))
        }
    )


@blueprint.route('/api/wishes', methods=['POST'])
def create_wish():
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    elif not all(key in request.json for key in
                 ['name', 'bio', 'url', 'list_id']):
        return make_response(jsonify({'error': 'Bad request'}), 400)
    db_sess = db_session.create_session()
    wish = Wishes(
        name=request.json['name'],
        bio=request.json['bio'],
        url=request.json['url'],
        list_id=request.json['list_id']
    )
    db_sess.add(wish)
    db_sess.commit()
    return jsonify({'id': wish.id})
