import sqlite3
import logging  # модуль для сбора логов
from config import *

# настраиваем запись логов в файл
logging.basicConfig(filename=LOGS, level=logging.DEBUG,
                    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")
path_to_db = DB1_FILE

def create_database_messages():
    try:
        with sqlite3.connect(path_to_db) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                message TEXT,
                role TEXT,
                total_gpt_tokens INTEGER,
                tts_symbols INTEGER,
                stt_blocks INTEGER)
            ''')
            logging.info("DATABASE: База данных создана")
    except Exception as e:
        logging.error(e)
        return None


def add_message(user_id, message, role, total_gpt_tokens, tts_symbols, stt_blocks):
    try:
        with sqlite3.connect(path_to_db) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                    INSERT INTO messages (user_id, message, role, total_gpt_tokens, tts_symbols, stt_blocks) 
                    VALUES (?, ?, ?, ?, ?, ?)''',
                           (user_id, message, role, total_gpt_tokens, tts_symbols, stt_blocks)
                           )
            conn.commit()
            logging.info(f"DATABASE: INSERT INTO messages "
                         f"VALUES ({user_id}, {message}, {role}, {total_gpt_tokens}, {tts_symbols}, {stt_blocks})")
    except Exception as e:
        print(e)
        logging.error(e)
        return None


def count_users(user_id):
    try:
        with sqlite3.connect(path_to_db) as conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT COUNT(DISTINCT user_id) FROM messages WHERE user_id <> ?''', (user_id,))
            count = cursor.fetchone()[0]
            return count < MAX_USERS
    except Exception as e:
        logging.error(e)
        return None


def select_n_last_messages(user_id, n_last_messages):
    messages = []
    total_spent_tokens = 0
    try:
        # подключаемся к базе данных
        with sqlite3.connect(path_to_db) as conn:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT message, role, total_gpt_tokens FROM messages WHERE user_id=? ORDER BY id DESC LIMIT ?''',
                           (user_id, n_last_messages))
            data = cursor.fetchall()
            messages.append({'role': 'user', 'content': 'Отвечай не более 100 слов', })
            if data and data[0]:
                # формируем список сообщений
                for message in reversed(data):
                    messages.append({'role': message[1], 'content': message[0], })
                    total_spent_tokens = max(total_spent_tokens, message[2])
            return messages, total_spent_tokens
    except Exception as e:
        logging.error(e)
        return messages, total_spent_tokens

def count_all_limits(user_id, limit_type):
    try:
        with sqlite3.connect(path_to_db) as conn:
            cursor = conn.cursor()
            cursor.execute(f'''SELECT SUM({limit_type}) FROM messages WHERE user_id=?''', (user_id,))
            data = cursor.fetchone()
            if data and data[0]:
                logging.info(f"DATABASE: У user_id={user_id} использовано {data[0]} {limit_type}")
                return data[0]
            else:
                return 0
    except Exception as e:
        logging.error(e)
        return 0


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