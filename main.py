import asyncio
import os
import logging
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InputMediaPhoto
)

# .env fayldan o'qish (local uchun)
load_dotenv()

# --- SOZLAMALAR - XAVFSIZ ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
# CHANNEL_ID ni Render'da -100 bilan boshlanadigan raqam sifatida yozing
# Masalan: -1002345678901
CHANNEL_ID_RAW = os.getenv("CHANNEL_ID", "@Telefon_Namangan_Savdo")
try:
    CHANNEL_ID = int(CHANNEL_ID_RAW)
except ValueError:
    CHANNEL_ID = CHANNEL_ID_RAW  # Agar username bo'lsa shunday qoladi

CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@Telefon_Namangan_Savdo")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "AliSheR_L")
CARD_NUMBER = os.getenv("CARD_NUMBER", "9860 3501 4726 3700")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN topilmadi! Render Environment ga qo'shing.")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Doimiy ekranda turadigan asosiy menyu
main_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Yangi e'lon berish")]
    ],
    resize_keyboard=True
)

class Form(StatesGroup):
    model = State()
    memory_color = State()
    condition = State()
    defect = State()
    battery = State()
    box_docs = State()
    price = State()
    location = State()
    phone = State()
    photo = State()

class AdminBroadcast(StatesGroup):
    waiting_for_post = State()

# --- START & MENYU ---
@dp.message(Command("start"))
@dp.message(F.text == "➕ Yangi e'lon berish")
async def start_cmd(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 **Xush kelibsiz!**\n\n"
        "📱 Telefoningizni sotish uchun e'lon berishni boshlaymiz.\n"
        "Iltimos, telefon modelini kiriting (masalan: *iPhone 13 Pro Max* yoki *Samsung S23*):\n\n"
        "❓ Savol yoki muammolar bo'lsa: /help buyrug'ini bosing.",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )
    await state.set_state(Form.model)

@dp.message(Command("help"))
async def help_cmd(message: Message):
    admin_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👨‍💻 Admin bilan bog'lanish", url=f"https://t.me/{ADMIN_USERNAME}")]
        ]
    )
    await message.answer(
        "❓ **Yordam va Murojaat**\n\n"
        "Botdan foydalanishda muammo yuzaga kelsa yoki takliflaringiz bo'lsa, "
        "admin bilan bog'lanishingiz mumkin:",
        reply_markup=admin_keyboard,
        parse_mode="Markdown"
    )

# --- ADMIN PANEL ---
@dp.message(Command("admin"))
async def admin_panel(message: Message):
    # Username ni kichik harfda solishtiramiz, @ belgisiz
    user_username = (message.from_user.username or "").lower()
    admin_check = ADMIN_USERNAME.lower().replace("@", "")

    if user_username == admin_check:
        admin_menu = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📢 Kanalga xabar/tabrik joylash", callback_data="admin_broadcast")]
            ]
        )
        await message.answer("🛠 **Admin Panel**\n\nQuyidagi tugma orqali kanalga post yoki tabrik yuborishingiz mumkin:", reply_markup=admin_menu, parse_mode="Markdown")
    else:
        await message.answer("❌ Siz admin emassiz!")

@dp.callback_query(F.data == "admin_broadcast")
async def start_broadcast(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer("📢 **Kanalga yubormoqchi bo'lgan xabaringizni kiriting:**\n\n(Bu matn, rasm yoki tayyor tabrik xabari bo'lishi mumkin)", parse_mode="Markdown")
    await state.set_state(AdminBroadcast.waiting_for_post)

@dp.message(AdminBroadcast.waiting_for_post)
async def send_broadcast_to_channel(message: Message, state: FSMContext):
    await state.clear()
    try:
        if message.photo:
            photo_id = message.photo[-1].file_id
            caption_text = message.caption if message.caption else ""
            await bot.send_photo(chat_id=CHANNEL_ID, photo=photo_id, caption=caption_text, parse_mode="HTML" if caption_text else None)
        elif message.text:
            await bot.send_message(chat_id=CHANNEL_ID, text=message.text, parse_mode="HTML")
        else:
            # Forward boshqa turdagi postlar uchun
            await bot.forward_message(chat_id=CHANNEL_ID, from_chat_id=message.chat.id, message_id=message.message_id)

        await message.answer("✅ Post/Tabrik kanalga muvaffaqiyatli joylandi!", reply_markup=main_menu_keyboard)
    except Exception as e:
        logging.error(f"Broadcast error: {e}")
        await message.answer(f"❌ Xatolik yuz berdi: {e}\n\nBot kanalga admin qilinganini va CHANNEL_ID to'g'riligini tekshiring.", reply_markup=main_menu_keyboard)

# --- E'LON QADAMLARI ---
@dp.message(Form.model)
async def process_model(message: Message, state: FSMContext):
    await state.update_data(model=message.text)
    await message.answer("💾 Xotirasi va rangini kiriting (masalan: *128GB / Qora*):", parse_mode="Markdown")
    await state.set_state(Form.memory_color)

@dp.message(Form.memory_color)
async def process_memory_color(message: Message, state: FSMContext):
    await state.update_data(memory_color=message.text)
    condition_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✨ Yangi (Ideal)", callback_data="cond_yangi"),
                InlineKeyboardButton(text="📱 Ishlatilgan", callback_data="cond_ishlatilgan")
            ]
        ]
    )
    await message.answer("🛠 Telefon holatini tanlang:", reply_markup=condition_keyboard)
    await state.set_state(Form.condition)

