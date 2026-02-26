#!/usr/bin/env python3
"""
💊 Dori Eslatma Boti / Бот напоминания о лекарствах
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Funksiyalar:
  ✅ Dori qo'shish (nom, doza, vaqt, davomiylik)
  ✅ Har kuni push-eslatmalar
  ✅ Qabul qilindi/o'tkazildi belgisi
  ✅ Bugungi jadval
  ✅ Statistika (%)
  ✅ O'zbek + Rus tili
  ✅ SQLite ma'lumotlar bazasi
"""

import asyncio
import logging
import os
import sqlite3
from datetime import datetime, date, time, timedelta
from contextlib import contextmanager

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from telegram.constants import ParseMode

# ══════════════════════════════════════════════════════
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "8562690623:AAHPoejmW6dT8qL8Au3mYEwmC_SWIcInVUM")
DB_PATH = os.getenv("DB_PATH", "medbot.db")

# ConversationHandler states
(
    LANG_SELECT,
    ADD_NAME, ADD_DOSE, ADD_TIMES, ADD_DAYS, ADD_NOTES,
    EDIT_CHOOSE, EDIT_FIELD, EDIT_VALUE,
    DELETE_CONFIRM,
) = range(10)

# ══════════════════════════════════════════════════════
# TRANSLATIONS
# ══════════════════════════════════════════════════════

