import os
import logging
from dotenv import load_dotenv
from django.contrib.auth import get_user_model
from rest_framework import permissions

load_dotenv()


admins_raw = os.getenv("ADMINS")
if not admins_raw:
    raise ValueError("Empty admin list given")
admins = set(map(str.strip, admins_raw.split("_")))


debug = os.getenv("DEBUG", "False").lower() == "true"


class PhotoIsAdminOrDebugOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        User = get_user_model()


        if request.method in permissions.SAFE_METHODS:
            return True


        if request.method.upper() != "PATCH":
            return False


        auth = request.headers.get("Authorization")
        if not auth:
            return False

        parts = auth.split(" ")
        if len(parts) != 2 or parts[0] != "Bot":
            return False

        token = parts[1]

        try:
            user = User.objects.get(telegram_id=token)
        except User.DoesNotExist:
            logging.warning(f"Пользователь с Telegram ID {token} не найден.")
            return False


        if (user.is_staff or token in admins):
            return True

        allowed_fields = {"photos"}
        incoming_fields = set(request.data.keys())
        return incoming_fields.issubset(allowed_fields)