import asyncio
import config
from pyrogram import filters
from pyrogram.errors import FloodWait
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from pymongo import MongoClient
from pyrogram.enums import ChatType
from promo import app, apps
from promo.modules.usernames import usernames
from promo.modules.block import blocked
from promo.modules.ref import referrals_collection

appslist = apps

db = MongoClient(config.MONGO_DB_URI)
DATABASE = db['MAIN']
users_collection = DATABASE['users']
referrals_collection = DATABASE['referrals']


start_button = InlineKeyboardMarkup([
    [InlineKeyboardButton(text='Chat', url=config.GROUP_LINK)],
    [InlineKeyboardButton(text='Help', callback_data='help_cb'),
     InlineKeyboardButton(text='Referral', callback_data='genreflink')]
])


@app.on_message(filters.command('start') & filters.private)
async def startcmd(_, message: Message):
    user_id = message.from_user.id
    user_mention = message.from_user.mention

    if blocked.find_one({'user_id': user_id}):
        await message.reply_text("You are blocked from using this bot.")
        return

    if len(message.command) == 2:
        referrer_id = int(message.command[1])
        good = await app.get_users(referrer_id)

        if user_id == referrer_id:
            await message.reply_text("You can't refer yourself.")
            return

        referral_data = referrals_collection.find_one({"user_id": user_id})
        if referral_data and referral_data.get("activated"):
            await message.reply_text("You have already used a referral link.")
            return

        referrals_collection.update_one(
            {"user_id": referrer_id},
            {"$inc": {"referrals_count": 1}},
            upsert=True
        )

        referrals_collection.update_one(
            {"user_id": user_id},
            {"$set": {"activated": True, "referrer_id": referrer_id}},
            upsert=True
        )

        await message.reply_text(f"Referral link activated! You've been referred by {good.mention}.")
    else:

        referrals_collection.update_one(
            {"user_id": user_id},
            {"$set": {"activated": False}},
            upsert=True
        )

    users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"user_id": user_id}},
        upsert=True
    )

    await message.reply_photo(
        config.START_IMG,
        caption=f"Hey {user_mention}, I'm {app.me.mention}!\n\n"
                f"➻ Elevate your telegram business with my incredible features.\n"
                f"──────────────────\n"
                f"๏ Click the help button to discover more about this rental bot for promotion purposes.",
        reply_markup=start_button
    )

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(f'{message.from_user.first_name}', user_id=f'{user_id}')]]
    )

    await app.send_message(config.LOGS_CHANNEL_ID, f'#start : {message.from_user.first_name} started the bot.', reply_markup=keyboard)


@app.on_callback_query(filters.regex('help_cb'))
async def help_callback(_, query: CallbackQuery):
    text = (
        f"Here's the help menu of {app.me.mention}\n"
        "Only the users who paid rent can use these commands.\n\n"
        "➻ /save : reply to a message you want to broadcast.\n"
        "➻ /stats : stats of the bot.\n"
        "➻ /state : to start or stop the state.\n"
        "➻ /source : source code info.\n"
        "➻ /list : list a username in marketplace.\n"
        "➻ /referral : Check your referrals.\n"
        "➻ For more details join @LettableChat."
    )

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(text='Back', callback_data='back_cb')]
    ])

    await query.edit_message_text(
        text=text,
        reply_markup=reply_markup
    )


@app.on_callback_query(filters.regex('back_cb'))
async def back_callback(_, query: CallbackQuery):
    text = (
        f"Hey {query.from_user.mention}, I'm {app.me.mention}!\n\n"
        "➻ Elevate your telegram business with my incredible features.\n"
        "──────────────────\n"
        "Click the help button to discover more about this rental bot"
        "for promotion purposes."
    )

    start_button = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Chat", url=config.GROUP_LINK)],
            [InlineKeyboardButton("Help", callback_data="help_cb"), InlineKeyboardButton("Referral", callback_data='genreflink')],
        ]
    )

    await query.edit_message_text(
        text=text,
        reply_markup=start_button,
        disable_web_page_preview=True
    )


