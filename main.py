from datetime import datetime, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters

from db_helper import DBHelper
from conf import TOKEN, DB_NAME

BTN_TODAY, BTN_TOMORROW, BTN_MONTH, BTN_REGION, BTN_DUA = ('βοΈ Bugun', 'β³ Ertaga', 'π To`liq taqvim', 'πΊπΏ Mintaqa', 'π€² Duo')
main_buttons = ReplyKeyboardMarkup([
    [BTN_TODAY], [BTN_TOMORROW, BTN_MONTH], [BTN_REGION], [BTN_DUA]
], resize_keyboard=True)

STATE_REGION = 1
STATE_CALENDAR = 2

user_region = dict()
db = DBHelper(DB_NAME)

def region_buttons():
    regions = db.get_regions()
    buttons = []
    tmp_b = []
    for region in regions:
        tmp_b.append(InlineKeyboardButton(region['name'], callback_data=region['id']))
        if len(tmp_b) == 2:
            buttons.append(tmp_b)
            tmp_b = []
    return buttons

def start(update, contaxt):
    user = update.message.from_user

    # buttons = [
    #     [
    #         InlineKeyboardButton('Toshkent', callback_data='region_1'),
    #         InlineKeyboardButton('Andijon', callback_data='region_2')
    #     ]
    # ]

    user_region[user.id] = None
    buttons = region_buttons()

    update.message.reply_html('Assalomu alaykum <b>{}</b>\n \nMintaqani tanlang π'.format(user.first_name), 
        reply_markup=InlineKeyboardMarkup(buttons))
    
    return STATE_REGION


def inline_callback(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    user_region[user_id] = int(query.data) 
    query.message.delete()
    query.message.reply_html(text='<b>Ramazon taqvimi</b> 2οΈβ£0οΈβ£2οΈβ£2οΈβ£\n \nQuyidagilardam birini tanlang π', reply_markup=main_buttons)

    return STATE_CALENDAR
    
def calendar_today(update, context):
    user_id = update.message.from_user.id
    if not user_region[user_id]:
        return STATE_REGION
    region_id = user_region[user_id]
    region = db.get_region(region_id)
    today = '2020-04-24' #str(datetime.now().date()) 

    if today == 'None':
        update.message.reply_html('<b>Hozir ramazon oyi emas</b>')
    else:
        calendar = db.get_calendar_by_region(region_id, today)

        update.message.reply_html('<b>Ramazon</b> 2023\n<b>{}</b> vaqti\n \nSaharlik: <b>{}</b>\nIftorlik: <b>{}</b>'. format(
            region['name'], calendar['fajr'], calendar['maghrib']))

def calendar_tomorrow(update, context):
    user_id = update.message.from_user.id
    if not user_region[user_id]:
        return STATE_REGION
    region_id = user_region[user_id]
    region = db.get_region(region_id)
    today = '2020-04-24' #str(datetime.now().date() + timedelta)

    if today == 'None':
        update.message.reply_html('<b>Hozir ramazon oyi emas</b>')
    else:
        calendar = db.get_calendar_by_region(region_id, today)

        update.message.reply_html('<b>Ramazon</b> 2023\n<b>{}</b> vaqti\n \nSaharlik: <b>{}</b>\nIftorlik: <b>{}</b>'. format(
            region['name'], calendar['fajr'], calendar['maghrib']))

    update.message.reply_text('Ertaga belgilandi')

def calendar_month(update, context):
    update.message.reply_text('To`liq taqvim belgilandi')

def select_region(update, context):
    buttons = region_buttons()
    update.message.reply_text('Sizga qaysi mintaqa bo`yicha ma`lumot kerak?', reply_markup=InlineKeyboardMarkup(buttons))
    return STATE_REGION

def select_dua(update, context):
    saharlik = "Saharlik duosi:\n \n<b>Β«ΠΠ°Π²Π°ΠΉΡΡ Π°Π½ Π°ΡΡΠΌΠ° ΡΠΎΠ²ΠΌΠ° ΡΠ°?³ΡΠΈ ΡΠ°ΠΌΠ°Π·ΠΎΠ½Π° ΠΌΠΈΠ½Π°Π» ΡΠ°ΠΆΡΠΈ ΠΈΠ»Π°Π» ΠΌΠ°?ΡΠΈΠ±ΠΈ, ΡΠΎΠ»ΠΈΡΠ°Π½ Π»ΠΈΠ»Π»Π°?³ΠΈ ΡΠ°ΡΠ°Π»Π° ΠΠ»Π»ΠΎ?³Ρ Π°ΠΊΠ±Π°ΡΒ»</b>"
    iftorlik = "Iftorlik duosi:\n \n<b>Β«ΠΠ»Π»ΠΎ?³ΡΠΌΠΌΠ° Π»Π°ΠΊΠ° ΡΡΠΌΡΡ Π²Π° Π±ΠΈΠΊΠ° Π°ΠΌΠ°Π½ΡΡ Π²Π° Π°ΡΠ»Π°ΠΉΠΊΠ° ΡΠ°Π²Π°ΠΊΠΊΠ°Π»ΡΡ Π²Π° Π°ΡΠ»Π°Π° ΡΠΈΠ·?ΠΈΠΊΠ° Π°ΡΡΠΎΡΡΡ, ΡΠ°?ΡΠΈΡΠ»ΠΈΠΉ ΠΉΠ° ?ΠΎΠ΄Π΄Π°ΠΌΡΡ Π²Π° ΠΌΠ°Π° Π°ΡΡΠΎΡΡΡΒ»</b>"
    update.message.reply_photo(photo=open('images/ramadan_dua.png', 'rb'), caption='{}\n \n{}'.format(saharlik, iftorlik), parse_mode='HTML', reply_markup=main_buttons)

def main():
    updater = Updater(TOKEN, use_context=True)

    dispatcher = updater.dispatcher

    # dispatcher.add_handler(CommandHandler('start', start)) #conversationHandler

    # dispatcher.add_handler(CallbackQueryHandler(inline_callback))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            STATE_REGION: [
                CallbackQueryHandler(inline_callback),
                MessageHandler(Filters.regex('^('+BTN_TODAY+')$'), calendar_today),
                MessageHandler(Filters.regex('^('+BTN_TOMORROW+')$'), calendar_tomorrow),
                MessageHandler(Filters.regex('^('+BTN_MONTH+')$'), calendar_month),
                MessageHandler(Filters.regex('^('+BTN_REGION+')$'), select_region),
                MessageHandler(Filters.regex('^('+BTN_DUA+')$'), select_dua)
            ],

            STATE_CALENDAR: [
                MessageHandler(Filters.regex('^('+BTN_TODAY+')$'), calendar_today),
                MessageHandler(Filters.regex('^('+BTN_TOMORROW+')$'), calendar_tomorrow),
                MessageHandler(Filters.regex('^('+BTN_MONTH+')$'), calendar_month),
                MessageHandler(Filters.regex('^('+BTN_REGION+')$'), select_region),
                MessageHandler(Filters.regex('^('+BTN_DUA+')$'), select_dua)
            ],
        },fallbacks=[CommandHandler('start', start)]
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

main()