@dp.callback_query(Form.condition, F.data.startswith("cond_"))
async def process_condition_callback(callback: CallbackQuery, state: FSMContext):
    cond_text = "Yangi (Ideal)" if callback.data == "cond_yangi" else "Ishlatilgan"
    await state.update_data(condition=cond_text)
    await callback.message.delete()
    await callback.message.answer(f"Holati: *{cond_text}*\n\n🔍 Aybi yoki defekti bormi? (Masalan: *Yo'q / Ekranida kichik tirnalgani bor*):", parse_mode="Markdown")
    await state.set_state(Form.defect)

@dp.message(Form.condition)
async def process_condition_text(message: Message, state: FSMContext):
    await state.update_data(condition=message.text)
    await message.answer("🔍 Aybi yoki defekti bormi? (Masalan: *Yo'q / Ekranida kichik tirnalgani bor*):", parse_mode="Markdown")
    await state.set_state(Form.defect)

@dp.message(Form.defect)
async def process_defect(message: Message, state: FSMContext):
    await state.update_data(defect=message.text)
    data = await state.get_data()
    model_name = data.get("model", "").lower()

    if "iphone" in model_name:
        await message.answer("🔋 Yomkost / Batareya foizini kiriting (masalan: *85%*):", parse_mode="Markdown")
        await state.set_state(Form.battery)
    else:
        await state.update_data(battery="-")
        await message.answer("📦 Karobka va hujjatlari bormi? (Masalan: *Bor / Yo'q*):", parse_mode="Markdown")
        await state.set_state(Form.box_docs)

@dp.message(Form.battery)
async def process_battery(message: Message, state: FSMContext):
    await state.update_data(battery=message.text)
    await message.answer("📦 Karobka va hujjatlari bormi? (Masalan: *Bor / Yo'q*):", parse_mode="Markdown")
    await state.set_state(Form.box_docs)

@dp.message(Form.box_docs)
async def process_box_docs(message: Message, state: FSMContext):
    await state.update_data(box_docs=message.text)
    await message.answer("💰 Narxini kiriting (masalan: *500$ / 6 000 000 so'm*):", parse_mode="Markdown")
    await state.set_state(Form.price)

@dp.message(Form.price)
async def process_price(message: Message, state: FSMContext):
    await state.update_data(price=message.text)
    await message.answer("📍 Manzilingizni kiriting (masalan: *Namangan sh, Chorsu*):", parse_mode="Markdown")
    await state.set_state(Form.location)

@dp.message(Form.location)
async def process_location(message: Message, state: FSMContext):
    await state.update_data(location=message.text)
    phone_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("📞 Aloqa uchun telefon raqamingizni yuboring (tugmani bosing yoki yozib yuboring):", reply_markup=phone_keyboard)
    await state.set_state(Form.phone)

@dp.message(Form.phone)
async def process_phone(message: Message, state: FSMContext):
    if message.contact:
        phone_num = message.contact.phone_number
        if not phone_num.startswith("+"):
            phone_num = "+" + phone_num
    else:
        phone_num = message.text

    await state.update_data(phone=phone_num, photos=[])
    await message.answer(
        "📸 Endi telefon rasmlarini yuboring (**1 tadan 4 tagacha** rasm yuborishingiz mumkin).\n\n"
        "Barcha rasmlarni yuborib bo'lgach, pastdagi tugmani bosing:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="✅ Rasmlarni yuklab bo'ldim / E'lonni joylash")]],
            resize_keyboard=True
        ),
        parse_mode="Markdown"
    )
    await state.set_state(Form.photo)

@dp.message(Form.photo, F.photo)
async def process_photo_collect(message: Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])

    if len(photos) >= 4:
        await message.answer("⚠️ Maksimal 4 ta rasm yuklay olasiz! Endi '✅ Rasmlarni yuklab bo'ldim / E'lonni joylash' tugmasini bosing.")
        return

    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)
    await message.answer(f"📸 {len(photos)}-rasm qabul qilindi. Yana rasm yuborishingiz yoki tugmani bosishingiz mumkin.")