@app.on_callback_query(filters.regex('source'))
async def source(_, query: CallbackQuery):
    maybebutton = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("ᴏᴡɴᴇʀ", url="https://t.me/mirzyave"),
            InlineKeyboardButton("ɢɪᴛʜᴜʙ", url="https://github.com/Lettable/LettableV5.1") 
        ],
        [
            InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="back_cb")
        ]
    ])
    text = (
        f"**ʜᴇʏ,\nᴛʜɪs ɪs {app.me.first_name},\nᴀɴ ᴘʀɪᴠᴀᴛᴇ ᴀᴜᴛᴏ ᴀᴅʙᴏᴛ.**\n\nᴡʀɪᴛᴛᴇɴ ɪɴ ᴩʏᴛʜᴏɴ ᴡɪᴛʜ ᴛʜᴇ ʜᴇʟᴩ ᴏғ :\n[ᴘʏʀᴏɢʀᴀᴍ](https://github.com/pyrogram/pyrogram)\n[ᴩʏᴛʜᴏɴ-ᴛᴇʟᴇɢʀᴀᴍ-ʙᴏᴛ](https://github.com/python-telegram-bot/python-telegram-bot)\nᴀɴᴅ ᴜsɪɴɢ [sǫʟᴀʟᴄʜᴇᴍʏ](https://www.sqlalchemy.org/) ᴀɴᴅ [ᴍᴏɴɢᴏ](https://cloud.mongodb.com/) ᴀs ᴅᴀᴛᴀʙᴀsᴇ.\n\n\n{app.me.first_name} 🫧 ɪs ʟɪᴄᴇɴsᴇᴅ ᴜɴᴅᴇʀ ᴛʜᴇ [ᴍɪᴛ ʟɪᴄᴇɴsᴇ](https://graph.org/MIT-License-06-27).\n© 2024 - 2025 | [sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ](https://t.me/mirzyave), ᴀʟʟ ʀɪɢʜᴛs ʀᴇsᴇʀᴠᴇᴅ."
    )
    await query.edit_message_text(
        text=text,
        reply_markup=maybebutton,
        disable_web_page_preview=True
    )



@app.on_message(filters.command('source') & filters.private)
async def sourceCMD(_, m: Message):

    if blocked.find_one({'user_id': message.from_user.id}):
        await message.reply_text("You are blocked from using this bot.")
        return

    photo = config.SOURCE_IMG
    text = (
        f"**ʜᴇʏ,\nᴛʜɪs ɪs {app.me.first_name},\nᴀɴ ᴘʀɪᴠᴀᴛᴇ ᴀᴜᴛᴏ ᴀᴅʙᴏᴛ.**\n\nᴡʀɪᴛᴛᴇɴ ɪɴ ᴩʏᴛʜᴏɴ ᴡɪᴛʜ ᴛʜᴇ ʜᴇʟᴩ ᴏғ :\n[ᴘʏʀᴏɢʀᴀᴍ](https://github.com/pyrogram/pyrogram)\n[ᴩʏᴛʜᴏɴ-ᴛᴇʟᴇɢʀᴀᴍ-ʙᴏᴛ](https://github.com/python-telegram-bot/python-telegram-bot)\nᴀɴᴅ ᴜsɪɴɢ [sǫʟᴀʟᴄʜᴇᴍʏ](https://www.sqlalchemy.org/) ᴀɴᴅ [ᴍᴏɴɢᴏ](https://cloud.mongodb.com/) ᴀs ᴅᴀᴛᴀʙᴀsᴇ.\n\n\n{app.me.first_name} 🫧 ɪs ʟɪᴄᴇɴsᴇᴅ ᴜɴᴅᴇʀ ᴛʜᴇ [ᴍɪᴛ ʟɪᴄᴇɴsᴇ](https://graph.org/MIT-License-06-27).\n© 2024 - 2025 | [sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ](https://t.me/mirzyave), ᴀʟʟ ʀɪɢʜᴛs ʀᴇsᴇʀᴠᴇᴅ."
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("ᴏᴡɴᴇʀ", url="https://t.me/mirzyave"),
            InlineKeyboardButton("ɢɪᴛʜᴜʙ", url="https://github.com/Lettable/LettableV5.1") 
        ],
        [
            InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="back_cb")
        ]
    ])

    await m.reply_photo(photo=photo, caption=text, reply_markup=keyboard)


@app.on_callback_query(filters.regex('genreflink'))
async def genreflink(_, query: CallbackQuery):
    user_id = query.from_user.id
    referrallink = f"https://t.me/{app.me.username}?start={query.from_user.id}"
    referrals_count = referrals_collection.count_documents({"referrer_id": user_id})
    text = f"Here is your referral link: [link]({referrallink})\n\nTotal Referrals: `{referrals_count}`\n\nShare this link to invite your friends."
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data='back_cb')]
    ])
    await query.edit_message_text(
        text=text,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )

