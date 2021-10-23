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


SEND_CONTACT_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton('Ручной ввод'),
            KeyboardButton('Отправить контакт', request_contact=True)
        ]
    ],
    resize_keyboard=True
)

START_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Согласен'),
            KeyboardButton(text='Не согласен')
        ],
    ],
    resize_keyboard=True
)


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
                [
                    KeyboardButton(text='Главное меню')
                ],
            ],
            resize_keyboard=True
        ),
    )

    return 5


def select_shape(update, context):
    user_id = update.effective_chat.id

    if update.message.text == "Главное меню":
        update.message.reply_text(
            f'Возвращаемся ...',
            reply_markup=cake_keyboard(user_id)
        )
        return ConversationHandler.END
    else:
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
                    [
                        KeyboardButton(text='Главное меню')
                    ],
                ],
                resize_keyboard=True
            ),
        )

        return 6


def select_toppings(update, context):
    user_id = update.effective_chat.id
    if update.message.text == "Главное меню":
        update.message.reply_text(
            f'Возвращаемся ...',
            reply_markup=cake_keyboard(user_id)
        )
        return ConversationHandler.END
    else:
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
                    [
                        KeyboardButton(text='Главное меню')
                    ],

                ],
                resize_keyboard=True
            ),
        )
        return 7


def select_berries(update, context):
    user_id = update.effective_chat.id
    if update.message.text == "Главное меню":
        update.message.reply_text(
            f'Возвращаемся ...',
            reply_markup=cake_keyboard(user_id)
        )
        return ConversationHandler.END
    else:
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
                    [
                        KeyboardButton(text='Главное меню')
                    ],
                ],
                resize_keyboard=True
            ),
        )
        return 8


def select_decor(update, context):
    user_id = update.effective_chat.id
    if update.message.text == "Главное меню":
        update.message.reply_text(
            f'Возвращаемся ...',
            reply_markup=cake_keyboard(user_id)
        )
        return ConversationHandler.END
    else:
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
                    [
                        KeyboardButton(text='Главное меню')
                    ],
                ],
                resize_keyboard=True
            ),
        )
        return 9


def select_print(update, context):
    user_id = update.effective_chat.id
    if update.message.text == "Главное меню":
        update.message.reply_text(
            f'Возвращаемся ...',
            reply_markup=cake_keyboard(user_id)
        )
        return ConversationHandler.END
    else:
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
                    [
                        KeyboardButton(text='Главное меню')
                    ],
                ],
                resize_keyboard=True
            ),
        )
        return 10


def check_print_selection(update, context):
    user_id = update.effective_chat.id
    if update.message.text == "Главное меню":
        update.message.reply_text(
            f'Возвращаемся ...',
            reply_markup=cake_keyboard(user_id)
        )
        return ConversationHandler.END
    else:
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
                        [
                            KeyboardButton(text='Главное меню')
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
                reply_markup=ReplyKeyboardRemove()
            )
        return 11


def save_print(update, context):
    user_id = update.effective_chat.id
    if update.message.text == "Главное меню":
        update.message.reply_text(
            f'Возвращаемся ...',
            reply_markup=cake_keyboard(user_id)
        )
        return ConversationHandler.END
    else:
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
                    [
                        KeyboardButton(text='Главное меню')
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
            reply_markup=ReplyKeyboardRemove()
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
            text='Укажите время доставки в формате ДД.ММ.2021 | ЧЧ:ММ\n'
                 'Например 21.11.2021 | 17:00\n'
            ,
            reply_markup=ReplyKeyboardRemove()
        )
        return 16
    elif update.message.text == "Нет":
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(f"Укажите адрес доставки:"),
            reply_markup=ReplyKeyboardRemove()
        )
        return 15


def save_address(update, context):
    user_id = update.effective_chat.id
    users_info[user_id]['street'] = update.message.text
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Укажите время доставки в формате ДД.ММ.2021 | ЧЧ:ММ'
             'Например 21.11.2021 | 17:00\n',
        reply_markup=ReplyKeyboardRemove()
    )
    return 16


