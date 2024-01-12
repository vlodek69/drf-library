import os

from django.db.models.signals import post_save
from django.dispatch import receiver
from dotenv import load_dotenv

from .telegram_utils import send_telegram_message
from .models import Borrowing


load_dotenv()


@receiver(post_save, sender=Borrowing)
async def send_telegram_notification(sender, instance, created, **kwargs):
    if created:
        try:
            await send_telegram_message(
                os.environ.get("BOT_TOKEN"),
                os.environ.get("CHAT_ID"),
                f"New borrowing created! \n{instance.telegram_message()}",
            )
        except Exception as e:
            print(f"Error sending Telegram message: {e}")
