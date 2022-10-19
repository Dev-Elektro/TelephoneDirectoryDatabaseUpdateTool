import time
from datetime import datetime

import pytz as pytz
from ldap3 import Server, Connection, SIMPLE, SYNC, ASYNC, SUBTREE, ALL
from loguru import logger


class SearchResult:
    is_vip: bool = 0
    mail: str = ''
    request: str = ''
    mobile: str = ''
    pc_name: str = ''
    last_logon: datetime = datetime.min
    disabled: bool = 0
    sid: str = ''
    name: str = ''
    account: str = ''
    company: str = ''
    department: str = ''
    position: str = ''
    when_changed: datetime = datetime.min

    def __repr__(self):
        return f"<SearchResult account: {self.account}, name: {self.name}>"


class ActiveDirectory:
    def __init__(self, server: str, search_tree: str, user: str, password: str):
        self.conn = None
        self.server = server
        self.search_tree = search_tree
        self.user = user
        self.password = password
        self.count = 0

    def connect(self) -> bool:
        server = Server(self.server)
        self.conn = Connection(server, user=self.user, password=self.password)
        return self.conn.bind()

    def getAllData(self, sleep_sec: float = 0) -> SearchResult:
        abc = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
        attributes = ['cn', 'mail', 'sAMAccountName', 'pager', 'info', 'objectSid',
                      'physicalDeliveryOfficeName', 'mobile', 'company', 'department', 'title',
                      'wWWHomePage', 'whenChanged', 'lastLogonTimestamp', 'userAccountControl']
        for a in abc:
            for b in abc:
                query = f'(&(objectClass=user)(cn={a}{b}*))'
                if not self.conn.search(self.search_tree, query, SUBTREE, attributes=attributes):
                    continue
                for entry in self.conn.response:
                    entry = entry.get("attributes")
                    if not entry:
                        continue
                    local_tz = pytz.timezone('Europe/Moscow')

                    if 'TEH' in entry.get('pager'):
                        continue

                    result = SearchResult()
                    if 'VIP' in entry.get('pager') or 'VIP' in entry.get('info'):
                        result.is_vip = True
                    if len(entry.get('mail')) > 2:
                        result.mail = entry.get('mail')
                    if len(entry.get('physicalDeliveryOfficeName')) > 2:
                        result.request = entry.get('physicalDeliveryOfficeName')
                    if len(entry.get('mobile')) > 2:
                        result.mobile = entry.get('mobile')
                    if len(entry.get('wWWHomePage')) > 2:
                        result.pc_name = entry.get('wWWHomePage')
                    result.sid = entry.get('objectSid')
                    result.name = entry.get('cn')
                    result.account = entry.get('sAMAccountName')
                    if len(entry.get('company')) > 2:
                        result.company = entry.get('company')
                    if len(entry.get('department')) > 2:
                        result.department = entry.get('department')
                    if len(entry.get('title')) > 2:
                        result.position = entry.get('title')
                    try:
                        if isinstance(entry.get('whenChanged'), datetime):
                            result.when_changed = entry.get('whenChanged').replace(tzinfo=pytz.utc).astimezone(local_tz)
                    except Exception as e:
                        logger.warning(e)
                    if entry.get('userAccountControl') == 514 or entry.get('userAccountControl') == 66050:
                        result.disabled = True
                    try:
                        if isinstance(entry.get('lastLogonTimestamp'), datetime):
                            result.last_logon = entry.get('lastLogonTimestamp').replace(tzinfo=pytz.utc)\
                                .astimezone(local_tz)
                    except Exception as e:
                        logger.warning(e)
                    self.count += 1
                    yield result
                if len(self.conn.response) > 3:
                    time.sleep(sleep_sec)
