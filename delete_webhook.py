#!/usr/bin/env python3
"""
Webhook'ni o'chirish va polling'ni restart qilish
"""

import asyncio
from telegram import Bot

BOT_TOKEN = "8562690623:AAHPoejmW6dT8qL8Au3mYEwmC_SWIcInVUM"

async def delete_webhook():
    bot = Bot(token=BOT_TOKEN)
    
    print("🔍 Checking webhook...")
    webhook_info = await bot.get_webhook_info()
    print(f"Current webhook: {webhook_info.url}")
    
    if webhook_info.url:
        print("🗑 Deleting webhook...")
        await bot.delete_webhook(drop_pending_updates=True)
        print("✅ Webhook deleted!")
    else:
        print("✅ No webhook set")
    
    print("\n✅ Bot ready for polling!")

if __name__ == "__main__":
    asyncio.run(delete_webhook())