T = {
    "uz": {
        "welcome": (
            "👋 *Dori Eslatma Botiga xush kelibsiz!*\n\n"
            "Bu bot sizga dori ichish vaqtlarini eslatib turadi.\n\n"
            "📋 *Imkoniyatlar:*\n"
            "• 💊 Dori qo'shish va boshqarish\n"
            "• ⏰ Har kuni eslatmalar\n"
            "• 📅 Kunlik jadval\n"
            "• 📊 Statistika\n\n"
            "Boshlash uchun /menu buyrug'ini bosing."
        ),
        "menu_title": "📋 *Asosiy menyu*\nNimani xohlaysiz?",
        "btn_add": "➕ Dori qo'shish",
        "btn_list": "💊 Mening dorilarim",
        "btn_today": "📅 Bugungi jadval",
        "btn_stats": "📊 Statistika",
        "btn_settings": "⚙️ Sozlamalar",
        "btn_lang": "🌐 Til o'zgartirish",
        "btn_help": "❓ Yordam",
        "add_name": "💊 *Dori nomini kiriting:*\n_Masalan: Paracetamol, Ibuprofen, Vitamin C_",
        "add_dose": "💉 *Dozasini kiriting:*\n_Masalan: 1 ta, 500mg, 2 ta tabletkа_",
        "add_times": (
            "⏰ *Qabul vaqtlarini kiriting:*\n"
            "Har bir vaqtni alohida qatorda yozing (24-soat):\n\n"
            "_Masalan:_\n`08:00`\n`14:00`\n`22:00`\n\n"
            "Yoki bir qatorda: `08:00, 14:00, 22:00`"
        ),
        "add_days": (
            "📆 *Necha kun ichasiz?*\n\n"
            "• Raqam kiriting: `7`, `14`, `30`\n"
            "• Doimiy uchun: `0` yoki `davomiy`"
        ),
        "add_notes": (
            "📝 *Qo'shimcha izoh (ixtiyoriy):*\n"
            "_Masalan: Ovqatdan keyin, Suv bilan iching_\n\n"
            "O'tkazib yuborish uchun /skip"
        ),
        "add_success": "✅ *{name}* muvaffaqiyatli qo'shildi!\n\n⏰ Vaqtlar: {times}\n📅 Davomiylik: {days}",
        "no_meds": "💊 Hali dori qo'shilmagan.\n\n➕ /add buyrug'i bilan qo'shing!",
        "today_title": "📅 *Bugungi jadval — {date}*\n",
        "today_empty": "🎉 Bugun dori yo'q yoki hammasi qabul qilindi!",
        "stats_title": "📊 *Statistika*\n",
        "stats_med": "💊 *{name}*\n  ✅ Qabul: {taken} | ❌ O'tkazildi: {missed} | 📈 {pct}%\n",
        "stats_empty": "📊 Hali statistika yo'q. Dori qo'shing!",
        "taken_yes": "✅ Qabul qildim",
        "taken_no": "❌ O'tkazib yubordim",
        "reminder": "⏰ *Dori vaqti!*\n\n💊 *{name}*\n💉 Doza: {dose}\n📝 {notes}\n\nQabul qildingizmi?",
        "confirmed_taken": "✅ Qabul qilindi! Yaxshi!",
        "confirmed_missed": "😔 O'tkazib yuborildi. Keyingisini unutmang!",
        "delete_confirm": "🗑 *{name}* ni o'chirmoqchimisiz?",
        "deleted": "🗑 *{name}* o'chirildi.",
        "cancel": "❌ Bekor qilindi.",
        "invalid_time": "⚠️ Noto'g'ri vaqt formati! HH:MM formatida kiriting.",
        "invalid_days": "⚠️ Noto'g'ri. Raqam kiriting (0 = davomiy).",
        "days_forever": "Davomiy",
        "days_left": "{n} kun",
        "help": (
            "❓ *Yordam*\n\n"
            "*/start* — Botni boshlash\n"
            "*/menu* — Asosiy menyu\n"
            "*/add* — Dori qo'shish\n"
            "*/list* — Dorilar ro'yxati\n"
            "*/today* — Bugungi jadval\n"
            "*/stats* — Statistika\n"
            "*/cancel* — Amalni bekor qilish\n\n"
            "📞 Muammo bo'lsa, botni qayta ishga tushiring: /start"
        ),
        "settings_title": "⚙️ *Sozlamalar*",
        "current_lang": "🌐 Hozirgi til: O'zbek",
        "lang_changed": "✅ Til o'zgartirildi!",
        "list_item": "💊 *{name}* — {dose}\n   ⏰ {times} | 📅 {days_left}\n",
        "no_times_today": "Bugun vaqt yo'q",
        "pending": "⏳ kutilmoqda",
        "done": "✅ qabul qilindi",
        "missed_label": "❌ o'tkazildi",
    },
    "ru": {
        "welcome": (
            "👋 *Добро пожаловать в Бот напоминания о лекарствах!*\n\n"
            "Этот бот напомнит вам о времени приёма лекарств.\n\n"
            "📋 *Возможности:*\n"
            "• 💊 Добавление и управление лекарствами\n"
            "• ⏰ Ежедневные напоминания\n"
            "• 📅 Расписание на день\n"
            "• 📊 Статистика\n\n"
            "Для начала нажмите /menu."
        ),
        "menu_title": "📋 *Главное меню*\nЧто вы хотите сделать?",
        "btn_add": "➕ Добавить лекарство",
        "btn_list": "💊 Мои лекарства",
        "btn_today": "📅 Расписание сегодня",
        "btn_stats": "📊 Статистика",
        "btn_settings": "⚙️ Настройки",
        "btn_lang": "🌐 Сменить язык",
        "btn_help": "❓ Помощь",
        "add_name": "💊 *Введите название лекарства:*\n_Например: Парацетамол, Ибупрофен, Витамин C_",
        "add_dose": "💉 *Введите дозировку:*\n_Например: 1 таблетка, 500мг, 2 капсулы_",
        "add_times": (
            "⏰ *Введите время приёма:*\n"
            "Каждое время с новой строки (24-часовой формат):\n\n"
            "_Например:_\n`08:00`\n`14:00`\n`22:00`\n\n"
            "Или в одну строку: `08:00, 14:00, 22:00`"
        ),
        "add_days": (
            "📆 *Сколько дней принимать?*\n\n"
            "• Введите число: `7`, `14`, `30`\n"
            "• Для постоянного приёма: `0` или `бессрочно`"
        ),
        "add_notes": (
            "📝 *Дополнительные заметки (необязательно):*\n"
            "_Например: После еды, Запить водой_\n\n"
            "Пропустить: /skip"
        ),
        "add_success": "✅ *{name}* успешно добавлено!\n\n⏰ Время: {times}\n📅 Длительность: {days}",
        "no_meds": "💊 Лекарства ещё не добавлены.\n\n➕ Добавьте через /add!",
        "today_title": "📅 *Расписание на сегодня — {date}*\n",
        "today_empty": "🎉 Сегодня лекарств нет или все приняты!",
        "stats_title": "📊 *Статистика*\n",
        "stats_med": "💊 *{name}*\n  ✅ Принято: {taken} | ❌ Пропущено: {missed} | 📈 {pct}%\n",
        "stats_empty": "📊 Статистики пока нет. Добавьте лекарство!",
        "taken_yes": "✅ Принял(а)",
        "taken_no": "❌ Пропустил(а)",
        "reminder": "⏰ *Время принять лекарство!*\n\n💊 *{name}*\n💉 Доза: {dose}\n📝 {notes}\n\nВы приняли?",
        "confirmed_taken": "✅ Отлично! Приём засчитан.",
        "confirmed_missed": "😔 Пропуск записан. Не забудьте следующий!",
        "delete_confirm": "🗑 Удалить *{name}*?",
        "deleted": "🗑 *{name}* удалено.",
        "cancel": "❌ Отменено.",
        "invalid_time": "⚠️ Неверный формат времени! Введите в формате ЧЧ:ММ.",
        "invalid_days": "⚠️ Неверный ввод. Введите число (0 = бессрочно).",
        "days_forever": "Бессрочно",
        "days_left": "{n} дней",
        "help": (
            "❓ *Помощь*\n\n"
            "*/start* — Запустить бота\n"
            "*/menu* — Главное меню\n"
            "*/add* — Добавить лекарство\n"
            "*/list* — Список лекарств\n"
            "*/today* — Расписание сегодня\n"
            "*/stats* — Статистика\n"
            "*/cancel* — Отменить действие\n\n"
            "📞 Если проблема — перезапустите: /start"
        ),
        "settings_title": "⚙️ *Настройки*",
        "current_lang": "🌐 Текущий язык: Русский",
        "lang_changed": "✅ Язык изменён!",
        "list_item": "💊 *{name}* — {dose}\n   ⏰ {times} | 📅 {days_left}\n",
        "no_times_today": "Сегодня нет времени",
        "pending": "⏳ ожидает",
        "done": "✅ принято",
        "missed_label": "❌ пропущено",
    },
}


