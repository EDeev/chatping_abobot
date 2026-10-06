import logging
import sqlite3

# номер счётчика в обработчиках → колонка таблицы статистики
COLUMNS = {1: "mes", 2: "rep", 3: "com", 4: "url", 5: "med", 6: "sti", 7: "voi"}

# Таблица на каждый чат — так устроены рабочие базы бота; имя таблицы — внутренний числовой id чата,
# поэтому перед подстановкой в SQL он приводится к int


def table(group_id):
    return f"[{int(group_id)}]"


class Base:
    def __init__(self, database):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

        # на новой установке таблиц ещё нет
        stat_columns = ", ".join(f"{c} INTEGER" for c in COLUMNS.values())
        with self.connection:
            self.cursor.execute("CREATE TABLE IF NOT EXISTS work (group_id INTEGER NOT NULL, "
                                "state BOOLEAN NOT NULL DEFAULT (True))")
            self.cursor.execute(f"CREATE TABLE IF NOT EXISTS stat (group_id INTEGER NOT NULL, {stat_columns})")
            self.cursor.execute(f"CREATE TABLE IF NOT EXISTS month (group_id INTEGER NOT NULL, {stat_columns})")
            self.cursor.execute("CREATE TABLE IF NOT EXISTS edit (user_id INTEGER NOT NULL)")
            self.cursor.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)")

    def get_meta(self, key):
        with self.connection:
            row = self.cursor.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
            return row[0] if row else None

    def set_meta(self, key, value):
        with self.connection:
            self.cursor.execute("INSERT INTO meta (key, value) VALUES (?, ?) "
                                "ON CONFLICT(key) DO UPDATE SET value = excluded.value", (key, value))

    def reset_month(self):
        """Обнуляем месячную статистику групп"""
        with self.connection:
            self.cursor.execute("UPDATE month SET " + ", ".join(f"{c} = 0" for c in COLUMNS.values()))

    def increment(self, name, group_id, var_id):
        """Счётчик +1 одним запросом: раньше SELECT и UPDATE с ручным +1 теряли сообщения,
        пришедшие одновременно"""
        column = COLUMNS[var_id]
        try:
            with self.connection:
                self.cursor.execute(f"UPDATE {name} SET {column} = {column} + 1 WHERE group_id = ?", (group_id,))
        except sqlite3.Error:
            # статистика не должна мешать остальной обработке сообщения
            logging.exception("Не удалось обновить статистику %s", name)

    # КОМАНДЫ
    def add_group(self, group_id):
        """Добавляем нового пользователя"""
        with self.connection:
            self.cursor.execute("INSERT INTO `work` (`group_id`) VALUES(?)", (group_id,))
            self.cursor.execute("INSERT INTO `stat` (`group_id`, `mes`, `rep`, `com`, `url`, `med`, `sti`, "
                                "`voi`) VALUES(?,?,?,?,?,?,?,?)", (group_id, 0, 0, 0, 0, 0, 0, 0))
            return

    def group_exists(self, group_id):
        """Проверяем, есть ли уже пользователь в базе"""
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `work` WHERE `group_id` = ?', (group_id,)).fetchall()
            return bool(len(result))

    # ТАБЛИЦА STAT
    def update_stat(self, group_id, var_id):
        """Обновляем статистику"""
        self.increment("stat", group_id, var_id)

    def stat_group(self, group_id):
        """Получение данных пользователя"""
        with self.connection:
            self.cursor.execute("SELECT * FROM `stat` WHERE `group_id` = ?", (group_id,))
            data = self.cursor.fetchone()
            return data[1:]

    # ТАБЛИЦА MONTH
    def group_exists_month(self, group_id):
        """Проверяем, есть ли уже пользователь в базе"""
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `month` WHERE `group_id` = ?', (group_id,)).fetchall()
            return bool(len(result))

    def add_group_month(self, group_id):
        """Добавляем нового пользователя"""
        with self.connection:
            return self.cursor.execute("INSERT INTO `month` (`group_id`, `mes`, `rep`, `com`, `url`, `med`, `sti`, "
                                       "`voi`) VALUES(?,?,?,?,?,?,?,?)", (group_id, 0, 0, 0, 0, 0, 0, 0))

    def update_month_stat(self, group_id, var_id):
        """Обновляем статистику"""
        self.increment("month", group_id, var_id)

    def month_stat_group(self, group_id):
        """Получение данных пользователя"""
        with self.connection:
            self.cursor.execute("SELECT * FROM `month` WHERE `group_id` = ?", (group_id,))
            data = self.cursor.fetchone()
            return data[1:]

    # ТАБЛИЦА EDIT
    def add_edit_user(self, user_id):
        """Добавляем нового пользователя"""
        with self.connection:
            return self.cursor.execute("INSERT INTO `edit` (`user_id`) VALUES(?)", (user_id,))

    def edit_user_exists(self, user_id):
        """Проверяем, есть ли уже пользователь в базе"""
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `edit` WHERE `user_id` = ?', (user_id,)).fetchall()
            return bool(len(result))

    def del_edit_user(self, user_id):
        """Удаление пользователя"""
        with self.connection:
            return self.cursor.execute('DELETE FROM `edit` WHERE `user_id` = ?', (user_id,))

    # ТАБЛИЦА WORK
    def check_status(self, group_id):
        """Получаем статус"""
        with self.connection:
            return self.cursor.execute('SELECT `state` FROM `work` WHERE `group_id` = ?', (group_id,)).fetchone()[0]

    def update_status(self, group_id):
        """Обновляем статус"""
        with self.connection:
            state = self.cursor.execute('SELECT `state` FROM `work` WHERE `group_id` = ?', (group_id,)).fetchone()[0]
            return self.cursor.execute("UPDATE `work` SET `state` = ? WHERE `group_id` = ?", (not state, group_id))

    # ЗАКРЫТИЕ ВЫЗОВА
    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()


