from telegram.ext.updater import Updater
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os


def check_nmbi_status(user_input):
    user_input_list = user_input.split(',', maxsplit=1) # username@email.com, password_text
    if len(user_input_list) != 2:
        return f"Input is incorrect! Please type your username (email address) followed by a comma (,) and password. Example: yourname@email.com,MyPa55word)"
    elif user_input_list[0] == "":
        return f"Input is incorrect! Please type your username (email address) followed by a comma (,) and password. Example: yourname@email.com,MyPa55word)"
    elif user_input_list[1] == "":
        return f"Input is incorrect! Please type your username (email address) followed by a comma (,) and password. Example: yourname@email.com,MyPa55word)"

    with sync_playwright() as p:
       
        browser = p.chromium.launch(headless=True,executable_path=os.environ.get("CHROMEDRIVER_PATH")) 
        page = browser.new_page()
        page.goto('https://my.nmbi.ie/login-page?op=ext',timeout=300000) 
        page.fill('input#UserName',user_input_list[0].strip())
        page.fill('input#Password',user_input_list[1].strip())
        page.click('input[type=submit]')
        try:
            page.goto('https://my.nmbi.ie/login-page/landingpage/home/my-applications?menuParent=My%20Applications',timeout=300000) #,timeout=500000
            page.is_visible('div.k-grid-content k-auto-scrollable')
            html = page.inner_html('#grdOvrRecognition_element')
        except:
            return 'Incorrect username(email) or password.'
        soup = BeautifulSoup(html,'html.parser')
        tds = soup.find_all('td')
        status_list = [] 
        for td in tds:
            status_list.append(td.text)
        if len(status_list) == 0:
            return 'Server is busy, try again later :)'
        else:
            return f'Your application\'s status is {status_list[3]}({status_list[5]} for {status_list[6]}), submitted on {status_list[4]}'

def reply(update, context):
    user_input = update.message.text
    update.message.reply_text(check_nmbi_status(user_input))

def start(update, context: CallbackContext):
    welcome_message = """Hello👋 \n\nNMBI Status Checker Bot 🤖 is here to help you. You can check application status by typing your user name (email address) followed by a comma (,) and password.\n\nHere is an example: \nyourname@email.com,MyPa55word.\n\nIf you have any suggestions or come across any issues, please contact @KingOfKerala"""
    update.message.reply_text(welcome_message)    

def main():
    #print('Waiting for input...')
    updater = Updater("TELEGRAM_BOT_KEY", use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.text, reply))
    updater.start_polling()
    updater.idle()
main()
