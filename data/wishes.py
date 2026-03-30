import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Wishes(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'wishes'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    bio = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    url = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    list_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('lists.id'))
    lists = orm.relationship('Lists')

    def __repr__(self):
        return f'<Wish> {self.name}'
