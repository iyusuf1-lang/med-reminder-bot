# 🔧 Med-Reminder Bot v2.0 - Fixes & Improvements

## 📋 Topilgan Muammolar

### 🔴 MUAMMO 1: Reminder SMS kelmayapti

**Sabab:** Scheduler loop **hech qachon ishlamagan**!

**Nima bo'lgan:**
```python
# OLD CODE (WRONG):
async def run_bot():
    async with app:
        await app.start()
        await app.updater.start_polling(...)  # ← Blocking!
        await scheduler_loop(app)  # ← Hech qachon bu yerga yetmasdi!
```

`start_polling()` blocking operation - u hech qachon tugamaydi. Shuning uchun `scheduler_loop` hech qachon ishga tushmaydi!

**Yechim:**
```python
# NEW CODE (FIXED):
async def run_bot():
    async with app:
        await app.start()
        
        # ✅ Scheduler'ni background task sifatida ishga tushirish
        scheduler_task = asyncio.create_task(scheduler_loop(app))
        
        # Polling alohida ishlaydi
        await app.updater.start_polling(...)
```

---

### 🔴 MUAMMO 2: "Ichtim" tugmasi bosilmayapti

**Sabab:** Aslida callback handler to'g'ri yozilgan, lekin reminder xabarlari kelmayotgani uchun tugmani test qilib bo'lmaydi.

**Yechim:** Scheduler fix qilingandan keyin avtomatik hal bo'ladi.

---

## ✅ QANDAY TUZATILDI

### Fix 1: Background Task Pattern

```python
# Scheduler'ni alohida task sifatida ishga tushirish
scheduler_task = asyncio.create_task(scheduler_loop(app))
logger.info("✅ Scheduler background task ishga tushdi!")

# Polling'ni boshlash (bu blocking, lekin scheduler alohida task'da)
await app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
```

### Fix 2: Better Logging

```python
# Har 60 soniyada check, har 10 daqiqada status log
if iteration % 10 == 0:
    logger.info(f"✅ Scheduler alive - {iteration} iterations completed")
```

### Fix 3: Debug Information

```python
logger.info(f"🔍 Scheduler tick: Toshkent = {now.strftime('%Y-%m-%d %H:%M')}")
logger.info(f"📊 Active medications: {total_meds}")
logger.info(f"📤 Total reminders sent: {reminders_sent}")
```

---

## 🚀 GitHub'ga Deploy

### Qadam 1: Faylni GitHub'ga push qiling

```bash
cd med-reminder-bot

# Fixed faylni copy qiling
cp bot.py bot.py  # faylni o'zgartiring

# Git'ga qo'shing
git add bot.py
git commit -m "fix: scheduler loop as background task + better logging"
git push origin main
```

### Qadam 2: Railway Avtomatik Deploy

Railway GitHub bilan bog'langan bo'lsa, avtomatik redeploy bo'ladi.

### Qadam 3: Logs'ni Tekshirish

Deploy'dan keyin Railway logs'ni kuzating:

```bash
railway logs -f
```

**Kutilayotgan output:**
```
💊 Dori Eslatma Boti ishga tushdi!
✅ Scheduler background task ishga tushdi!
🔄 Scheduler loop started - checking every 60 seconds
🔍 Scheduler tick: Toshkent = 2026-03-04 15:30
📊 Active medications: 3
💤 No reminders to send at 15:30
```

---

## 🧪 Test Qilish

### Test 1: Scheduler Ishlashini Tekshirish (1 daqiqa)

**Railway logs'da qidiring:**
```
✅ Scheduler background task ishga tushdi!
🔄 Scheduler loop started
```

Agar ko'rsangiz → ✅ Scheduler ishlayapti!

---

### Test 2: Dori Qo'shish va Reminder Test (5-10 daqiqa)

