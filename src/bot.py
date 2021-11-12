import time
import sched
import vk_api
import datetime
import sqlite3
import json
import threading
import config
import messages

from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.exceptions import ApiError
from vk_api.utils import get_random_id
from contextlib import closing
from config import TOKEN, KEY, SERVER, TS


vk_session = vk_api.VkApi(token=TOKEN)
longpoll = VkBotLongPoll(vk_session, 202243542, wait=25)
vk = vk_session.get_api()

def current_week() -> str:
    return " Сейчас нечётная неделя." if is_week_odd() else " Сейчас чётная неделя."

def is_week_odd() -> bool:
    now = datetime.datetime.now() + datetime.timedelta(hours=3)
    return (int(now.strftime('%W')) + config.shift_parity) % 2

def change_name() -> None:
    now = datetime.datetime.now() + datetime.timedelta(hours=3)

    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()
    if is_week_odd():
        data = cursor.execute("SELECT id, odd_week FROM chats").fetchall()
    else:
        data = cursor.execute("SELECT id, even_week FROM chats").fetchall()
    closing(sqlite3.connect('data.db'))
    closing(connection.cursor())

    for current_conversation in data:
        try:
            if vk.messages.getConversationsById(peer_ids=2000000000+current_conversation[0])['items'] != []:
                if vk.messages.getConversationsById(peer_ids=2000000000+current_conversation[0])['items'][0]['chat_settings']['title'] != current_conversation[1]:
                    vk.messages.editChat(chat_id=current_conversation[0], title=current_conversation[1])
        except ApiError as e:
            #print(str(e))
            if '925' in str(e):
                vk.messages.send(key=KEY, server=SERVER, ts=TS, random_id=get_random_id(), chat_id=current_conversation[0], message=messages.bot_is_not_admin)

    next_mon = now + datetime.timedelta(days=7-now.weekday())
    #next_changing_time = datetime.datetime.now() + datetime.timedelta(minutes=5)
    next_changing_time = datetime.datetime(next_mon.year, next_mon.month, next_mon.day) - datetime.timedelta(hours=3)
    #print(next_changing_time)

    #следующая планировка
    s = sched.scheduler(time.time, time.sleep) 
    s.enterabs(time.mktime(next_changing_time.timetuple()), 0, change_name)
    s.run()

def listening() -> None:
    while True:
        try:
            for event in longpoll.listen():
                if event.type == VkBotEventType.MESSAGE_NEW:
                    # приветственное сообщение при добавлении в беседу
                    if event.from_chat and 'action' in event.message.keys() and event.message['action']['type'] == 'chat_invite_user':
                        vk.messages.send(key=KEY, server=SERVER, ts=TS, random_id=get_random_id(), chat_id=event.chat_id, message=messages.greeting + current_week())
                    # сообщение о настройке
                    elif event.from_chat and ('@wchanger] настройка' in str(event) or '@wchanger], настройка' in str(event)):
                        vk.messages.send(key=KEY, server=SERVER, ts=TS, random_id=get_random_id(), chat_id=event.chat_id, message=messages.setting + current_week())
                    # настройка
                    elif event.from_chat and '@wchanger]' in str(event):
                        json_object = json.loads(json.dumps(event.object.message))
                        message = json_object['text']
                        names = message.split("|")
                        # при корректном сообщении
                        if len(names) == 3:
                            name_even = names[1].replace('@wchanger]', '').strip(' ').strip(',')
                            name_odd = names[2].strip(' ')
                            users = None
                            # если бот админ, исключения не будет
                            try:
                                users = vk.messages.getConversationMembers(peer_id=event.message['peer_id'])
                            except ApiError:
                                vk.messages.send(key=KEY, server=SERVER, ts=TS, random_id=get_random_id(), chat_id=event.chat_id, message=messages.bot_is_not_admin)
                            # если пользователь админ
                            if users != None and 'is_admin' in next(member for member in users['items'] if member['member_id'] == event.message['from_id']):
                                # обновление бд  
                                connection = sqlite3.connect('data.db')
                                cursor = connection.cursor()
                                current_id = cursor.execute("SELECT id FROM chats WHERE id = ?", (event.chat_id,),).fetchone()
                                if current_id == None:
                                    cursor.execute("INSERT INTO chats VALUES (?, ?, ?)", (event.chat_id, name_odd, name_even))
                                else:
                                    cursor.execute("UPDATE chats SET odd_week = ?, even_week = ? WHERE id = ?", (name_odd, name_even, event.chat_id))
                                connection.commit()
                                closing(sqlite3.connect('data.db'))
                                closing(connection.cursor())

                                name = name_odd if is_week_odd() else name_even
                                vk.messages.send(key=KEY, server=SERVER, ts=TS, random_id=get_random_id(), chat_id=event.chat_id, message=messages.success)  
                                vk.messages.editChat(chat_id=event.chat_id, title=name)
                            # пользователь не админ
                            elif users != None:
                                vk.messages.send(key=KEY, server = SERVER, ts = TS, random_id = get_random_id(), chat_id = event.chat_id, message=messages.user_is_not_admin) 
                        # если сообщение некорректное
                        else:
                            vk.messages.send(key=KEY, server = SERVER, ts = TS, random_id = get_random_id(), chat_id = event.chat_id, message=messages.error)
                            vk.messages.send(key=KEY, server=SERVER, ts=TS, random_id=get_random_id(), chat_id=event.chat_id, message=messages.setting + current_week())
                    #print(event)
        except:
            vk_session = vk_api.VkApi(token=TOKEN)
            longpoll = VkBotLongPoll(vk_session, 202243542, wait=25)
            vk = vk_session.get_api()
            time.sleep(2)

connection = sqlite3.connect('data.db')
cursor = connection.cursor()
try:
    cursor.execute("CREATE TABLE chats (id INTEGER, odd_week TEXT, even_week TEXT)")
except:
    pass
closing(sqlite3.connect('data.db'))
closing(connection.cursor())

t1 = threading.Thread(target=listening)
t2 = threading.Thread(target=change_name)
t1.start()
t2.start()
