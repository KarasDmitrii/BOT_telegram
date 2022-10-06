from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
import logging
import requests
from bs4 import BeautifulSoup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from urllib import parse

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)
name = []
link = []


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text='Для поиска введите название, или автора книги')


def not_f(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text='Ничего не найдено')


try:
    def get_name_link(url_t):
        r = requests.get(url_t)
        soup = BeautifulSoup(r.text, 'lxml')
        for i in soup.find('ul', class_=False).find_all('li', class_=False):
            name.append(i.find('a').text)
            link.append('https://flibusta.site' + i.find('a').get('href') + '/fb2')
        n_book = int(soup.find('div', id='main').find('h3', style=True).text.replace('):', '').split(' ')[-1])
        return name, link, n_book


    def echo(update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text='загрузка...')
        global name, link, n_book
        name.clear()
        link.clear()
        mess = ''
        args_dict = {'ask': update.message.text, 'chb': 'on'}
        url_parts = list(parse.urlparse('https://flibusta.site'))
        url_parts[2] = '/booksearch'
        url_parts[4] = parse.urlencode(args_dict)
        text1 = parse.urlunparse(url_parts)
        name, link, n_book = get_name_link(text1)
        if n_book > 5:
            for i in range(5):
                mess += f'{name[i]}\n{link[i]}\n\n'
            keyboard = [
                [InlineKeyboardButton('<==', callback_data='-'),
                 InlineKeyboardButton('==>', callback_data='+')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(text=mess, reply_markup=reply_markup)
        else:
            for i in range(len(name)):
                mess += f'{name[i]}\n{link[i]}\n\n'
            context.bot.send_message(chat_id=update.effective_chat.id, text=mess)
except BaseException:
    not_f


g = 0
def button(update, _):
    global g
    query = update.callback_query
    variant = query.data
    query.answer()
    mess = ''
    if variant == '+':
        g += 5
    if variant == '-' and g > 5:
        g -= 5
    if (n_book - g) < 5:
        for i in range(n_book-g):
            mess += f'{name[i + g]}\n{link[i + g]}\n\n'
    else:
        for i in range(5):
            mess += f'{name[i+g]}\n{link[i+g]}\n\n'
    keyboard1 = [
        [InlineKeyboardButton('<==', callback_data='-'),
         InlineKeyboardButton('==>', callback_data='+')]]
    reply_markup1 = InlineKeyboardMarkup(keyboard1)
    query.edit_message_text(text=mess, reply_markup=reply_markup1)


def main():
    TOKEN = '5513616314:AAFO0qwEuZRL557radde4Z5fFGAsUrTnKWs'
    updater = Updater(token=TOKEN)
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_handler)
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
