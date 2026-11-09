from pyrogram import filters
from pyrogram.types import Message
import random

from core.clients import app
from modules.owner.sudoers import sudo_only

PREFIXES = [".", "!"]

JOKES = [
    "Teacher: Why are you late?\nStudent: Because of the sign.\nTeacher: What sign?\nStudent: The one that says 'School Ahead, Go Slow'.",
    "Why don't scientists trust atoms? Because they make up everything!",
    "I told my computer I needed a break... now it won't stop sending me KitKat ads.",
    "Why did the scarecrow win an award? Because he was outstanding in his field.",
    "I'm reading a book about anti-gravity. It's impossible to put down.",
]

QUOTES = [
    "The only way to do great work is to love what you do. - Steve Jobs",
    "In the middle of every difficulty lies opportunity. - Albert Einstein",
    "Success is not final, failure is not fatal. - Winston Churchill",
    "Believe you can and you're halfway there. - Theodore Roosevelt",
    "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt",
]


@app.on_message(filters.command(["joke", "jokes"], prefixes=PREFIXES))
@sudo_only
async def joke_cmd(client, message: Message):
    await message.reply_text(f"😂 {random.choice(JOKES)}")


@app.on_message(filters.command(["quote", "quotes"], prefixes=PREFIXES))
@sudo_only
async def quote_cmd(client, message: Message):
    await message.reply_text(f"📝 {random.choice(QUOTES)}")


@app.on_message(filters.command(["dice", "roll"], prefixes=PREFIXES))
@sudo_only
async def dice_cmd(client, message: Message):
    await message.reply_text(f"🎲 You rolled: **{random.randint(1, 6)}**")


@app.on_message(filters.command(["coin", "flip"], prefixes=PREFIXES))
@sudo_only
async def coin_cmd(client, message: Message):
    result = random.choice(["Heads", "Tails"])
    await message.reply_text(f"🪙 {result}!")


@app.on_message(filters.command(["choose", "pick"], prefixes=PREFIXES))
@sudo_only
async def choose_cmd(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: `.choose option1 | option2 | option3`")
    text = message.text.split(None, 1)[1]
    options = [o.strip() for o in text.split("|") if o.strip()]
    if len(options) < 2:
        return await message.reply_text("Give at least 2 options separated by |")
    choice = random.choice(options)
    await message.reply_text(f"🎯 I choose: **{choice}**")
