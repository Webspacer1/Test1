import sqlite3
from html import escape, unescape
from pyrogram import Filters, Message, User
from pyrobot import BOT, PYRO_DB, LOGGER_GROUP

SET_AFKTEXT = """INSERT OR FAIL INTO afk VALUES ("{}", "{}")"""
GET_AFK = "SELECT afktext, checker FROM afk"
SET_AFKOFF = """INSERT OR FAIL INTO afk VALUES ("{}", "{}")"""
REMOVE_AFKTEXT = "DELETE FROM afk"

# Switch on AFK
@BOT.on_message(Filters.command("afk", "..") & Filters.me)
def set_afk(bot: BOT, message: Message):
    afk_text = message.text.markdown[5:]
    checker = 1
    db = sqlite3.connect(PYRO_DB)
    c = db.cursor()
    c.execute(REMOVE_AFKTEXT.format(message.chat.id))
    db.commit()
    db = sqlite3.connect(PYRO_DB)
    c = db.cursor()
    c.execute(SET_AFKTEXT.format(escape(afk_text), checker))
    message.edit(f"AFK message set:\n{afk_text[1:]}", disable_web_page_preview=True)        
    db.commit()

# Reply at private and mentioned messages
@BOT.on_message(Filters.private | Filters.mentioned, group=1)
def answer_mentioned(bot: BOT, message: Message):
    chatid = str(message.chat.id).replace("-100", "")
    messageID = message.message_id
    username = message.from_user.first_name
    usertype = message.chat.type
    if usertype == 'private' or 'supergroup' or 'group':
        db = sqlite3.connect(PYRO_DB)
        c = db.cursor()
        c.execute(GET_AFK.format(message.chat.id))
        res = c.fetchone()
        try:   
            mes = str(res[0])[1:]
            check = str(res[1])
            if check == "1":
#                bot.send_message(message.chat.id, f"`Sorry, i'm away from Keyboard!\n{mes}`")
                bot.send_message(chat_id=message.chat.id, text=f"`Sorry, i'm away from Keyboard!\n{mes}`", reply_to_message_id=messageID)
                if usertype == 'supergroup':
                    bot.send_message(LOGGER_GROUP, f"<b>Sent away message to <a href='t.me/c/{chatid}/{messageID}'>{username}</a> ({usertype})!</b>", parse_mode="html")
                elif usertype == 'private' or 'group':
                    bot.send_message(LOGGER_GROUP, f"<b>Sent away message to {username} ({usertype})!</b>", parse_mode="html")
                else:
                    bot.send_message(LOGGER_GROUP, f"<b>Sent away message to unknown!</b>", parse_mode="html")
        except:
            return
    else:
        return
 
 # Automatic switch off AFK
@BOT.on_message(Filters.outgoing, group=-1)
def set_afk(bot: BOT, message: Message):
    db = sqlite3.connect(PYRO_DB)
    c = db.cursor()
    c.execute(GET_AFK.format(message.chat.id))
    res = c.fetchone()
    try:   
        check = str(res[1])
        if check == "1":
            afk_text = "disabled"
            checker = 0
            db = sqlite3.connect(PYRO_DB)
            c = db.cursor()
            c.execute(REMOVE_AFKTEXT.format(message.chat.id))
            db.commit()
            db = sqlite3.connect(PYRO_DB)
            c = db.cursor()
            c.execute(SET_AFKOFF.format(escape(afk_text), checker))
            db.commit()
#            message.edit(f"AFK switched off!\n", disable_web_page_preview=True)
            if checker == 0:
                bot.send_message(LOGGER_GROUP, f"AFK mode switched off", parse_mode="html")
    except:
        return   