def t(lang: str, key: str, **kwargs) -> str:
    text = T.get(lang, T["uz"]).get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except Exception:
            pass
    return text


# ══════════════════════════════════════════════════════
# DATABASE
# ══════════════════════════════════════════════════════

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id     INTEGER PRIMARY KEY,
            username    TEXT,
            first_name  TEXT,
            lang        TEXT DEFAULT 'uz',
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS medications (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            name        TEXT NOT NULL,
            dose        TEXT NOT NULL,
            times       TEXT NOT NULL,   -- JSON: ["08:00","20:00"]
            days_total  INTEGER DEFAULT 0,  -- 0 = forever
            start_date  TEXT DEFAULT (date('now')),
            notes       TEXT DEFAULT '',
            active      INTEGER DEFAULT 1,
            created_at  TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );

        CREATE TABLE IF NOT EXISTS intake_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            med_id      INTEGER NOT NULL,
            log_date    TEXT NOT NULL,   -- YYYY-MM-DD
            log_time    TEXT NOT NULL,   -- HH:MM
            status      TEXT NOT NULL,   -- 'taken' | 'missed' | 'pending'
            logged_at   TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (med_id) REFERENCES medications(id)
        );
        """)
        conn.commit()
    logger.info("DB initialized")


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_user(user_id: int) -> dict | None:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
        return dict(row) if row else None


def upsert_user(user_id: int, username: str, first_name: str, lang: str = "uz"):
    with get_db() as conn:
        conn.execute("""
            INSERT INTO users (user_id, username, first_name, lang)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET username=excluded.username, first_name=excluded.first_name
        """, (user_id, username, first_name, lang))


def set_lang(user_id: int, lang: str):
    with get_db() as conn:
        conn.execute("UPDATE users SET lang=? WHERE user_id=?", (lang, user_id))


def get_lang(user_id: int) -> str:
    user = get_user(user_id)
    return user["lang"] if user else "uz"


def add_medication(user_id, name, dose, times: list, days_total: int, notes: str) -> int:
    import json
    with get_db() as conn:
        cur = conn.execute("""
            INSERT INTO medications (user_id, name, dose, times, days_total, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, name, dose, json.dumps(times), days_total, notes))
        return cur.lastrowid


def get_medications(user_id: int) -> list:
    import json
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM medications WHERE user_id=? AND active=1 ORDER BY id",
            (user_id,)
        ).fetchall()
        result = []
        for row in rows:
            d = dict(row)
            d["times"] = json.loads(d["times"])
            result.append(d)
        return result


def delete_medication(med_id: int):
    with get_db() as conn:
        conn.execute("UPDATE medications SET active=0 WHERE id=?", (med_id,))


def log_intake(user_id: int, med_id: int, log_date: str, log_time: str, status: str):
    with get_db() as conn:
        # Avoid duplicates
        existing = conn.execute(
            "SELECT id FROM intake_log WHERE med_id=? AND log_date=? AND log_time=?",
            (med_id, log_date, log_time)
        ).fetchone()
        if existing:
            conn.execute(
                "UPDATE intake_log SET status=? WHERE id=?",
                (status, existing["id"])
            )
        else:
            conn.execute(
                "INSERT INTO intake_log (user_id, med_id, log_date, log_time, status) VALUES (?,?,?,?,?)",
                (user_id, med_id, log_date, log_time, status)
            )