class User:
    def __init__(self, database):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

        with self.connection:
            self.cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, "
                                "user_id INTEGER NOT NULL)")
            self.cursor.execute("CREATE TABLE IF NOT EXISTS \"groups\" (id INTEGER PRIMARY KEY AUTOINCREMENT, "
                                "group_id INTEGER NOT NULL)")

    # СВЯЗКА ПОЛЬЗОВАТЕЛЯ
    def user_exists(self, user_id):
        """Проверяем, есть ли уже пользователь в базе"""
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `users` WHERE `user_id` = ?', (user_id,)).fetchall()
            return bool(len(result))

    def add_user(self, user_id):
        """Добавляем нового пользователя"""
        with self.connection:
            return self.cursor.execute("INSERT INTO `users` (`user_id`) VALUES(?)", (user_id,))

    def get_user_id(self, user_id):
        """Получаем короткое айди юзера"""
        with self.connection:
            return self.cursor.execute('SELECT `id` FROM `users` WHERE `user_id` = ?', (user_id,)).fetchone()[0]

    def get_first_user_id(self, user_id):
        """Получаем длинное айди юзера"""
        with self.connection:
            return self.cursor.execute('SELECT `user_id` FROM `users` WHERE `id` = ?', (user_id,)).fetchone()[0]

    # СВЯЗКА ГРУППЫ
    def group_exists(self, group_id):
        """Проверяем, есть ли уже группа в базе"""
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `groups` WHERE `group_id` = ?', (group_id,)).fetchall()
            return bool(len(result))

    def add_group(self, group_id):
        """Добавляем новую группу в таблицу"""
        with self.connection:
            return self.cursor.execute("INSERT INTO `groups` (`group_id`) VALUES(?)", (group_id,))

    def get_group_id(self, group_id):
        """Получаем короткое айди юзера"""
        with self.connection:
            return self.cursor.execute('SELECT `id` FROM `groups` WHERE `group_id` = ?', (group_id,)).fetchone()[0]

    def get_first_group_id(self, group_id):
        """Получаем длинное айди юзера"""
        with self.connection:
            return self.cursor.execute('SELECT `group_id` FROM `groups` WHERE `id` = ?', (group_id,)).fetchone()[0]

    def update_group_id(self, from_id, to_id):
        """Заменяем на новый айди"""
        with self.connection:
            return self.cursor.execute("UPDATE `groups` SET `group_id` = ? WHERE `id` = ?", (to_id, from_id))

    # ЗАКРЫТИЕ ВЫЗОВА
    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()


