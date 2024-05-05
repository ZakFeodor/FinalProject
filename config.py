language_list = {"English": 'en',
                 "O'zbek tili": 'uz',
                 "Русский": 'ru',
                 "Қазақша": 'kk',
                 "Deutsch": 'de',
                 "עברית": 'iw'
                 }
language_cods_vocabulary = {
        'en': ['en-US', 'john'],
        'uz': ['uz-UZ', 'nigora'],
        'ru': ['ru-RU', 'zahar'],
        'kk': ['kk-KK', 'amira'],
        'de': ['de-DE', 'lea'],
        'iw': ['he-IL', 'naomi']
}
mode_list = ['Audio', 'Text']
MAX_PROJECT_TOKENS = 10000
MAX_USER_TOKENS = 2000
MAX_USERS = 5
MAX_USER_STT_BLOCKS = 25
MAX_USER_TTS_SYMBOLS = 25000


HOME_DIR = '/home/student/FinalProject'
LOGS = f'{HOME_DIR}/logs.txt'
DB1_FILE = f'{HOME_DIR}/messages.sqlite'
DB2_FILE = f'{HOME_DIR}/users.sqlite'

IAM_TOKEN_PATH = f'{HOME_DIR}/creds/iam_token.txt'  # файл для хранения iam_token
FOLDER_ID_PATH = f'{HOME_DIR}/creds/folder_id.txt'  # файл для хранения folder_id
BOT_TOKEN_PATH = f'{HOME_DIR}/creds/bot_token.txt'  # файл для хранения bot_token