def get_today_schedule(user_id: int) -> list:
    """Returns list of {med, time, status} for today"""
    import json
    today = date.today().isoformat()
    meds = get_medications(user_id)
    schedule = []

    with get_db() as conn:
        for med in meds:
            # Check if still active (days_total)
            if med["days_total"] > 0:
                start = date.fromisoformat(med["start_date"])
                end = start + timedelta(days=med["days_total"])
                if date.today() > end:
                    continue

            for tm in med["times"]:
                log = conn.execute(
                    "SELECT status FROM intake_log WHERE med_id=? AND log_date=? AND log_time=?",
                    (med["id"], today, tm)
                ).fetchone()
                status = log["status"] if log else "pending"
                schedule.append({
                    "med": med,
                    "time": tm,
                    "status": status,
                })

    schedule.sort(key=lambda x: x["time"])
    return schedule


def get_stats(user_id: int) -> list:
    meds = get_medications(user_id)
    result = []
    with get_db() as conn:
        for med in meds:
            taken = conn.execute(
                "SELECT COUNT(*) as c FROM intake_log WHERE med_id=? AND status='taken'",
                (med["id"],)
            ).fetchone()["c"]
            missed = conn.execute(
                "SELECT COUNT(*) as c FROM intake_log WHERE med_id=? AND status='missed'",
                (med["id"],)
            ).fetchone()["c"]
            total = taken + missed
            pct = round(taken / total * 100) if total > 0 else 0
            result.append({
                "name": med["name"],
                "taken": taken,
                "missed": missed,
                "pct": pct,
            })
    return result


# ══════════════════════════════════════════════════════
# KEYBOARDS
# ══════════════════════════════════════════════════════

def main_menu_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(t(lang, "btn_add"), callback_data="cmd_add"),
            InlineKeyboardButton(t(lang, "btn_list"), callback_data="cmd_list"),
        ],
        [
            InlineKeyboardButton(t(lang, "btn_today"), callback_data="cmd_today"),
            InlineKeyboardButton(t(lang, "btn_stats"), callback_data="cmd_stats"),
        ],
        [
            InlineKeyboardButton(t(lang, "btn_settings"), callback_data="cmd_settings"),
            InlineKeyboardButton(t(lang, "btn_help"), callback_data="cmd_help"),
        ],
    ])


def back_to_menu_kb(lang: str) -> InlineKeyboardMarkup:
    label = "🔙 Menyu" if lang == "uz" else "🔙 Меню"
    return InlineKeyboardMarkup([[InlineKeyboardButton(label, callback_data="cmd_menu")]])


def reminder_kb(lang: str, med_id: int, log_date: str, log_time: str) -> InlineKeyboardMarkup:
    data_taken = f"intake:taken:{med_id}:{log_date}:{log_time}"
    data_missed = f"intake:missed:{med_id}:{log_date}:{log_time}"
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(t(lang, "taken_yes"), callback_data=data_taken),
        InlineKeyboardButton(t(lang, "taken_no"), callback_data=data_missed),
    ]])


def today_intake_kb(lang: str, schedule: list) -> InlineKeyboardMarkup:
    """Inline buttons for today's schedule"""
    buttons = []
    today = date.today().isoformat()
    for item in schedule:
        med = item["med"]
        tm = item["time"]
        status = item["status"]

        if status == "pending":
            icon = "⏳"
        elif status == "taken":
            icon = "✅"
        else:
            icon = "❌"

        label = f"{icon} {tm} — {med['name']}"
        if status == "pending":
            data = f"intake:taken:{med['id']}:{today}:{tm}"
        else:
            data = f"show_status:{status}"
        buttons.append([InlineKeyboardButton(label, callback_data=data)])

    back_label = "🔙 Menyu" if lang == "uz" else "🔙 Меню"
    buttons.append([InlineKeyboardButton(back_label, callback_data="cmd_menu")])
    return InlineKeyboardMarkup(buttons)


def med_list_kb(lang: str, meds: list) -> InlineKeyboardMarkup:
    buttons = []
    for med in meds:
        times_str = ", ".join(med["times"])
        label = f"💊 {med['name']} ({times_str})"
        buttons.append([
            InlineKeyboardButton(label, callback_data=f"show_med:{med['id']}"),
            InlineKeyboardButton("🗑", callback_data=f"delete_med:{med['id']}"),
        ])
    back_label = "🔙 Menyu" if lang == "uz" else "🔙 Меню"
    buttons.append([InlineKeyboardButton(back_label, callback_data="cmd_menu")])
    return InlineKeyboardMarkup(buttons)


def delete_confirm_kb(lang: str, med_id: int) -> InlineKeyboardMarkup:
    yes = "✅ Ha" if lang == "uz" else "✅ Да"
    no = "❌ Yo'q" if lang == "uz" else "❌ Нет"
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(yes, callback_data=f"confirm_delete:{med_id}"),
        InlineKeyboardButton(no, callback_data="cmd_list"),
    ]])


def lang_select_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🇺🇿 O'zbek", callback_data="set_lang:uz"),
        InlineKeyboardButton("🇷🇺 Русский", callback_data="set_lang:ru"),
    ]])


