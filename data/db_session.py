import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import os

SqlAlchemyBase = orm.declarative_base()

__factory = None


def global_init(db_file):
    global __factory

    if __factory:
        return

    database_url = os.environ.get('DATABASE_URL')

    if database_url:
        engine = sa.create_engine(database_url)
    else:
        if not db_file or not db_file.strip():
            db_file = "db/wishly.db"
        conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
        engine = sa.create_engine(conn_str, echo=True)

    __factory = orm.sessionmaker(bind=engine)

    from . import __all_models

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    if __factory is None:
        if os.environ.get('DATABASE_URL'):
            global_init(None)
        else:
            global_init("db/wishly.db")
    return __factory()
