import asyncio
from aiogram import Bot, Dispatcher, F, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

TOKEN = "8921085376:AAGp6utDQjBM5ChHsGdzRccnJR_SdVNPoO8"
ADMIN_ID = 7818671307
CHANNEL_ID = "@AronAccount"

dp = Dispatcher()

users_db = {}
global_ad_counter = 191  # E'lonlar raqami shu yerdan boshlanadi va avtomatik oshib boradi

def get_user(user_id: int):
    if user_id not in users_db:
        users_db[user_id] = {"balance": 0, "ads_count": 0, "last_ad_status": "Hali e'lon bermagansiz"}
    return users_db[user_id]

class AdStates(StatesGroup):
    waiting_for_details = State()
    waiting_for_photos = State()

class TopUpStates(StatesGroup):
    waiting_for_receipt = State()

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📢 E'lon joylash"), KeyboardButton(text="💳 Hisob to'ldirish")],
        [KeyboardButton(text="👤 Profili"), KeyboardButton(text="📊 E'lon holati")],
        [KeyboardButton(text="🛠 Yordam")]
    ],
    resize_keyboard=True
)

@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    get_user(message.from_user.id)
    text = (
        f"Salom, {html.bold(message.from_user.full_name)}! ⚡️\n\n"
        "Ushbu botga siz o'z accountingizni joylashingiz va "
        "sotishingiz mumkin. Kerakli tugmani tanlang 👇"
    )
    
    start_inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📖 Botdan foydalanish qo'llanmasi", url="https://t.me/qullama")]
        ]
    )
    
    await message.answer(text, reply_markup=main_keyboard, parse_mode=ParseMode.HTML)
    await message.answer("💡 Botdan qanday foydalanishni bilish uchun quyidagi qo'llanma kanaliga o'ting:", reply_markup=start_inline_kb)

@dp.message(F.text == "🛠 Yordam")
async def help_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("🛠 Yordam bo'limi\n\nAdmin bilan bog'lanish: @AronAccountAdmin", reply_markup=main_keyboard)

@dp.message(F.text == "🏠 Asosiy menyu")
async def back_to_main_text(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("🏠 Asosiy menyudasiz:", reply_markup=main_keyboard)


# --- 📊 E'LON HOLATI ---
@dp.message(F.text == "📊 E'lon holati")
async def status_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    user_data = get_user(message.from_user.id)
    text = (
        f"📊 <b>Sizning e'loningiz holati:</b>\n\n"
        f"Joriy holat: <b>{user_data['last_ad_status']}</b>\n"
        f"Jami joylangan e'lonlar: <b>{user_data['ads_count']} ta</b>"
    )
    await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=main_keyboard)


# --- 👤 PROFILI ---
@dp.message(F.text == "👤 Profili")
async def profile_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    user_data = get_user(message.from_user.id)
    text = (
        f"👤 <b>Sizning profilingiz:</b>\n\n"
        f"💳 Hisobingiz: <b>{user_data['balance']} UZS</b>\n"
        f"📢 Joylagan e'lonlaringiz: <b>{user_data['ads_count']} ta</b>"
    )
    await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=main_keyboard)


# --- 📢 E'LON JOYLASH ---
@dp.message(F.text == "📢 E'lon joylash")
async def start_ad(message: Message, state: FSMContext) -> None:
    await state.clear()
    user_id = message.from_user.id
    user_data = get_user(user_id)

    if user_data["balance"] < 5000:
        await message.answer(
            "❌ <b>Mablag' yetarli emas!</b>\n\n"
            "E'lon joylash narxi: <b>5,000 UZS</b>.\n"
            f"Sizning hisobingizda: <b>{user_data['balance']} UZS</b> bor.\n\n"
            "Iltimos, hisobingizni to'ldiring:",
            parse_mode=ParseMode.HTML,
            reply_markup=main_keyboard
        )
        return

    instruction_text = (
        "✍️ <b>Accountingiz ma'lumotlarini quyidagicha yuboring:</b>\n\n"
        "9 Sezon\n"
        "Medal\n"
        "Rank: rasmda\n"
        "Invintor: rasmda\n"
        "PRICE : 130.000\n\n"
        "<i>Shu ma'lumotlarni yozib yuboring:</i>"
    )
    
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🏠 Asosiy menyu")]],
        resize_keyboard=True
    )
    
    await message.answer(instruction_text, parse_mode=ParseMode.HTML, reply_markup=kb)
    await state.set_state(AdStates.waiting_for_details)

