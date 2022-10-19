# TelephoneDirectoryDatabaseUpdateTool
Выгрузка данных из Active Directory для обновления базы данных справочника телефонов.

## Установка в Linux
1. cd /opt/
2. sudo git clone https://github.com/Dev-Elektro/TelephoneDirectoryDatabaseUpdateTool.git
3. sudo chown -R user:user /opt/TelephoneDirectoryDatabaseUpdateTool
4. sudo touch /var/log/telephoneDirectoryDBUpdateTool.log
5. sudo chown -R user:user /var/log/telephoneDirectoryDBUpdateTool.log
6. cd TelephoneDirectoryDatabaseUpdateTool
7. mv .env.dist .env
8. nano .env `Редактируем настройки под себя`
9. python3 -m venv venv
10. source venv/bin/activate
11. pip install -r requirements.txt
12. nano systemd/telephone-directory-db-update-tool.service `В секции Service указываем своего пользователя и группу`
13. sudo cp systemd/telephone-directory-db-update-tool.service /etc/systemd/system/
14. sudo systemctl daemon-reload
15. sudo systemctl enable telephone-directory-db-update-tool.service
16. sudo sudo systemctl start telephone-directory-db-update-tool.service
