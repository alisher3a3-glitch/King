import os
import sqlite3
import telebot
from telebot import types
from datetime import datetime

# --- SOZLAMALAR (Render Environment dan olinadi) ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "8949101318:AAHeOelqglF9NJfEmkRq2csgPYyQzeA_gEA")
ADMIN_ID = int(os.getenv("ADMIN_ID", "3594418817"))
CHANNEL = os.getenv("CHANNEL", "@qaldirgoch_mobile")
ADMIN_USERNAME = "@AliSheR"
BOT_USERNAME = "@AiElonchibot"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# --- BAZA ---
conn = sqlite3.connect('elonlar.db', check_same_thread=False)
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS elonlar
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER,
              message_id INTEGER,
              channel_message_id INTEGER,
              kategoriya TEXT,
              model TEXT,
              xotira TEXT,
              batareya TEXT,
              rangi TEXT,
              komplekt TEXT,
              narx TEXT,
              tavsif TEXT,
              manzil TEXT,
              tel TEXT,
              bezovta_vaqti TEXT,
              rasmlar TEXT,
              status TEXT)""")
conn.commit()

user_states = {}

# --- KEYBOARDS ---
def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("📢 E'lon berish", "📋 Mening e'lonlarim")
    kb.add("🤝 Hamkorlik va Reklama", "🛡️ Ishonchli savdo")
    kb.add("☕ Choy chaqa")
    return kb

def kategoriya_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("📱 Smartphone", "📞 Knopkali telefon")
    kb.add("🎧 Aksessuar", "⬅️ Orqaga")
    return kb

def contact_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton("📱 Raqamni ulashish", request_contact=True))
    kb.add("✍️ Yozib kiritish", "⬅️ Orqaga")
    return kb

def tasdiqlash_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("✅ Tasdiqlash va kanalga yuborish", "❌ Bekor qilish")
    return kb

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 
        f"👋 Assalomu alaykum!\n\n"
        f"📱 <b>{CHANNEL} kanalining rasmiy botiga xush kelibsiz!</b>\n\n"
        f"Bu yerda telefon va aksessuarlaringizni tez va oson sotasiz.\n"
        f"Har bir e'londa 🛡️ Ishonchli savdo mavjud!\n\n"
        f"👇 Quyidagi menyudan tanlang:",
        reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "🤝 Hamkorlik va Reklama")
def hamkorlik(m):
    bot.send_message(m.chat.id,
        "🤝 <b>Hamkorlik va Reklama</b>\n\n"
        "Reklama joylashtirish, hamkorlik va boshqa masalalar bo'yicha:\n"
        f"👨‍💼 Admin: {ADMIN_USERNAME}\n"
        "⏰ Javob berish vaqti: 24 soat ichida\n\n"
        "E'loningizni tezroq sotmoqchimisiz? Admin bilan bog'laning!",
        reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "🛡️ Ishonchli savdo")
def ishonchli(m):
    bot.send_message(m.chat.id,
        "🛡️ <b>Admin orqali ishonchli savdo (100% Xavfsiz)</b>\n\n"
        "Firibgarlardan qo'rqasizmi? Admin orqali savdo qiling!\n\n"
        "<b>Qanday ishlaydi:</b>\n"
        "1️⃣ Sotuvchi va oluvchi @AliSheR ga murojaat qiladi\n"
        "2️⃣ Sotuvchi telefonni adminga ko'rsatadi / olib keladi\n"
        "3️⃣ Oluvchi pulni vaqtincha adminga beradi\n"
        "4️⃣ Hammasi tekshirilgach, admin telefonni oluvchiga, pulni sotuvchiga beradi\n\n"
        "💰 <b>Xizmat haqi:</b> Kelishilgan narxda\n"
        f"👨‍💼 <b>Murojaat:</b> {ADMIN_USERNAME}\n\n"
        "Kanaldagi har bir e'londa ham bu xizmat ko'rsatilgan!",
        reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "☕ Choy chaqa")
def choy(m):
    bot.send_message(m.chat.id,
        "☕ <b>Choy chaqa (Ixtiyoriy)</b>\n\n"
        "Bot sizga yoqdimi? Xizmatimizni qo'llab-quvvatlamoqchi bo'lsangiz:\n\n"
        "💳 <b>Karta:</b> <code>9860350147263700</code>\n"
        "👤 Alisher Abdullayev\n\n"
        "Bu majburiy emas, ixtiyoriy. Rahmat!",
        reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "📢 E'lon berish")
def elon_berish(m):
    user_states[m.from_user.id] = {"step": "kategoriya", "data": {}, "photos": []}
    bot.send_message(m.chat.id, "📂 Qaysi turdagi e'lon bermoqchisiz?", reply_markup=kategoriya_menu())

@bot.message_handler(func=lambda m: m.text == "⬅️ Orqaga")
def orqaga(m):
    user_states.pop(m.from_user.id, None)
    bot.send_message(m.chat.id, "Asosiy menyu:", reply_markup=main_menu())

def make_caption(data, sold=False):
    xotira_line = f"💾 Xotira: {data.get('xotira','—')}\n" if data.get('xotira') and data.get('xotira') != "—" else ""
    batareya_line = f"🔋 Batareya: {data.get('batareya','—')}\n" if data.get('batareya') and data.get('batareya') != "—" else ""
    hashtag_model = "#" + "".join(data['model'].split()[:2]).replace("-","_")
    hashtag_manzil = "#" + data['manzil'].split()[0]
    sold_header = "✅ <b>SOTILDI!</b>\n\n" if sold else ""
    caption = f"""{sold_header}<b>{data['kategoriya']} — {data['model']}</b>

