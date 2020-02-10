import json
import datetime
import logging
import telegram

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

from onepa_reqs import (get_cc_hash_mapping, check_cc_for_day, check_date_availability, check_cc_availability)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

START, DATE_ANSWER, CC_ANSWER = range(3)

def start(update, context):
    """Send a message when the command /start is issued."""
    reply_keyboard = [['/date','/cc']]
    update.message.reply_markdown(
        'Hi! Commands are as follows:\n'
        '**/date**: Enter a date and get all CCs that have available timings on that date\n'
        '**/cc**: Enter a CC and get all timings over the next 2 weeks\n'
        'Enjoy!'
        ,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=False
        )
    )

def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_markdown('Help!')

def date_question(update, context):
    reply_keyboard = [[(datetime.datetime.now()+datetime.timedelta(days=i)).strftime('%d/%m/%Y') for i in range(15)]]
    update.message.reply_markdown(
        'Hi! What date would you like to lookup CCs for? Enter in "DD/MM/YYYY" format, please.',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=False
        )
    )
    return DATE_ANSWER

def date_answer(update, context):
    date = update.message.text
    update.message.reply_markdown(
        'Looking up all CCs... This might take a while'
    )
    all_cc_availability = check_date_availability(date)
    cc_str = ''
    for cc in all_cc_availability:
        cc_str += f'**{cc}**:\n'
        for timeslot in all_cc_availability[cc]:
            cc_str += f'{timeslot}\n'
        cc_str += '\n'
    reply = '**CCs Available**:\n' + cc_str
    if len(reply) > telegram.constants.MAX_MESSAGE_LENGTH:
        split_reply = reply.split('\n')
        halfway_mark = len(split_reply)//2
        reply = ['\n'.join(split_reply[:halfway_mark]), '\n'.join(split_reply[halfway_mark:])]
    else:
        reply = [reply]
    for rep in reply:
        update.message.reply_markdown(
            rep,
            reply_markup=ReplyKeyboardRemove()
        )
    return ConversationHandler.END


def cc_question(update, context):
    update.message.reply_markdown(
        'Hi! What CC would you like to lookup availabilities for?'
    )
    return CC_ANSWER

def cc_answer(update, context):
    cc = update.message.text
    update.message.reply_markdown(
        f'Please wait - Looking up all Dates for {cc}...'
    )
    all_date_availability = check_cc_availability(cc)
    date_str = ''
    for date in all_date_availability:
        date_str += f'**{date}**:\n'
        for timeslot in all_date_availability[date]:
            date_str += f'{timeslot}\n'
        date_str += '\n'
    reply = '**Dates Available:**\n' + date_str
    if len(reply) > telegram.constants.MAX_MESSAGE_LENGTH:
        split_reply = reply.split('\n')
        halfway_mark = len(split_reply)//2
        reply = ['\n'.join(split_reply[:halfway_mark]), '\n'.join(split_reply[halfway_mark:])]
    else:
        reply = [reply]
    for rep in reply:
        update.message.reply_markdown(
            rep,
            reply_markup=ReplyKeyboardRemove()
        )
    return ConversationHandler.END


def echo(update, context):
    """Echo the user message."""
    update.message.reply_markdown(update.message.text)

def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_markdown(
        'Bye! I hope we can talk again some day.',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    with open('./credentials.json', 'r') as f:
        credentials = json.load(f)
    telegram_token = credentials['telegram_key']

    updater = Updater(telegram_token, use_context=True)

    # Get the dispatcher to register handlers
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            CommandHandler('date', date_question),
            CommandHandler('cc', cc_question)
        ],
        states={
            DATE_ANSWER: [MessageHandler(Filters.text, date_answer)],
            CC_ANSWER: [MessageHandler(Filters.text, cc_answer)],
            START: [MessageHandler(Filters.text, start)],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()



if __name__ == '__main__':
    main()
    # cc_hash_mapping = {}
    # cc_hash_mapping = get_cc_hash_mapping()
    # desired_cc = 'Eunos CC'
    # cc_hash = cc_hash_mapping[desired_cc]
    # print(check_cc_availability(desired_cc, '18/02/2020'))