import re
from collections import defaultdict
from dotenv import load_dotenv
from telegram import KeyboardButton, ReplyKeyboardMarkup,\
    ReplyKeyboardRemove
from telegram.ext import CommandHandler, ConversationHandler,\
    Filters, MessageHandler

from cake.serve import *
from cake.models import *

load_dotenv()
users_info = defaultdict()

contact_keyboard = KeyboardButton('Отправить контакт', request_contact=True)
location_keyboard = KeyboardButton('Ручной ввод')
make_order_button = KeyboardButton('Сделать заказ')
all_orders_button = KeyboardButton('История заказов')
custom_keyboard = [[contact_keyboard, location_keyboard]]
make_order = [[make_order_button]]

MAKE_ORDER_KEYBOARD = ReplyKeyboardMarkup(make_order, resize_keyboard=True)
SEND_CONTACT_KEYBOARD = ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)

START_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Согласен'), KeyboardButton(text='Не согласен')
        ],
    ],
    resize_keyboard=True
)


LEVELS_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='1 Уровень')
        ],
        [
            KeyboardButton(text='2 Уровня')
        ],
        [
            KeyboardButton(text='3 Уровня')
        ],
    ],
    resize_keyboard=True
)


def contact_keyboard(user_id):
    if check_client_orders(user_id):
        markup = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='Собрать торт'),
                    KeyboardButton(text='🔍 Мои заказы')
                ],
            ],
            resize_keyboard=True
        )
        return markup
    else:
        markup = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='Собрать торт'),
                ],
            ],
            resize_keyboard=True
        )
        return markup


def cake_keyboard(user_id):
    if check_client_orders(user_id):
        markup = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='Собрать торт'),
                    KeyboardButton(text='🔍 Мои заказы')
                ],
            ],
            resize_keyboard=True
        )
        return markup
    else:
        markup = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='Собрать торт'),
                ],
            ],
            resize_keyboard=True
        )
        return markup


def start(update, context):
    message = update.message
    user_name = message.chat.first_name
    user_id = message.chat_id
    # Если пользователь в базе пропустить этот шаг
    database_user_id = Profile.objects.filter(tg_id=user_id)
    if database_user_id.count() == 0:
        context.bot.send_message(
            chat_id=user_id,
            text=(
                f"Привет, {user_name}.🤚\n\n"
                "В начале нашего общения я должен получить от вас согласие на обработку предоставляемых"
                "вами персональных данных, с целью регистрации и обработки вашего обращения.\n\n"
                "Нажимая кнопку 'Согласен' вы подтверждаете свое согласие с правилами обработки персональных данных.\n\n"
                "Вы можете ознакомиться с ними в прикрепленном файле"
            ),
            reply_markup=START_KEYBOARD,
        )
        context.bot.send_document(
            chat_id=user_id,
            document=open('Agree.pdf', 'rb')
        )
        return 1
    else:
        context.bot.send_message(
            chat_id=user_id,
            text=(
                f"Привет, {user_name}.🤚\n\n"
                "Давайте собирать ваш торт!"

            ),
            reply_markup=cake_keyboard(user_id),
        )


def check_agreement(update, context):
    if update.message.text == "Согласен":
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=("Отлично, теперь укажите контактный номер телефона"),
            reply_markup=SEND_CONTACT_KEYBOARD
        )
        return 2
    else:
        update.message.reply_text(
            "Для продолжения работы с сервисом необходимо согласие на обработку пресональных данных"),
        return 1


def ask_contacts(update, context):
    message = update.message
    user_id = message.chat_id
    users_info[user_id] = get_base_user_info(update)
    if message.contact:
        text = (
            'Контактные данные\n'
            f'Имя: {users_info[user_id]["name"]}\n'
            f'Фамилия: {users_info[user_id]["last_name"]}\n'
            f'Телефон: {users_info[user_id]["phone"]}\n'
            'Cохранены!\n\n'
            'УКАЖИТЕ АДРЕС ДОСТАВКИ'
        )
        message.reply_text(
            text,
            reply_markup=ReplyKeyboardRemove()
        )
        return 4

    elif message.text == "Ручной ввод":
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=('Введите номер телефона в формате +71231231212'),
            reply_markup=ReplyKeyboardRemove(),
        )
        users_info[user_id]["phone"] = update.message.text
        return 3


def ask_address(update, context):
    user_id = update.message.chat_id
    address = update.message.text
    if address:
        update.message.reply_text(
            f"Адрес доставки, {address}, сохранен"
        )
        users_info[user_id]["street"] = address
        users_info[user_id]["house_number"] = ''
        users_info[user_id]["flat_number"] = ''
        write_user_to_db(users_info[user_id])
        users_info[user_id] = {}
        update.message.reply_text(
            f"Регистрация закончена. Можно начинать собирать тортики",
            reply_markup=cake_keyboard(user_id)
        )
    return ConversationHandler.END