def ask_delivery_time(update, context):
    user_id = update.effective_chat.id
    delivery_date = validate_delivery_time(update.message.text)
    if delivery_date:
        cakes_info[user_id]['delivery_date'] = delivery_date
        order_price = get_order_info(cakes_info[user_id])[1]
        if check_fast_delivery(delivery_date):
            order_price = float(order_price)*1.2
        cakes_info[user_id]['price'] = order_price
        context.bot.send_message(
            chat_id=user_id,
            text=(f'СУММА ВАШЕГО ЗАКАЗА: {order_price}\n'
                  f'Есть ПРОМОКОД для получения скиди?'),
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(text='ВВЕСТИ ПРОМОКОД'),
                        KeyboardButton(text='ОФОРМИТЬ ЗАКАЗ'),
                        KeyboardButton(text='ОТМЕНИТЬ ЗАКАЗ'),
                    ],
                ],
                resize_keyboard=True,
            )
        )
        return 18
    else:
        context.bot.send_message(
            chat_id=user_id,
            text=(
                'Дата введена с ошибкой, попробуйте еще раз'
            ),
        )
        return 16


def apply_promocode(update, context):
    user_id = update.effective_chat.id
    promo = update.message.text
    if promo == 'devman_20':
        price = float(cakes_info[user_id]['price'])*0.8
        cakes_info[user_id]['price'] = price
        context.bot.send_message(
            chat_id=user_id,
            text=f'Промокод введен! Новая цена {price}',
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(text='ОФОРМИТЬ ЗАКАЗ'),
                        KeyboardButton(text='ОТМЕНИТЬ ЗАКАЗ'),
                    ],
                ],
                resize_keyboard=True,
            )
        )
        return 18
    else:
        context.bot.send_message(
            chat_id=user_id,
            text=(
                'Неправильный промокод, попробуйте еще раз'
            ),
        )
        return 17


def create_order_menu(update, context):
    user_id = update.effective_chat.id
    if update.message.text == "ВВЕСТИ ПРОМОКОД":
        context.bot.send_message(
            chat_id=user_id,
            text='Введите промокод',
            reply_markup=ReplyKeyboardRemove()
        )
        return 17
    elif update.message.text == "ОТМЕНИТЬ ЗАКАЗ":
        context.bot.send_message(
            chat_id=user_id,
            text='ЗАКАЗ ОТМЕНЕН!',
            reply_markup=cake_keyboard(user_id)
        )
    elif update.message.text == "ОФОРМИТЬ ЗАКАЗ":
        create_cake_order(update, context)
        return ConversationHandler.END


def create_cake_order(update, context):
    user_id = update.effective_chat.id
    info = cakes_info[user_id]
    user = users_info[user_id]
    order = create_order(user, info)
    create_cake(order, info)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'ЗАКАЗ ОФОРМЛЕН!',
        reply_markup=cake_keyboard(user_id)
    )
    return ConversationHandler.END


def show_orders(update, context):
    user_id = update.effective_chat.id
    client = Profile.objects.get(tg_id=user_id)
    statuses = {i[0]: i[1] for i in Order.ORDER_STATUS}
    if update.message.text == '🔍 Мои заказы':
        orders = Order.objects.filter(profile=client)

        for order in orders:
            context.bot.send_message(
                chat_id=user_id,
                text=f'Цена: {order.price}\n'
                     f'Дата доставки: {order.delivery_date}\n'
                     f'Статус: {statuses[order.status]}',
                reply_markup=cake_keyboard(user_id),
            )


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
        17: [MessageHandler(Filters.text, apply_promocode, pass_user_data=True)],
        18: [MessageHandler(Filters.text, create_order_menu, pass_user_data=True)],
    },


    fallbacks=[CommandHandler('stop', stop)]
)