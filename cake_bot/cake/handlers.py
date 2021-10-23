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
cakes_info = defaultdict()

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
            chat_id=user_id,
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
            chat_id=user_id,
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


def select_level(update, context):
    user_id = update.effective_chat.id
    users_info[user_id] = get_user_info_from_db(user_id)
    cakes_info[user_id] = {}
    context.bot.send_message(
        chat_id=user_id,
        text=("Выберите количество уровней тортика"),
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='1 уровень')
                ],
                [
                    KeyboardButton(text='2 уровня')
                ],
                [
                    KeyboardButton(text='3 уровня')
                ],
            ],
            resize_keyboard=True
        ),
    )

    return 5


def select_shape(update, context):
    user_id = update.effective_chat.id

    cake_level = update.message.text
    cakes_info[user_id]['level'] = cake_level

    context.bot.send_message(
        chat_id=user_id,
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
    user_id = update.effective_chat.id

    cake_shape = update.message.text
    cakes_info[user_id]['shape'] = cake_shape

    context.bot.send_message(
        chat_id=user_id,
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
    user_id = update.effective_chat.id

    cake_topping = update.message.text
    cakes_info[user_id]['topping'] = cake_topping

    context.bot.send_message(
        chat_id=user_id,
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
    user_id = update.effective_chat.id

    cake_berry = update.message.text
    cakes_info[user_id]['berry'] = cake_berry

    context.bot.send_message(
        chat_id=user_id,
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
    user_id = update.effective_chat.id

    cake_decor = update.message.text
    cakes_info[user_id]['decor'] = cake_decor

    context.bot.send_message(
        chat_id=user_id,
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
    return 10


def check_print_selection(update, context):
    user_id = update.effective_chat.id

    if update.message.text == 'Без надписи':
        cakes_info[user_id]['title'] = ''
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=("Комментарий к заказу (можно пропустить)"),
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(text='Добавить комментарий')
                    ],
                    [
                        KeyboardButton(text='Пропустить')
                    ],
                ],
                resize_keyboard=True
            ),
        )
        return 12

    elif update.message.text == 'Добавить надпись':
        context.bot.send_message(
            chat_id=user_id,
            text=("Введите надпись:"),
        )
    return 11


def save_print(update, context):
    user_id = update.effective_chat.id

    cake_title = update.message.text
    cakes_info[user_id]['title'] = cake_title

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=("Комментарий к заказу (можно пропустить)"),
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='Добавить комментарий')
                ],
                [
                    KeyboardButton(text='Пропустить')
                ],
            ],
            resize_keyboard=True
        ),
    )
    return 12


def ask_comment(update, context):
    user_id = update.effective_chat.id
    if update.message.text == 'Пропустить':
        cakes_info[user_id]['comment'] = ''
        address = users_info[user_id]['street']
        context.bot.send_message(
            chat_id=user_id,
            text=(f"Адрес доставки {address}?"),
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(text='Да'),
                        KeyboardButton(text='Нет'),
                    ],
                ],
                resize_keyboard=True
            ),
        )
        return 14
    elif update.message.text == 'Добавить комментарий':
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=("Напишите комментарий"),
        )
        return 13


def save_comment(update, context):
    user_id = update.effective_chat.id

    cake_comment = update.message.text
    cakes_info[user_id]['comment'] = cake_comment
    address = users_info[user_id]['street']
    context.bot.send_message(
        chat_id=user_id,
        text=(f"Адрес доставки {address}?"),
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='Да'),
                    KeyboardButton(text='Нет'),
                ],
            ],
            resize_keyboard=True,
        )
    )
    return 14


def check_address(update, context):
    if update.message.text == "Да":
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(f"Укажите время доставки в формате дд.мм.гггг"),
        )
        return 16
    elif update.message.text == "Нет":
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(f"Укажите адрес доставки:"),
        )
        return 15


def save_address(update, context):
    user_id = update.effective_chat.id
    users_info[user_id]['street'] = update.message.text
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(f"Укажите время доставки в формате дд.мм.гггг:"),
    )
    return 16


