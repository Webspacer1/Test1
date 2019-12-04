from pyrogram import Filters, Message
from datetime import datetime
from pyrobot import BOT

@BOT.on_message(Filters.command("t", ".") & Filters.me)   # Command: .t ChatID UserID
def word_count(bot: BOT, message: Message):
    chat = message.chat.id
    check1 = str(message.command[0])   # t
    check2 = int(message.command[1])   # 1   ChatID
    check3 = int(message.command[2])  # 2   UserID
	
#    print(check1)
#    print(check2)
#    print(check3)
    
    message.delete()

    if not check2 < 1 and check3 > 1:
        bot.send_message(message.chat.id, "Wrong input! Correct Syntax: .t ChatID UserID")
        return
    else:
        ChatID = int(message.command[1])
        UserID = int(message.command[2]) 

    progress = bot.send_message(message.chat.id, "`processed 0 messages...`")
    total = 0

    for msg in bot.iter_history(ChatID, reverse=True):
        total += 1
        if total % 200 == 0:
            progress.edit_text(f"`Searching for\nChatID: {ChatID}\nUserID: {UserID}\nprocessed {total} messages...`")
        mes_date = None
        Username = None
        if msg.from_user.id:
            if UserID == msg.from_user.id:
                Username = msg.from_user.username
                from_chat = bot.get_chat(ChatID)
                mes_date = msg.date
                if not mes_date == None:
                   # Calculate Unix to time (first message)
                    date_time_fm = datetime.fromtimestamp(mes_date)
                    dfm = date_time_fm.strftime("%d.%m.%Y, %H:%M:%S")
                    progress.edit_text(f"`Processed {total} messages.\n@{Username} is in {from_chat.title} since:\n{dfm}`")
                    return

    progress.edit_text(out, parse_mode="html")