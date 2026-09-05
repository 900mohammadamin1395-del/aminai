# -*- coding: utf-8 -*-

import json
import os
import threading


DATA_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "user_memory.json"
)

_lock = threading.Lock()


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


def get_fact(user_id, key):

    with _lock:
        data = _load()

    return data.get(user_id, {}).get(key)


def set_fact(user_id, key, value):

    with _lock:
        data = _load()

        if user_id not in data:
            data[user_id] = {}

        data[user_id][key] = value

        _save(data)


def get_all_facts(user_id):

    with _lock:
        data = _load()

    return data.get(user_id, {})
