import vk_api
#from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
#from vk_api.longpoll import VkLongPoll, VkEventType
import datetime
import time

def IsParity(now):
    sep = datetime.datetime(now.year if now.month >= 9 else now.year - 1, 9, 1)
    d1 = sep - datetime.timedelta(days=sep.weekday())
    d2 = now - datetime.timedelta(days=now.weekday())
    return ((d2 - d1).days // 7 + shift_parity) % 2

def ChangeName(new, time):
    vk_session = vk_api.VkApi(token = TOKEN)
    print(new)
    print(time)
    print()
    vk_session.method('messages.editChat', {'chat_id': chat_id, 'title': new})

TOKEN = ''
vk_session = vk_api.VkApi(token = TOKEN)

#my_groups = vk_session.method('messages.getConversations', {'group_id' : 202243542})
# vk_session.method('messages.editChat', {'chat_id': 1, 'title': 'Group 1'})
#print(my_groups)

shift_parity = 1
now = datetime.datetime.now() + datetime.timedelta(hours=3)
last_change = datetime.datetime.weekday(now) == 0
chat_id = 2
#print(last_change)

while True:
    now = datetime.datetime.now() + datetime.timedelta(hours=3)
    if last_change and datetime.datetime.weekday(now) == 0:
        current_parity = 'Чёт' if IsParity(now) else 'Нечёт'
        chat_name = 'Группа 4132, ' + current_parity
        ChangeName(chat_name, time)
        last_change = False
    elif not last_change and datetime.datetime.weekday(now) == 5 and now.hour >= 22 and now.minute >= 30:
        current_parity = 'Нечёт' if IsParity(now) else 'Чёт'
        chat_name = 'Группа 4132, ' + current_parity + ' След'
        #print(chat_name)
        ChangeName(chat_name, time)
        last_change = True
    time.sleep(20)