@dp.message(AdStates.waiting_for_details)
async def process_ad_details(message: Message, state: FSMContext) -> None:
    if message.text in ["📢 E'lon joylash", "💳 Hisob to'ldirish", "👤 Profili", "📊 E'lon holati", "🛠 Yordam", "🏠 Asosiy menyu"]:
        return
    
    if not message.text:
        return

    await state.update_data(details=message.text, photos=[])
    
    done_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Rasmlarni yuborib bo'ldim")],
            [KeyboardButton(text="🏠 Asosiy menyu")]
        ],
        resize_keyboard=True
    )
    
    await message.answer("📸 Endi o'sha accountning **rasmlarini** yuboring (bir nechta bo'lishi mumkin). Rasmlarni yuborib bo'lgach, pastdagi tugmani bosing:", reply_markup=done_kb)
    await state.set_state(AdStates.waiting_for_photos)

@dp.message(AdStates.waiting_for_photos, F.photo)
async def process_ad_photos(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    photos = data.get("photos", [])
    
    photo_id = message.photo[-1].file_id
    photos.append(photo_id)
    await state.update_data(photos=photos)

    await message.answer(f"📸 Rasm qabul qilindi (Jami: {len(photos)} ta). Yana yuborishingiz yoki tugmani bosishingiz mumkin.")

@dp.message(AdStates.waiting_for_photos, F.text == "✅ Rasmlarni yuborib bo'ldim")
async def finish_ad_posting(message: Message, state: FSMContext, bot: Bot) -> None:
    global global_ad_counter
    user_id = message.from_user.id
    user_data = get_user(user_id)

    if user_data["balance"] < 5000:
        await message.answer("❌ Hisobingizda mablag' yetarli emas!", reply_markup=main_keyboard)
        await state.clear()
        return

    data = await state.get_data()
    photos = data.get("photos", [])
    details = data.get("details", "")

    if not photos:
        await message.answer("❌ Iltimos, kamida bitta rasm yuboring!")
        return

    # E'lon raqamini avtomatik shakllantirish va oshirish
    current_ad_number = global_ad_counter
    global_ad_counter += 1

    # Siz so'ragan aniq shablon va emojilar
    final_caption = (
        f'<a href="https://t.me/AronAccount">ARON ACCOUNT SALE</a> 🤝\n\n'
        f"STANDOFF 2 🎮\n\n"
        f"{details}\n\n"
        f"MUROJAT UCHUN : @AronAccountAdmin 🥷\n\n"
        f"E’LON BERISH : @AronAccountElon_Bot 🥷\n\n"
        f"GARANT XIZMATI : @AronAccountAdmin 🥷\n\n"
        f"#{current_ad_number}\n\n"
        f"🔝🔝🔝🔝🔝🔝🔝🔝🔝"
    )

    user_data["balance"] -= 5000
    user_data["ads_count"] += 1
    user_data["last_ad_status"] = f"✅ Faol (#{current_ad_number} bo'lib kanalga joylandi)"

    media_group_channel = []
    for i, p_id in enumerate(photos):
        if i == 0:
            media_group_channel.append(InputMediaPhoto(media=p_id, caption=final_caption, parse_mode=ParseMode.HTML))
        else:
            media_group_channel.append(InputMediaPhoto(media=p_id))

    try:
        await bot.send_media_group(chat_id=CHANNEL_ID, media=media_group_channel)
    except Exception as e:
        print(f"Kanalga yuborishda XATOLIK: {e}")
        await message.answer(f"⚠️ Kanalga yuborishda xatolik yuz berdi: {e}")
        return

    username_str = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.from_user.id}"
    admin_notification = f"📢 {username_str} user kanalga #{current_ad_number}-e'lonni joyladi. (Balansidan 5000 UZS yechildi)"
    
    media_group_admin = []
    for i, p_id in enumerate(photos):
        if i == 0:
            media_group_admin.append(InputMediaPhoto(media=p_id, caption=admin_notification))
        else:
            media_group_admin.append(InputMediaPhoto(media=p_id))

    try:
        await bot.send_media_group(chat_id=ADMIN_ID, media=media_group_admin)
    except Exception as e:
        print(f"Adminga yuborishda xato: {e}")

    await message.answer(
        f"✅ E'loningiz #{current_ad_number} raqami ostida muvaffaqiyatli kanalga joylandi!\n💰 Hisobingizdan 5,000 UZS yechildi. Qoldiq: {user_data['balance']} UZS",
        reply_markup=main_keyboard
    )
    await state.clear()


