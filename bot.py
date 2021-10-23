import os
from datetime import datetime

from dotenv import load_dotenv
from telegram import (Bot, KeyboardButton, ReplyKeyboardMarkup,
                      ReplyKeyboardRemove, Update, update)
from telegram.ext import (CallbackContext, CommandHandler, ConversationHandler,
                          Filters, MessageHandler, Updater)

load_dotenv()

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


def start(update, context):
    message = update.message
    user_name = message.chat.first_name
    user_id = message.chat_id
    context.user_data["user_name"] = user_name
    context.user_data["user_id"] = user_id
    # Если пользователь в базе пропустить этот шаг

    context.bot.send_message(
        chat_id=update.effective_chat.id,
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
        chat_id=update.effective_chat.id,
        document=open('Agree.pdf', 'rb')
    )
    return 1


def check_agreement(update, context):
    if update.message.text == "Согласен":
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=("Отлично, теперь укажите контактный номер телефона"),
            reply_markup=SEND_CONTACT_KEYBOARD
        )
        return 2
    else:
        update.message.reply_text("Для продолжения работы с сервисом необходимо согласие на обработку пресональных данных"),
        return 1


def ask_contacts(update, context):
    message = update.message
    
    if message.contact:
        phone_number = message.contact.phone_number
        text = (
            f"Контактный номер {phone_number} телефона сохранен."
            "Укажите адрес доставки:"
        )
        message.reply_text(
            text,
            reply_markup=ReplyKeyboardRemove()
        )
        return 4

    elif message.text == "Ручной ввод":
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=("Введите номер телефона в формате +71231231212"),
            reply_markup=ReplyKeyboardRemove(),
        )
        return 3


def ask_address(update, context):
    address = update.message.text
    context.user_data["address"] = address
    update.message.reply_text(
        f"Адрес доставки, {address}, сохранен. Регистрация закончена."
    )
    return main_menu(update, context)


def check_phone_number(update, context):
    phone_number = update.message.text
    
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            f"Контактный номер телефона {phone_number} сохранен.\n "
            "Укажите адрес доставки:"
        ),
        reply_markup=ReplyKeyboardRemove(),
    )
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
                [
                    KeyboardButton(text='Главное меню')
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
                [
                KeyboardButton(text='Главное меню')
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
    return 10


def check_print_selection(update, context):
    if update.message.text == 'Без надписи':
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
            chat_id=update.effective_chat.id,
            text=("Введите надпись:"),
    )
    return 11


def save_print(update, context):
    cake_print = update.message.text

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
    if update.message.text == 'Пропустить':
        address = context.user_data["address"]

        context.bot.send_message(
            chat_id=update.effective_chat.id,
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
    comment = update.message.text
    address = context.user_data["address"]

    context.bot.send_message(
        chat_id=update.effective_chat.id,
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
    context.user_data["address"] = update.message.text
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(f"Укажите время и дату доставки в формате дд.мм.гггг:"),
        reply_markup=ReplyKeyboardRemove(),
    )
    return 16


def ask_delivery_time(update, context):
    delivery_time = update.message.text


def main_menu(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(f"Давай собирать новый тортик!"),
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='Сделать заказ')
                ],
            ],
        resize_keyboard=True
        ),
    )
    return ConversationHandler.END


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
        4: [MessageHandler(Filters.text, ask_address, pass_user_data=True)],
    },
    
    fallbacks=[CommandHandler('stop', stop)]
)


constructor_handler = ConversationHandler(
    entry_points = [MessageHandler(Filters.text("Сделать заказ"), select_levels)],
    states = {
        5:[MessageHandler(Filters.text, select_shape, pass_user_data=True)],
        6:[MessageHandler(Filters.text, select_toppings, pass_user_data=True)],
        7:[MessageHandler(Filters.text, select_berries, pass_user_data=True)],
        8:[MessageHandler(Filters.text, select_decor, pass_user_data=True)],
        9:[MessageHandler(Filters.text, select_print, pass_user_data=True)],
        10:[MessageHandler(Filters.text, check_print_selection, pass_user_data=True)],
        11:[MessageHandler(Filters.text, save_print, pass_user_data=True)],
        12:[MessageHandler(Filters.text, ask_comment, pass_user_data=True)],
        13:[MessageHandler(Filters.text, save_comment, pass_user_data=True)],
        14:[MessageHandler(Filters.text, check_address, pass_user_data=True)],
        15:[MessageHandler(Filters.text, save_address, pass_user_data=True)],
        16:[MessageHandler(Filters.text, ask_delivery_time, pass_user_data=True)],
    },

    fallbacks=[MessageHandler(Filters.text("Главное меню"), main_menu)]
)


def main():
    load_dotenv()

    token = os.environ['TG_TOKEN']
    bot = Updater(token, use_context=True)
    dp = bot.dispatcher

    dp.add_handler(registration_handler)
    dp.add_handler(constructor_handler)
    dp.add_handler(CommandHandler("help", help))


    bot.start_polling()
    # run the bot until Ctrl-C
    bot.idle()


if __name__ == "__main__":
    main()
