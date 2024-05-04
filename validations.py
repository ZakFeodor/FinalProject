import math
from messagesdb import *

def is_tts_symbols_limit(user_id, text):
    text_symbols = len(text)

    all_symbols = count_all_limits(user_id, 'tts_symbols') + text_symbols

    if all_symbols >= MAX_USER_TTS_SYMBOLS:
        msg = f'''Превышен общий лимит SpeechKit TTS {MAX_USER_TTS_SYMBOLS}.
        Использовано: {all_symbols} символов.
        Доступно: {MAX_USER_TOKENS - all_symbols}'''
        return False, msg
    return True, len(text)


def is_stt_block_limit(message, duration):
    user_id = message.from_user.id

    audio_blocks = math.ceil(duration / 15)
    all_blocks = count_all_limits(user_id, 'stt_blocks') + audio_blocks

    if duration >= 30:
        msg = "SpeechKit STT работает с голосовыми сообщениями меньше 30 секунд"
        return False, msg

    if all_blocks >= MAX_USER_STT_BLOCKS:
        msg = f'''Превышен общий лимит SpeechKit STT {MAX_USER_STT_BLOCKS}.
         Использовано {all_blocks} блоков. Доступно: {MAX_USER_STT_BLOCKS - all_blocks}'''
        return False, msg

    return True, audio_blocks