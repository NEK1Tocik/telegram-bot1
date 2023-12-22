import webbrowser
import telebot
from telebot import types
import sqlite3


bot = telebot.TeleBot('6975282716:AAEax_3HQQ0EgrLRYGPW6iyMTQRdMnkTz-I')
name = None

# обработчик комманды /start
@bot.message_handler(commands=['start'])
def start(message):
    conn = sqlite3.connect('database.sql') # функция принимает один параметр, который отвечает за файл, который будет создан, в котором будет храниться вся база данных
    cur = conn.cursor() # создаём объект (курсор), с помощью него мы сможем выполнять разные команды в базе данных, тоесть подключаемся к базе данных

    cur.execute('CREATE TABLE IF NOT EXISTS users(id int auto_increment primary key, name varchar(50), pass varchar(50))') # метод execute позволяет нам выполнять некие sql-команды
    conn.commit() # синхронизируем команду с файлом (сохраняем изменение)
    cur.close() # закрываем соединение с базой данных
    conn.close() # закрываем соединение с базой данных


    bot.send_message(message.chat.id, 'Привет, сейчас тебя зарегистрируем! Введите ваше имя')
    bot.register_next_step_handler(message, user_name)

def user_name(message): # в этой функции мы будем записывать пользовательский текст, в переменную name
    global name
    name = message.text.strip() # фунцкия strip удаляет пробелы до и пробелы после текста
    bot.send_message(message.chat.id, 'Введите пароль')
    bot.register_next_step_handler(message, user_pass)


def user_pass(message):  # в этой функции мы будем записывать пользовательский текст
    password = message.text.strip()

    conn = sqlite3.connect('database.sql')
    cur = conn.cursor()

    cur.execute("INSERT INTO users (name, pass) VALUES ('%s', '%s')" % (name, password))  # INSERT INTO добавляет записи в таблицу (в нашем случае мы передаём значения name и password)
    conn.commit()
    cur.close()
    conn.close()

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton('Список пользователей', callback_data='users'))
    bot.send_message(message.chat.id, 'Пользователь зарегистрирован', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    conn = sqlite3.connect('database.sql')
    cur = conn.cursor()

    cur.execute("SELECT * FROM users")
    users = cur.fetchall() # эта функция вернёт нам все найденные записи

    info = ''
    for el in users:
        info += f'Имя: {el[1]}, пароль: {el[2]}\n' # здесь мы передаём имя и пароль которые написал пользователь (по индексу имя это 1, пароль это 2, так как индексация начинается с 0)

    cur.close()
    conn.close()
    bot.send_message(call.message.chat.id, info) # передаём отформатированную строку (строку info)

# обработчик команды /help
@bot.message_handler(commands=['help'])
def main(message):
    bot.send_message(message.chat.id, '<b>Help information: </b>/start - запускает бота', parse_mode='html') # передаём третий параметр parse_mode отвечающий за отфарматированнную строку


@bot.message_handler(commands=['site', 'website']) # обрабатываем эти две команды
def site(message):
    webbrowser.open('https://google.com') # в кавычках указываем путь по которому перейдёт пользователь (с помощью метода webbrowser)


@bot.message_handler() # принимаем любые данные которые поступают от пользователя
def info(message):
    if message.text.lower() == 'привет':
        bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}')
    elif message.text.lower() == 'id':
        bot.reply_to(message, f'Твой ID: {message.from_user.id}') # reply_to отличается от send_message тем, что он не просто отправляет, а отвечает на сообщение


@bot.message_handler(content_types=['photo']) # обработчик сообщения конкретного типа (фото, аудио, видео и т.д.)
def get_photo(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Перейти на сайт', url='https://google.com') # добовляем (создаём) inline кнопку
    # markup.add(types.InlineKeyboardButton('Перейти на сайт', url='https://google.com')) аналагичный вариант создания inline кнопки
    markup.row(btn1)
    btn2 = types.InlineKeyboardButton('Удалить фото', callback_data='delete') # callback_data это параметр в котором указывается, что при нажатии будет вызываться некая функция, которая будет отвечать за действие этой кнопки
    btn3 = types.InlineKeyboardButton('Изменить текст', callback_data='edit')
    markup.row(btn2, btn3)
    bot.reply_to(message, 'Какое красивое фото!', reply_markup=markup) # при создании кнопки должен быть третий параметр с названием переменной reply_markup




@bot.callback_query_handler(func=lambda callback: True) # декоратор который обрабатывает callback_data
def callback_message(callback):
    if callback.data == 'delete':
        bot.delete_message(callback.message.chat.id, callback.message.message_id - 1) # удаляем предпоследнее сообщение (в нашем случае фото)
    elif callback.data == 'edit':
        bot.edit_message_text('Edit text', callback.message.chat.id, callback.message.message_id) # редактируем текст




bot.polling(none_stop=True) # показываем что программа (бот) будет работать постоянно (до того пока мы не остановим бота)
# bot.infinity_polling() аналогичная функция, которая показывает что бот будет работать постоянно
