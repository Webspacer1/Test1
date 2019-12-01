"""Get info about Supergroups
Syntax: ..wg"""

from time import sleep
from datetime import datetime

from pyrogram import Filters, Message, Chat
from pyrogram.errors import PeerIdInvalid
from pyrogram.api import functions
from pyrobot import BOT, LOGGER_GROUP, NO_PICTURE_PATH

import readline

from pyrogram import Client, Filters

import os

# Constants
#ADMINTITLE = "<b>Admins in \"{}\"</b>:\n"
ADMINTITLE = " "
ADMINCREATOR = (
    '<b>Creator:</b>\n'
    '{} (<a href="tg://user?id={}">{}</a>)\n\n')
ADMINLISTLASTBOT = '{} (<a href="tg://user?id={}">{}</a>) `ᴮᴼᵀ`\n'
ADMINLISTLAST = '{} (<a href="tg://user?id={}">{}</a>)\n'
ADMINLISTBOT = '{} (<a href="tg://user?id={}">{}</a>) `ᴮᴼᵀ`\n'
ADMINLIST = '{} (<a href="tg://user?id={}">{}</a>)\n'


# Get full informations
@BOT.on_message(Filters.command("wg", "..")  & Filters.me)
def who_is(client: BOT, message: Message):
    message.delete()
    from_chat = None
    if " " in message.text:
        chat_id = message.text.split(" ")
        try:
#            chat_id = int(chat_id)
            from_chat = client.get_chat(message.command[1])
#            print(from_chat)
#            print(message.chat.id)
        except Exception as e:
            message.edit(str(e))
            return
    elif message.reply_to_message:
        from_chat = message.reply_to_message.from_chat
    elif message.chat.type == 'supergroup':
        from_chat = client.get_chat(message.chat.id)
    else:
        client.send_message(LOGGER_GROUP, "<b>Whois Group command error message:</b>\nPlease post ..wg directly in the target group or ..wg -100123456789", parse_mode="html")
        message.delete()
        return

    if from_chat is not None:
        #Get ID
        cmd = message.command
#        print(cmd)
        if not message.reply_to_message and len(cmd) == 1:
            get_chats= message.chat.id
        elif message.reply_to_message and len(cmd) == 1:
            get_chats= message.reply_to_message.from_chat.id
        elif len(cmd) > 1:
            get_chats= cmd[1]
            try:
                get_chats= int(cmd[1])
            except ValueError:
                pass

    #Count Messages
    counter = client.get_history_count(from_chat.id)

    #First Message
    firstmessage = client.get_history(message.chat.id, limit=1, reverse=True)[0]["date"]
    # Calculate Unix to time (first message)
    date_time_fm = datetime.fromtimestamp(firstmessage)
    dfm = date_time_fm.strftime("%d.%m.%Y, %H:%M:%S")

	#First ID in the group
    timestamp = client.get_messages(message.chat.id, 1, replies=0).date
    # Calculate Unix to time (first ID)
    if timestamp is not None:
        # Calculate Unix to time (first ID)
        date_time = datetime.fromtimestamp(timestamp)
        DateFirstID = date_time.strftime("%d.%m.%Y, %H:%M:%S")
    else:
        DateFirstID = None

    #Filter Creator and Admins
    all_admins = client.iter_chat_members(
        chat_id=from_chat.id,
        filter='administrators')
    creator = None
    admins = []

    for admin in all_admins:
        if admin.status == 'creator':
            creator = admin
        elif admin.status == 'administrator':
            admins.append(admin)
    sorted_admins = sorted(admins, key=lambda usid: usid.user.id)

    AdminList = ADMINTITLE.format(message.chat.title)

    if creator:
        AdminList += ADMINCREATOR.format(
            str(creator.user.id).rjust(10),
            creator.user.id,
            creator.user.first_name)

    AdminList += "<b>Admins:</b>\n"
    for admin in sorted_admins:
        if admin is sorted_admins[-1]:
            if admin.user.is_bot:
                AdminList += ADMINLISTLASTBOT.format(
                    str(admin.user.id).rjust(10),
                    admin.user.id,
                    admin.user.first_name)
            else:
                AdminList += ADMINLISTLAST.format(
                    str(admin.user.id).rjust(10),
                    admin.user.id,
                    admin.user.first_name)
        else:
            if admin.user.is_bot:
                AdminList += ADMINLISTBOT.format(
                    str(admin.user.id).rjust(10),
                    admin.user.id,
                    admin.user.first_name)
            else:
                AdminList += ADMINLIST.format(
                    str(admin.user.id).rjust(10),
                    admin.user.id,
                    admin.user.first_name)

    #Get deleted Accounts
    deleted = 0

    for member in BOT.iter_chat_members(from_chat.id):
        if member.user.is_deleted:
            deleted += 1

    #Get Profile Picture
    chat_photo = from_chat.photo

    #Count Members of the group