def check_phone_number(update, context):
    user_id = update.effective_chat.id
    phone_number = update.message.text
    phone_number_valid = re.findall(r'\+?[\d]{1}[\d]{10}', phone_number)
    if phone_number_valid:
        phone_number_valid = phone_number_valid[0]
    if phone_number == phone_number_valid:
        users_info[user_id]['phone'] = phone_number
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                'Контактные данные\n'
                f'Имя: {users_info[user_id]["name"]}\n'
                f'Фамилия: {users_info[user_id]["last_name"]}\n'
                f'Телефон: {users_info[user_id]["phone"]}\n'
                'Cохранены!\n\n'
                'УКАЖИТЕ АДРЕС ДОСТАВКИ'
            ),
            reply_markup=ReplyKeyboardRemove(),
        )

    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                'Номер введен с ошибкой, попробуйте еще раз'
            ),
            reply_markup=SEND_CONTACT_KEYBOARD,
        )
        return 2

    return 4


def select_levels(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=("Выберите количество уровней тортика"),
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='1 Уровень')
                ],
                [
                    KeyboardButton(text='2 Уровня')
                ],
                [
                    KeyboardButton(text='3 Уровня')
                ],
            ],
            resize_keyboard=True
        ),
    )
    return 5


def select_shape(update, context):
    # Сохраняем количество уровней из прошлого шага
    levels = update.message.text

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=("Выберите форму"),
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='Квадрат')
                ],
                [
                    KeyboardButton(text='Круг')
                ],
                [
                    KeyboardButton(text='Прямоугольник')
                ],
            ],
            resize_keyboard=True
        ),
    )
    return 6


def select_toppings(update, context):
    # Сохраняем Выбранную форму из прошлого шага
    shape = update.message.text

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=("Выберите топпинг"),
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='Без топпинга')
                ],
                [
                    KeyboardButton(text='Белый соус')
                ],
                [
                    KeyboardButton(text='Карамельный сироп')
                ],
                [
                    KeyboardButton(text='Кленовый сироп')
                ],
                [
                    KeyboardButton(text='Клубничный сироп')
                ],
                [
                    KeyboardButton(text='Черничный сироп')
                ],
                [
                    KeyboardButton(text='Молочный шоколад')
                ],

            ],
            resize_keyboard=True
        ),
    )
    return 7


def select_berries(update, context):
    topping = update.message.text

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=("Добавить ягоды?"),
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='Без ягод')
                ],
                [
                    KeyboardButton(text='Ежевика')
                ],
                [
                    KeyboardButton(text='Малина')
                ],
                [
                    KeyboardButton(text='Голубика')
                ],
                [
                    KeyboardButton(text='Клубника')
                ],
            ],
            resize_keyboard=True
        ),
    )
    return 8


def select_decor(update, context):
    berry = update.message.text

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=("Как украсить?"),
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='Без декора')
                ],
                [
                    KeyboardButton(text='Фисташки')
                ],
                [
                    KeyboardButton(text='Безе')
                ],
                [
                    KeyboardButton(text='Фундук')
                ],
                [
                    KeyboardButton(text='Пекан')
                ],
                [
                    KeyboardButton(text='Маршмеллоу')
                ],
                [
                    KeyboardButton(text='Марципан')
                ],
            ],
            resize_keyboard=True
        ),
    )
    return 9


def select_print(update, context):
    decor = update.message.text

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=("Мы можем разместить на торте любую надпись, например: «С днем рождения!»"),
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='Добавить надпись')
                ],
                [
                    KeyboardButton(text='Без надписи')
                ],
            ],
            resize_keyboard=True
        ),
    )
    return check_print_selection(update, context)


def check_print_selection(update, context):
    if update.message.text == 'Без надписи':
        print("Выбрал Без надписи")

    elif update.message.text == 'Добавить надпись':
        pass


def help(update, context):
    update.message.reply_text("Справка по проекту")


def stop(update):
    update.message.reply_text("Стоп")
    return ConversationHandler.END


registration_handler = ConversationHandler(

    entry_points=[CommandHandler('start', start)],

    states={
        1: [MessageHandler(Filters.all, check_agreement, pass_user_data=True)],
        2: [MessageHandler(Filters.all, ask_contacts, pass_user_data=True)],
        3: [MessageHandler(Filters.text, check_phone_number, pass_user_data=True)],
        4: [MessageHandler(Filters.text, ask_address, pass_user_data=True)]
    },

    fallbacks=[CommandHandler('stop', stop)]
)

constructor_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.text("Собрать торт"), select_levels)],
    states={
        5: [MessageHandler(Filters.text, select_shape, pass_user_data=True)],
        6: [MessageHandler(Filters.text, select_toppings, pass_user_data=True)],
        7: [MessageHandler(Filters.text, select_berries, pass_user_data=True)],
        8: [MessageHandler(Filters.text, select_decor, pass_user_data=True)],
        9: [MessageHandler(Filters.text, select_print, pass_user_data=True)],
    },

    fallbacks=[CommandHandler('stop', stop)]
)