import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class WishBook(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'listsub'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    wish_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('wishes.id'))
