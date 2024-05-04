import sqlite3
import logging  # модуль для сбора логов
from config import *

# настраиваем запись логов в файл
logging.basicConfig(filename=LOGS, level=logging.DEBUG,
                    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")
path_to_db = DB2_FILE


def create_database_users():
    try:
        with sqlite3.connect(path_to_db) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                language TEXT,
                mode TEXT)
            ''')
            logging.info("DATABASE: База данных создана")
    except Exception as e:
        logging.error(e)
        return None


def write_settings(user_id, language, mode):
    try:
        with sqlite3.connect(path_to_db) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                    INSERT INTO users (user_id, language, mode) 
                    VALUES (?, ?, ?)''',
                           (user_id, language, mode)
                           )
            conn.commit()  # сохраняем изменения
            logging.info(f"DATABASE: INSERT INTO users "
                         f"VALUES ({user_id}, {language}, {mode})")
    except Exception as e:
        logging.error(e)  # если ошибка - записываем её в логи
        return None


def update_settings(id, language, mode):
    con = sqlite3.connect('users.sqlite')
    cur = con.cursor()
    sql_query = f"UPDATE users SET 'language' = ?, 'mode' = ? WHERE user_id = ?;"
    cur.execute(sql_query, (language, mode, id))
    con.commit()
    logging.info(f"DATABASE: UPDATE INTO users "
                 f"VALUES ({language}, {mode})")
    con.close()


def is_user_in_table(id):
    con = sqlite3.connect('users.sqlite')
    cur = con.cursor()
    info = cur.execute(f'SELECT * FROM users WHERE user_id={id}').fetchone()
    print(info)
    if info is not None:
        return True
    else:
        return False


def read_settings(user_id):
    try:
        # подключаемся к базе данных
        with sqlite3.connect(path_to_db) as conn:
            cursor = conn.cursor()
            readed_data = cursor.execute('''
               SELECT language, mode FROM users WHERE user_id=?''',
                           (user_id,))
            for result in readed_data:
                return result
        con.close()
    except Exception as e:
        logging.error(e)


if __name__ == '__main__':
    choice = input('Удалить данные таблицы?')
    if choice.lower() == 'да':
        con = sqlite3.connect(path_to_db)
        cur = con.cursor()
        cur.execute("DELETE FROM users;")
        con.commit()
        con.close()
    else:
        exit()
