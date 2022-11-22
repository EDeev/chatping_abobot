import sqlite3


class Base:
    def __init__(self, database):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    # КОМАНДЫ
    def add_group(self, group_id):
        """Добавляем нового пользователя"""
        with self.connection:
            self.cursor.execute(f"INSERT INTO `work` (`group_id`) VALUES(?)", (group_id,))
            self.cursor.execute(f"INSERT INTO `stat` (`group_id`, `mes`, `rep`, `com`, `url`, `med`, `sti`, "
                                f"`voi`) VALUES(?,?,?,?,?,?,?,?)", (group_id, 0, 0, 0, 0, 0, 0, 0))
            return

    def group_exists(self, group_id):
        """Проверяем, есть ли уже пользователь в базе"""
        with self.connection:
            result = self.cursor.execute(f'SELECT * FROM `work` WHERE `group_id` = ?', (group_id,)).fetchall()
            return bool(len(result))

    # ТАБЛИЦА STAT
    def update_stat(self, group_id, var_id):
        """Обновляем статистику"""
        try:
            with self.connection:
                self.cursor.execute(f"SELECT * FROM `stat` WHERE `group_id` = ?", (group_id,))
                if var_id == 1:
                    return self.cursor.execute(f"UPDATE `stat` SET `mes` = ? WHERE `group_id` = ?",
                                               ((self.cursor.fetchone()[1] + 1), group_id))
                elif var_id == 2:
                    return self.cursor.execute(f"UPDATE `stat` SET `rep` = ? WHERE `group_id` = ?",
                                               ((self.cursor.fetchone()[2] + 1), group_id))
                elif var_id == 3:
                    return self.cursor.execute(f"UPDATE `stat` SET `com` = ? WHERE `group_id` = ?",
                                               ((self.cursor.fetchone()[3] + 1), group_id))
                elif var_id == 4:
                    return self.cursor.execute(f"UPDATE `stat` SET `url` = ? WHERE `group_id` = ?",
                                               ((self.cursor.fetchone()[4] + 1), group_id))
                elif var_id == 5:
                    return self.cursor.execute(f"UPDATE `stat` SET `med` = ? WHERE `group_id` = ?",
                                               ((self.cursor.fetchone()[5] + 1), group_id))
                elif var_id == 6:
                    return self.cursor.execute(f"UPDATE `stat` SET `sti` = ? WHERE `group_id` = ?",
                                               ((self.cursor.fetchone()[6] + 1), group_id))
                elif var_id == 7:
                    return self.cursor.execute(f"UPDATE `stat` SET `voi` = ? WHERE `group_id` = ?",
                                               ((self.cursor.fetchone()[7] + 1), group_id))
        except Exception as e:
            print(repr(e))

    def stat_group(self, group_id):
        """Получение данных пользователя"""
        with self.connection:
            self.cursor.execute(f"SELECT * FROM `stat` WHERE `group_id` = ?", (group_id,))
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
        try:
            with self.connection:
                self.cursor.execute(f"SELECT * FROM `month` WHERE `group_id` = ?", (group_id,))
                if var_id == 1:
                    return self.cursor.execute(f"UPDATE `month` SET `mes` = ? WHERE `group_id` = ?",
                                               ((self.cursor.fetchone()[1] + 1), group_id))
                elif var_id == 2:
                    return self.cursor.execute(f"UPDATE `month` SET `rep` = ? WHERE `group_id` = ?",
                                               ((self.cursor.fetchone()[2] + 1), group_id))
                elif var_id == 3:
                    return self.cursor.execute(f"UPDATE `month` SET `com` = ? WHERE `group_id` = ?",
                                               ((self.cursor.fetchone()[3] + 1), group_id))
                elif var_id == 4:
                    return self.cursor.execute(f"UPDATE `month` SET `url` = ? WHERE `group_id` = ?",
                                               ((self.cursor.fetchone()[4] + 1), group_id))
                elif var_id == 5:
                    return self.cursor.execute(f"UPDATE `month` SET `med` = ? WHERE `group_id` = ?",
                                               ((self.cursor.fetchone()[5] + 1), group_id))
                elif var_id == 6:
                    return self.cursor.execute(f"UPDATE `month` SET `sti` = ? WHERE `group_id` = ?",
                                               ((self.cursor.fetchone()[6] + 1), group_id))
                elif var_id == 7:
                    return self.cursor.execute(f"UPDATE `month` SET `voi` = ? WHERE `group_id` = ?",
                                               ((self.cursor.fetchone()[7] + 1), group_id))
        except Exception as e:
            print(repr(e))

    def month_stat_group(self, group_id):
        """Получение данных пользователя"""
        with self.connection:
            self.cursor.execute(f"SELECT * FROM `month` WHERE `group_id` = ?", (group_id,))
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
            return self.cursor.execute(f'DELETE FROM `edit` WHERE `user_id` = ?', (user_id,))

    # ТАБЛИЦА WORK
    def check_status(self, group_id):
        """Получаем статус"""
        with self.connection:
            return self.cursor.execute(f'SELECT `state` FROM `work` WHERE `group_id` = ?', (group_id,)).fetchone()[0]

    def update_status(self, group_id):
        """Обновляем статус"""
        with self.connection:
            state = self.cursor.execute(f'SELECT `state` FROM `work` WHERE `group_id` = ?', (group_id,)).fetchone()[0]
            return self.cursor.execute(f"UPDATE `work` SET `state` = ? WHERE `group_id` = ?", (not state, group_id))

    # ЗАКРЫТИЕ ВЫЗОВА
    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()


