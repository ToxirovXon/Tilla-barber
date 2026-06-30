"""Bot dispetcherini yig'ish va polling. Ham lokal (python -m bot), ham
admin API ichidan (bitta servis sifatida) ishlatiladi."""
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import load_config
from bot.handlers import admin, booking, registration

logger = logging.getLogger(__name__)


def build() -> tuple[Bot, Dispatcher]:
    config = load_config()
    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.include_router(registration.router)
    dp.include_router(booking.router)
    dp.include_router(admin.router)
    return bot, dp


async def run_polling() -> None:
    bot, dp = build()
    logger.info("Tilla Barber bot polling boshlandi ✅")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
