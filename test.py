from pyrogram import Filters, Message
from datetime import datetime
from pyrobot import BOT, LOGGER_GROUP

@BOT.on_message(Filters.command("t", ".") & Filters.me)   # Command: .t ChatID Username
def word_count(bot: BOT, message: Message):
    chat = message.chat.id
    check1 = str(message.command[0])   # t
    check2 = str(message.command[1])   # 1   Chat_ID
    check3 = str(message.command[2])  # 2   User_ID
	
    print(check1)
    print(check2)
    print(check3)

    if not len(message.command) > 1:
        bot.send_message(LOGGER_GROUP, "Wrong input.............")
#        message.delete()
        return
    else:
        ChatID = int(message.command[1])
        UserName = str(message.command[2]) 

    progress = bot.send_message(LOGGER_GROUP, "`processed 0 messages...`")
    total = 0
#        message.delete()

    for msg in bot.iter_history(ChatID, reverse=True):
        total += 1
        if total % 200 == 0:
            progress.edit_text(f"`processed {total} messages...`")
        mes_date = None
        if msg.from_user.username:
            if UserName in msg.from_user.username:
                mes_date = msg.date
                if not mes_date == None:
                   # Calculate Unix to time (first message)
                    date_time_fm = datetime.fromtimestamp(mes_date)
                    dfm = date_time_fm.strftime("%d.%m.%Y, %H:%M:%S")
                    bot.send_message(LOGGER_GROUP, dfm)
                    print(dfm)
                    return

    progress.edit_text(out, parse_mode="html")