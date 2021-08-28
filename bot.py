import time
import sched
import vk_api
import datetime

from config import TOKEN, shift_parity, chat_id


vk_session = vk_api.VkApi(token=TOKEN)


def is_week_odd(shift_parity: int, now) -> bool:
    return (int(now.strftime('%W')) + shift_parity) % 2


def change_name(shift_parity: int, chat_id: int) -> None:
    name = 'Группа 4232, '
    now = datetime.datetime.now() + datetime.timedelta(hours=3)

    if (now.weekday() < 5) or (now.weekday() == 5 and now.hour < 18):
        name += 'Нечёт.' if is_week_odd(shift_parity, now) else 'Чёт.'
        next_sat = now + datetime.timedelta(days=5 - now.weekday())
        next_changing_time = datetime.datetime(next_sat.year, next_sat.month, next_sat.day, 18)
    else:
        name += 'Чёт. След.' if is_week_odd(shift_parity, now) else 'Нечёт. След.'
        next_mon = now + datetime.timedelta(days=7 - now.weekday())
        next_changing_time = datetime.datetime(next_mon.year, next_mon.month, next_mon.day)

    next_changing_time -= datetime.timedelta(hours=3)

    vk_session.method('messages.editChat', {'chat_id': chat_id, 'title': name})

    s = sched.scheduler(time.time, time.sleep)
    s.enterabs(time.mktime(next_changing_time.timetuple()), 0, change_name, argument=(shift_parity, chat_id,))
    s.run()

    
change_name(shift_parity, chat_id)
