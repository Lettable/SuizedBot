from pyrogram import filters
from pyrogram.types import Message
from promo.modules.sudo import get_all_sudo_users

def sudo_user_filter():
    async def func(_, __, message: Message):
        if not message.from_user:
            return False
        sudo_list = await get_all_sudo_users()
        return message.from_user.id in sudo_list
    return filters.create(func)