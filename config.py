from dataclasses import dataclass
from typing import List

from environs import Env
from sqlalchemy.engine import URL


@dataclass
class DbConfig:
    database: str
    username: str
    password: str
    host: str
    port: int

    def construct_sqlalchemy_url(self) -> URL:
        return URL.create(
            drivername="mysql+pymysql",
            username=self.username,
            password=self.password,
            database=self.database,
            host=self.host,
            port=self.port
        )


@dataclass
class ADConfig:
    server: str
    search_tree: str
    user: str
    password: str


@dataclass
class Log:
    path: str
    level: str
    rotation: str


@dataclass
class Config:
    db: DbConfig
    ad: ADConfig
    log: Log
    update_start_time: List[int]


def loadConfig(path: str = None):
    env = Env()
    env.read_env(path)

    return Config(
        db=DbConfig(
            database=env.str('DB_NAME'),
            username=env.str('DB_USER'),
            password=env.str('DB_PASS'),
            host=env.str('DB_HOST'),
            port=env.int('DB_PORT', 3306)
        ),
        ad=ADConfig(
            server=env.str('AD_SERVER'),
            search_tree=env.str('AD_SEARCH_TREE'),
            user=env.str('AD_USER'),
            password=env.str('AD_PASS')
        ),
        log=Log(
            path=env.str('LOG_PATH'),
            level=env.str('LOG_LEVEL'),
            rotation=env.str('LOG_ROTATION')
        ),
        update_start_time=list(map(int, env.list("UPDATE_START_TIME")))
    )
