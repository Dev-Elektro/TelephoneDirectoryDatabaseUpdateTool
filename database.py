from typing import List

from loguru import logger
from sqlalchemy import create_engine, select, delete
from sqlalchemy.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm import sessionmaker, Session

from active_directory import SearchResult
from config import DbConfig
from models import Base, People, PhoneList, ComputerList


def createDataBaseSession(db: DbConfig, echo=False):
    engine = create_engine(db.construct_sqlalchemy_url(), echo=echo)

    Base.metadata.create_all(engine)

    return sessionmaker(bind=engine, expire_on_commit=False)


def shortName(name: str) -> str:
    """Конвертирует полное ФИО в сокращенное."""
    short_name = ''
    name = name.split(' ')
    if len(name) > 2:
        for i in name[:len(name) - 2]:
            short_name += i + ' '
        short_name += name[len(name) - 2][:1] + '.'
        short_name += name[len(name) - 1][:1] + '.'
    if len(name) == 2:
        short_name += name[0] + ' '
        short_name += name[1][:1] + '.'
    if len(name) == 1:
        short_name += name[0]
    return short_name


def getAllPCList(session: Session) -> List[str]:
    list_names = []
    raw = select(ComputerList)
    for i in session.execute(raw).fetchall():
        pc_name = i[0].pc_name
        if not pc_name:
            continue
        name = pc_name.split(' - ')[0]
        if name not in list_names:
            list_names.append(name)
    return list_names


def updateVersionPC(session: Session, name: str, in_domain: bool, version: str):
    raw = select(ComputerList).where(ComputerList.pc_name.like(f"{name}%"))
    try:
        results = session.scalars(raw).all()
        for pc_obj in results:
            pc_obj.in_domain = in_domain
            pc_obj.version_os = version
            session.commit()
            session.flush()
    except NoResultFound:
        pass


def insertOrUpdate(session: Session, item: SearchResult):
    """Добавляет или обновляет запись в базе данных."""
    try:
        # Запрос в базе существует ли пользователя в базе с текущим SID.
        raw = select(People).where(People.sid == item.sid)
        people: People = session.scalars(raw).one()
        if people.verified > 1 and not people.disabled:
            people.verified = 0
        logger.debug(f"Update: {item.account}")
    except NoResultFound:
        # Пользователя в базе нет, создаем новую запись.
        people = People()
        people.verified = 0
        logger.debug(f"Insert: {item.account}")

    people.full_name = item.name
    people.short_name = shortName(item.name)
    people.account = item.account
    people.vip = item.is_vip
    people.sid = item.sid
    people.mail = item.mail
    people.company = item.company
    people.department = item.department
    people.position = item.position
    people.lastLogon = item.last_logon
    people.task_create = item.request
    people.disabled = item.disabled

    session.add(people)
    session.commit()

    # Заполняем таблицу с телефонными номерами.
    try:
        phone = people.phones.where(PhoneList.type == 0).one()
    except NoResultFound:
        phone = PhoneList(id_people=people.id)
        people.phones.append(phone)
    phone.type = 0
    phone.number = item.mobile
    session.commit()

    # Если в AD есть информация об имени компьютера, то заносим в базу данных.
    if not item.pc_name:
        return
    buf = item.pc_name.split(" - ")
    try:
        # Проверяем если ли запись в базе данных для текущего имени компьютера.
        pc_list = people.computers.where(ComputerList.pc_name.like(f"{buf[0]}%")).one()
    except NoResultFound:
        # Если нет, то создаем новую запись
        pc_list = ComputerList(id_people=people.id)
        people.computers.append(pc_list)
    except MultipleResultsFound:
        logger.warning(f'Найдены дублирующиеся записи в таблице: {ComputerList.__tablename__} для {buf[0]}. Удаление.')
        raw = delete(ComputerList).where(ComputerList.id_people == people.id)\
            .where(ComputerList.pc_name.like(f"{buf[0]}%"))\
            .execution_options(synchronize_session="fetch")
        session.execute(raw)
        # Создаем новую запись
        pc_list = ComputerList(id_people=people.id)
        people.computers.append(pc_list)
    pc_list.pc_name = item.pc_name
    pc_list.when_changed = item.when_changed
    session.commit()

    # Проверяем объем списка компьютеров, оставляем 5 свежих записей, остальное удаляем.
    raw = select(ComputerList).where(ComputerList.id_people == people.id).order_by(ComputerList.when_changed.desc())\
        .limit(10).offset(5)
    pc_list_for_delete: List[ComputerList] = session.scalars(raw).all()
    for i in pc_list_for_delete:
        raw = delete(ComputerList).where(ComputerList.id == i.id).execution_options(synchronize_session="fetch")
        session.execute(raw)
