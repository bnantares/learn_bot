import telebot
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import settings
import ephem
from datetime import datetime, date, time
from random import choice, randint
from glob import glob
from emoji import emojize

logging.basicConfig(filename="bot.log", level=logging.INFO)

def greet_user(update, context):
    print("Вызван /start")
    context.user_data['emoji'] = get_smile(context.user_data)
    update.message.reply_text(f"Здравствуй, пользователь!{context.user_data['emoji']}")

def get_smile(user_data):
    if 'emoji' not in user_data:
        smile = choice(settings.USER_EMOJI)
        return emojize(smile, use_aliases=True)
    return user_data['emoji']
 
def planet_where(update, context):
    print("Вызван /planet")
    planet = update.message.text.split(" ")[1]
    planet_list = [x[2] for x in ephem._libastro.builtin_planets() if x[1] == 'Planet']
    if planet in planet_list:
        now = datetime.now()
        dt = now.strftime("%y/%m/%d")
        obj = getattr(ephem, planet)
        planet_obj = obj(dt)
        const = ephem.constellation(planet_obj)   
        update.message.reply_text(f"Твоя планета {planet} тут: {const}")
    else:
        update.message.reply_text("Твоя планета не найдена")
    

def talk_to_me(update, context):
    context.user_data['emoji'] = get_smile(context.user_data)
    text = update.message.text
    print(text)
    update.message.reply_text(f"{text} {context.user_data['emoji']}")

def play_random_numbers(user_number):
    bot_number = randint(user_number - 10, user_number + 10)
    if user_number > bot_number:
        message = f"Ваше число {user_number}, моё число {bot_number}, вы выиграли"
    elif user_number == bot_number:
        message = f"Ваше число {user_number}, моё число {bot_number}, ничья!" 
    else:        
        message = f"Ваше число {user_number}, моё число {bot_number}, вы проиграли!"
    return message    

def guess_number(update, context):
    print(context.args)
    if context.args:
        try:
            user_number = int(context.args[0])
            message = play_random_numbers(user_number)
        except(TypeError, ValueError):
            message = "Введите целое число"
    else:
        message = "Введите число"
    update.message.reply_text(message)

def send_cat_picture(update, context):
    cat_photos_list = glob('images/cat*.jp*g')
    cat_pic_filename = choice(cat_photos_list)
    chat_id = update.effective_chat.id
    context.bot.send_photo(chat_id=chat_id, photo=open(cat_pic_filename, 'rb'))

def main():
    mybot = Updater(settings.API_KEY, use_context=True)
    
    dp = mybot.dispatcher
    dp.add_handler(CommandHandler("start", greet_user))
    dp.add_handler(CommandHandler("planet", planet_where))
    dp.add_handler(CommandHandler("guess", guess_number))
    dp.add_handler(CommandHandler("cat", send_cat_picture))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))
    
    
    logging.info("Bot started")
    mybot.start_polling()
    mybot.idle()

if __name__ == "__main__":
    main()