def ask_delivery_time(update, context):
    user_id = update.effective_chat.id
    cakes_info[user_id]['delivery_date'] = update.message.text
    cake = cakes_info[user_id]
    info = users_info[user_id]
    context.bot.send_message(
        chat_id=user_id,
        text=(f'Вы указали {cake}, {info}'),
    )



# def select_print(update, context):
#     user_id = update.effective_chat.id
#
#     cake_decor = update.message.text
#     cakes_info[user_id]['decor'] = cake_decor
#
#     context.bot.send_message(
#         chat_id=update.effective_chat.id,
#         text=('Мы можем разместить на торте любую надпись, например:'
#               ' «С днем рождения!»'),
#         reply_markup=ReplyKeyboardMarkup(
#             keyboard=[
#                 [
#                     KeyboardButton(text='Добавить надпись')
#                 ],
#                 [
#                     KeyboardButton(text='Без надписи')
#                 ],
#             ],
#             resize_keyboard=True
#         ),
#     )
#     return 10
#
#
# def check_print_selection(update, context):
#     user_id = update.effective_chat.id
#
#     if update.message.text == 'Без надписи':
#         context.bot.send_message(
#             chat_id=update.effective_chat.id,
#             text='Торт будет без надписи',
#             reply_markup=cake_keyboard(user_id)
#         )
#         cakes_info[user_id]['title'] = ''
#         # order = create_order(update)
#         # cakes_info[user_id]['order'] = order
#         # write_title_db(order, name='', price=0)
#
#     elif update.message.text == 'Добавить надпись':
#         context.bot.send_message(
#             chat_id=update.effective_chat.id,
#             text='Введите текст для торта',
#             reply_markup=ReplyKeyboardRemove()
#         )
#         return 11
#
#
# def show_order_price(update, context):
#     user_id = update.effective_chat.id
#
#     if update.message.text == 'Сделать заказ':
#         cake_price = create_cake(
#             cakes_info[user_id],
#             cakes_info[user_id]['order']
#         )
#         context.bot.send_message(
#             chat_id=update.effective_chat.id,
#             text=f'Цена вашего заказа составила: {cake_price}',
#             reply_markup=cake_keyboard(user_id)
#         )
#
#
# def save_cake_title(update, context):
#     user_id = update.message.chat_id
#     title = update.message.text
#
#     if title:
#         cakes_info[user_id]['title'] = title
#         context.bot.send_message(
#             chat_id=user_id,
#             text=f'Надпись на торт : {title}, сохранена\n',
#             #reply_markup=cake_keyboard(user_id)
#         )
#         info = cakes_info[user_id]
#         context.bot.send_message(
#             chat_id=user_id,
#             text=f'Данные заказа {info}',
#             # reply_markup=cake_keyboard(user_id)
#         )
#         return ConversationHandler.END

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
    entry_points=[MessageHandler(Filters.text("Собрать торт"), select_level)],
    states={
        5: [MessageHandler(Filters.text, select_shape, pass_user_data=True)],
        6: [MessageHandler(Filters.text, select_toppings, pass_user_data=True)],
        7: [MessageHandler(Filters.text, select_berries, pass_user_data=True)],
        8: [MessageHandler(Filters.text, select_decor, pass_user_data=True)],
        9: [MessageHandler(Filters.text, select_print, pass_user_data=True)],
        10: [MessageHandler(Filters.text, check_print_selection, pass_user_data=True)],
        11: [MessageHandler(Filters.text, save_print, pass_user_data=True)],
        12: [MessageHandler(Filters.text, ask_comment, pass_user_data=True)],
        13: [MessageHandler(Filters.text, save_comment, pass_user_data=True)],
        14: [MessageHandler(Filters.text, check_address, pass_user_data=True)],
        15: [MessageHandler(Filters.text, save_address, pass_user_data=True)],
        16: [MessageHandler(Filters.text, ask_delivery_time, pass_user_data=True)],
    },

    fallbacks=[CommandHandler('stop', stop)]
)