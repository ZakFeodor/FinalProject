from googletrans import Translator
def translate(text, language):
    translate = Translator()
    translated_text = translate.translate(text, dest=language).text
    return translated_text


if __name__ == '__main__':
    lang = input('Введи язык\n')
    text = input('Введи текст для перевода\n')
    print(translate(text, lang))