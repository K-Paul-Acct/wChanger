from .config import TOKEN, TS, KEY, SERVER

from vk_api.utils import get_random_id

import vk_api


vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()


class Bot:

    def get_conversations_by_id(peer_id: int):
        chat_id = 2000000000
        return vk.messages.getConversationsById(peer_ids=chat_id+peer_id)['items']

    def send_message(chat_id: int, message: str):
        vk.messages.send(
            chat_id=chat_id,
            message=message,
            key=KEY, ts=TS,
            server=SERVER,
            random_id=get_random_id()
        )