class Group:
    def __init__(self, database):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    # КОМАНДЫ
    def created_group(self, group_id):
        """Создаём новую таблицу"""
        with self.connection:
            return self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS {table(group_id)} (
                                            user_id    INTEGER NOT NULL,
                                            first_name STRING,
                                            mes        INTEGER,
                                            rep        INTEGER,
                                            com        INTEGER,
                                            url        INTEGER,
                                            med        INTEGER,
                                            sti        INTEGER,
                                            voi        INTEGER);""")

    def add_user(self, group_id, user_id, name):
        """Добавляем нового пользователя"""
        with self.connection:
            return self.cursor.execute(f"INSERT INTO {table(group_id)} (`user_id`, `first_name`, `mes`, `rep`, `com`, `url`, "
                                       f"`med`, `sti`, `voi`) VALUES(?,?,?,?,?,?,?,?,?)", (user_id, name, 0, 0, 0, 0, 0,
                                                                                           0, 0))

    def all_names(self, group_id):
        """Список имён"""
        with self.connection:
            return self.cursor.execute(f'SELECT `first_name` FROM {table(group_id)}').fetchall()

    def all_ids(self, group_id):
        """Список айди"""
        with self.connection:
            return self.cursor.execute(f'SELECT `user_id` FROM {table(group_id)}').fetchall()

    def update_stat(self, user_id, group_id, var_id):
        """Обновляем статистику"""
        column = COLUMNS[var_id]
        try:
            with self.connection:
                self.cursor.execute(f"UPDATE {table(group_id)} SET {column} = {column} + 1 WHERE user_id = ?",
                                    (user_id,))
        except sqlite3.Error:
            logging.exception("Не удалось обновить статистику участника")

    def user_exists(self, user_id, group_id):
        """Проверяем, есть ли уже пользователь в базе"""
        with self.connection:
            result = self.cursor.execute(f'SELECT * FROM {table(group_id)} WHERE `user_id` = ?', (user_id,)).fetchall()
            return bool(len(result))

    def update_name(self, user_id, group_id, name):
        """Обновляем имя пользователя"""
        with self.connection:
            return self.cursor.execute(f"UPDATE {table(group_id)} SET `first_name` = ? WHERE `user_id` = ?", (name, user_id))

    def user_name(self, user_id, group_id):
        """Получаем имя пользователя по айди"""
        with self.connection:
            return self.cursor.execute(f"SELECT `first_name` FROM {table(group_id)} WHERE `user_id` = ?", (user_id,)).fetchone()[0]

    def stat_user(self, user_id, group_id):
        """Получение данных пользователя"""
        with self.connection:
            self.cursor.execute(f"SELECT * FROM {table(group_id)} WHERE `user_id` = ?", (user_id,))
            data = self.cursor.fetchone()
            return data[2:]

    def del_user(self, group_id, user_id):
        """Удаление пользователя"""
        with self.connection:
            return self.cursor.execute(f'DELETE FROM {table(group_id)} WHERE `user_id` = ?', (user_id,))

    # ЗАКРЫТИЕ ВЫЗОВА
    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()


class Month:
    def __init__(self, database):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def reset_all(self):
        """Обнуляем месячную статистику участников во всех чатах"""
        with self.connection:
            tables = [r[0] for r in self.cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table'")]
            for name in tables:
                if name.lstrip("-").isdigit():
                    self.cursor.execute(f"UPDATE {table(name)} SET " + ", ".join(f"{c} = 0" for c in COLUMNS.values()))

    # КОМАНДЫ
    def update_stat(self, user_id, group_id, var_id):
        """Обновляем статистику"""
        column = COLUMNS[var_id]
        try:
            with self.connection:
                self.cursor.execute(f"UPDATE {table(group_id)} SET {column} = {column} + 1 WHERE user_id = ?",
                                    (user_id,))
        except sqlite3.Error:
            logging.exception("Не удалось обновить статистику участника")

    def created_group(self, group_id):
        """Создаём новую таблицу"""
        with self.connection:
            return self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS {table(group_id)} (
                                            user_id    INTEGER NOT NULL,
                                            mes        INTEGER,
                                            rep        INTEGER,
                                            com        INTEGER,
                                            url        INTEGER,
                                            med        INTEGER,
                                            sti        INTEGER,
                                            voi        INTEGER);""")

    def add_user(self, group_id, user_id):
        """Добавляем нового пользователя"""
        with self.connection:
            return self.cursor.execute(f"INSERT INTO {table(group_id)} (`user_id`, `mes`, `rep`, `com`, `url`, `med`, "
                                       f"`sti`, `voi`) VALUES(?,?,?,?,?,?,?,?)", (user_id, 0, 0, 0, 0, 0, 0, 0))

    def all_ids(self, group_id):
        """Список айди"""
        with self.connection:
            return self.cursor.execute(f'SELECT `user_id` FROM {table(group_id)}').fetchall()

    def user_exists(self, user_id, group_id):
        """Проверяем, есть ли уже пользователь в базе"""
        with self.connection:
            result = self.cursor.execute(f'SELECT * FROM {table(group_id)} WHERE `user_id` = ?', (user_id,)).fetchall()
            return bool(len(result))

    def stat_user(self, user_id, group_id):
        """Получение данных пользователя"""
        with self.connection:
            self.cursor.execute(f"SELECT * FROM {table(group_id)} WHERE `user_id` = ?", (user_id,))
            data = self.cursor.fetchone()
            return data[1:]

    def del_user(self, group_id, user_id):
        """Удаление пользователя"""
        with self.connection:
            return self.cursor.execute(f'DELETE FROM {table(group_id)} WHERE `user_id` = ?', (user_id,))

    # ЗАКРЫТИЕ ВЫЗОВА
    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()
