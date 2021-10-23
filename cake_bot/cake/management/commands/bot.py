import os
from django.core.management.base import BaseCommand
from cake.models import *
from cake.serve import *
from cake.handlers import registration_handler, constructor_handler, show_orders, help
from django.core.files import File
from telegram import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, Update, user
from telegram.ext import ConversationHandler, MessageHandler, CommandHandler, Updater, Filters, CallbackContext
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('TELEGRAM_TOKEN')


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        updater = Updater(token, use_context=True)
        dispatcher = updater.dispatcher

        dispatcher.add_handler(registration_handler)
        dispatcher.add_handler(constructor_handler)
        dispatcher.add_handler(MessageHandler(filters=Filters.text, callback=show_orders))
        dispatcher.add_handler(CommandHandler("help", help))

        updater.start_polling()
        updater.idle()


# def main_keyboard(user_id):
#     database_user_id = Profile.objects.filter(tg_id=user_id)
#     if database_user_id.count() > 0:
#         markup = ReplyKeyboardMarkup(
#             keyboard=[
#                 [
#                     KeyboardButton(text='✅ Собрать торт'),
#                     KeyboardButton(text='🔍 Мои заказы')
#                 ],
#             ],
#             resize_keyboard=True
#         )
#         return markup
#     else:
#         markup = ReplyKeyboardMarkup(
#             keyboard=[
#                 [
#                     KeyboardButton(text='✅ Даю согласие', request_contact=True),
#                 ],
#             ],
#             resize_keyboard=True
#         )
#         return markup


# def start_bot(update, context):
#     user_id = update.effective_chat.id
#     context.bot.send_message(
#         chat_id=update.effective_chat.id,
#         text=('Привет!\n'
#               'Я бот для создания вашего уникального торта!\n\n'
#               'Чтобы начать, мне нужно получить от вас\n'
#               'согласие на обработку персональных данных.'),
#         reply_markup=main_keyboard(user_id),
#     )
#     context.bot.send_document(
#         chat_id=update.effective_chat.id,
#         document=open('agree.pdf', 'rb'),
#         filename='Согласие на обработку данных'
#     )
#     #print(create_order(update))
#     print(create_cake({
#         'level': '2 уровня',
#         'shape': 'Круг',
#         'topping': 'Черничный сироп'
#     }, 1))


# def cancel_handler(update, context):
#     if update.message.text == '❌ Отменить':
#         user_id = update.effective_chat.id
#         context.bot.send_message(
#             chat_id=update.effective_chat.id,
#             text=f'Вы отменили размещение вещи. Чтобы начать заново отправьте /start',
#             reply_markup=main_keyboard(user_id)
#         )
#         return ConversationHandler.END