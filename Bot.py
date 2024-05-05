import telebot
from telebot.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from validations import *
from messagesdb import *
from usersdb import *
from config import *
from gpt import *
from Translator import *
from Speechkit import *
from creds import get_bot_token, get_creds

bot = telebot.TeleBot(get_bot_token())

logging.basicConfig(filename=LOGS, level=logging.DEBUG,
                    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")


def send_message(id, text):
    bot.send_message(id, text)


iam_token, folder_id = get_creds()


def count_tokens(text):
    headers = {
        'Authorization': f'Bearer {iam_token}',
        'Content-Type': 'application/json'
    }
    data = {
        "modelUri": f"gpt://{folder_id}/yandexgpt/latest",
        "maxTokens": 1000,
        "text": text
    }
    return len(
        requests.post(
            "https://llm.api.cloud.yandex.net/foundationModels/v1/tokenize",
            json=data,
            headers=headers
        ).json()['tokens']
    )


system_tokens = count_tokens('Отвечай не более 100 слов')


@bot.message_handler(commands=['start'])
def start(message):
    create_database_users()
    global id
    id = message.chat.id
    logging.info("Обнаружение нового пользователя")
    if not count_users(id):
        send_message(id,
                     'Error! The number of users exceeded')
        return
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for lg in language_list.keys():
        markup.add(InlineKeyboardButton(text=lg), row_width=4)
    bot.send_message(id, 'Choose the language', reply_markup=markup)
    bot.register_next_step_handler(message, get_lang)


def get_lang(message):
    if message.content_type == 'text':
        if message.text in language_list.keys():
            global language
            language = language_list[message.text]
            logging.info("Обновлен язык")
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            for mode in mode_list:
                markup.add(InlineKeyboardButton(text=mode))
            bot.send_message(id, translate('Выбери предпочитаемый формат ответов модели GPT', language), reply_markup=markup)
            bot.register_next_step_handler(message, get_mode)
        elif message.text not in language_list:
            logging.warning("Ошибка идентификации при получении языка ")
            send_message(id, 'Error! Incorrect language has been entered. Try again')
            bot.register_next_step_handler(message, get_lang)
    else:
        send_message(id, 'Error! Enter text')
        bot.register_next_step_handler(message, get_lang)
def get_mode(message):
    if message.content_type == 'text':
        mode = message.text
        if mode not in mode_list:
            send_message(id, translate('Введен неверный режим', language))
            bot.register_next_step_handler(message, get_mode)
        if is_user_in_table(id):
            update_settings(id, language, mode)
        else:
            write_settings(id, language, mode)
        bot.send_message(id, translate('Готово! Теперь отправь голосовое сообщение или текст для общения с GPT', language),
                         reply_markup=ReplyKeyboardRemove())
    else:
        send_message(id, 'Error! Enter text')
        bot.register_next_step_handler(message, get_mode)

@bot.message_handler(commands=['debug'])
def send_logs(message):
    if message.chat.id in [1671928691, 1752643398]:
        logging.info("Получен файл debug")
        with open(LOGS, "rb") as f:
            bot.send_document(message.chat.id, f)
    else:
        return


@bot.message_handler(content_types=['voice', 'text'])
def forming_response(message):
    create_database_messages()
    id = message.chat.id
    try:
        readed_settings = read_settings(id)
    except:
        send_message(id, 'Please enter /start before forming response')
        return
    language, mode = readed_settings[0], readed_settings[1]
    if message.content_type == 'voice':
        file_id = message.voice.file_id
        file_info = bot.get_file(file_id)
        file = bot.download_file(file_info.file_path)
        stt_status, stt_blocks_or_msg = is_stt_block_limit(message, message.voice.duration)
        if stt_status:
            stt_status = stt_blocks_or_msg
            success, result = speech_to_text(file)
            gpt_response = result
            if not success:
                bot.send_message(id, translate(result, language))
                return
        else:
            send_message(id, translate(stt_blocks_or_msg, language))
            return
    else:
        gpt_response = message.text
        stt_status = 0
    response_tokens = count_tokens(gpt_response)
    collection, total_tokens = select_n_last_messages(id, 4)
    new_total_tokens = total_tokens + response_tokens + system_tokens
    if new_total_tokens >= MAX_USER_TOKENS:
        send_message(id, translate('Превышено количество токенов на пользователя', language))
        return
    add_message(id, gpt_response, role='user', total_gpt_tokens=new_total_tokens, tts_symbols=0, stt_blocks=stt_status)
    collection.append({'role': 'user', 'content': gpt_response})
    answer_gpt = ask_gpt(collection)
    counted_tokens_answer_gpt = count_tokens(answer_gpt)
    new_total_tokens += counted_tokens_answer_gpt
    translated_answer_gpt = translate(answer_gpt, language)
    if mode == 'Text':
        send_message(id, translated_answer_gpt)
        add_message(id, answer_gpt, role='assistant', total_gpt_tokens=new_total_tokens, tts_symbols=0, stt_blocks=0)
    else:
        tts_status, tts_symbols_or_msg = is_tts_symbols_limit(id, translated_answer_gpt)
        if tts_status:
            success, response = text_to_speech(translated_answer_gpt, language_cods_vocabulary[language][0], language_cods_vocabulary[language][1])
            if success:
                bot.send_voice(id, response)
                add_message(id, answer_gpt, role='assistant', total_gpt_tokens=new_total_tokens, tts_symbols=tts_symbols_or_msg, stt_blocks=0)
            else:
                bot.send_message(id, translate(response, language))
        else:
            add_message(id, answer_gpt, role='assistant', total_gpt_tokens=new_total_tokens,
                        tts_symbols=0, stt_blocks=0)
            if language == 'iw':
                send_message(id, 'סינתזת דיבור לא עובדת עם עברית')
            else:
                send_message(id, translate(tts_symbols_or_msg, language))
        return

bot.polling()


