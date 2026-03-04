#!/usr/bin/env python3
"""
🔍 Med-Reminder Bot Diagnostika
Bu skript botning muammosini topadi
"""

import sys
import os

print("=" * 60)
print("🔍 MED-REMINDER BOT DIAGNOSTIKA")
print("=" * 60)

# 1. Python versiyasini tekshirish
print(f"\n1️⃣ Python versiyasi: {sys.version}")
if sys.version_info < (3, 9):
    print("   ❌ XATO: Python 3.9+ kerak!")
    print("   💡 Fix: runtime.txt'da python-3.11 yozing")
else:
    print("   ✅ Python versiyasi OK")

# 2. BOT_TOKEN'ni tekshirish
print(f"\n2️⃣ BOT_TOKEN:")
bot_token = os.getenv("BOT_TOKEN")
if not bot_token:
    print("   ❌ XATO: BOT_TOKEN environment variable topilmadi!")
    print("   💡 Fix: Railway Variables'da BOT_TOKEN qo'shing")
    bot_token = input("   Test uchun BOT_TOKEN kiriting (yoki ENTER): ").strip()
    if bot_token:
        os.environ["BOT_TOKEN"] = bot_token
else:
    print(f"   ✅ BOT_TOKEN mavjud: {bot_token[:20]}...")

# 3. Dependencies tekshirish
print(f"\n3️⃣ Dependencies:")
required = [
    "telegram",
    "python-telegram-bot",
    "asyncio",
    "sqlite3",
]

missing = []
for module in required:
    try:
        __import__(module)
        print(f"   ✅ {module}")
    except ImportError:
        print(f"   ❌ {module} topilmadi!")
        missing.append(module)

if missing:
    print(f"\n   💡 Fix: pip install {' '.join(missing)}")

# 4. Timezone tekshirish
print(f"\n4️⃣ Timezone:")
try:
    from zoneinfo import ZoneInfo
    tz = ZoneInfo("Asia/Tashkent")
    from datetime import datetime
    now = datetime.now(tz)
    print(f"   ✅ Timezone OK: {now.strftime('%Y-%m-%d %H:%M %Z')}")
except Exception as e:
    print(f"   ❌ Timezone xato: {e}")
    print(f"   💡 Python 3.9+ ishlatilmoqda?")

# 5. Bot.py syntax tekshirish
print(f"\n5️⃣ bot.py syntax:")
try:
    import py_compile
    py_compile.compile("bot.py", doraise=True)
    print(f"   ✅ Syntax OK")
except FileNotFoundError:
    print(f"   ⚠️ bot.py topilmadi (bu normal, agar boshqa joyda bo'lsa)")
except Exception as e:
    print(f"   ❌ Syntax xato: {e}")

# 6. Database tekshirish
print(f"\n6️⃣ Database:")
try:
    import sqlite3
    db_path = os.getenv("DB_PATH", "medbot.db")
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM medications WHERE active=1")
        count = cursor.fetchone()[0]
        print(f"   ✅ Database OK: {count} active medications")
        conn.close()
    else:
        print(f"   ⚠️ Database topilmadi: {db_path} (birinchi run'da yaratiladi)")
except Exception as e:
    print(f"   ❌ Database xato: {e}")

# 7. Asyncio tekshirish
print(f"\n7️⃣ Asyncio:")
try:
    import asyncio
    async def test():
        return "OK"
    result = asyncio.run(test())
    print(f"   ✅ Asyncio ishlayapti: {result}")
except Exception as e:
    print(f"   ❌ Asyncio xato: {e}")

# 8. Telegram bot connection test (agar BOT_TOKEN bo'lsa)
print(f"\n8️⃣ Telegram connection test:")
if bot_token:
    try:
        print("   Testing connection...")
        from telegram import Bot
        import asyncio
        
        async def test_bot():
            bot = Bot(token=bot_token)
            me = await bot.get_me()
            return me
        
        me = asyncio.run(test_bot())
        print(f"   ✅ Bot connection OK!")
        print(f"      Bot username: @{me.username}")
        print(f"      Bot name: {me.first_name}")
    except Exception as e:
        print(f"   ❌ Connection xato: {e}")
        print(f"   💡 BOT_TOKEN noto'g'ri yoki internet yo'q")
else:
    print(f"   ⏭ Skipped (BOT_TOKEN yo'q)")

# Summary
print("\n" + "=" * 60)
print("📊 XULOSA:")
print("=" * 60)

issues = []
if sys.version_info < (3, 9):
    issues.append("Python versiyasi juda eski")
if not bot_token:
    issues.append("BOT_TOKEN topilmadi")
if missing:
    issues.append(f"Modules topilmadi: {', '.join(missing)}")

if issues:
    print("❌ MUAMMOLAR TOPILDI:")
    for i, issue in enumerate(issues, 1):
        print(f"   {i}. {issue}")
    print("\n💡 YECHIM:")
    print("   1. Railway Variables'da BOT_TOKEN sozlang")
    print("   2. requirements.txt'ni tekshiring")
    print("   3. runtime.txt'da python-3.11 yozing")
else:
    print("✅ BARCHA TEKSHIRUVLAR OK!")
    print("\n🚀 Bot ishga tushishi kerak.")
    print("   Agar ishlamasa, Railway logs'ni yuboring!")

print("=" * 60)