@dp.message(Form.photo, F.text == "✅ Rasmlarni yuklab bo'ldim / E'lonni joylash")
async def process_photo_finish(message: Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])

    if not photos:
        await message.answer("⚠️ Iltimos, kamida 1 ta rasm yuboring!")
        return

    await state.clear()

    caption = (
        f"📱 **Model:** {data.get('model')}\n"
        f"💾 **Xotira/Rang:** {data.get('memory_color')}\n"
        f"🛠 **Holati:** {data.get('condition')}\n"
        f"🔍 **Aybi/Defekti:** {data.get('defect')}\n"
    )

    if data.get('battery') and data.get('battery') != '-':
        caption += f"🔋 **Yomkost:** {data.get('battery')}\n"

    caption += (
        f"📦 **Karobka-dok:** {data.get('box_docs')}\n"
        f"💰 **Narxi:** {data.get('price')}\n"
        f"📍 **Manzil:** {data.get('location')}\n\n"
        f"📞 **Aloqa:** {data.get('phone')}\n"
        f"👤 **Sotuvchi:** @{message.from_user.username if message.from_user.username else 'mavjud_emas'}\n\n"
        f"📣 {CHANNEL_USERNAME}"
    )

    try:
        if len(photos) == 1:
            channel_msg = await bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=photos[0],
                caption=caption,
                parse_mode="Markdown"
            )
            msg_id = channel_msg.message_id
        else:
            media_group = [InputMediaPhoto(media=photos[0], caption=caption, parse_mode="Markdown")]
            for photo_id in photos[1:]:
                media_group.append(InputMediaPhoto(media=photo_id))

            msgs = await bot.send_media_group(
                chat_id=CHANNEL_ID,
                media=media_group
            )
            msg_id = msgs[0].message_id

        sold_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔴 Sotildi (E'lonni yopish)", callback_data=f"sold_{msg_id}")]
            ]
        )

        await message.answer(
            "✅ **E'loningiz kanalingizga muvaffaqiyatli joylandi!**\n\n"
            "Telefoningiz sotilgach, kanaldagi e'lonni yopish uchun ushbu botdagi '🔴 Sotildi' tugmasini bosing.",
            reply_markup=sold_keyboard,
            parse_mode="Markdown"
        )
        await message.answer("Yangi e'lon berish uchun menyu:", reply_markup=main_menu_keyboard)

    except Exception as e:
        logging.error(f"Channel send error: {e}")
        await message.answer(f"❌ Kanalga yuborishda xatolik: {e}\n\nBotni kanalga admin qilganingizni va CHANNEL_ID to'g'ri ekanini tekshiring.", reply_markup=main_menu_keyboard)

@dp.callback_query(F.data.startswith("sold_"))
async def process_sold(callback: CallbackQuery):
    msg_id = int(callback.data.split("_")[1])

    sold_text = (
        "🔴 **SOTILDI! / ПРОДАНО!**\n"
        "-------------------------------------\n"
        "❌ Ushbu telefon sotib bo'lindi!\n\n"
        f"📣 {CHANNEL_USERNAME}"
    )

    try:
        # Avval yakka rasm bo'lib yuborilganmi deb urinib ko'ramiz
        try:
            await callback.bot.edit_message_caption(
                chat_id=CHANNEL_ID,
                message_id=msg_id,
                caption=sold_text,
                parse_mode="Markdown"
            )
        except Exception:
            # Agar media_group bo'lsa, caption ni edit qilib bo'lmaydi - xabar yuboramiz
            await callback.bot.edit_message_text(
                chat_id=CHANNEL_ID,
                message_id=msg_id,
                text=sold_text,
                parse_mode="Markdown"
            )

        donation_message = (
            "🎉 **E'loningiz 'SOTILDI' deb belgilandi!**\n\n"
            "Muvaffaqiyatli savdo bilan tabriklaymiz! 🤝\n\n"
            "☕️ Agar xizmatimiz sizga ma'qul kelgan bo'lsa, "
            "loyihamiz rivoji uchun ko'nglingizdan chiqgan miqdorda **choy puli (ehson)** o'tkazishingiz mumkin:\n\n"
            f"💳 **Karta raqami:** `{CARD_NUMBER}`\n\n"
            "E'tiboringiz uchun rahmat! 🚀"
        )

        admin_and_don_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="➕ Yangi e'lon berish", callback_data="new_ad")],
                [InlineKeyboardButton(text="👨‍💻 Admin bilan bog'lanish", url=f"https://t.me/{ADMIN_USERNAME}")]
            ]
        )

        await callback.message.edit_text(donation_message, reply_markup=admin_and_don_keyboard, parse_mode="Markdown")
        await callback.message.answer("Yangi e'lon berish uchun pastdagi tugmani bosing:", reply_markup=main_menu_keyboard)
        await callback.answer("Sotildi deb belgilandi!")

    except Exception as e:
        logging.error(f"Sold error: {e}")
        await callback.answer("⚠️ Xatolik yuz berdi yoki e'lon allaqachon tahrirlangan.", show_alert=True)

@dp.callback_query(F.data == "new_ad")
async def new_ad_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await start_cmd(callback.message, state)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
