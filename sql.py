import sqlite3


class SQLighter:
    def __init__(self, database):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()
        self.cursor.execute("PRAGMA temp_store = 2")

    # СВЯЗКА ГРУППЫ
    def group_exists(self, id_group):
        """Проверяем, есть ли уже группа в базе"""
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `group` WHERE `id_group` = ?', (id_group,)).fetchall()
            return bool(len(result))

    def add_group(self, id_group, status=True):
        """Добавляем новую группу в таблицу"""
        with self.connection:
            return self.cursor.execute("INSERT INTO `group` (`id_group`, `status`, `time`, `message`, `reply`, "
                                       "`command`, `url`, `tik_tok`, `media`, `sticker`, `voice`, `bool`, `cool`) "
                                       "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                                       (id_group, status, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))

    def add_month_group(self, id_group):
        """Добавляем новую группу в таблицу месяца"""
        with self.connection:
            return self.cursor.execute("INSERT INTO `month` (`id_group`, `message`, `reply`, `command`, `url`, "
                                       "`tik_tok`, `media`, `sticker`, `voice`, `bool`, `cool`) "
                                       "VALUES(?,?,?,?,?,?,?,?,?,?,?)", (id_group, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))

    def created_group(self, id_group):
    	"""Создаём новую таблицу"""
    	with self.connection:
    		return self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS [{id_group}] (
    									id         INTEGER       PRIMARY KEY AUTOINCREMENT,
    									id_user    VARCHAR (255) NOT NULL,
    									first_name TEXT (40)     NOT NULL,
                                        edit       BOOLEAN       NOT NULL
                                                                 DEFAULT (FALSE),
                                        time       INTEGER       NOT NULL
                                                                 DEFAULT (1),
									    message    INTEGER       NOT NULL,
                                        reply      INTEGER       NOT NULL,
                                        command    INTEGER       NOT NULL,
                                        url        INTEGER       NOT NULL,
                                        tik_tok    INTEGER       NOT NULL,
                                        media      INTEGER       NOT NULL,
                                        sticker    INTEGER       NOT NULL,
                                        voice      INTEGER       NOT NULL,
                                        bool       INTEGER       NOT NULL,
                                        cool       INTEGER       NOT NULL
                                        );""")

    def update_status_group(self, id_group, status):
        """Обновляем статус группы"""
        with self.connection:
            return self.cursor.execute("UPDATE `group` SET `status` = ? WHERE `id_group` = ?", (status, id_group))

    def get_group(self, status=True):
        """Получаем все активные группы"""
        with self.connection:
            return self.cursor.execute("SELECT * FROM `group` WHERE `status` = ?", (status,)).fetchall()

    def id_group_lst(self, status=True):
        """Список айди активных групп"""
        with self.connection:
            return [i[1] for i in self.cursor.execute("SELECT * FROM `group` WHERE `status` = ?", (status,)).fetchall()]

    def all_id_group_lst(self):
        """Список всех айди групп"""
        with self.connection:
            return [i[0] for i in self.cursor.execute(f'SELECT id_group FROM `group`').fetchall()]

    def statistics_group(self, id_group, var):
        """Обновляем статистику"""
        with self.connection:
            self.cursor.execute("SELECT * FROM `group` WHERE `id_group` = ?", (id_group,))
            if var == 0:
                return self.cursor.execute("UPDATE `group` SET `time` = ? WHERE `id_group` = ?",
                                           ((self.cursor.fetchone()[3] + 1), id_group))
            elif var == 1:
                return self.cursor.execute("UPDATE `group` SET `message` = ? WHERE `id_group` = ?",
                                           ((self.cursor.fetchone()[4] + 1), id_group))
            elif var == 2:
                return self.cursor.execute("UPDATE `group` SET `reply` = ? WHERE `id_group` = ?",
                                           ((self.cursor.fetchone()[5] + 1), id_group))
            elif var == 3:
                return self.cursor.execute("UPDATE `group` SET `command` = ? WHERE `id_group` = ?",
                                           ((self.cursor.fetchone()[6] + 1), id_group))
            elif var == 4:
                return self.cursor.execute("UPDATE `group` SET `url` = ? WHERE `id_group` = ?",
                                           ((self.cursor.fetchone()[7] + 1), id_group))
            elif var == 5:
                return self.cursor.execute("UPDATE `group` SET `tik_tok` = ? WHERE `id_group` = ?",
                                           ((self.cursor.fetchone()[8] + 1), id_group))
            elif var == 6:
                return self.cursor.execute("UPDATE `group` SET `media` = ? WHERE `id_group` = ?",
                                           ((self.cursor.fetchone()[9] + 1), id_group))
            elif var == 7:
                return self.cursor.execute("UPDATE `group` SET `sticker` = ? WHERE `id_group` = ?",
                                           ((self.cursor.fetchone()[10] + 1), id_group))
            elif var == 8:
                return self.cursor.execute("UPDATE `group` SET `voice` = ? WHERE `id_group` = ?",
                                           ((self.cursor.fetchone()[11] + 1), id_group))
            elif var == 9:
                return self.cursor.execute("UPDATE `group` SET `bool` = ? WHERE `id_group` = ?",
                                           ((self.cursor.fetchone()[12] + 1), id_group))
            elif var == 10:
                return self.cursor.execute("UPDATE `group` SET `cool` = ? WHERE `id_group` = ?",
                                           ((self.cursor.fetchone()[13] + 1), id_group))

    def stat_element_group(self, id_group):
        """Получение данных группы"""
        with self.connection:
            self.cursor.execute("SELECT * FROM `group` WHERE `id_group` = ?", (id_group,))
            data = self.cursor.fetchone()
            time, message, reply, command, url = int(data[3]), int(data[4]), int(data[5]), int(data[6]), int(data[7])
            tik_tok, media, sticker, voice = int(data[8]), int(data[9]), int(data[10]), int(data[11])
            bol, cool = int(data[12]), int(data[13])
            return [message, reply, command, url, tik_tok, media, sticker, voice, time, bol, cool]

    def stat_element_month_group(self, id_group):
        """Получение месячных данных группы"""
        with self.connection:
            self.cursor.execute("SELECT * FROM `month` WHERE `id_group` = ?", (id_group,))
            data = self.cursor.fetchone()
            message, reply, command, url = int(data[2]), int(data[3]), int(data[4]), int(data[5])
            tik_tok, media, sticker, voice = int(data[6]), int(data[7]), int(data[8]), int(data[9])
            bol, cool = int(data[10]), int(data[11])
            return [message, reply, command, url, tik_tok, media, sticker, voice, bol, cool]

    def month_stat_group(self, id_group):
        """Перезапись месечной статистики"""
        with self.connection:
            self.cursor.execute("SELECT * FROM `group` WHERE `id_group` = ?", (id_group,))
            group = self.cursor.fetchone()

            self.cursor.execute("SELECT * FROM `month` WHERE `id_group` = ?", (id_group,))
            month = self.cursor.fetchone()

            message, reply, command = (group[4] - month[2]), (group[5] - month[3]), (group[6] - month[4])
            url, tik_tok, media = (group[7] - month[5]), (group[8] - month[6]), (group[9] - month[7])
            sticker, voice, bol = (group[10] - month[8]), (group[11] - month[9]), (group[12] - month[10])
            cool = (group[13] - month[11])

            self.cursor.execute("UPDATE `month` SET `message` = ? WHERE `id_group` = ?", ((group[4]), id_group))
            self.cursor.execute("UPDATE `month` SET `reply` = ? WHERE `id_group` = ?", ((group[5]), id_group))
            self.cursor.execute("UPDATE `month` SET `command` = ? WHERE `id_group` = ?", ((group[6]), id_group))
            self.cursor.execute("UPDATE `month` SET `url` = ? WHERE `id_group` = ?", ((group[7]), id_group))
            self.cursor.execute("UPDATE `month` SET `tik_tok` = ? WHERE `id_group` = ?", ((group[8]), id_group))
            self.cursor.execute("UPDATE `month` SET `media` = ? WHERE `id_group` = ?", ((group[9]), id_group))
            self.cursor.execute("UPDATE `month` SET `sticker` = ? WHERE `id_group` = ?", ((group[10]), id_group))
            self.cursor.execute("UPDATE `month` SET `voice` = ? WHERE `id_group` = ?", ((group[11]), id_group))
            self.cursor.execute("UPDATE `month` SET `bool` = ? WHERE `id_group` = ?", ((group[12]), id_group))
            self.cursor.execute("UPDATE `month` SET `cool` = ? WHERE `id_group` = ?", ((group[13]), id_group))

            return [message, reply, command, url, tik_tok, media, sticker, voice, bol, cool]

    # СВЯЗКА ПОЛЬЗОВАТЕЛЯ
    def user_exists(self, id_user, db):
        """Проверяем, есть ли уже пользователь в базе"""
        with self.connection:
            result = self.cursor.execute(f'SELECT * FROM `{db}` WHERE `id_user` = ?', (id_user,)).fetchall()
            return bool(len(result))

    def add_user(self, id_user, name, db):
        """Добавляем нового пользователя"""
        with self.connection:
            return self.cursor.execute(f"INSERT INTO `{db}` (`id_user`, `first_name`, `edit`, `time`, `message`, "
                                       f"`reply`, `command`, `url`, `tik_tok`, `media`, `sticker`, `voice`, `bool`, "
                                       f"`cool`) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                                       (id_user, name, False, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))

    def update_name(self, id_user, name, db):
        """Обновляем имя пользователя"""
        with self.connection:
            return self.cursor.execute(f"UPDATE `{db}` SET `first_name` = ? WHERE `id_user` = ?", (name, id_user))


    def edit_name(self, id_user, name, db, var):
        """Заменяем имеющиеся имя на желаемое"""
        with self.connection:
            if var == 1:
                self.cursor.execute(f"UPDATE `{db}` SET `edit` = ? WHERE `id_user` = ?", (True, id_user))
                return self.cursor.execute(f"UPDATE `{db}` SET `first_name` = ? WHERE `id_user` = ?", (name, id_user))
            elif var == 0:
                self.cursor.execute(f"UPDATE `{db}` SET `edit` = ? WHERE `id_user` = ?", (False, id_user))
                return self.cursor.execute(f"UPDATE `{db}` SET `first_name` = ? WHERE `id_user` = ?", (name, id_user))

    def get_users(self, db, status=True):
        """Получаем всех активных пользователей"""
        with self.connection:
            return [i[1] for i in self.cursor.execute(f"SELECT * FROM `{db}` WHERE `edit` = ?", (status,)).fetchall()]

    def id_lst(self, db):
        """Список айди"""
        with self.connection:
            return [i[0] for i in self.cursor.execute(f'SELECT id_user FROM `{db}`').fetchall()]

    def name_lst(self, db):
        """Список имён"""
        with self.connection:
            return [i[0] for i in self.cursor.execute(f'SELECT first_name FROM `{db}`').fetchall()]

    def user_statistic(self, id_user, id_group, var):
        """Обновляем статистику"""
        with self.connection:
            self.cursor.execute(f"SELECT * FROM `{id_group}` WHERE `id_user` = ?", (id_user,))
            if var == 0:
                return self.cursor.execute(f"UPDATE `{id_group}` SET `time` = ? WHERE `id_user` = ?",
                                           ((self.cursor.fetchone()[4] + 1), id_user))
            elif var == 1:
                return self.cursor.execute(f"UPDATE `{id_group}` SET `message` = ? WHERE `id_user` = ?",
                                           ((self.cursor.fetchone()[5] + 1), id_user))
            elif var == 2:
                return self.cursor.execute(f"UPDATE `{id_group}` SET `reply` = ? WHERE `id_user` = ?",
                                           ((self.cursor.fetchone()[6] + 1), id_user))
            elif var == 3:
                return self.cursor.execute(f"UPDATE `{id_group}` SET `command` = ? WHERE `id_user` = ?",
                                           ((self.cursor.fetchone()[7] + 1), id_user))
            elif var == 4:
                return self.cursor.execute(f"UPDATE `{id_group}` SET `url` = ? WHERE `id_user` = ?",
                                           ((self.cursor.fetchone()[8] + 1), id_user))
            elif var == 5:
                return self.cursor.execute(f"UPDATE `{id_group}` SET `tik_tok` = ? WHERE `id_user` = ?",
                                           ((self.cursor.fetchone()[9] + 1), id_user))
            elif var == 6:
                return self.cursor.execute(f"UPDATE `{id_group}` SET `media` = ? WHERE `id_user` = ?",
                                           ((self.cursor.fetchone()[10] + 1), id_user))
            elif var == 7:
                return self.cursor.execute(f"UPDATE `{id_group}` SET `sticker` = ? WHERE `id_user` = ?",
                                           ((self.cursor.fetchone()[11] + 1), id_user))
            elif var == 8:
                return self.cursor.execute(f"UPDATE `{id_group}` SET `voice` = ? WHERE `id_user` = ?",
                                           ((self.cursor.fetchone()[12] + 1), id_user))
            elif var == 9:
                return self.cursor.execute(f"UPDATE `{id_group}` SET `bool` = ? WHERE `id_user` = ?",
                                           ((self.cursor.fetchone()[13] + 1), id_user))
            elif var == 10:
                return self.cursor.execute(f"UPDATE `{id_group}` SET `cool` = ? WHERE `id_user` = ?",
                                           ((self.cursor.fetchone()[14] + 1), id_user))

    def stat_element_user(self, id_user, id_group):
        """Получение данных пользователя"""
        with self.connection:
            self.cursor.execute(f"SELECT * FROM `{id_group}` WHERE `id_user` = ?", (id_user,))
            data = self.cursor.fetchone()
            time, message, reply, command, url = int(data[4]), int(data[5]), int(data[6]), int(data[7]), int(data[8])
            tik_tok, media, sticker, voice = int(data[9]), int(data[10]), int(data[11]), int(data[12])
            bol, cool = int(data[13]), int(data[14])
            return [message, reply, command, url, tik_tok, media, sticker, voice, time, bol, cool]

    def get_name_user(self, id_user, id_group):
        """Получение имени пользователя"""
        with self.connection:
            self.cursor.execute(f"SELECT * FROM `{id_group}` WHERE `id_user` = ?", (id_user,))
            return self.cursor.fetchone()[2]

    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()