#    count = client.get_chat_members_count(from_chat.username)

    #Check if there is no gif or animation in the pinned message
    messagepinned= client.get_chat(message.chat.id)
    messagecontent= messagepinned.pinned_message

    if messagecontent == None:
        pinned = "There is no pinned message in the group."
    elif messagecontent.photo:
        pinned = "There is an photo in the pinned message. Unfortunately, media content can not be displayed."
    elif messagecontent.animation:
        pinned = "There is an animation in the pinned message. Unfortunately, media content can not be displayed."
    elif messagecontent.sticker:
        pinned = "There is an sticker in the pinned message. Unfortunately, media content can not be displayed."
    elif messagecontent.voice:
        pinned = "There is an voice message in the pinned message. Unfortunately, media content can not be displayed."
    elif messagecontent.text:
        pinned = messagecontent.text
    else:
        pinned = "Nothing to show!"

    if from_chat is not None:
        # Whois Message Part1
        message_out_str_1 = ""
        message_out_str_1 += f"Whois from <b>{from_chat.title}</b>:\n"
        message_out_str_1 += f"\n"
#        message_out_str_1 += f"ID: <a href='https://t.me/{from_chat.username}'>{from_chat.id}</a>\n"
        message_out_str_1 += f"ID: <a href='{from_chat.id}'>{from_chat.id}</a>\n"
        message_out_str_1 += f"Chatname: @{from_chat.username}\n"
        message_out_str_1 += f"Currently Messages: {counter}\n"
        message_out_str_1 += f"<a href='https://t.me/{from_chat.username}/1'>First post:</a> {dfm}\n"
        message_out_str_1 += f"First ID:     {DateFirstID}\n"
#        message_out_str_1 += f"Members: {count}\n"
        message_out_str_1 += f"Members: {from_chat.members_count}\n"
        message_out_str_1 += f"Deleted Accounts: {deleted}\n"

        # Whois Message Part2
        message_out_str_2 = ""
        message_out_str_2 += f"\n"
        message_out_str_2 += f"{AdminList}\n"
        message_out_str_2 += f"\n"
        message_out_str_2 += f"<b>Description:</b>\n"
        message_out_str_2 += f"{from_chat.description}\n"
        message_out_str_2 += f"\n"
#        message_out_str_2 += f"\n"
        message_out_str_2 += f"<b>Permissions:</b>\n"
        message_out_str_2 += f"Can send Messages: {from_chat.permissions.can_send_messages}\n"
        message_out_str_2 += f"Can send Media: {from_chat.permissions.can_send_media_messages}\n"
        message_out_str_2 += f"Other messages: {from_chat.permissions.can_send_other_messages}\n"
        message_out_str_2 += f"Add web page previews: {from_chat.permissions.can_add_web_page_previews}\n"
        message_out_str_2 += f"Add polls: {from_chat.permissions.can_send_polls}\n"
        message_out_str_2 += f"Can change info: {from_chat.permissions.can_change_info}\n"
        message_out_str_2 += f"Invite user: {from_chat.permissions.can_invite_users}\n"
        message_out_str_2 += f"Can pin messages: {from_chat.permissions.can_pin_messages}\n"
        message_out_str_2 += f"Can set sticker: {from_chat.can_set_sticker_set}\n"
#        print(message_out_str_2)

        # Whois Message Part3
        message_out_str_3 = ""
        message_out_str_3 += f"<b>Pinned Message:</b>\n"
        message_out_str_3 += f"{pinned}\n"
        message_out_str_3 += f"\n"

    if from_chat.photo is not None:
        local_chat_photo = client.download_media(
            message=chat_photo.big_file_id
        )
        # Send Part 1 (Photo and Infos)
        client.send_photo(
            LOGGER_GROUP,
            photo=local_chat_photo,
            caption=message_out_str_1,
            parse_mode="html",
            disable_notification=True
        )
        os.remove(local_chat_photo)
        # Send Part 2 (Admins)
        client.send_message(
            LOGGER_GROUP,
            message_out_str_2,
            parse_mode="html",
            disable_web_page_preview=True,
            disable_notification=True
        )
        # Send Part 3 (Pinned Message)
        client.send_message(
            LOGGER_GROUP,
            message_out_str_3,
            parse_mode="html",
            disable_web_page_preview=True,
            disable_notification=True
        )
    else:
        # If there is no Group Photo
        local_chat_photo = NO_PICTURE_PATH

        # Send Part 1 (Photo and Infos)
        client.send_photo(
            LOGGER_GROUP,
            photo=local_chat_photo,
            caption=message_out_str_1,
            parse_mode="html",
            disable_notification=True
        )
        # Send Part 2 (Admins)
        client.send_message(
            LOGGER_GROUP,
            message_out_str_2,
            parse_mode="html",
            disable_web_page_preview=True,
            disable_notification=True
        )
        # Send Part 3 (Pinned Message)
        client.send_message(
            LOGGER_GROUP,
            message_out_str_3,
            parse_mode="html",
            disable_web_page_preview=True,
            disable_notification=True
        )

