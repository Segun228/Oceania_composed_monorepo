import os

from rest_framework import permissions
from dotenv import load_dotenv
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
import logging

load_dotenv()


admins = (os.getenv("ADMINS"))
if not admins:
    raise ValueError("Empty admin list given")
else:
    admins = list(map(str.strip, admins.split("_")))

debug = os.getenv("DEBUG", "False").lower() == "true"



class IsAdminOrDebugOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        User = get_user_model()
        if request.method in permissions.SAFE_METHODS:
            return True
        auth = request.headers.get("Authorization")
        if not auth:
            return False
        header = auth.split(" ")
        if header[0] != "Bot":
            return False
        try:
            user = User.objects.get(telegram_id=header[1])
            if (user.is_staff or header[1] in admins):
                return True
        except User.DoesNotExist:
            logging.error("Пользователь с таким Telegram ID не найден.")
            return False

