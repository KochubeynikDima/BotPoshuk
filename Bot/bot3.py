import logging
import telebot
from telebot import types
from config import bot_id

#Вводимо параметр для відстежування логів
logger = logging.getLogger('my_logger')
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
logging.basicConfig(level=logging.INFO)

#ініціалізуємо бота, кодом який отримали
bot = telebot.TeleBot(bot_id)
#Змінні та помилки
n_class=''
ErrClass = 'Нажаль ми не маємо підручників за: '
ErrSubject = 'Нажаль у нас немає підручника з: '
#Глобальна зміна, завершення або продовження пошуку
is_url_received = False
Err = 'Натисни /start для нового запита'
#Список підручників
class_to_books = {
    "1": {
        "математика": "https://pidruchnyk.com.ua/2744-matematyka-1-klas-budna-2023.html",
        "англійська": "https://pidruchnyk.com.ua/2717-angliiska-mova-1-klas-karpuk-2023.html",
        "мистецтво": "https://pidruchnyk.com.ua/2727-mystetstvo-1-klas-masol-2023.html",
        "українська мова": "https://pidruchnyk.com.ua/2766-ukrmova-1-klas-vashulenko-2023.html",
    },
    "2": {
        "математика": "https://pidruchnyk.com.ua/1305-matematika-2-logachevska.html",
        "англійська": "https://pidruchnyk.com.ua/68-anglyska-mova-karpyuk-2-klas.html",
        "мистецтво": "https://pidruchnyk.com.ua/1312-mystectvo-ostrovskiy-2-klas.html",
        "українська мова": "https://pidruchnyk.com.ua/63-ukrayinska-mova-zaharychuk-2-klas.html",
    },
    '11': {
        "математика":"\nГеометрія " +"https://pidruchnyk.com.ua/1247-geometriya-11-klas-merzlyak.html\n" f"Алгебра  "+ " https://pidruchnyk.com.ua/439-algebra-merzlyak-nomrovskiy-polonskiy-yakr-11-klas.html",
        "геометрія": "https://drive.google.com/file/d/1xHh8pRLLV9_9xSilPOslKx_tJWAFRPoW/view",
        "англійська": "\nStudents book: "+"https://drive.google.com/drive/u/0/my-drive\n" f"Work book: "+ " https://drive.google.com/drive/u/0/my-drive",
        "мистецтво": "https://pidruchnyk.com.ua/1339-mistectvo-gaydamaka-10-11-klas.html",
        "українська мова": "https://pidruchnyk.com.ua/1239-ukrainska-mova-11-klas-avramenko.html",
        "географія": "https://pidruchnyk.com.ua/1313-geografiya-bezugliy-11-klas.html",
        "алгебра": "https://pidruchnyk.com.ua/439-algebra-merzlyak-nomrovskiy-polonskiy-yakr-11-klas.html",
        "українська література": "https://pidruchnyk.com.ua/1237-ukrliteratura-avramenko-11klas.html",
        "біологія":"https://uahistory.co/pidruchniki/zadorozhnij-biology-and-ecology-11-class-2019-standard-level/",
        "хімія": "https://lib.imzo.gov.ua/wa-data/public/site/books2/pidruchnyky-11-klas-2019/20-himiya-11-klas/himiya-riven-standartu-pidruchnyk-dlia-11-klasu-zzso-grigorovich-o-v.pdf",
        "астрономія": "https://uroky.com.ua/astronomiya-11klas-pryshlyak/",
        "фінансова грамотність": "\nПідручник " +"http://www.fst-ua.info/wp-content/uploads/2019/08/Financial_Literacy_Textbook_Aug2019.pdf" "\nРобочий зошит  "+ " https://mon.gov.ua/storage/app/media/zagalna%20serednya/fingram/2Financial_Literacy_Workbook_Aug2019.pdf",
        "фізика":"https://pidruchnyk.com.ua/481-fzika-baryahtar-bozhinova-kryuhn-11-klas.html",
        "історія": "https://pidruchnyk.com.ua/1265-storya-ukrayina-svt-mudriy-arkusha-11-klas.html",
        "зарубіжна література": "https://pidruchnyk.com.ua/458-svtova-lteratura-sayeva-klimenko-melnik-11-klas.html",
        "інформатика":"https://informatik.pp.ua/pidruchniki/11-klas/pidruchnyk-informatyka-11-klas-profilnyi-riven-rudenko-2019/",
        "захист вітчизни":"https://pidruchnyk.com.ua/1270-zahyst-vitchyzny-11-klass-gudyma-med.html",


    }
}
#Запуск бота при отриманні команди
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    logging.info('надійшло повідомлення: ' + message.text)
    global is_url_received  # Об'являемо, что будемо використовувати глобальный флаг
    is_url_received = True  # Сбрасуємо флаг у початкове положення
    bot.reply_to(message, "Привіт, підручник якого класу тебе цікавить?")

