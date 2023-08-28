from datetime import datetime

import pytz
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


def datetimeNow() -> datetime:
    local_tz = pytz.timezone('Europe/Moscow')
    return datetime.now(local_tz)


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user = Column(String(255))
    pc = Column(String(255))
    date = Column(DateTime, default=datetimeNow(), onupdate=datetimeNow())
    program = Column(String(255))
    history = relationship("History", backref='user', lazy='dynamic')

    def __repr__(self):
        return f"<Users: user={self.user}, pc={self.pc}, program={self.program}>"


class History(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    query = Column(String(255))
    date = Column(DateTime, default=datetimeNow(), onupdate=datetimeNow())

    def __repr__(self):
        return f"<History: user_id={self.user_id}, query={self.query}>"


class People(Base):
    __tablename__ = "people"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    full_name = Column(String(255))
    short_name = Column(String(255))
    account = Column(String(255))
    verified = Column(Integer)
    vip = Column(Integer)
    sid = Column(String(255))
    mail = Column(String(255))
    company = Column(String(255))
    department = Column(String(255))
    position = Column(String(255))
    location = Column(String(255))
    isui = Column(String(255))
    lastLogon = Column(String(255))
    task_create = Column(String(255))
    disabled = Column(Integer)
    phones = relationship("PhoneList", backref='people', lazy='dynamic')
    computers = relationship("ComputerList", backref='people', lazy='dynamic')

    def __repr__(self):
        return f"<People: id={self.id}, full_name={self.full_name}, account={self.account}, SID={self.sid}>"


class PhoneList(Base):
    __tablename__ = "phone_list"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    id_people = Column(Integer, ForeignKey("people.id", ondelete="CASCADE", onupdate="CASCADE"))
    number = Column(String(255))
    type = Column(Integer)
    last_change = Column(DateTime, default=datetimeNow(), onupdate=datetimeNow())

    def __repr__(self):
        return f"<PhoneList: id={self.id}, id_people={self.id_people}, number={self.number}, type={self.type}>"


class ComputerList(Base):
    __tablename__ = "pc_list"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    id_people = Column(Integer, ForeignKey("people.id", ondelete="CASCADE", onupdate="CASCADE"))
    pc_name = Column(String(255))
    when_changed = Column(DateTime)
    in_domain = Column(Integer)
    version_os = Column(String(255))

    def __repr__(self):
        return f"<ComputerList: id={self.id}, id_people={self.id_people}, pc_name={self.pc_name}>"
