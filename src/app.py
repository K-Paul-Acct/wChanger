from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.exceptions import ApiError

from datetime import datetime, timedelta

from time import time, sleep, mktime

from bot import Bot, vk_session
from messages import *
from config import *
import db

import threading
import sqlite3
import sched
import json
import os


bot = Bot
longpoll = VkBotLongPoll(vk_session, ID)
vk = vk_session.get_api()

connection = sqlite3.connect(os.path.join(BASE_DIR, 'db.sqlite3'))
cursor = connection.cursor()

db.create_table(cursor)

def cur_week() -> str:
    return " Сейчас нечётная неделя." if is_week_odd() else " Сейчас чётная неделя."

def is_week_odd() -> bool:
    now = datetime.now()
    return (int(now.strftime('%W')) + shift_parity) % 2

def change_name():
    now = datetime.now()

    data = db.select_odd_week(cursor) \
        if is_week_odd() else \
            db.select_even_week(cursor)

    for cur_id in data:
        try:
            conversations = bot.get_conversations_by_id(cur_id[0])
            if conversations is not dict() and \
                conversations[0]['chat_settings']['title'] != cur_id[1]:
                    vk.messages.editChat(chat_id=cur_id[0], title=cur_id[1])
        except ApiError as e:
            if '925' in str(e):
                bot.send_message(cur_id[0], bot_is_not_admin)

    next_mon = now + timedelta(days=7-now.weekday())
    next_changing_time = datetime(next_mon.year, next_mon.month, next_mon.day)

    '''следующая планировка'''
    s = sched.scheduler(time, sleep) 
    s.enterabs(mktime(next_changing_time.timetuple()), 0, change_name)
    s.run()

def message_handler():
    for event in longpoll.listen():
        chat_id = event.chat_id

        if event.type == VkBotEventType.MESSAGE_NEW:

            if event.from_chat and 'action' in event.message.keys() \
                and event.message['action']['type'] == 'chat_invite_user':

                '''приветственное сообщение при добавлении в беседу'''
                bot.send_message(chat_id, greeting + cur_week())

            elif event.from_chat and \
                ('@wchanger] настройка' in str(event) or \
                    '@wchanger], настройка' in str(event)):

                '''сообщение о настройке'''
                bot.send_message(chat_id, setting + cur_week())

            elif event.from_chat and '@wchanger]' in str(event):
                '''настройка'''

                json_object = json.loads(json.dumps(event.object.message))
                message = json_object['text']
                names = message.split("|")

                if len(names) == 3:
                    '''при корректном сообщении'''
                    name_even = names[1].replace('@wchanger]', '').strip(' ').strip(',')
                    name_odd = names[2].strip(' ')
                    users = None

                    '''если бот админ, исключения не будет'''
                    try:
                        users = vk.messages.getConversationMembers(peer_id=event.message['peer_id'])
                    except ApiError:
                        bot.send_message(chat_id, bot_is_not_admin)
                    
                    '''если пользователь админ'''
                    if users != None and \
                        'is_admin' in next(member
                            for member in users['items'] \
                                if member['member_id'] == event.message['from_id']):
                        '''обновление бд'''

                        current_id = db.select_id_where(cursor, chat_id)
                        if current_id == None:
                            db.insert(cursor, chat_id, name_odd, name_even)
                        else:
                            db.update(cursor, name_odd, name_even, chat_id)
                        connection.commit()

                        name = name_odd if is_week_odd() else name_even
                        bot.send_message(chat_id, success)
                        vk.messages.editChat(chat_id=chat_id, title=name)

                    elif users != None:
                        '''пользователь не админ'''
                        bot.send_message(chat_id, user_is_not_admin)

                else:
                    '''если сообщение некорректное'''
                    bot.send_message(chat_id, error)
                    bot.send_message(chat_id, setting + cur_week())


if __name__ == '__main__':
    t1 = threading.Thread(target=change_name)
    t1.start(); message_handler()
    connection.close()