class User:
    def __init__(self, database):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    # СВЯЗКА ПОЛЬЗОВАТЕЛЯ
    def user_exists(self, user_id):
        """Проверяем, есть ли уже пользователь в базе"""
        with self.connection:
            result = self.cursor.execute(f'SELECT * FROM `users` WHERE `user_id` = ?', (user_id,)).fetchall()
            return bool(len(result))

    def add_user(self, user_id):
        """Добавляем нового пользователя"""
        with self.connection:
            return self.cursor.execute(f"INSERT INTO `users` (`user_id`) VALUES(?)", (user_id,))

    def get_user_id(self, user_id):
        """Получаем короткое айди юзера"""
        with self.connection:
            return self.cursor.execute(f'SELECT `id` FROM `users` WHERE `user_id` = ?', (user_id,)).fetchone()[0]

    def get_first_user_id(self, user_id):
        """Получаем длинное айди юзера"""
        with self.connection:
            return self.cursor.execute(f'SELECT `user_id` FROM `users` WHERE `id` = ?', (user_id,)).fetchone()[0]

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
            return self.cursor.execute(f'SELECT `id` FROM `groups` WHERE `group_id` = ?', (group_id,)).fetchone()[0]

    def get_first_group_id(self, group_id):
        """Получаем длинное айди юзера"""
        with self.connection:
            return self.cursor.execute(f'SELECT `group_id` FROM `groups` WHERE `id` = ?', (group_id,)).fetchone()[0]

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
            return self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS [{group_id}] (
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
            return self.cursor.execute(f"INSERT INTO `{group_id}` (`user_id`, `first_name`, `mes`, `rep`, `com`, `url`, "
                                       f"`med`, `sti`, `voi`) VALUES(?,?,?,?,?,?,?,?,?)", (user_id, name, 0, 0, 0, 0, 0,
                                                                                           0, 0))

    def all_names(self, group_id):
        """Список имён"""
        with self.connection:
            return self.cursor.execute(f'SELECT `first_name` FROM `{group_id}`').fetchall()

    def all_ids(self, group_id):
        """Список айди"""
        with self.connection:
            return self.cursor.execute(f'SELECT `user_id` FROM `{group_id}`').fetchall()

    def update_stat(self, user_id, group_id, var_id):
        """Обновляем статистику"""
        try:
            with self.connection:
                self.cursor.execute(f"SELECT * FROM `{group_id}` WHERE `user_id` = ?", (user_id,))
                if var_id == 1:
                    return self.cursor.execute(f"UPDATE `{group_id}` SET `mes` = ? WHERE `user_id` = ?",
                                               ((self.cursor.fetchone()[2] + 1), user_id))
                elif var_id == 2:
                    return self.cursor.execute(f"UPDATE `{group_id}` SET `rep` = ? WHERE `user_id` = ?",
                                               ((self.cursor.fetchone()[3] + 1), user_id))
                elif var_id == 3:
                    return self.cursor.execute(f"UPDATE `{group_id}` SET `com` = ? WHERE `user_id` = ?",
                                               ((self.cursor.fetchone()[4] + 1), user_id))
                elif var_id == 4:
                    return self.cursor.execute(f"UPDATE `{group_id}` SET `url` = ? WHERE `user_id` = ?",
                                               ((self.cursor.fetchone()[5] + 1), user_id))
                elif var_id == 5:
                    return self.cursor.execute(f"UPDATE `{group_id}` SET `med` = ? WHERE `user_id` = ?",
                                               ((self.cursor.fetchone()[6] + 1), user_id))
                elif var_id == 6:
                    return self.cursor.execute(f"UPDATE `{group_id}` SET `sti` = ? WHERE `user_id` = ?",
                                               ((self.cursor.fetchone()[7] + 1), user_id))
                elif var_id == 7:
                    return self.cursor.execute(f"UPDATE `{group_id}` SET `voi` = ? WHERE `user_id` = ?",
                                               ((self.cursor.fetchone()[8] + 1), user_id))
        except Exception as e:
            print(repr(e))

    def user_exists(self, user_id, group_id):
        """Проверяем, есть ли уже пользователь в базе"""
        with self.connection:
            result = self.cursor.execute(f'SELECT * FROM `{group_id}` WHERE `user_id` = ?', (user_id,)).fetchall()
            return bool(len(result))

    def update_name(self, user_id, group_id, name):
        """Обновляем имя пользователя"""
        with self.connection:
            return self.cursor.execute(f"UPDATE `{group_id}` SET `first_name` = ? WHERE `user_id` = ?", (name, user_id))

    def user_name(self, user_id, group_id):
        """Получаем имя пользователя по айди"""
        with self.connection:
            return self.cursor.execute(f"SELECT `first_name` FROM `{group_id}` WHERE `user_id` = ?", (user_id,)).fetchone()[0]

    def stat_user(self, user_id, group_id):
        """Получение данных пользователя"""
        with self.connection:
            self.cursor.execute(f"SELECT * FROM `{group_id}` WHERE `user_id` = ?", (user_id,))
            data = self.cursor.fetchone()
            return data[2:]

    def del_user(self, group_id, user_id):
        """Удаление пользователя"""
        with self.connection:
            return self.cursor.execute(f'DELETE FROM `{group_id}` WHERE `user_id` = ?', (user_id,))

    # ЗАКРЫТИЕ ВЫЗОВА
    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()


class Month:
    def __init__(self, database):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    # КОМАНДЫ
    def update_stat(self, user_id, group_id, var_id):
        """Обновляем статистику"""
        try:
            with self.connection:
                self.cursor.execute(f"SELECT * FROM `{group_id}` WHERE `user_id` = ?", (user_id,))
                if var_id == 1:
                    return self.cursor.execute(f"UPDATE `{group_id}` SET `mes` = ? WHERE `user_id` = ?",
                                               ((self.cursor.fetchone()[1] + 1), user_id))
                elif var_id == 2:
                    return self.cursor.execute(f"UPDATE `{group_id}` SET `rep` = ? WHERE `user_id` = ?",
                                               ((self.cursor.fetchone()[2] + 1), user_id))
                elif var_id == 3:
                    return self.cursor.execute(f"UPDATE `{group_id}` SET `com` = ? WHERE `user_id` = ?",
                                               ((self.cursor.fetchone()[3] + 1), user_id))
                elif var_id == 4:
                    return self.cursor.execute(f"UPDATE `{group_id}` SET `url` = ? WHERE `user_id` = ?",
                                               ((self.cursor.fetchone()[4] + 1), user_id))
                elif var_id == 5:
                    return self.cursor.execute(f"UPDATE `{group_id}` SET `med` = ? WHERE `user_id` = ?",
                                               ((self.cursor.fetchone()[5] + 1), user_id))
                elif var_id == 6:
                    return self.cursor.execute(f"UPDATE `{group_id}` SET `sti` = ? WHERE `user_id` = ?",
                                               ((self.cursor.fetchone()[6] + 1), user_id))
                elif var_id == 7:
                    return self.cursor.execute(f"UPDATE `{group_id}` SET `voi` = ? WHERE `user_id` = ?",
                                               ((self.cursor.fetchone()[7] + 1), user_id))
        except Exception as e:
            print(repr(e))

    def created_group(self, group_id):
        """Создаём новую таблицу"""
        with self.connection:
            return self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS [{group_id}] (
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
            return self.cursor.execute(f"INSERT INTO `{group_id}` (`user_id`, `mes`, `rep`, `com`, `url`, `med`, "
                                       f"`sti`, `voi`) VALUES(?,?,?,?,?,?,?,?)", (user_id, 0, 0, 0, 0, 0, 0, 0))

    def all_ids(self, group_id):
        """Список айди"""
        with self.connection:
            return self.cursor.execute(f'SELECT `user_id` FROM `{group_id}`').fetchall()

    def user_exists(self, user_id, group_id):
        """Проверяем, есть ли уже пользователь в базе"""
        with self.connection:
            result = self.cursor.execute(f'SELECT * FROM `{group_id}` WHERE `user_id` = ?', (user_id,)).fetchall()
            return bool(len(result))

    def stat_user(self, user_id, group_id):
        """Получение данных пользователя"""
        with self.connection:
            self.cursor.execute(f"SELECT * FROM `{group_id}` WHERE `user_id` = ?", (user_id,))
            data = self.cursor.fetchone()
            return data[1:]

    def del_user(self, group_id, user_id):
        """Удаление пользователя"""
        with self.connection:
            return self.cursor.execute(f'DELETE FROM `{group_id}` WHERE `user_id` = ?', (user_id,))

    # ЗАКРЫТИЕ ВЫЗОВА
    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()
