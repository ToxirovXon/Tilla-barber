"""Bot kirish nuqtasi (lokal). Ishga tushirish: python -m bot"""
import asyncio
import logging

from bot.runner import run_polling

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    try:
        asyncio.run(run_polling())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi")