1. **Botga /start yuboring**
2. **"➕ Dori qo'shish" tugmasini bosing**
3. **Dori ma'lumotlarini kiriting:**
   - Nom: `Test Dori`
   - Doza: `1 ta`
   - Vaqtlar: Hozirgi vaqtdan **2-3 daqiqa keyin** (masalan, hozir 15:30 bo'lsa, kiriting: `15:33`)
   - Kunlar: `1` (1 kun test)
   - Izoh: `/skip`

4. **2-3 daqiqa kutib turing**

5. **Railway logs'ni kuzating:**
```bash
railway logs -f
```

**Kutilayotgan output:**
```
🔍 Scheduler tick: Toshkent = 2026-03-04 15:33
📊 Active medications: 1
✅ Reminder sent → user 123456, med: Test Dori @ 15:33
📤 Total reminders sent: 1
```

6. **Telegram'da reminder xabari kelishi kerak!**

7. **"✅ Ichtim" yoki "❌ Ichmadim" tugmasini bosing**

**Natija:**
- ✅ PASS: Reminder keldi, tugma ishladi, confirmation xabari ko'rsatildi
- ❌ FAIL: Logs'ni tekshiring

---

### Test 3: "Ichtim" Tugmasini Test Qilish

Reminder kelgandan keyin:

1. **"✅ Ichtim" tugmasini bosing**
2. **Kutilayotgan natija:**
   ```
   ✅ Qabul qilindi!
   [📅 Jadval] [🏠 Menyu]
   ```
3. **"📅 Jadval" tugmasini bosing**
4. **Bugungi jadvalda dori "✅" belgisi bilan ko'rinishi kerak**

---

## 🐛 Troubleshooting

### Muammo: Scheduler ishlamayapti

**Belgi:** Logs'da "Scheduler background task" ko'rinmaydi

**Fix:**
1. Railway'da redeploy qiling
2. Bot to'g'ri build bo'lganligini tekshiring
3. Python 3.11+ ekanligini tekshiring (`runtime.txt`)

---

### Muammo: Reminder kelmayapti (lekin scheduler ishlayapti)

**Tekshiring:**

1. **Vaqt to'g'rimi?**
   ```bash
   railway logs | grep "Scheduler tick"
   ```
   Toshkent vaqti to'g'ri ko'rsatilmoqda?

2. **Active medications bormi?**
   ```bash
   railway logs | grep "Active medications"
   ```
   Agar 0 bo'lsa → Dori qo'shilmagan yoki inactive

3. **Dori vaqti to'g'rimi?**
   Database'da dori vaqtini tekshiring:
   ```sql
   SELECT * FROM medications WHERE active=1;
   ```

4. **User ID to'g'rimi?**
   Reminder yuborilayotgan user_id to'g'ri user'ga tegishlimi?

---

### Muammo: "Ichtim" tugmasi error beradi

**Tekshiring:**

1. Railway logs'da error xabari bormi?
2. Database'da `intake_log` table mavjudmi?
3. Callback data format to'g'rimi?

**Fix:** Database'ni reset qiling:
```bash
railway run python
>>> import sqlite3
>>> conn = sqlite3.connect('medbot.db')
>>> conn.execute('SELECT * FROM intake_log LIMIT 5')
```

---

## 💡 QO'SHIMCHA TAVSIYALAR

### 1. Timezone Display for Users

Foydalanuvchilarga vaqt ko'rsatilganda doim Toshkent vaqtini aytib qo'ying:

```python
# settings_title translation'ga qo'shing:
"settings_title": (
    "⚙️ *Sozlamalar*\n\n"
    "🕐 Vaqt zonasi: Toshkent (UTC+5)\n"
    "📅 Bugungi sana: {date}"
),
```

### 2. Test Mode

Development uchun test mode qo'shing:

```python
# .env file:
TEST_MODE=true
CHECK_INTERVAL=10  # 10 seconds instead of 60

# bot.py:
TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "60"))

async def scheduler_loop(app):
    interval = 10 if TEST_MODE else CHECK_INTERVAL
    logger.info(f"Scheduler interval: {interval}s")
    # ...
    await asyncio.sleep(interval)
```

### 3. Health Check Endpoint

Bot ishlashini tekshirish uchun HTTP endpoint:

```python
from aiohttp import web

async def health_check(request):
    return web.Response(text="OK")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/health", health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", "8080"))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Health check server: http://0.0.0.0:{port}/health")

# run_bot() da:
health_task = asyncio.create_task(start_web_server())
```

### 4. Notification Grouping

Bir vaqtda ko'p dori bo'lsa, bitta xabarda yuborish:

```python
# Group reminders by user
reminders_by_user = {}
for med in meds:
    user_id = med["user_id"]
    if user_id not in reminders_by_user:
        reminders_by_user[user_id] = []
    reminders_by_user[user_id].append(med)

# Send grouped notifications
for user_id, user_meds in reminders_by_user.items():
    if len(user_meds) == 1:
        # Single reminder
        # ...existing code...
    else:
        # Multiple reminders in one message
        text = f"⏰ {len(user_meds)} ta dori ichish vaqti!\n\n"
        for med in user_meds:
            text += f"💊 {med['name']} - {med['dose']}\n"
        # ...
```

### 5. Snooze Feature

Reminder'ni keyinroqqa qoldirish:

```python
def reminder_kb_with_snooze(lang, med_id, log_date, log_time):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Ichtim", callback_data=f"intake:taken:{med_id}:{log_date}:{log_time}"),
            InlineKeyboardButton("❌ Ichmadim", callback_data=f"intake:missed:{med_id}:{log_date}:{log_time}"),
        ],
        [
            InlineKeyboardButton("⏰ 5 daqiqadan keyin", callback_data=f"snooze:5:{med_id}:{log_date}:{log_time}"),
        ]
    ])

# Callback handler:
elif data.startswith("snooze:"):
    _, minutes, med_id, log_date, log_time = data.split(":")
    # Schedule reminder for N minutes later
    # ...
```

### 6. Weekly Statistics

Haftalik statistika yuborish (har dushanba):

```python
async def send_weekly_stats(app):
    # Check if today is Monday
    now = datetime.now(TIMEZONE)
    if now.weekday() != 0:  # 0 = Monday
        return
    
    # Get all users
    with get_db() as conn:
        users = conn.execute("SELECT user_id, lang FROM users").fetchall()
    
    for user in users:
        stats = get_stats(user["user_id"])
        if not stats:
            continue
        
        # Send weekly summary
        text = "📊 Haftalik hisobot\n\n"
        # ... build stats text ...
        
        await app.bot.send_message(
            chat_id=user["user_id"],
            text=text,
            parse_mode=ParseMode.MARKDOWN
        )
```

---

## 🎯 Expected Behavior (Normal Flow)

### 1. Dori qo'shish:
```
User → "➕ Dori qo'shish"
Bot  → "Dori nomini kiriting"
User → "Paracetamol"
Bot  → "Dozasini kiriting"
User → "500mg"
Bot  → "Vaqtlarini kiriting"
User → "08:00, 14:00, 22:00"
Bot  → "Necha kun?"
User → "7"
Bot  → "Izoh?"
User → "/skip"
Bot  → "✅ Dori saqlandi!"
```

### 2. Reminder flow:
```
[08:00] Bot → "⏰ Eslatma: Paracetamol - 500mg"
               [✅ Ichtim] [❌ Ichmadim]
User clicks "✅ Ichtim"
Bot  → "✅ Qabul qilindi!"
       [📅 Jadval] [🏠 Menyu]
```

### 3. Logs flow:
```
[Railway logs every minute]:
🔍 Scheduler tick: Toshkent = 2026-03-04 08:00
📊 Active medications: 5
✅ Reminder sent → user 123456, med: Paracetamol @ 08:00
✅ Reminder sent → user 789012, med: Vitamin C @ 08:00
📤 Total reminders sent: 2
```

---

## ✅ Success Checklist

Deploy muvaffaqiyatli bo'lgandan keyin:

- [ ] Railway logs'da "Scheduler background task ishga tushdi" ko'rinadi
- [ ] Har 60 soniyada "Scheduler tick" xabari
- [ ] Har 10 daqiqada "Scheduler alive" status
- [ ] Test dori qo'shish ishlaydi
- [ ] Reminder vaqtida xabar keladi
- [ ] "Ichtim" tugmasi ishlaydi
- [ ] "Bugungi jadval"da status ko'rsatiladi
- [ ] Statistika ishlaydi

---

## 📞 Yordam

Muammo bo'lsa:
1. Railway logs'ni tekshiring
2. Timezone to'g'ri sozlanganligini tekshiring
3. Database'ni tekshiring (SQLite)
4. TEST_MODE'ni yoqing (10s interval)

Omad! 🚀
