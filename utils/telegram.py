from pyrogram import Client, filters
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

# Replace these with your own values
api_id = os.environ.get("TELEGRAM_API_ID")
api_hash = os.environ.get("TELEGRAM_API_HASH")
bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")

app_tg = Client("mom_ai_tg_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

@app_tg.on_message(filters.command("start"))
async def get_chat_id(client, message):
    chat_id = message.chat.id
    await message.reply('Hi! Please insert the code provided below on your account dashboard in the section Profile -> Notifications on mom-ai-restaurant.pro\n\nAfter the insertion MOM AI Restaurant Assistant will send the notifications in this chat upon the arrival of successfully paid orders!')
    await message.reply('The code to insert:')
    await message.reply(f'{chat_id}')
app_tg.run()