# --- 💳 HISOB TO'LDIRISH ---
@dp.message(F.text == "💳 Hisob to'ldirish")
async def topup_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    amount = "5000"
    await state.update_data(amount=amount)

    rekvizit_text = (
        "to'lov uchun bank: Paynet 🟢\n\n"
        "Hisobni to'ldirish summasi:\n\n"
        "qabul qiluvchi: Aktamov Elshod 👤\n"
        "rekvizitlar: <code>9860 3501 4744 9895</code> 💳\n"
        f"yig'indisi: <b>{amount} UZS</b> 💰\n\n"
        "to'lovni amalga oshirgandan so'ng, chekning skrinshotini yuboring 📥"
    )
    
    inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚫 to'lov muammosi", callback_data="topup_problem")],
            [InlineKeyboardButton(text="🏠 asosiy menyu", callback_data="back_home")]
        ]
    )

    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🏠 Asosiy menyu")]],
        resize_keyboard=True
    )

    await message.answer(rekvizit_text, parse_mode=ParseMode.HTML, reply_markup=inline_kb)
    await message.answer("Iltimos, yuqoridagi kartaga pul o'tkazib, chek rasmini yuboring:", reply_markup=kb)
    await state.set_state(TopUpStates.waiting_for_receipt)

@dp.message(TopUpStates.waiting_for_receipt, F.photo)
async def process_receipt(message: Message, state: FSMContext, bot: Bot) -> None:
    user = message.from_user
    username_str = f"@{user.username}" if user.username else f"ID: {user.id}"
    photo_file_id = message.photo[-1].file_id
    data = await state.get_data()
    amount = data.get("amount", "5000")

    await message.answer("💡 to'lovni tekshirgandan so'ng kuting, sizga xabar keladi!", reply_markup=main_keyboard)

    admin_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"topup_yes_{user.id}"),
                InlineKeyboardButton(text="❌ Rad etish", callback_data=f"topup_no_{user.id}")
            ]
        ]
    )

    admin_msg = (
        f"Yangi to'lov cheki keldi! 💳\n"
        f"Foydalanuvchi: {username_str} ({user.full_name})\n"
        f"Summa: {amount} UZS\n"
        f"ID: {user.id}"
    )
    
    try:
        await bot.send_photo(chat_id=ADMIN_ID, photo=photo_file_id, caption=admin_msg, reply_markup=admin_markup)
    except Exception as e:
        print(f"Adminga yuborishda xato: {e}")

    await state.clear()

@dp.message(TopUpStates.waiting_for_receipt)
async def not_receipt_photo(message: Message) -> None:
    await message.answer("❌ Iltimos, to'lov chekini rasm (skrinshot) ko'rinishida yuboring!")

@dp.callback_query(F.data == "topup_problem")
async def topup_problem_cb(callback: CallbackQuery) -> None:
    await callback.message.answer("🛠 To'lov bo'yicha muammo yuzaga kelsa, adminga yozing: @AronAccountAdmin")
    await callback.answer()

@dp.callback_query(F.data == "back_home")
async def back_home_cb(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.answer("🏠 Asosiy menyu:", reply_markup=main_keyboard)
    await callback.answer()

@dp.callback_query(F.data.startswith("topup_"))
async def callback_topup_handler(callback: CallbackQuery, bot: Bot) -> None:
    parts = callback.data.split("_")
    if len(parts) < 3:
        return
    action, user_id_str = parts[1], parts[2]
    target_user_id = int(user_id_str)

    if action == "yes":
        user_data = get_user(target_user_id)
        user_data["balance"] += 5000

        success_text = f"🎉 Tabriklaymiz! To'lovingiz admin tomonidan tasdiqlandi. Hisobingizga 5,000 UZS qo'shildi. Joriy balans: {user_data['balance']} UZS"
        await bot.send_message(chat_id=target_user_id, text=success_text)
        
        await callback.message.edit_caption(caption=callback.message.caption + "\n\n✅ HOLAT: Tasdiqlandi (Balans to'ldirildi)", reply_markup=None)
    elif action == "no":
        await bot.send_message(chat_id=target_user_id, text="❌ Afsuski, to'lovingiz rad etildi yoki chek yaroqsiz.")
        await callback.message.edit_caption(caption=callback.message.caption + "\n\n❌ HOLAT: Rad etildi", reply_markup=None)

    await callback.answer("Bajarildi!")

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
