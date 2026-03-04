# 🚀 Med-Reminder Bot - Quick Deploy Guide

## ⚡ 3 MINUTDA DEPLOY

### 1. GitHub'ga Push (1 min)
```bash
cd med-reminder-bot
cp bot.py bot.py  # yangi faylni copy qiling
git add bot.py
git commit -m "fix: scheduler loop as background task v2.0"
git push origin main
```

### 2. Railway Auto-Deploy (1 min)
Railway avtomatik deploy qiladi. Kutib turing...

### 3. Logs Tekshirish (1 min)
```bash
railway logs -f
```

**Qidiring:**
```
✅ Scheduler background task ishga tushdi!
🔄 Scheduler loop started
```

✅ Ko'rsangiz → SUCCESS!

---

## 🧪 TEZ TEST (5 daqiqa)

1. **Botga /start yuboring**
2. **"➕ Dori qo'shish"**
3. **Ma'lumotlarni kiriting:**
   - Nom: `Test`
   - Doza: `1 ta`
   - Vaqt: **Hozirdan 2 daqiqa keyin** (15:32 → kiriting `15:34`)
   - Kunlar: `1`
   - Izoh: `/skip`
4. **2 daqiqa kuting...**
5. **Telegram'da xabar keladi!** 🎉
6. **"✅ Ichtim" tugmasini bosing**
7. **"✅ Qabul qilindi!" xabari keladi** ✅

---

## 🐛 AGAR MUAMMO BO'LSA

### Scheduler ishlamayapti?
```bash
railway logs | grep "Scheduler"
```
Agar hech narsa ko'rinmasa → Railway'ni restart qiling

### Reminder kelmayapti?
```bash
railway logs | grep "Active medications"
```
Agar "0" bo'lsa → Dori qo'shilmagan

### Vaqt noto'g'ri?
```bash
railway logs | grep "Toshkent"
```
UTC+5 bo'lishi kerak

---

## 📊 EXPECTED OUTPUT

**Normal working bot logs:**
```
💊 Dori Eslatma Boti ishga tushdi!
✅ Scheduler background task ishga tushdi!
🔄 Scheduler loop started - checking every 60 seconds
🔍 Scheduler tick: Toshkent = 2026-03-04 15:30
📊 Active medications: 2
💤 No reminders to send at 15:30
[60 seconds later...]
🔍 Scheduler tick: Toshkent = 2026-03-04 15:31
📊 Active medications: 2
💤 No reminders to send at 15:31
[...]
🔍 Scheduler tick: Toshkent = 2026-03-04 15:34
📊 Active medications: 2
✅ Reminder sent → user 123456, med: Test @ 15:34
📤 Total reminders sent: 1
```

---

## 💡 KEY FIXES

1. ✅ **Scheduler endi BACKGROUND TASK** (blocking emas)
2. ✅ **Better logging** (har 10 daqiqada status)
3. ✅ **Debug info** (active meds, reminders sent)

---

## ✅ CHECKLIST

- [ ] GitHub'ga push qilindi
- [ ] Railway deploy tugadi
- [ ] Logs'da "Scheduler background task" ko'rinadi
- [ ] Test dori qo'shildi
- [ ] Reminder keldi
- [ ] "Ichtim" tugmasi ishladi

**Hammasi ✅ bo'lsa → TAYYOR! 🎉**

---

Muammo bo'lsa → MED_BOT_FIXES.md'ni o'qing!