# ══════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════

def parse_times(text: str) -> list[str] | None:
    """Parse time strings like '08:00\n14:00' or '08:00, 14:00'"""
    import re
    raw = text.replace(",", "\n").replace(";", "\n")
    times = []
    for part in raw.split("\n"):
        part = part.strip()
        if not part:
            continue
        match = re.match(r"^(\d{1,2}):(\d{2})$", part)
        if not match:
            return None
        h, m = int(match.group(1)), int(match.group(2))
        if not (0 <= h <= 23 and 0 <= m <= 59):
            return None
        times.append(f"{h:02d}:{m:02d}")
    return times if times else None


def parse_days(text: str) -> int | None:
    text = text.strip().lower()
    if text in ("0", "davomiy", "бессрочно", "forever", "∞"):
        return 0
    try:
        n = int(text)
        return n if n >= 0 else None
    except ValueError:
        return None


def format_days_left(med: dict, lang: str) -> str:
    if med["days_total"] == 0:
        return t(lang, "days_forever")
    start = date.fromisoformat(med["start_date"])
    end = start + timedelta(days=med["days_total"])
    remaining = (end - date.today()).days
    if remaining <= 0:
        return "⛔ Tugagan" if lang == "uz" else "⛔ Завершён"
    return t(lang, "days_left", n=remaining)


# ══════════════════════════════════════════════════════
# COMMAND HANDLERS
# ══════════════════════════════════════════════════════

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    upsert_user(user.id, user.username or "", user.first_name or "")
    lang = get_lang(user.id)

    await update.message.reply_text(
        t(lang, "welcome"),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=main_menu_kb(lang),
    )


async def cmd_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_lang(user_id)
    await update.message.reply_text(
        t(lang, "menu_title"),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=main_menu_kb(lang),
    )


async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(update.effective_user.id)
    await update.message.reply_text(
        t(lang, "help"),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=back_to_menu_kb(lang),
    )


