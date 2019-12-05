"""Get info about the replied user/user id/or in privat chat
Syntax: .whois"""

from time import sleep
from datetime import datetime

from pyrogram import Filters, Message, User
from pyrogram.errors import PeerIdInvalid
from pyrogram.api import functions
from pyrobot import BOT, NO_PICTURE_PATH, LOGGER_GROUP

from pyrogram import Client, Filters

import os

#Get User Information
@BOT.on_message(Filters.command("wi", "..")  & Filters.me)
def who_is(client: BOT, message: Message):
    message.delete()
    from_user = None
    if " " in message.text:
        recvd_command, user_id = message.text.split(" ")
        try:
            user_id = int(user_id)
#            from_user = client.get_users(user_id)
            from_user = client.get_users(message.command[1])
        except Exception as e:
            message.edit(str(e))
            return
    elif message.reply_to_message:
        from_user = message.reply_to_message.from_user
    elif message.chat.type == 'private':
        from_user = client.get_users(message.chat.id)
    else:
        message.edit("no valid user_id / message specified")
        return

    if from_user is not None:
        #Get ID
        cmd = message.command
        if not message.reply_to_message and len(cmd) == 1:
            get_user = message.chat.id
        elif message.reply_to_message and len(cmd) == 1:
            get_user = message.reply_to_message.from_user.id
        elif len(cmd) > 1:
            get_user = cmd[1]
            try:
                get_user = int(cmd[1])
            except ValueError:
                pass

    #Online Status
#        onlinestatus = client.get_users(user_id)
        onlinestatus=from_user.status
        if from_user.status=="recently":
            onlinestatus="Recently"
        elif from_user.status=="within_week":
            onlinestatus="Within the last week"
        elif from_user.status=="within_month":
            onlinestatus="Within the last month"
        elif from_user.status=="long_time_ago":
            onlinestatus="A long time ago :("
        elif from_user.status=="online":
            onlinestatus="Currently Online"
        elif from_user.status=="offline":
            onlinestatus="Offline"
        else:
            onlinestatus="Error: Unkown Online Status!"
            
        #Userpics count
        pic_count = client.get_profile_photos_count(from_user.id)

		#Common Chats
        common = client.get_common_chats(from_user.id)
        sendcommon = len(common)
		
        #Get Profile Picture
        chat_photo = from_user.photo
		
        #Calculate Last Online Time
        time=None
        if from_user.last_online_date:
            timeunix = from_user.last_online_date
            time = datetime.fromtimestamp(timeunix).strftime("%a, %d %b %Y, %H:%M:%S")
		
        #Variable for BIO
        bio = client.get_chat(get_user).description

        #Message with Picture
        message_out_str = ""
        message_out_str += f"Profile Pictures: {pic_count}\n"
        message_out_str += f"\n"
        message_out_str += f"ID: <a href='tg://user?id={from_user.id}'>{from_user.id}</a>\n"
        message_out_str += f"\n"
        message_out_str += f"First Name: <a href='tg://user?id={from_user.id}'>{from_user.first_name}</a>\n"
        message_out_str += f"Last Name: {from_user.last_name}\n"
        message_out_str += f"Username: @{from_user.username}\n"
        message_out_str += f"Common Groups: {sendcommon}\n"
        message_out_str += f"\n"
        message_out_str += f"Is self: {from_user.is_self}\n"
        message_out_str += f"Is Bot: {from_user.is_bot}\n"
        message_out_str += f"Is Scam: {from_user.is_scam}\n"
        message_out_str += f"Is Support: {from_user.is_support}\n"
        message_out_str += f"Is Contact: {from_user.is_contact}\n"
        message_out_str += f"Is mutual Contact: {from_user.is_mutual_contact}\n"
        message_out_str += f"Is Deleted: {from_user.is_deleted}\n"
        message_out_str += f"Is Verified: {from_user.is_verified}\n"
        message_out_str += f"Is Restricted: {from_user.is_restricted}\n"
        message_out_str += f"\n"
        message_out_str += f"Last online: {onlinestatus}\n"
        message_out_str += f"DC ID: {from_user.dc_id}\n"
#        message_out_str += f"\n"
        if not time == None:
            message_out_str += f"Last online: {time}\n"
#        message_out_str += f"Last offline: {from_user.next_offline_date}\n"
#        message_out_str += f"Language: {from_user.language_code}\n"
#        message_out_str += f"Restrictions: {from_user.restrictions}\n"
        message_out_str += f"\n"
        message_out_str += f"Bio: \n{bio}\n"

    if from_user.photo is not None:
        local_user_photo = client.download_media(
            message=chat_photo.big_file_id
        )
        client.send_photo(
            LOGGER_GROUP,
            photo=local_user_photo,
            caption=message_out_str,
            parse_mode="html",
            disable_notification=True
        )
        os.remove(local_user_photo)
        message.delete()
        # If User without Picture
    else:
        client.send_photo=NO_PICTURE_PATH
        message.reply_photo(
            LOGGER_GROUP,
            photo=local_user_photo,
            caption=message_out_str,
            parse_mode="html",
            disable_notification=True
        )


@BOT.on_message(Filters.command("wj", "..") & Filters.me)   # Command: ..wj ChatID UserID
def when_joined(client: BOT, message: Message):
    chat = message.chat.id
    check1 = str(message.command[0])   # t
    check2 = int(message.command[1])   # 1   ChatID
    check3 = int(message.command[2])  # 2   UserID
    
    mes_date = None
    Username = None
	
#    print(check1)
#    print(check2)
#    print(check3)
    
    message.delete()

    #Count Messages of the Chat
    Chat_ID = int(message.command[1])
    counter = client.get_history_count(Chat_ID)

    if not check2 < 1 and check3 > 1:
        client.send_message(message.chat.id, "Wrong input! Correct Syntax: ..wj ChatID UserID")
        return
    else:
        ChatID = int(message.command[1])
        UserID = int(message.command[2]) 

    progress = client.send_message(message.chat.id, "`processed 0 messages...`")
    total = 0

    for msg in client.iter_history(ChatID, reverse=True):
        total += 1
        if total % 200 == 0:
            progress.edit_text(f"`Searching for\nChatID: {ChatID}\nUserID: {UserID}\nprocessed {total} of {counter} messages...`")
        if msg.from_user.id:
            if UserID == msg.from_user.id:
                Username = msg.from_user.username
                from_chat = client.get_chat(ChatID)
                mes_date = msg.date
                if not mes_date == None:
                   # Calculate Unix to time (first message)
                    date_time_fm = datetime.fromtimestamp(mes_date)
                    dfm = date_time_fm.strftime("%d.%m.%Y, %H:%M:%S")

                    message_out_str = ""
                    message_out_str += f"Processed {total} of {counter} messages:\n"
                    message_out_str += f"<a href='tg://user?id={UserID}'>@{Username}</a> joined @{from_chat.username}:\n"
                    message_out_str += f"<a href='https://t.me/{from_chat.username}/{msg.message_id}'>{dfm}</a>\n"
                    message_out_str += f"\n"
                    progress.edit_text(message_out_str, parse_mode="html")
                    return
        if total == counter:
            message_out_str1 = ""
            message_out_str1 += f"Cannot find this UserID in this group!\n"
            message_out_str1 += f"Chat ID: {ChatID}\n"
            message_out_str1 += f"User ID: {UserID}\n"
            progress.edit_text(message_out_str1, parse_mode="html")
            return