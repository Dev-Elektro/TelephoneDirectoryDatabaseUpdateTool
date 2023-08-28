import sys
import time
import signal
from environs import EnvError
from loguru import logger
from active_directory import ActiveDirectory
from config import loadConfig
from database import createDataBaseSession, insertOrUpdate, getAllPCList, updateVersionPC
from models import datetimeNow


def terminate(signal_number, frame):
    logger.info(f'Received signal {signal_number}')
    sys.exit()


def updateDataBase(info: bool = False) -> int:
    with createDataBaseSession(config.db, echo=False)() as session:
        ad = ActiveDirectory(config.ad.server, config.ad.search_tree, config.ad.user, config.ad.password)
        res = ad.connect()
        logger.debug(f"Подключение к Active Directory: {res}")

        for i in ad.getAllData(sleep_sec=1):
            if info:
                logger.info(f"Запись из AD № {ad.count}: {i}")
            insertOrUpdate(session, i)

        logger.debug(f"Обновление версий ОС.")
        for name in getAllPCList(session):
            in_domain, version = ad.getComputerVersion(name)
            updateVersionPC(session, name, in_domain, version)

        return ad.count


if __name__ == '__main__':
    try:
        config = loadConfig(".env")
    except EnvError as e:
        logger.critical(f"Ошибка чтения переменных окружающей среды: {e}")
        sys.exit(1)

    if len(sys.argv) == 1:
        try:
            updateDataBase(info=True)
        except KeyboardInterrupt:
            logger.info("Завершение работы.")
    else:
        logger.remove()
        logger.add(sys.stderr, level="INFO")
        if config.log.path:
            logger.add(config.log.path, level=config.log.level, rotation=config.log.rotation,
                       format="{time:YYYY-MM-DD HH:mm:ss} - {level} - {message}")
        signal.signal(signal.SIGTERM, terminate)
        logger.info(f'Сервис обновления базы данных телефонного справочника запущен.')
        logger.info(f'Запуск обновления в {config.update_start_time} часов.')
        while True:
            dt = datetimeNow()
            if dt.hour in config.update_start_time and dt.minute == 20:
                logger.info('Запущено обновление базы данных.')
                count_entries = updateDataBase(info=False)
                logger.info(f'Обработано {count_entries} записей.')
            time.sleep(60)
