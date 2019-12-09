import sqlite3
from html import escape, unescape
from pyrogram import Filters, Message, User
from pyrobot import BOT, PYRO_DB

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
    message.edit(f"AFK message set:\n\n{afk_text[1:]}", disable_web_page_preview=True)        
    db.commit()

# Reply at mentioned and private messages
@BOT.on_message(Filters.mentioned or Filters.private)
def answer_mentioned(bot: BOT, message: Message):
    db = sqlite3.connect(PYRO_DB)
    c = db.cursor()
    c.execute(GET_AFK.format(message.chat.id))
    res = c.fetchone()
    try:   
        mes = str(res[0])[1:]
        check = str(res[1])
        if check == "1":
            bot.send_message(message.chat.id, f"`Sorry, i'm away from Keyboard!\n{mes}`")
    except:
        return
 
 # Automatic switch off AFK
@BOT.on_message(Filters.outgoing)
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
    except:
        return   