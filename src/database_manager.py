from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert

from src.config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER
from src.models import Patents, Logs

# Строка подключения к базе данных
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# Модель базы данных
Base = declarative_base()

# Создание интерфейса для взаимодействия с БД
engine = create_engine(DATABASE_URL)
# Создатель сессий
session_maker = sessionmaker(bind=engine)


def insert_patent(session, patent):
    '''
    Добавление словаря патента в сессию

    :param session: Сессия, через которую происходит общение с БД
    :param patent: Словарь, содержащий информацию о патенте
    :return: None
    '''

    stmt = insert(Patents).values(patent)
    stmt = stmt.on_conflict_do_nothing()
    session.execute(stmt)


def insert_log(session, log):
    '''
    Добавление лога в сессию

    :param session: Сессия, через которую происходит общение с БД
    :param log: Словарь, содержащий информацию о логе
    :return: None
    '''

    stmt = insert(Logs).values(log)
    session.execute(stmt)
