# -*- coding: utf-8 -*-

import re


STOPWORDS = set([
    "و", "در", "به", "از", "که", "این", "را", "با", "است", "برای",
    "آن", "یک", "تا", "می", "شود", "شد", "کرد", "های", "هم", "یا",
    "بر", "اما", "نیز", "خود", "ما", "شما", "آنها", "او", "هر",
    "چون", "پس", "اگر", "چه", "بود", "دارد", "کند", "کنند", "شده",
    "می‌شود", "می‌کند", "دو", "سه", "روی", "بین", "همه", "دیگر",
    "باید", "نمی", "بی", "چند", "همچنین", "درباره", "طبق", "طی"
])


def split_sentences(text):
    text = re.sub(r"\s+", " ", text).strip()

    parts = re.split(r"(?<=[\.\!\?؟])\s+", text)

    sentences = []

    for part in parts:
        part = part.strip()

        if len(part) > 15:
            sentences.append(part)

    return sentences


def clean_word(word):
    word = re.sub(r"[^\w\u0600-\u06FF]", "", word)
    return word.lower()


def word_frequencies(sentences):
    freq = {}

    for sentence in sentences:
        words = sentence.split(" ")

        for word in words:
            word = clean_word(word)

            if not word or word in STOPWORDS or len(word) < 2:
                continue

            freq[word] = freq.get(word, 0) + 1

    return freq


def score_sentences(sentences, freq):
    scores = []

    for sentence in sentences:
        words = sentence.split(" ")

        score = 0
        word_count = 0

        for word in words:
            word = clean_word(word)

            if word in freq:
                score += freq[word]
                word_count += 1

        if word_count > 0:
            score = score / word_count

        scores.append(score)

    return scores


def is_similar(a, b):
    words_a = set(clean_word(w) for w in a.split(" ") if clean_word(w))
    words_b = set(clean_word(w) for w in b.split(" ") if clean_word(w))

    if not words_a or not words_b:
        return False

    overlap = len(words_a & words_b)
    smaller = min(len(words_a), len(words_b))

    return overlap / smaller > 0.6


def summarize(text, max_sentences=4):
    sentences = split_sentences(text)

    if len(sentences) <= max_sentences:
        return " ".join(sentences)

    freq = word_frequencies(sentences)
    scores = score_sentences(sentences, freq)

    ranked = sorted(
        range(len(sentences)),
        key=lambda i: scores[i],
        reverse=True
    )

    chosen_indexes = []
    chosen_sentences = []

    for i in ranked:
        candidate = sentences[i]

        duplicate = False

        for existing in chosen_sentences:
            if is_similar(candidate, existing):
                duplicate = True
                break

        if not duplicate:
            chosen_indexes.append(i)
            chosen_sentences.append(candidate)

        if len(chosen_indexes) >= max_sentences:
            break

    chosen_indexes.sort()

    final_sentences = [sentences[i] for i in chosen_indexes]

    return " ".join(final_sentences)
