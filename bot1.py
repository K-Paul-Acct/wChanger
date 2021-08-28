import vk_api, datetime, time, sched


def NowIsOddWeek(shift_parity):
    now = datetime.datetime.now() + datetime.timedelta(hours=3)
    jan = datetime.datetime(now.year, 1, 1, 3)
    d1 = jan - datetime.timedelta(days=jan.weekday())
    d2 = now - datetime.timedelta(days=now.weekday())
    return ((d2 - d1).days // 7 + shift_parity) % 2

def ChangeName(shift_parity, chat_id):
    name = 'Группа 4232, '
    now = datetime.datetime.now() + datetime.timedelta(hours=3)
    
    if (now.weekday() < 5) or (now.weekday() == 5 and now.hour < 18):
        name += 'Нечёт.' if NowIsOddWeek(shift_parity) else 'Чёт.'
        next_sat = now + datetime.timedelta(days=5-now.weekday())
        next_changing_time = datetime.datetime(next_sat.year, next_sat.month, next_sat.day, 18)
    else:
        name += 'Чёт. След.' if NowIsOddWeek(shift_parity) else 'Нечёт. След.'
        next_mon = now + datetime.timedelta(days=7-now.weekday())
        next_changing_time = datetime.datetime(next_mon.year, next_mon.month, next_mon.day)
    
    vk_session.method('messages.editChat', {'chat_id': chat_id, 'title': name})
        
    s = sched.scheduler(time.time, time.sleep)
    s.enterabs(time.mktime(next_changing_time.timetuple()), 1, ChangeName, argument=(shift_parity, chat_id,))
    s.run()


TOKEN = ''
vk_session = vk_api.VkApi(token=TOKEN)

shift_parity = 0
chat_id = 1

ChangeName(shift_parity, chat_id)