async def cmd_list(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_lang(user_id)
    meds = get_medications(user_id)

    if not meds:
        await update.message.reply_text(
            t(lang, "no_meds"),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=back_to_menu_kb(lang),
        )
        return

    text = ""
    for med in meds:
        times_str = ", ".join(med["times"])
        days_left = format_days_left(med, lang)
        text += t(lang, "list_item", name=med["name"], dose=med["dose"],
                  times=times_str, days_left=days_left)

    await update.message.reply_text(
        text, parse_mode=ParseMode.MARKDOWN,
        reply_markup=med_list_kb(lang, meds),
    )


async def cmd_today(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_lang(user_id)
    await _show_today(update.message, user_id, lang)


async def _show_today(message, user_id: int, lang: str):
    schedule = get_today_schedule(user_id)
    today_str = datetime.now().strftime("%d.%m.%Y")

    if not schedule:
        await message.reply_text(
            t(lang, "today_title", date=today_str) + t(lang, "today_empty"),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=back_to_menu_kb(lang),
        )
        return

    lines = [t(lang, "today_title", date=today_str)]
    for item in schedule:
        med = item["med"]
        tm = item["time"]
        status = item["status"]

        if status == "taken":
            icon = "✅"
            status_label = t(lang, "done")
        elif status == "missed":
            icon = "❌"
            status_label = t(lang, "missed_label")
        else:
            icon = "⏳"
            status_label = t(lang, "pending")

        notes = f" _{med['notes']}_" if med.get("notes") else ""
        lines.append(f"{icon} `{tm}` — *{med['name']}* ({med['dose']}){notes}\n   → _{status_label}_\n")

    await message.reply_text(
        "\n".join(lines),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=today_intake_kb(lang, schedule),
    )


async def cmd_stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_lang(user_id)
    stats = get_stats(user_id)

    if not stats:
        await update.message.reply_text(
            t(lang, "stats_empty"),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=back_to_menu_kb(lang),
        )
        return

    text = t(lang, "stats_title")
    for s in stats:
        bar_filled = int(s["pct"] / 10)
        bar = "█" * bar_filled + "░" * (10 - bar_filled)
        text += t(lang, "stats_med",
                  name=s["name"], taken=s["taken"],
                  missed=s["missed"], pct=s["pct"])
        text += f"   `{bar}` {s['pct']}%\n\n"

    await update.message.reply_text(
        text, parse_mode=ParseMode.MARKDOWN,
        reply_markup=back_to_menu_kb(lang),
    )


# ══════════════════════════════════════════════════════
# ADD MEDICATION — ConversationHandler
# ══════════════════════════════════════════════════════

async def add_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_lang(user_id)
    ctx.user_data.clear()
    ctx.user_data["lang"] = lang

    # Handle both command and callback
    msg = update.message or update.callback_query.message
    if update.callback_query:
        await update.callback_query.answer()
        await msg.reply_text(t(lang, "add_name"), parse_mode=ParseMode.MARKDOWN)
    else:
        await msg.reply_text(t(lang, "add_name"), parse_mode=ParseMode.MARKDOWN)

    return ADD_NAME


async def add_got_name(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lang = ctx.user_data.get("lang", "uz")
    ctx.user_data["name"] = update.message.text.strip()
    await update.message.reply_text(t(lang, "add_dose"), parse_mode=ParseMode.MARKDOWN)
    return ADD_DOSE


async def add_got_dose(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lang = ctx.user_data.get("lang", "uz")
    ctx.user_data["dose"] = update.message.text.strip()
    await update.message.reply_text(t(lang, "add_times"), parse_mode=ParseMode.MARKDOWN)
    return ADD_TIMES


async def add_got_times(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lang = ctx.user_data.get("lang", "uz")
    times = parse_times(update.message.text)
    if not times:
        await update.message.reply_text(
            t(lang, "invalid_time"), parse_mode=ParseMode.MARKDOWN
        )
        return ADD_TIMES

    ctx.user_data["times"] = times
    await update.message.reply_text(t(lang, "add_days"), parse_mode=ParseMode.MARKDOWN)
    return ADD_DAYS


async def add_got_days(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lang = ctx.user_data.get("lang", "uz")
    days = parse_days(update.message.text)
    if days is None:
        await update.message.reply_text(
            t(lang, "invalid_days"), parse_mode=ParseMode.MARKDOWN
        )
        return ADD_DAYS

    ctx.user_data["days"] = days
    await update.message.reply_text(t(lang, "add_notes"), parse_mode=ParseMode.MARKDOWN)
    return ADD_NOTES


async def add_got_notes(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lang = ctx.user_data.get("lang", "uz")
    text = update.message.text.strip()
    notes = "" if text.startswith("/skip") else text

    user_id = update.effective_user.id
    name = ctx.user_data["name"]
    dose = ctx.user_data["dose"]
    times = ctx.user_data["times"]
    days = ctx.user_data["days"]

    add_medication(user_id, name, dose, times, days, notes)

    days_label = (
        t(lang, "days_forever") if days == 0
        else t(lang, "days_left", n=days)
    )
    times_str = ", ".join(times)

    await update.message.reply_text(
        t(lang, "add_success", name=name, times=times_str, days=days_label),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=main_menu_kb(lang),
    )
    ctx.user_data.clear()
    return ConversationHandler.END


async def add_skip_notes(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["notes_text"] = ""
    return await add_got_notes(update, ctx)


async def conv_cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lang = ctx.user_data.get("lang", get_lang(update.effective_user.id))
    ctx.user_data.clear()
    await update.message.reply_text(
        t(lang, "cancel"),
        reply_markup=main_menu_kb(lang),
    )
    return ConversationHandler.END


# ══════════════════════════════════════════════════════
# CALLBACK HANDLER
# ══════════════════════════════════════════════════════

async def handle_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    user_id = update.effective_user.id
    lang = get_lang(user_id)

    # ── Navigation ──
    if data == "cmd_menu":
        await q.edit_message_text(
            t(lang, "menu_title"),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=main_menu_kb(lang),
        )

    elif data == "cmd_add":
        ctx.user_data["lang"] = lang
        await q.edit_message_text(
            t(lang, "add_name"), parse_mode=ParseMode.MARKDOWN
        )
        ctx.user_data["conv_state"] = ADD_NAME

    elif data == "cmd_list":
        meds = get_medications(user_id)
        if not meds:
            await q.edit_message_text(
                t(lang, "no_meds"), parse_mode=ParseMode.MARKDOWN,
                reply_markup=back_to_menu_kb(lang),
            )
        else:
            text = ""
            for med in meds:
                times_str = ", ".join(med["times"])
                days_left = format_days_left(med, lang)
                text += t(lang, "list_item", name=med["name"], dose=med["dose"],
                          times=times_str, days_left=days_left)
            await q.edit_message_text(
                text, parse_mode=ParseMode.MARKDOWN,
                reply_markup=med_list_kb(lang, meds),
            )

    elif data == "cmd_today":
        schedule = get_today_schedule(user_id)
        today_str = datetime.now().strftime("%d.%m.%Y")
        if not schedule:
            await q.edit_message_text(
                t(lang, "today_title", date=today_str) + t(lang, "today_empty"),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=back_to_menu_kb(lang),
            )
        else:
            lines = [t(lang, "today_title", date=today_str)]
            for item in schedule:
                med = item["med"]
                tm = item["time"]
                status = item["status"]
                icon = "✅" if status == "taken" else ("❌" if status == "missed" else "⏳")
                status_label = t(lang, "done" if status == "taken" else ("missed_label" if status == "missed" else "pending"))
                notes = f" _{med['notes']}_" if med.get("notes") else ""
                lines.append(f"{icon} `{tm}` — *{med['name']}* ({med['dose']}){notes}\n   → _{status_label}_\n")
            await q.edit_message_text(
                "\n".join(lines),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=today_intake_kb(lang, schedule),
            )

    elif data == "cmd_stats":
        stats = get_stats(user_id)
        if not stats:
            await q.edit_message_text(
                t(lang, "stats_empty"), parse_mode=ParseMode.MARKDOWN,
                reply_markup=back_to_menu_kb(lang),
            )
        else:
            text = t(lang, "stats_title")
            for s in stats:
                bar_filled = int(s["pct"] / 10)
                bar = "█" * bar_filled + "░" * (10 - bar_filled)
                text += t(lang, "stats_med", name=s["name"], taken=s["taken"],
                          missed=s["missed"], pct=s["pct"])
                text += f"   `{bar}` {s['pct']}%\n\n"
            await q.edit_message_text(
                text, parse_mode=ParseMode.MARKDOWN,
                reply_markup=back_to_menu_kb(lang),
            )

    elif data == "cmd_settings":
        text = (
            t(lang, "settings_title") + "\n\n" +
            (t(lang, "current_lang")) + "\n\n" +
            (t(lang, "btn_lang")) + ":"
        )
        await q.edit_message_text(
            text, parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🇺🇿 O'zbek", callback_data="set_lang:uz"),
                 InlineKeyboardButton("🇷🇺 Русский", callback_data="set_lang:ru")],
                [InlineKeyboardButton("🔙", callback_data="cmd_menu")],
            ]),
        )

    elif data == "cmd_help":
        await q.edit_message_text(
            t(lang, "help"), parse_mode=ParseMode.MARKDOWN,
            reply_markup=back_to_menu_kb(lang),
        )

    # ── Language ──
    elif data.startswith("set_lang:"):
        new_lang = data.split(":")[1]
        set_lang(user_id, new_lang)
        await q.edit_message_text(
            t(new_lang, "lang_changed") + "\n\n" + t(new_lang, "menu_title"),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=main_menu_kb(new_lang),
        )

    # ── Intake ──
    elif data.startswith("intake:"):
        _, status, med_id, log_date, log_time = data.split(":")
        log_intake(user_id, int(med_id), log_date, log_time, status)
        confirm_key = "confirmed_taken" if status == "taken" else "confirmed_missed"
        await q.edit_message_text(
            t(lang, confirm_key), parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    "📅 Jadval" if lang == "uz" else "📅 Расписание",
                    callback_data="cmd_today"
                ),
                InlineKeyboardButton(
                    "🏠 Menyu" if lang == "uz" else "🏠 Меню",
                    callback_data="cmd_menu"
                ),
            ]]),
        )

    elif data.startswith("show_status:"):
        status = data.split(":")[1]
        if status == "taken":
            await q.answer(t(lang, "done"), show_alert=False)
        else:
            await q.answer(t(lang, "missed_label"), show_alert=False)

    # ── Delete ──
    elif data.startswith("delete_med:"):
        med_id = int(data.split(":")[1])
        with get_db() as conn:
            med = conn.execute("SELECT name FROM medications WHERE id=?", (med_id,)).fetchone()
        if med:
            await q.edit_message_text(
                t(lang, "delete_confirm", name=med["name"]),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=delete_confirm_kb(lang, med_id),
            )

    elif data.startswith("confirm_delete:"):
        med_id = int(data.split(":")[1])
        with get_db() as conn:
            med = conn.execute("SELECT name FROM medications WHERE id=?", (med_id,)).fetchone()
        name = med["name"] if med else "?"
        delete_medication(med_id)
        meds = get_medications(user_id)
        if not meds:
            await q.edit_message_text(
                t(lang, "deleted", name=name) + "\n\n" + t(lang, "no_meds"),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=back_to_menu_kb(lang),
            )
        else:
            text = t(lang, "deleted", name=name) + "\n\n"
            for m in meds:
                times_str = ", ".join(m["times"])
                days_left = format_days_left(m, lang)
                text += t(lang, "list_item", name=m["name"], dose=m["dose"],
                          times=times_str, days_left=days_left)
            await q.edit_message_text(
                text, parse_mode=ParseMode.MARKDOWN,
                reply_markup=med_list_kb(lang, meds),
            )

    elif data.startswith("show_med:"):
        med_id = int(data.split(":")[1])
        import json
        with get_db() as conn:
            med = conn.execute("SELECT * FROM medications WHERE id=?", (med_id,)).fetchone()
        if med:
            med = dict(med)
            med["times"] = json.loads(med["times"])
            times_str = ", ".join(med["times"])
            days_left = format_days_left(med, lang)
            notes = f"\n📝 {med['notes']}" if med.get("notes") else ""
            text = (
                f"💊 *{med['name']}*\n"
                f"💉 {med['dose']}\n"
                f"⏰ {times_str}\n"
                f"📅 {days_left}{notes}"
            )
            await q.edit_message_text(
                text, parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🗑 " + ("O'chirish" if lang == "uz" else "Удалить"),
                                         callback_data=f"delete_med:{med_id}")],
                    [InlineKeyboardButton("🔙", callback_data="cmd_list")],
                ]),
            )


