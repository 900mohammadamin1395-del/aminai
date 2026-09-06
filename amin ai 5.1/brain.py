# -*- coding: utf-8 -*-

import random
import re

import user_memory


REMEMBER_PATTERNS = [
    (r"اسمم\s+(.+?)\s+(است|هست|ه)$", "name"),
    (r"اسم من\s+(.+?)\s+(است|هست|ه)$", "name"),
    (r"غذای مورد ?علاقه ?ام\s+(.+?)\s+(است|هست)$", "favorite_food"),
    (r"شهر من\s+(.+?)\s+(است|هست)$", "city"),
    (r"من اهل\s+(.+?)(?:\s+هستم)?$", "city"),
    (r"من\s+(.+?)\s+هستم$", "name"),
]

FACT_LABELS = {
    "name": "اسمت",
    "favorite_food": "غذای موردعلاقه‌ات",
    "city": "شهرت"
}


def remember(user_id, message):

    text = message.strip()

    for pattern, key in REMEMBER_PATTERNS:

        match = re.search(pattern, text)

        if match:

            value = match.group(1).strip()

            if value:

                user_memory.set_fact(user_id, key, value)

                label = FACT_LABELS.get(key, key)

                return "باشه، یادم موند که " + label + " " + value + " است 👍"

    return None


def recall(user_id, message):

    text = message.strip().lower()

    if (
        "اسمم چیه" in text
        or "اسم من چیه" in text
        or "اسم من رو یادته" in text
        or "اسمم رو میدونی" in text
        or "اسمم یادته" in text
    ):

        name = user_memory.get_fact(user_id, "name")

        if name:
            return "اسمت " + name + " است 😎"

        return "هنوز اسمت رو بهم نگفتی. می‌تونی بگی «اسمم ... است»."


    if (
        "غذای موردعلاقه ام چیه" in text
        or "غذای مورد علاقه ام چیه" in text
    ):

        food = user_memory.get_fact(user_id, "favorite_food")

        if food:
            return "غذای موردعلاقه‌ات " + food + " است 😋"

        return "هنوز نگفتی غذای موردعلاقه‌ات چیه."


    if (
        "شهرم چیه" in text
        or "شهر من کجاست" in text
        or "من اهل کجام" in text
    ):

        city = user_memory.get_fact(user_id, "city")

        if city:
            return "تو اهل " + city + " هستی 🏙️"

        return "هنوز نگفتی اهل کجایی."


    return None


def think(message):
    text = message.strip().lower()

    if text == "":
        return "لطفاً یک سؤال بنویس."


    if "سلام" in text or "درود" in text:
        return random.choice([
            "سلام! 👋",
            "درود! 🤖",
            "سلام! آماده‌ام 😎"
        ])


    if "اسمت" in text or "کی هستی" in text or "تو کی هستی" in text:
        return "من Amin AI هستم 🤖🧠"


    if "خوبی" in text or "حالت چطوره" in text:
        return "ممنون! خوبم 😎"


    if "پایتون" in text or "python" in text:
        return "پایتون یک زبان برنامه‌نویسی قدرتمند است 🐍"


    if "ماینکرفت" in text or "minecraft" in text:
        return "ماینکرفت یک بازی سندباکس است ⛏️"


    if "کامپیوتر" in text or "pc" in text:
        return "کامپیوتر دستگاهی برای پردازش اطلاعات است 💻"


    if "هوش مصنوعی" in text or "artificial intelligence" in text:
        return "هوش مصنوعی یعنی سیستم‌هایی که می‌توانند بعضی کارهای هوشمندانه انجام دهند 🤖"


    if "جوک" in text or "شوخی" in text:
        return random.choice([
            "چرا کامپیوتر رفت دکتر؟ چون ویروس گرفته بود! 😂",
            "کامپیوتر گفت: من یک بایت می‌خوام! 😂"
        ])


    if "ممنون" in text or "مرسی" in text:
        return "خواهش می‌کنم! 😎"


    if "خداحافظ" in text or "بای" in text:
        return "خداحافظ! 👋"


    return None