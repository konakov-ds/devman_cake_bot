import os
from django.core.management.base import BaseCommand
from cake.models import*
from django.core.files import File
from telegram import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, Update, user
from telegram.ext import ConversationHandler, MessageHandler, CommandHandler, Updater, Filters, CallbackContext
from dotenv import load_dotenv
import random

load_dotenv()
token = os.getenv('TELEGRAM_TOKEN')


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        updater = Updater(token, use_context=True)
        dispatcher = updater.dispatcher

        # conv_handler = ConversationHandler(
        #     entry_points=[
        #         MessageHandler(Filters.text(categories), start_bot),
        #     ],
        #     states={
        #         PHOTO: [
        #             MessageHandler(Filters.photo, photo_handler, pass_user_data=True),
        #         ],
        #         NAME: [
        #             MessageHandler(Filters.text, name_thing_handler, pass_user_data=True),
        #         ]
        #     },
        #     fallbacks=[
        #         MessageHandler(Filters.text, cancel_handler),
        #     ],
        # )

        dispatcher.add_handler(CommandHandler('start', start_bot))
        updater.start_polling()
        updater.idle()


def main_keyboard(user_id):
    database_user_id = Profile.objects.filter(tg_id=user_id)
    if database_user_id.count() > 0:
        markup = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='✅ Собрать торт'),
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
                    KeyboardButton(text='✅ Даю согласие'),
                ],
            ],
            resize_keyboard=True
        )
        return markup


def start_bot(update, context):
    #write_user_to_db(update)
    user_id = update.effective_chat.id
    # random_photo[update.effective_chat.id] = []
    # random_photo_ex[update.effective_chat.id] = []
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=('Привет!\n'
              'Я бот для создания вашего уникального торта!\n\n'
              'Чтобы начать, мне нужно получить от вас\n'
              'согласие на обработку персональных данных.'),
        reply_markup=main_keyboard(user_id),
    )
    context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=open('agree.png', 'rb')
    )


def get_user_info(update, context):
    user_id = update.effective_chat.id
    update.message.chat.


def cancel_handler(update, context):
    if update.message.text == '❌ Отменить':
        user_id = update.effective_chat.id
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Вы отменили размещение вещи. Чтобы начать заново отправьте /start',
            reply_markup=main_keyboard(user_id)
        )
        return ConversationHandler.END