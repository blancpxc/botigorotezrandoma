import os
import json
import ast
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from aiogram.utils.exceptions import BotBlocked

API_TOKEN = ''
CHANNEL_LINK = 'https://t.me/+aWJE6yMlzp1jYzQy'
ADMIN_ID =   # замени на свой Telegram ID

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

USERS_FILE = "users.json"

def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_user(user_id):
    users = load_users()
    if user_id not in users:
        users.append(user_id)
        with open(USERS_FILE, "w") as f:
            json.dump(users, f)

# Воронка
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    save_user(message.from_user.id)
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton("🚀 Дальше", callback_data="step_2")
    )
    await message.answer(
        "*Привет, я — Отец Рандома 🎲*\n*Без фальши и мифов.*\n\nКрутим, кайфуем, показываем казино таким, какое оно есть.\n\nХочешь заценить? Погнали 👇",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

@dp.callback_query_handler(lambda c: c.data == 'step_2')
async def step_two(callback_query: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton("🔍 Что внутри?", callback_data="step_3")
    )
    await bot.send_message(
        callback_query.from_user.id,
        "*Просто кручка, просто сессии, просто по кайфу 🎰*\nПоказываю как есть — где фарт, где слив, где рофлы.\n\nДальше покажу, что тебя ждёт.",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

@dp.callback_query_handler(lambda c: c.data == 'step_3')
async def step_three(callback_query: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton("📲 В канал", callback_data="step_4", url=CHANNEL_LINK)
    )
    await bot.send_message(
        callback_query.from_user.id,
        "*Что тебя ждёт:*\n• Настоящие сессии\n• Реальные плюсы и минусы\n• Никаких сказок про «подними с 200₽»\n\nВся движуха — в канале.\n\n🔗 " + CHANNEL_LINK,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

@dp.callback_query_handler(lambda c: c.data == 'step_4')
async def step_four(callback_query: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton("✅ Подписался", callback_data="done")
    )
    await bot.send_message(
        callback_query.from_user.id,
        "*Вот он — мой уголок рандома 🎲*\nСтримы, скрины, движ, общение — всё по кайфу и без буллшита.\n\nПодписывайся, если по пути 👇\n\n🔗 " + CHANNEL_LINK,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

@dp.callback_query_handler(lambda c: c.data == 'done')
async def done(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "🔥 Добро пожаловать в движ! Если что — пиши сюда.")

# Автопостинг
@dp.channel_post_handler()
async def repost_to_users(message: types.Message):
    users = load_users()
    for user_id in users:
        try:
            kwargs = {}
            if message.reply_markup:
                kwargs["reply_markup"] = message.reply_markup

            if message.content_type == 'text':
                await bot.send_message(user_id, message.text, **kwargs)
            elif message.content_type == 'photo':
                await bot.send_photo(user_id, message.photo[-1].file_id, caption=message.caption, **kwargs)
            elif message.content_type == 'video':
                await bot.send_video(user_id, message.video.file_id, caption=message.caption, **kwargs)
            elif message.content_type == 'document':
                await bot.send_document(user_id, message.document.file_id, caption=message.caption, **kwargs)
            elif message.content_type == 'audio':
                await bot.send_audio(user_id, message.audio.file_id, caption=message.caption, **kwargs)
            elif message.content_type == 'voice':
                await bot.send_voice(user_id, message.voice.file_id, caption=message.caption, **kwargs)
            elif message.content_type == 'video_note':
                await bot.send_video_note(user_id, message.video_note.file_id, **kwargs)
            elif message.content_type == 'animation':
                await bot.send_animation(user_id, message.animation.file_id, caption=message.caption, **kwargs)
            else:
                await bot.send_message(user_id, "📢 Новый пост в канале!", **kwargs)
        except BotBlocked:
            continue

# Админ-панель
admin_kb = ReplyKeyboardMarkup(resize_keyboard=True)
admin_kb.add(
    KeyboardButton("📊 Статистика"),
    KeyboardButton("📁 Выгрузить пользователей")
)
admin_kb.add(
    KeyboardButton("📢 Рассылка")
)

@dp.message_handler(lambda m: m.from_user.id == ADMIN_ID and m.text == "/admin")
async def admin_panel(m: types.Message):
    await m.reply("🔐 *Админ-панель запущена*", parse_mode='Markdown', reply_markup=admin_kb)

@dp.message_handler(lambda m: m.from_user.id == ADMIN_ID and m.text == "📊 Статистика")
async def show_stats(m: types.Message):
    users = load_users()
    await m.reply(f"👥 *Пользователей в базе:* {len(users)}", parse_mode='Markdown')

@dp.message_handler(lambda m: m.from_user.id == ADMIN_ID and m.text == "📁 Выгрузить пользователей")
async def dump_users(m: types.Message):
    await m.reply_document(types.InputFile(USERS_FILE), caption="📂 Пользователи (JSON)")

# Рассылка с кнопками
broadcast_media_state = {}

@dp.message_handler(lambda m: m.from_user.id == ADMIN_ID and m.text == "📢 Рассылка")
async def ask_broadcast(m: types.Message):
    broadcast_media_state[m.from_user.id] = {}
    await m.reply("✏️ Пришли текст для рассылки (можно с медиа и кнопками):")

@dp.message_handler(lambda m: m.from_user.id == ADMIN_ID and m.text.startswith("!кнопки"))
async def custom_buttons_input(m: types.Message):
    try:
        btn_data = m.text.replace("!кнопки", "").strip()
        buttons = ast.literal_eval(btn_data)

        kb = InlineKeyboardMarkup()
        for btn in buttons:
            kb.add(InlineKeyboardButton(text=btn["text"], url=btn["url"]))

        broadcast_media_state[m.from_user.id] = {"custom_markup": kb}
        await m.reply("✅ Кнопки сохранены. Теперь отправь текст или медиа.")
    except Exception:
        await m.reply(
            '⚠️ Ошибка в формате. Пример:\n`!кнопки [{\"text\": \"Перейти\", \"url\": \"https://t.me/yourlink\"}]`',
            parse_mode="Markdown"
        )

@dp.message_handler(lambda m: m.from_user.id == ADMIN_ID and m.text == "!лог")
async def send_broadcast_log(m: types.Message):
    if os.path.exists("broadcast_log.txt"):
        await m.reply_document(types.InputFile("broadcast_log.txt"), caption="📜 Лог последней рассылки")
    else:
        await m.reply("⚠️ Лог ещё не создан.")

@dp.message_handler(content_types=types.ContentType.ANY)
async def handle_broadcast_content(m: types.Message):
    if m.from_user.id != ADMIN_ID or m.from_user.id not in broadcast_media_state:
        return

    users = load_users()
    count = 0
    text = m.caption if m.caption else m.text
    markup = broadcast_media_state[m.from_user.id].get("custom_markup", m.reply_markup)

    for uid in users:
        try:
            if m.content_type == 'photo':
                await bot.send_photo(uid, m.photo[-1].file_id, caption=text, reply_markup=markup, parse_mode='Markdown')
            elif m.content_type == 'video':
                await bot.send_video(uid, m.video.file_id, caption=text, reply_markup=markup, parse_mode='Markdown')
            elif m.content_type == 'animation':
                await bot.send_animation(uid, m.animation.file_id, caption=text, reply_markup=markup, parse_mode='Markdown')
            elif m.content_type == 'document':
                await bot.send_document(uid, m.document.file_id, caption=text, reply_markup=markup, parse_mode='Markdown')
            elif m.content_type == 'voice':
                await bot.send_voice(uid, m.voice.file_id, caption=text, reply_markup=markup, parse_mode='Markdown')
            elif m.content_type == 'text':
                await bot.send_message(uid, text, reply_markup=markup, parse_mode='Markdown')
            else:
                await bot.send_message(uid, "📢 Новый пост!", reply_markup=markup)

            with open("broadcast_log.txt", "a", encoding="utf-8") as log_file:
                log_file.write(f"{uid}\n")

            count += 1
        except:
            continue

    del broadcast_media_state[m.from_user.id]
    await m.reply(f"📬 Рассылка завершена. Отправлено: {count}", parse_mode='Markdown')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