{xotira_line}{batareya_line}🎨 Rangi: {data['rangi']}
📦 Komplekt: {data['komplekt']}
💰 Narxi: {data['narx']}

📝 <b>Tavsif:</b> {data['tavsif']}

📍 Manzil: {data['manzil']}
📞 Tel: {data['tel']}
⏰ Bezovta vaqti: {data['bezovta_vaqti']}

—————————————
🛡️ <b>ISHONCHLI SAVDO MAVJUD!</b>
Ushbu e'lonni Admin {ADMIN_USERNAME} orqali 100% xavfsiz olishingiz mumkin. Xizmati kelishilgan narxda.

📢 Kanal: {CHANNEL}
🤖 Bot: {BOT_USERNAME}
{hashtag_model} {hashtag_manzil} #QaldirgochMobile
"""
    return caption

@bot.message_handler(content_types=['text', 'contact', 'photo'])
def state_handler(message):
    user_id = message.from_user.id
    if user_id not in user_states:
        return
    state = user_states[user_id]
    step = state["step"]
    data = state["data"]

    if step == "kategoriya":
        if message.text not in ["📱 Smartphone", "📞 Knopkali telefon", "🎧 Aksessuar"]:
            return
        data["kategoriya"] = message.text
        state["step"] = "model"
        bot.send_message(message.chat.id, "📱 Modelini yozing? (Masalan: iPhone 14 Pro Max)", reply_markup=types.ReplyKeyboardRemove())
        return
    if step == "model":
        data["model"] = message.text
        if "iphone" in message.text.lower():
            state["step"] = "xotira"
            bot.send_message(message.chat.id, "💾 Xotira hajmi? (Masalan: 128GB)")
        else:
            data["xotira"] = "—"
            state["step"] = "rangi"
            bot.send_message(message.chat.id, "🎨 Rangi qanday?")
        return
    if step == "xotira":
        data["xotira"] = message.text
        state["step"] = "batareya"
        bot.send_message(message.chat.id, "🔋 Batareya holati necha %?")
        return
    if step == "batareya":
        data["batareya"] = message.text
        state["step"] = "rangi"
        bot.send_message(message.chat.id, "🎨 Rangi qanday?")
        return
    if step == "rangi":
        data["rangi"] = message.text
        state["step"] = "komplekt"
        bot.send_message(message.chat.id, "📦 Komplektda nimalar bor?")
        return
    if step == "komplekt":
        data["komplekt"] = message.text
        state["step"] = "narx"
        bot.send_message(message.chat.id, "💰 Narxini yozing?")
        return
    if step == "narx":
        data["narx"] = message.text
        state["step"] = "rasm"
        bot.send_message(message.chat.id, "📸 Rasm yuboring (4 tagacha).\nTayyor bo'lgach '✅ Rasmlar tayyor' deb yozing.")
        return
    if step == "rasm":
        if message.content_type == 'photo':
            if len(state["photos"]) < 4:
                state["photos"].append(message.photo[-1].file_id)
                bot.send_message(message.chat.id, f"✅ {len(state['photos'])}/4 qabul qilindi.")
            else:
                bot.send_message(message.chat.id, "❗ Maksimal 4 ta. '✅ Rasmlar tayyor' deb yozing.")
            return
        if message.text == "✅ Rasmlar tayyor":
            if len(state["photos"]) == 0:
                bot.send_message(message.chat.id, "❗ Kamida 1 ta rasm kerak!")
                return
            state["step"] = "tavsif"
            bot.send_message(message.chat.id, "📝 Tavsif / nuqsoni bormi?")
            return
    if step == "tavsif":
        data["tavsif"] = message.text
        state["step"] = "manzil"
        bot.send_message(message.chat.id, "📍 Manzil qayer?")
        return
    if step == "manzil":
        data["manzil"] = message.text
        state["step"] = "tel"
        bot.send_message(message.chat.id, "📞 Telefon raqamingiz:", reply_markup=contact_menu())
        return
    if step == "tel":
        if message.contact:
            data["tel"] = message.contact.phone_number
        else:
            if message.text == "✍️ Yozib kiritish":
                bot.send_message(message.chat.id, "📞 Raqamingizni yozing:", reply_markup=types.ReplyKeyboardRemove())
                state["step"] = "tel_yozish"
                return
            data["tel"] = message.text
        state["step"] = "bezovta"
        bot.send_message(message.chat.id, "⏰ Bezovta qilmaslik vaqti?", reply_markup=types.ReplyKeyboardRemove())
        return
    if step == "tel_yozish":
        data["tel"] = message.text
        state["step"] = "bezovta"
        bot.send_message(message.chat.id, "⏰ Bezovta qilmaslik vaqti?")
        return
    if step == "bezovta":
        data["bezovta_vaqti"] = message.text
        preview = make_caption(data)
        state["step"] = "tasdiqlash"
        if state["photos"]:
            media = []
            for i, fid in enumerate(state["photos"]):
                if i == 0:
                    media.append(types.InputMediaPhoto(fid, caption=preview))
                else:
                    media.append(types.InputMediaPhoto(fid))
            bot.send_media_group(message.chat.id, media)
        else:
            bot.send_message(message.chat.id, preview)
        bot.send_message(message.chat.id, "👆 Shunday ko'rinishda chiqadi. Tasdiqlaysizmi?", reply_markup=tasdiqlash_menu())
        return
    if step == "tasdiqlash":
        if message.text == "✅ Tasdiqlash va kanalga yuborish":
            caption = make_caption(data)
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(types.InlineKeyboardButton(f"📞 Sotuvchi: {data['tel']}", url=f"https://t.me/{ADMIN_USERNAME[1:]}"))
            markup.add(types.InlineKeyboardButton("🛡️ Admin orqali xavfsiz olish", url=f"https://t.me/{ADMIN_USERNAME[1:]}"))
            try:
                if len(state["photos"]) == 1:
                    sent = bot.send_photo(CHANNEL, state["photos"][0], caption=caption, reply_markup=markup)
                    ch_msg_id = sent.message_id
                else:
                    sent_msgs = bot.send_media_group(CHANNEL, [types.InputMediaPhoto(fid, caption=caption if i==0 else "") for i, fid in enumerate(state["photos"])])
                    # Ikkinchi xabar tugmalar uchun
                    sent2 = bot.send_message(CHANNEL, f"☝️ {data['model']} — Bog'lanish:", reply_markup=markup)
                    ch_msg_id = sent_msgs[0].message_id

                c.execute("INSERT INTO elonlar (user_id, channel_message_id, kategoriya, model, xotira, batareya, rangi, komplekt, narx, tavsif, manzil, tel, bezovta_vaqti, rasmlar, status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                          (user_id, ch_msg_id, data['kategoriya'], data['model'], data.get('xotira','—'), data.get('batareya','—'), data['rangi'], data['komplekt'], data['narx'], data['tavsif'], data['manzil'], data['tel'], data['bezovta_vaqti'], ",".join(state["photos"]), "active"))
                conn.commit()
                bot.send_message(message.chat.id, f"✅ E'lon {CHANNEL} ga joylandi!\n🛡️ Ishonchli savdo bilan!", reply_markup=main_menu())
                bot.send_message(ADMIN_ID, f"🆕 Yangi e'lon: {data['model']} - {data['narx']}")
            except Exception as e:
                bot.send_message(message.chat.id, f"❌ Xatolik: {e}\nBotni kanalda admin qiling!", reply_markup=main_menu())
            user_states.pop(user_id, None)
        else:
            bot.send_message(message.chat.id, "❌ Bekor qilindi.", reply_markup=main_menu())
            user_states.pop(user_id, None)
        return

@bot.message_handler(func=lambda m: m.text == "📋 Mening e'lonlarim")
def mening_elonlarim(m):
    c.execute("SELECT id, model, narx, status, channel_message_id FROM elonlar WHERE user_id=? ORDER BY id DESC", (m.from_user.id,))
    rows = c.fetchall()
    if not rows:
        bot.send_message(m.chat.id, "📭 Hali e'lonlaringiz yo'q.", reply_markup=main_menu())
        return
    for elon_id, model, narx, status, ch_msg_id in rows:
        icon = "✅ SOTILDI" if status == "sold" else "🟢 Aktiv"
        kb = types.InlineKeyboardMarkup()
        if status == "active":
            kb.add(types.InlineKeyboardButton("✅ SOTILDI deb belgilash", callback_data=f"sold_{elon_id}_{ch_msg_id}"))
        bot.send_message(m.chat.id, f"{icon}\n📱 {model}\n💰 {narx}\nID: {elon_id}", reply_markup=kb)

@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    if call.data.startswith("sold_"):
        _, elon_id, ch_msg_id = call.data.split("_")
        c.execute("UPDATE elonlar SET status='sold' WHERE id=?", (elon_id,))
        conn.commit()
        try:
            c.execute("SELECT kategoriya, model, xotira, batareya, rangi, komplekt, narx, tavsif, manzil, tel, bezovta_vaqti FROM elonlar WHERE id=?", (elon_id,))
            r = c.fetchone()
            if r:
                data = {"kategoriya": r[0], "model": r[1], "xotira": r[2], "batareya": r[3], "rangi": r[4], "komplekt": r[5], "narx": r[6], "tavsif": r[7], "manzil": r[8], "tel": r[9], "bezovta_vaqti": r[10]}
                new_cap = make_caption(data, sold=True)
                bot.edit_message_caption(chat_id=CHANNEL, message_id=int(ch_msg_id), caption=new_cap)
        except Exception as e:
            print(e)
        bot.answer_callback_query(call.id, "✅ Sotildi deb belgilandi, o'chirilmadi!")
        bot.send_message(call.message.chat.id, f"✅ E'lon SOTILDI deb belgilandi. Kanalda qoladi, tepasida SOTILDI yozuvi chiqadi.\n\n☕ Ixtiyoriy choy chaqa: 9860350147263700 Alisher Abdullayev")

print("Bot ishga tushdi...")
bot.infinity_polling()
