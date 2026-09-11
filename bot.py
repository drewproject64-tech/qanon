import asyncio
import logging
import os

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

router = Router()

WELCOME = (
    "<b>Welcome to QAnon Reference</b>\n\n"
    "This bot provides a neutral, educational reference about the history, "
    "terminology, major events, and public record surrounding QAnon.\n\n"
    "Choose a section below to explore the information. Content is presented "
    "for educational and reference purposes and does not treat unverified claims as facts."
)

ABOUT = (
    "<b>About QAnon Reference</b>\n\n"
    "QAnon Reference is an informational bot covering the history and public "
    "record of the QAnon movement. It is designed for simple browsing and "
    "educational use."
)

TEXTS = {
    "overview": (
        "<b>Overview</b>\n\n"
        "QAnon is a conspiracy theory movement that emerged online in the United States. "
        "This section provides neutral background and context rather than endorsing its claims."
    ),
    "history": (
        "<b>History</b>\n\n"
        "Explore a brief timeline of notable developments, online communities, and public events "
        "associated with QAnon."
    ),
    "terms": (
        "<b>Terminology</b>\n\n"
        "Learn common terms associated with QAnon and what those terms mean in their historical and online context."
    ),
    "facts": (
        "<b>Fact Checks</b>\n\n"
        "This section is intended for reviewing claims critically and distinguishing documented information "
        "from allegations or unsupported statements."
    ),
}


def main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📚 Overview", callback_data="overview"),
                InlineKeyboardButton(text="🕰️ History", callback_data="history"),
            ],
            [
                InlineKeyboardButton(text="📖 Terminology", callback_data="terms"),
                InlineKeyboardButton(text="🔎 Fact Checks", callback_data="facts"),
            ],
            [InlineKeyboardButton(text="ℹ️ About", callback_data="about")],
        ]
    )


def back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="🔙 Back to Menu", callback_data="menu")]]
    )


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    await message.answer(WELCOME, reply_markup=main_keyboard())


@router.message(Command("help"))
async def help_handler(message: Message) -> None:
    await message.answer(
        "<b>How to use this bot</b>\n\n"
        "Tap any button below to browse the available sections. You can return to the main menu at any time.",
        reply_markup=main_keyboard(),
    )


@router.callback_query(F.data == "menu")
async def menu_handler(callback: CallbackQuery) -> None:
    await callback.message.edit_text(WELCOME, reply_markup=main_keyboard())
    await callback.answer()


@router.callback_query(F.data == "about")
async def about_handler(callback: CallbackQuery) -> None:
    await callback.message.edit_text(ABOUT, reply_markup=back_keyboard())
    await callback.answer()


@router.callback_query(F.data.in_({"overview", "history", "terms", "facts"}))
async def section_handler(callback: CallbackQuery) -> None:
    await callback.message.edit_text(TEXTS[callback.data], reply_markup=back_keyboard())
    await callback.answer()


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
