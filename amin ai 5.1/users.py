# -*- coding: utf-8 -*-

import json
import os
import re
import threading

from werkzeug.security import generate_password_hash, check_password_hash


DATA_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "users.json"
)

_lock = threading.Lock()

USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_ا-ی]{3,30}$")


def _load():
    if not os.path.exists(DATA_FILE):
        return {}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def validate_credentials(username, password):

    username = (username or "").strip()
    password = password or ""

    if not USERNAME_PATTERN.match(username):
        return "نام کاربری باید بین ۳ تا ۳۰ حرف/عدد باشد (بدون فاصله)."

    if len(password) < 4:
        return "رمز عبور باید حداقل ۴ کاراکتر باشد."

    return None


def user_exists(username):

    username = (username or "").strip().lower()

    with _lock:
        data = _load()

    return username in data


def create_user(username, password):

    username = username.strip().lower()

    with _lock:
        data = _load()

        if username in data:
            return False

        data[username] = {
            "password_hash": generate_password_hash(password),
            "google": False
        }

        _save(data)

    return True


def create_google_user(email):

    email = email.strip().lower()

    with _lock:
        data = _load()

        if email not in data:

            data[email] = {
                "password_hash": None,
                "google": True
            }

            _save(data)

    return email


def is_google_user(username):

    username = (username or "").strip().lower()

    with _lock:
        data = _load()

    user = data.get(username)

    return bool(user and user.get("google"))


def verify_user(username, password):

    username = (username or "").strip().lower()

    with _lock:
        data = _load()

    user = data.get(username)

    if not user:
        return False

    if user.get("google") or not user.get("password_hash"):
        return False

    return check_password_hash(user["password_hash"], password or "")


def change_password(username, old_password, new_password):

    username = (username or "").strip().lower()

    if is_google_user(username):
        return "این حساب با گوگل ساخته شده و رمز عبور جداگانه ندارد."

    if not verify_user(username, old_password):
        return "رمز فعلی اشتباه است."

    if len(new_password or "") < 4:
        return "رمز جدید باید حداقل ۴ کاراکتر باشد."

    with _lock:
        data = _load()

        if username not in data:
            return "کاربر پیدا نشد."

        data[username]["password_hash"] = generate_password_hash(new_password)

        _save(data)

    return None


def delete_user(username):

    username = (username or "").strip().lower()

    with _lock:
        data = _load()

        if username in data:
            del data[username]
            _save(data)
            return True

        return False
