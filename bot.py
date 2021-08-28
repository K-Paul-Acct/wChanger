import time
import sched
import vk_api

from datetime import datetime, timedelta
from config import TOKEN, shift_parity, chat_id

vk_session = vk_api.VkApi(token=TOKEN)


def type_week(shift_parity: int) -> datetime:
    now = datetime.now(tz='Europe/Moscow')
    jan = datetime(now.year, 1, 1, 3)
    d1 = jan - timedelta(days=jan.weekday())
    d2 = now - timedelta(days=now.weekday())
    return ((d2 - d1).days // 7 + shift_parity) % 2


def change_name(shift_parity: int, chat_id: int) -> None:
    name = 'Группа 4232, '
    now = datetime.now(tz='Europe/Moscow')

    if (now.weekday() < 5) or (now.weekday() == 5 and now.hour < 18):
        name += 'Нечёт.' if type_week(shift_parity) else 'Чёт.'
        next_sat = now + timedelta(days=5 - now.weekday())
        next_changing_time = datetime(next_sat.year, next_sat.month, next_sat.day, 18)
    else:
        name += 'Чёт. След.' if type_week(shift_parity) else 'Нечёт. След.'
        next_mon = now + timedelta(days=7 - now.weekday())
        next_changing_time = datetime(next_mon.year, next_mon.month, next_mon.day)

    vk_session.method('messages.editChat', {'chat_id': chat_id, 'title': name})

    s = sched.scheduler(time.time, time.sleep)
    s.enterabs(time.mktime(next_changing_time.timetuple()), 1, change_name, argument=(shift_parity, chat_id,))
    s.run()


change_name(shift_parity, chat_id)
