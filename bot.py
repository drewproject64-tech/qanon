import asyncio
import html
import logging
import os
import re

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
router = Router()

BOT_NAME = "QAnon TextFix Bot"

WELCOME = (
    f"<b>Welcome to {BOT_NAME} ✍️</b>\n\n"
    "A simple text-fixing utility that helps make your writing cleaner and easier to read.\n\n"
    "<b>What I can do:</b>\n"
    "• Fix common spacing issues\n"
    "• Clean up punctuation\n"
    "• Improve sentence capitalization\n"
    "• Apply basic text formatting\n\n"
    "<b>How to use:</b>\n"
    "1. Tap <b>Fix My Text</b>.\n"
    "2. Send your text.\n"
    "3. Get a cleaned-up version ready to copy.\n\n"
    "No complicated setup — just send your text and get started."
)

ABOUT = (
    f"<b>About {BOT_NAME}</b>\n\n"
    "QAnon TextFix Bot is a lightweight writing utility for cleaning up everyday text. "
    "It focuses on spelling-related formatting, punctuation, spacing, capitalization, "
    "and basic readability improvements.\n\n"
    "It is designed for simple text editing and does not provide news, political guidance, "
    "financial advice, or specialized professional advice."
)

HELP = (
    "<b>How to use</b>\n\n"
    "Send a text message of up to 4,000 characters. The bot will clean common formatting "
    "issues such as extra spaces, repeated punctuation, and sentence capitalization.\n\n"
    "Use <b>Fix Another</b> whenever you want to process another message."
)


def menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✍️ Fix My Text", callback_data="fix")],
            [
                InlineKeyboardButton(text="ℹ️ About", callback_data="about"),
                InlineKeyboardButton(text="❓ Help", callback_data="help"),
            ],
        ]
    )


def action_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✍️ Fix Another", callback_data="fix")],
            [InlineKeyboardButton(text="🏠 Main Menu", callback_data="menu")],
        ]
    )


def clean_spacing(text: str) -> str:
    text = text.strip()
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def clean_punctuation(text: str) -> str:
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r"([,.;:!?])(?=\S)", r"\1 ", text)
    text = re.sub(r"([!?.,])\1+", r"\1", text)
    return text


def capitalize_sentences(text: str) -> str:
    chars = list(text)
    should_capitalize = True
    for index, char in enumerate(chars):
        if char.isalpha() and should_capitalize:
            chars[index] = char.upper()
            should_capitalize = False
        elif char in ".!?":
            should_capitalize = True
    return "".join(chars)


def fix_text(text: str) -> str:
    result = clean_spacing(text)
    result = clean_punctuation(result)
    return capitalize_sentences(result).strip()


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    await message.answer(WELCOME, reply_markup=menu_keyboard())


@router.message(Command("help"))
async def help_handler(message: Message) -> None:
    await message.answer(HELP, reply_markup=menu_keyboard())


@router.callback_query(F.data == "menu")
async def menu_handler(callback: CallbackQuery) -> None:
    await callback.message.edit_text(WELCOME, reply_markup=menu_keyboard())
    await callback.answer()


@router.callback_query(F.data == "about")
async def about_handler(callback: CallbackQuery) -> None:
    await callback.message.edit_text(ABOUT, reply_markup=action_keyboard())
    await callback.answer()


@router.callback_query(F.data == "help")
async def help_callback_handler(callback: CallbackQuery) -> None:
    await callback.message.edit_text(HELP, reply_markup=action_keyboard())
    await callback.answer()


@router.callback_query(F.data == "fix")
async def fix_handler(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "<b>Send your text ✍️</b>\n\n"
        "I'll clean up spacing, punctuation, and sentence capitalization.",
        reply_markup=action_keyboard(),
    )
    await callback.answer()


@router.message(F.text)
async def text_handler(message: Message) -> None:
    original = message.text.strip()

    if not original:
        await message.answer("Please send some text to fix.", reply_markup=menu_keyboard())
        return

    if len(original) > 4000:
        await message.answer(
            "Your message is too long. Please send up to 4,000 characters at a time.",
            reply_markup=menu_keyboard(),
        )
        return

    fixed = fix_text(original)
    safe_text = html.escape(fixed)

    await message.answer(
        f"<b>✅ Improved text</b>\n\n<blockquote>{safe_text}</blockquote>",
        reply_markup=action_keyboard(),
    )


@router.message()
async def unsupported_handler(message: Message) -> None:
    await message.answer(
        "Please send a text message. QAnon TextFix Bot works with written text and basic formatting.",
        reply_markup=menu_keyboard(),
    )


async def main() -> None:
    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.include_router(router)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