# ══════════════════════════════════════════════════════
# REMINDER SCHEDULER
# ══════════════════════════════════════════════════════

async def send_reminders(app):
    """Run every minute — send reminders for current time"""
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    today = now.date().isoformat()

    with get_db() as conn:
        import json
        # Get all active medications
        meds = conn.execute(
            "SELECT m.*, u.lang FROM medications m JOIN users u ON m.user_id = u.user_id WHERE m.active=1"
        ).fetchall()

        for med in meds:
            med = dict(med)
            times = json.loads(med["times"])

            if current_time not in times:
                continue

            # Check days_total
            if med["days_total"] > 0:
                from datetime import date, timedelta
                start = date.fromisoformat(med["start_date"])
                end = start + timedelta(days=med["days_total"])
                if date.today() > end:
                    continue

            # Check if already notified
            existing = conn.execute(
                "SELECT id FROM intake_log WHERE med_id=? AND log_date=? AND log_time=?",
                (med["id"], today, current_time)
            ).fetchone()
            if existing:
                continue

            # Create pending log
            conn.execute(
                "INSERT INTO intake_log (user_id, med_id, log_date, log_time, status) VALUES (?,?,?,?,?)",
                (med["user_id"], med["id"], today, current_time, "pending")
            )

            lang = med.get("lang", "uz")
            notes = med["notes"] or ("—" if lang == "uz" else "—")

            kb = reminder_kb(lang, med["id"], today, current_time)
            text = t(lang, "reminder",
                     name=med["name"], dose=med["dose"], notes=notes)

            try:
                await app.bot.send_message(
                    chat_id=med["user_id"],
                    text=text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=kb,
                )
            except Exception as e:
                logger.warning(f"Reminder error for user {med['user_id']}: {e}")