#Функція яка активується при отриманні повідомлення
@bot.message_handler(func=lambda message: True)
def handle_class(message):
    global n_class
    n_class = message.text #Запам'ятовуємо обраний клас
    call_telegram(message) #Викликаємо наступну функцію

def call_telegram(message):
    global is_url_received
    if is_url_received: #Перевіряємов чи це перший запит
        class_number = message.text
        if class_number in class_to_books:#Шукаємо номер классу у списку
            try:
                bot.send_message(message.chat.id, "Який предмет тебе цікавить?")
                bot.register_next_step_handler(message, handle_subject, class_number) #Викникаємо наступний крок(уточнюючє питання)
                logging.info('відправлено повідомлення в telegram bot: ' + message.text)
            except Exception as e: #На випадок незапланованої помилки
                logging.error(f"Помилка при відправленні повідомлення: {e}")
        else: #якщо клас невірний
            bot.send_message(message.chat.id, ErrClass + class_number + ' клас')
            logging.info('відправлено повідомлення у telegram bot про помилку: ' + ErrClass + class_number + ' клас')
    else:#Якщо запит не перший
        bot.send_message(message.chat.id, Err)
        logging.info('відправлено повідомлення у telegram bot про помилку: ' + Err)


def handle_subject(message, class_number):
    global is_url_received
    # Створення кнопок
    op1 = types.InlineKeyboardMarkup()
    op1.add(telebot.types.InlineKeyboardButton(text='Ще з цим класом', callback_data='bt1'))
    op1.add(telebot.types.InlineKeyboardButton(text='Завершити', callback_data='bt2'))
    op1.add(telebot.types.InlineKeyboardButton(text='Усі підручники', url='https://pidruchnyk.com.ua/'))

    subject = message.text.lower() #пошук предмета у списку
    if subject in class_to_books[class_number]:
        book_url = class_to_books[class_number][subject]
        try:
            bot.send_message(message.chat.id, f"Ось посилання на підручник: {book_url}")
            bot.send_message(message.chat.id, f"Обери наступний крок", reply_markup=op1)
            logging.info('response url = ' + book_url)
            is_url_received = False #При отриманні посилання, закінчуємо пошук

        except Exception as e: #На випадок незапланованої помилки
            logging.error(f"Помилка при відправленні уточнюючого повідомлення: {e}")
    else: #якщо предмет невірний
        bot.send_message(message.chat.id, ErrSubject + subject)
        logging.info('відправлено повідомлення у telegram bot про помилку: ' + ErrSubject)

#Приймаємо данні які передають кнопки
@bot.callback_query_handler(func=lambda callback: callback.data)
def check_callback(callback):
    global is_url_received
    global n_class
    if callback.data == 'bt1':
        class_number = n_class #Якщо обрана кнопка "ЩЕ" використовуємо номер классу який запам'ятали
        if class_number in class_to_books:
            try:
                bot.send_message(callback.message.chat.id, "Який предмет тебе цікавить?")
                bot.register_next_step_handler(callback.message, handle_subject, class_number)
                logging.info('відправлено повідомлення в telegram bot: ' + callback.message.text)
            except Exception as e:
                logging.error(f"Помилка при відправленні повідомлення: {e}")
        else:
            bot.send_message(callback.message.chat.id, ErrClass + class_number + ' клас')
            logging.info('відправлено повідомлення у telegram bot про помилку: ' + ErrClass + class_number + ' клас')

    elif callback.data == 'bt2':
        bot.send_message(callback.message.chat.id, 'Натисни /start для нового запита')
        n_class=''
bot.polling(none_stop=True, interval=0)