
import os
import html
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
CARD_NUMBER = os.getenv("CARD_NUMBER")

# Render tekin Web Service uchun port ochish hiyasi
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")
    def log_message(self, format, *args):
        return

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"Dummy server started on port {port}")
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class Form(StatesGroup):
    model = State()
    memory = State()
    defect = State()
    box = State()
    price = State()
    location = State()
    phone = State()
    photos = State()

user_photos = {}

def esc(text):
    if not text:
        return ""
    return html.escape(str(text))

@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    user_photos[message.from_user.id] = []
    await message.answer("📱 Telefon modelini kiriting\n(masalan: iPhone 13 Pro Max yoki Honor x9d):", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Form.model)

@dp.message(Form.model)
async def get_model(message: types.Message, state: FSMContext):
    await state.update_data(model=message.text)
    await message.answer("💾 Xotirasi va rangini kiriting\n(masalan: 128GB / Qora):")
    await state.set_state(Form.memory)

@dp.message(Form.memory)
async def get_memory(message: types.Message, state: FSMContext):
    await state.update_data(memory=message.text)
    await message.answer("🔍 Aybi yoki defekti bormi?\n(Masalan: Yo'q / Ekranida kichik tirnalgani bor):")
    await state.set_state(Form.defect)

@dp.message(Form.defect)
async def get_defect(message: types.Message, state: FSMContext):
    await state.update_data(defect=message.text)
    await message.answer("📦 Karobka va hujjatlari bormi?\n(Masalan: Bor / Yo'q):")
    await state.set_state(Form.box)

@dp.message(Form.box)
async def get_box(message: types.Message, state: FSMContext):
    await state.update_data(box=message.text)
    await message.answer("💰 Narxini kiriting (masalan: 500$ / 6 000 000 so'm):")
    await state.set_state(Form.price)

@dp.message(Form.price)
async def get_price(message: types.Message, state: FSMContext):
    await state.update_data(price=message.text)
    await message.answer("📍 Manzilingizni kiriting (masalan: Namangan sh, Chorsu):")
    await state.set_state(Form.location)

@dp.message(Form.location)
async def get_location(message: types.Message, state: FSMContext):
    await state.update_data(location=message.text)
    kb = [[KeyboardButton(text="📞 Telefon raqamni yuborish", request_contact=True)]]
    markup = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
    await message.answer("📞 Telefon raqamingizni tugma orqali yuboring:", reply_markup=markup)
    await state.set_state(Form.phone)

@dp.message(Form.phone, F.contact | F.text)
async def get_phone(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number if message.contact else message.text
    await state.update_data(phone=phone)
    user_photos[message.from_user.id] = []
    await message.answer("📸 Endi telefon rasmlarini yuboring (10 tagacha).\nTayyor bo'lgach '✅ Tayyor' deb yozing:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Form.photos)

@dp.message(Form.photos, F.photo)
async def collect_photos(message: types.Message, state: FSMContext):
    uid = message.from_user.id
    if uid not in user_photos:
        user_photos[uid] = []
    user_photos[uid].append(message.photo[-1].file_id)
    await message.answer(f"✅ {len(user_photos[uid])} ta rasm qabul qilindi. Yana yuboring yoki '✅ Tayyor' deb yozing.")

@dp.message(Form.photos, F.text)
async def finish_photos(message: types.Message, state: FSMContext):
    if "tayyor" not in message.text.lower() and "yuklab" not in message.text.lower():
        if len(user_photos.get(message.from_user.id, [])) == 0:
            await message.answer("Rasm yuboring yoki '✅ Tayyor' deb yozing")
            return

    uid = message.from_user.id
    photos = user_photos.get(uid, [])
    data = await state.get_data()

    caption = (
        f"📱 Model: {esc(data.get('model'))}\n"
        f"💾 Xotira / Rang: {esc(data.get('memory'))}\n"
        f"🔍 Holati: {esc(data.get('defect'))}\n"
        f"📦 Karobka: {esc(data.get('box'))}\n"
        f"💰 Narxi: {esc(data.get('price'))}\n"
        f"📍 Manzil: {esc(data.get('location'))}\n"
        f"📞 Tel: {esc(data.get('phone'))}\n\n"
        f"👤 Sotuvchi: @{esc(message.from_user.username) if message.from_user.username else esc(message.from_user.full_name)}"
    )

    try:
        if photos:
            media = []
            for i, fid in enumerate(photos[:10]):
                if i == 0:
                    media.append(types.InputMediaPhoto(media=fid, caption=caption))
                else:
                    media.append(types.InputMediaPhoto(media=fid))
            await bot.send_media_group(chat_id=CHANNEL_ID, media=media)
        else:
            await bot.send_message(chat_id=CHANNEL_ID, text=caption)

        await message.answer(f"✅ E'loningiz kanalga yuborildi!\n{CHANNEL_USERNAME}\n\nYangi e'lon uchun /start bosing")
    except Exception as e:
        await message.answer(f"❌ Xatolik: {e}\nAdmin: {ADMIN_USERNAME}")
        print(f"ERROR: {e}")

    await state.clear()
    if uid in user_photos:
        del user_photos[uid]

async def main():
    print("Bot polling started...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
