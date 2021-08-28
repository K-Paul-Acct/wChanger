import vk_api

from datetime import datetime
from config import TOKEN, chat_id


vk_session = vk_api.VkApi(token=TOKEN)


def odd_week() -> bool:
    now = datetime.now()
    type = int(now.strftime('%W')) % 2
    return type


def change_name(chat_id: int) -> None:
    name = 'Группа 4232, '
    now = datetime.now()

    if now.weekday() == 0 and now.hour == 0:
        name += 'Нечёт' if odd_week else 'Чёт'
        vk_session.method('messages.editChat', {'chat_id': chat_id, 'title': name})

    elif now.weekday() == 5 and now.hour == 18:
        name += 'Чёт. След.' if odd_week else 'Нечёт. След.'
        vk_session.method('messages.editChat', {'chat_id': chat_id, 'title': name})


change_name(chat_id)