async def scheduler_loop(app):
    """Background loop for sending reminders every minute"""
    while True:
        try:
            await send_reminders(app)
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
        await asyncio.sleep(60)


# ══════════════════════════════════════════════════════
# UNKNOWN MESSAGE HANDLER
# ══════════════════════════════════════════════════════

async def handle_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle text messages during conversation flow"""
    state = ctx.user_data.get("conv_state")
    if state is None:
        lang = get_lang(update.effective_user.id)
        await update.message.reply_text(
            t(lang, "menu_title"),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=main_menu_kb(lang),
        )
        return

    # Route to appropriate conversation step
    if state == ADD_NAME:
        return await add_got_name(update, ctx)
    elif state == ADD_DOSE:
        return await add_got_dose(update, ctx)
    elif state == ADD_TIMES:
        return await add_got_times(update, ctx)
    elif state == ADD_DAYS:
        return await add_got_days(update, ctx)
    elif state == ADD_NOTES:
        ctx.user_data.pop("conv_state", None)
        return await add_got_notes(update, ctx)


# ══════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════

def main():
    init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    # Conversation handler for adding medications
    add_conv = ConversationHandler(
        entry_points=[
            CommandHandler("add", add_start),
        ],
        states={
            ADD_NAME:  [MessageHandler(filters.TEXT & ~filters.COMMAND, add_got_name)],
            ADD_DOSE:  [MessageHandler(filters.TEXT & ~filters.COMMAND, add_got_dose)],
            ADD_TIMES: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_got_times)],
            ADD_DAYS:  [MessageHandler(filters.TEXT & ~filters.COMMAND, add_got_days)],
            ADD_NOTES: [
                CommandHandler("skip", add_skip_notes),
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_got_notes),
            ],
        },
        fallbacks=[CommandHandler("cancel", conv_cancel)],
        allow_reentry=True,
    )

    # Register handlers
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("menu", cmd_menu))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("list", cmd_list))
    app.add_handler(CommandHandler("today", cmd_today))
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(add_conv)
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("💊 Dori Eslatma Boti ishga tushdi!")

    async def run_bot():
        async with app:
            await app.start()
            await app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
            await scheduler_loop(app)

    asyncio.run(run_bot())


if __name__ == "__main__":
    main()
