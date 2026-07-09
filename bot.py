import os
from flask import Flask, request
import telebot

# Bot tokenini shu yerga yozasiz (yoki server sozlamalaridan olinadi)
BOT_TOKEN = os.environ.get('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
bot = telebot.TeleBot(BOT_TOKEN)

app = Flask(__name__)

# Adminlar ro'yxati (123456789 o'rniga o'zingizning Telegram ID raqamingizni yozing)
ADMINS = [123456789]
# VIP foydalanuvchilar ro'yxati (vaqtincha xotirada saqlanadi)
VIP_USERS = set()

# /start komandasi
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if user_id in VIP_USERS:
        bot.reply_to(message, "🌟 Salom! Siz VIP foydalanuvchisiz. Barcha signallar va funksiyalar siz uchun ochiq!")
    else:
        bot.reply_to(message, "👋 Botga xush kelibsiz!\n\nSiz hozircha oddiy foydalanuvchisiz. VIP statusga ega bo'lish va signallarni ko'rish uchun adminga murojaat qiling.")

# Admin panel komandasi
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id in ADMINS:
        bot.reply_to(message, "👨‍💻 Admin panelga xush kelibsiz!\n\nBuyruqlar:\n/addvip [ID] - VIP a'zo qo'shish\n/delvip [ID] - VIPdan o'chirish")
    else:
        bot.reply_to(message, "❌ Bu buyruq faqat adminlar uchun!")

# VIP a'zo qo'shish (Faqat admin uchun)
@bot.message_handler(commands=['addvip'])
def add_vip(message):
    if message.from_user.id in ADMINS:
        try:
            target_id = int(message.text.split()[1])
            VIP_USERS.add(target_id)
            bot.reply_to(message, f"✅ Foydalanuvchi {target_id} VIP ro'yxatiga qo'shildi!")
        except (IndexError, ValueError):
            bot.reply_to(message, "⚠️ Xatolik! IDni to'g'ri kiriting.\nMisol: `/addvip 123456789`")

# VIP a'zodan o'chirish (Faqat admin uchun)
@bot.message_handler(commands=['delvip'])
def del_vip(message):
    if message.from_user.id in ADMINS:
        try:
            target_id = int(message.text.split()[1])
            if target_id in VIP_USERS:
                VIP_USERS.remove(target_id)
                bot.reply_to(message, f"❌ Foydalanuvchi {target_id} VIP ro'yxatidan o'chirildi.")
            else:
                bot.reply_to(message, "Bu foydalanuvchi VIP ro'yxatida yo'q.")
        except (IndexError, ValueError):
            bot.reply_to(message, "⚠️ Misol: `/delvip 123456789`")

# Flask va Webhook qismi (gunicorn serverda ishlashi uchun)
@app.route('/' + BOT_TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    return "Bot muvaffaqiyatli ishlamoqda!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
      
