from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
import logging

class TelegramAuthentication(BaseAuthentication):
    def authenticate(self, request):
        telegram_header = request.headers.get("Authorization")
        logging.info("Header received: '%s'", telegram_header)

        if not telegram_header:
            logging.error("No Authorization header")
            return None

        try:
            prefix, telegram_id_str = telegram_header.split(" ", 1)
        except ValueError:
            logging.error("Incorrect header format")
            return None

        if prefix.strip() != "Bot":
            logging.error("Incorrect header prefix")
            return None

        telegram_id_str = telegram_id_str.strip()
        User = get_user_model()
        try:
            user = User.objects.get(telegram_id=telegram_id_str)
            logging.info("Found user: %s", user)
        except User.DoesNotExist:
            logging.error("Telegram ID %s not found. IDs in DB: %s",
                telegram_id_str,
                list(User.objects.values_list("telegram_id", flat=True))
            )
            raise AuthenticationFailed(f"User with id {telegram_id_str} does not exist")
        return (user, None)