# Get partly informations
@BOT.on_message(Filters.command("wgp", "..")  & Filters.me)
def who_is(client: BOT, message: Message):
    message.delete()
    from_chat = None
    if " " in message.text:
        chat_id = message.text.split(" ")
        try:
#            chat_id = int(chat_id)
            from_chat = client.get_chat(message.command[1])
            print(from_chat)
#            print(from_chat)
#            print(message.chat.id)
        except Exception as e:
            message.edit(str(e))
            return
    elif message.reply_to_message:
        from_chat = message.reply_to_message.from_chat
        print(from_chat)
    elif message.chat.type == 'supergroup':
        from_chat = client.get_chat(message.chat.id)
        print(from_chat)
    else:
        client.send_message(LOGGER_GROUP, "<b>Whois Group command error message:</b>\nPlease post ..wg directly in the target group or ..wg -100123456789", parse_mode="html")
        message.delete()
        return

    if from_chat is not None:
        #Get ID
        cmd = message.command
#        print(cmd)
        if not message.reply_to_message and len(cmd) == 1:
            get_chats= message.chat.id
        elif message.reply_to_message and len(cmd) == 1:
            get_chats= message.reply_to_message.from_chat.id
        elif len(cmd) > 1:
            get_chats= cmd[1]
            try:
                get_chats= int(cmd[1])
            except ValueError:
                pass

    #Count Messages
    counter = client.get_history_count(from_chat.id)

    #First Message
    firstmessage = client.get_history(message.chat.id, limit=1, reverse=True)[0]["date"]
    # Calculate Unix to time (first message)
    date_time_fm = datetime.fromtimestamp(firstmessage)
    dfm = date_time_fm.strftime("%d.%m.%Y, %H:%M:%S")

	#First ID in the group
    timestamp = client.get_messages(message.chat.id, 1, replies=0).date
    # Calculate Unix to time (first ID)
    if timestamp is not None:
        # Calculate Unix to time (first ID)
        date_time = datetime.fromtimestamp(timestamp)
        DateFirstID = date_time.strftime("%d.%m.%Y, %H:%M:%S")
    else:
        DateFirstID = None

    #Get deleted Accounts
    deleted = 0

    for member in BOT.iter_chat_members(from_chat.id):
        if member.user.is_deleted:
            deleted += 1

    #Get Profile Picture
    chat_photo = from_chat.photo

    #Count Members of the group
#    count = client.get_chat_members_count(from_chat.username)

    if from_chat is not None:
        # Whois Message Part1
        message_out_str_1 = ""
        message_out_str_1 += f"Whois from <b>{from_chat.title}</b>:\n"
        message_out_str_1 += f"\n"
#        message_out_str_1 += f"ID: <a href='https://t.me/{from_chat.username}'>{from_chat.id}</a>\n"
        message_out_str_1 += f"ID: <a href='{from_chat.id}'>{from_chat.id}</a>\n"
        message_out_str_1 += f"Chatname: @{from_chat.username}\n"
        message_out_str_1 += f"Currently Messages: {counter}\n"
        message_out_str_1 += f"<a href='https://t.me/{from_chat.username}/1'>First post:</a> {dfm}\n"
        message_out_str_1 += f"First ID:     {DateFirstID}\n"
#        message_out_str_1 += f"Members: {count}\n"
        message_out_str_1 += f"Members: {from_chat.members_count}\n"
        message_out_str_1 += f"Deleted Accounts: {deleted}\n"

    if from_chat.photo is not None:
        local_chat_photo = client.download_media(
            message=chat_photo.big_file_id
        )
        # Send Photo and Infos
        client.send_photo(
            LOGGER_GROUP,
            photo=local_chat_photo,
            caption=message_out_str_1,
            parse_mode="html",
            disable_notification=True
        )
        os.remove(local_chat_photo)
    else:
        # If there is no Group Photo
        local_chat_photo = NO_PICTURE_PATH

        # Send Photo and Infos
        client.send_photo(
            LOGGER_GROUP,
            photo=local_chat_photo,
            caption=message_out_str_1,
            parse_mode="html",
            disable_notification=True
        )