# -*- coding: utf-8 -*-

import os
import secrets

from flask import Flask, request, jsonify, render_template, session, redirect, url_for

from brain import think, remember, recall
from web_search import web_search
from weather import get_weather
import conversations
import users
import user_memory
import google_auth
import image_gen
import music_gen


app = Flask(__name__)

app.secret_key = os.environ.get("AMIN_SECRET_KEY", "amin-ai-secret-key-change-me")


def weather_answer():

    temperature, code = get_weather()

    if code == 0:
        condition = "آسمان صاف است"
    elif code in [1, 2, 3]:
        condition = "هوا ابری است"
    elif code in [45, 48]:
        condition = "هوا مه‌آلود است"
    elif code in [51, 53, 55, 56, 57]:
        condition = "نم‌نم باران می‌بارد"
    elif code in [61, 63, 65, 66, 67]:
        condition = "بارانی است"
    elif code in [71, 73, 75, 77, 85, 86]:
        condition = "برفی است"
    elif code in [80, 81, 82]:
        condition = "رگباری است"
    elif code in [95, 96, 99]:
        condition = "رعد و برق است"
    else:
        condition = "وضعیت هوا مشخص نیست"

    return "دمای فعلی حدود " + str(temperature) + " درجه است و " + condition + " 🌤"


def needs_search(message):

    text = message.lower()

    words = [
        "آخرین",
        "جدیدترین",
        "امروز",
        "امسال",
        "قیمت",
        "خبر",
        "اخبار",
        "کی میاد",
        "چه زمانی",
        "چند است",
        "چنده",
        "نسخه جدید"
    ]

    for word in words:

        if word in text:
            return True

    return False


def memory_answer(message, messages):

    text = message.lower()

    if (
        "چی گفتم" in text
        or "یادت هست" in text
    ):

        if messages:
            return "آره، پیام‌های این گفتگو رو یادم هست 🧠💾"

        return "فعلاً چیزی در این گفتگو نگفتی."

    return None


def current_user():
    return session.get("username")


def require_login():
    return bool(current_user())


@app.route("/")
def home():

    if not current_user():
        return render_template("login.html", google_enabled=google_auth.is_configured())

    return render_template(
        "chat.html",
        is_google_account=users.is_google_user(current_user())
    )


@app.route("/register")
def register_page():

    if current_user():
        return render_template("chat.html")

    return render_template("register.html", google_enabled=google_auth.is_configured())


@app.route("/api/register", methods=["POST"])
def api_register():

    data = request.get_json() or {}

    username = data.get("username", "")
    password = data.get("password", "")

    error = users.validate_credentials(username, password)

    if error:
        return jsonify({"success": False, "error": error})

    if users.user_exists(username):
        return jsonify({"success": False, "error": "این نام کاربری قبلاً ثبت شده است."})

    users.create_user(username, password)

    session["username"] = username.strip().lower()

    return jsonify({"success": True})


@app.route("/login", methods=["POST"])
def login():

    data = request.get_json() or {}

    username = data.get("username", "")
    password = data.get("password", "")

    if users.verify_user(username, password):

        session["username"] = username.strip().lower()

        return jsonify({"success": True})

    return jsonify({"success": False})


@app.route("/logout", methods=["POST"])
def logout():

    session.pop("username", None)

    return jsonify({"success": True})


@app.route("/login/google")
def login_google():

    if not google_auth.is_configured():
        return render_template(
            "login.html",
            google_enabled=False,
            google_error="ورود با گوگل هنوز روی این سرور تنظیم نشده است."
        )

    state = secrets.token_urlsafe(16)
    session["oauth_state"] = state

    redirect_uri = url_for("login_google_callback", _external=True)

    return redirect(google_auth.build_auth_url(redirect_uri, state))


@app.route("/login/google/callback")
def login_google_callback():

    if not google_auth.is_configured():
        return redirect(url_for("home"))

    if request.args.get("error"):
        return redirect(url_for("home"))

    state = request.args.get("state")

    if not state or state != session.pop("oauth_state", None):
        return redirect(url_for("home"))

    code = request.args.get("code")

    if not code:
        return redirect(url_for("home"))

    redirect_uri = url_for("login_google_callback", _external=True)

    try:

        token_data = google_auth.exchange_code(code, redirect_uri)

        access_token = token_data.get("access_token")

        email, verified = google_auth.get_user_email(access_token)

    except Exception:
        return redirect(url_for("home"))

    if not email or not verified:
        return redirect(url_for("home"))

    if not users.user_exists(email):
        users.create_google_user(email)

    session["username"] = email.strip().lower()

    return redirect(url_for("home"))


@app.route("/api/conversations", methods=["GET"])
def api_list_conversations():

    if not require_login():
        return jsonify({"error": "unauthorized"}), 401

    return jsonify(conversations.list_conversations(current_user()))


