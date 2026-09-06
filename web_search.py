# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

from summarizer import summarize


def fetch_results(query, limit=6):
    url = "https://html.duckduckgo.com/html/?q=" + quote(query)

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=15
    )

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    results = soup.select(".result")

    texts = []

    count = 0

    for result in results:

        title = result.select_one(".result__title")
        snippet = result.select_one(".result__snippet")

        title_text = title.get_text(" ", strip=True) if title else ""
        snippet_text = snippet.get_text(" ", strip=True) if snippet else ""

        if not title_text and not snippet_text:
            continue

        combined = (title_text + ". " + snippet_text).strip()
        texts.append(combined)

        count += 1

        if count >= limit:
            break

    return texts


def web_search(query):
    try:
        texts = fetch_results(query)

        if not texts:
            return "نتیجه‌ای پیدا نشد."

        full_text = " ".join(texts)

        summary = summarize(full_text, max_sentences=4)

        if not summary.strip():
            return "نتیجه‌ای برای خلاصه‌سازی پیدا نشد."

        return "🔎 خلاصه:\n\n" + summary

    except Exception as error:
        return "خطا در جستجو: " + str(error)
