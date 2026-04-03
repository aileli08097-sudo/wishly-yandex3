import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase
import secrets


class Lists(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'lists'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    feast = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    date = sqlalchemy.Column(sqlalchemy.Date,
                                   default=datetime.date.today, nullable=True)
    time = sqlalchemy.Column(sqlalchemy.Time,
                             default=datetime.time(hour=13, minute=30), nullable=True)
    notification = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    token = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=True)
    user = orm.relationship('User')

    def __repr__(self):
        return f'<List> {self.feast}'

    def generate_token(self):
        self.token = secrets.token_urlsafe(32)