@app.route("/api/conversations", methods=["POST"])
def api_create_conversation():

    if not require_login():
        return jsonify({"error": "unauthorized"}), 401

    conv = conversations.create_conversation(current_user())

    return jsonify({
        "id": conv["id"],
        "title": conv["title"]
    })


@app.route("/api/conversations/<conv_id>", methods=["GET"])
def api_get_conversation(conv_id):

    if not require_login():
        return jsonify({"error": "unauthorized"}), 401

    conv = conversations.get_conversation(current_user(), conv_id)

    if conv is None:
        return jsonify({"error": "not found"}), 404

    return jsonify(conv)


@app.route("/api/conversations/<conv_id>", methods=["DELETE"])
def api_delete_conversation(conv_id):

    if not require_login():
        return jsonify({"error": "unauthorized"}), 401

    ok = conversations.delete_conversation(current_user(), conv_id)

    if not ok:
        return jsonify({"error": "not found"}), 404

    return jsonify({"success": True})


@app.route("/api/conversations/<conv_id>/rename", methods=["POST"])
def api_rename_conversation(conv_id):

    if not require_login():
        return jsonify({"error": "unauthorized"}), 401

    data = request.get_json() or {}

    title = data.get("title", "")

    ok = conversations.rename_conversation(current_user(), conv_id, title)

    if not ok:
        return jsonify({"error": "invalid"}), 400

    return jsonify({"success": True})


@app.route("/api/conversations", methods=["DELETE"])
def api_delete_all_conversations():

    if not require_login():
        return jsonify({"error": "unauthorized"}), 401

    conversations.delete_all_conversations(current_user())

    return jsonify({"success": True})


@app.route("/api/memory", methods=["GET"])
def api_get_memory():

    if not require_login():
        return jsonify({"error": "unauthorized"}), 401

    return jsonify(user_memory.get_all_facts(current_user()))


@app.route("/api/memory/<key>", methods=["DELETE"])
def api_delete_memory(key):

    if not require_login():
        return jsonify({"error": "unauthorized"}), 401

    ok = user_memory.delete_fact(current_user(), key)

    if not ok:
        return jsonify({"error": "not found"}), 404

    return jsonify({"success": True})


@app.route("/api/change-password", methods=["POST"])
def api_change_password():

    if not require_login():
        return jsonify({"error": "unauthorized"}), 401

    data = request.get_json() or {}

    old_password = data.get("old_password", "")
    new_password = data.get("new_password", "")

    error = users.change_password(current_user(), old_password, new_password)

    if error:
        return jsonify({"success": False, "error": error})

    return jsonify({"success": True})


@app.route("/api/account", methods=["DELETE"])
def api_delete_account():

    if not require_login():
        return jsonify({"error": "unauthorized"}), 401

    user_id = current_user()

    users.delete_user(user_id)
    conversations.delete_all_conversations(user_id)
    user_memory.delete_all_facts(user_id)

    session.pop("username", None)

    return jsonify({"success": True})


@app.route("/chat", methods=["POST"])
def chat():

    user_id = current_user()

    if not user_id:

        return jsonify({
            "answer": "لطفاً ابتدا وارد شوید."
        }), 401


    data = request.get_json()

    message = data.get(
        "message",
        ""
    ).strip()

    conv_id = data.get("conversation_id")


    if not message:

        return jsonify({
            "answer": "پیامی دریافت نشد."
        })


    conv = None

    if conv_id:
        conv = conversations.get_conversation(user_id, conv_id)

    if conv is None:
        conv = conversations.create_conversation(user_id)
        conv_id = conv["id"]


    conversations.add_message(
        user_id,
        conv_id,
        "user",
        message
    )


    existing_messages = conv.get("messages", [])

    image_url = None
    melody = None

    answer = remember(user_id, message)

    if answer is None:
        answer = recall(user_id, message)

    if answer is None:
        answer = memory_answer(message, existing_messages)


    if answer is None:

        image_prompt = image_gen.detect_prompt(message)

        if image_prompt:
            image_url = image_gen.build_image_url(image_prompt)
            answer = "🎨 بفرما، این هم عکسی که خواستی:"


    if answer is None:

        if music_gen.detect_request(message):
            melody = music_gen.generate_melody(message)
            answer = "🎵 بفرما، یه آهنگ " + melody["mood"] + " برات ساختم:"


    if answer is None:

        if (
            "هوا" in message
            or "آب و هوا" in message
            or "آبوهوا" in message
        ):

            answer = weather_answer()


        elif needs_search(message):

            answer = web_search(message)


        else:

            answer = think(message)

            if answer is None:

                answer = web_search(message)


    updated_conv = conversations.add_message(
        user_id,
        conv_id,
        "assistant",
        answer,
        image_url=image_url,
        melody=melody
    )


    return jsonify({

        "answer": answer,

        "image_url": image_url,

        "melody": melody,

        "conversation_id": conv_id,

        "title": updated_conv["title"] if updated_conv else "گفتگوی جدید"

    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )
