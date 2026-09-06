# -*- coding: utf-8 -*-

import random


ROOT_FREQ = 261.63  # C4

SCALES = {
    "major": [0, 2, 4, 5, 7, 9, 11],
    "minor": [0, 2, 3, 5, 7, 8, 10]
}

TRIGGER_VERBS = ["بساز", "بزن", "پخش کن", "بنواز", "درست کن", "تولید کن"]
SUBJECT_WORDS = ["آهنگ", "موزیک", "ملودی", "موسیقی"]

MOOD_PROFILES = [
    (["شاد", "خوشحال", "شادی"], "major", 140, [0.2, 0.2, 0.4]),
    (["غمگین", "غم", "ناراحت", "دلتنگ"], "minor", 80, [0.4, 0.4, 0.8]),
    (["آروم", "ارام", "ملایم", "آرامش"], "major", 70, [0.5, 0.5, 1.0]),
    (["انرژیک", "پرانرژی", "هیجان"], "major", 160, [0.15, 0.15, 0.3]),
    (["رقص", "رقصی"], "major", 128, [0.25, 0.25, 0.5]),
    (["حماسی", "قهرمان"], "minor", 110, [0.3, 0.3, 0.6])
]

MOOD_LABELS = {
    "major_140": "شاد",
    "minor_80": "غمگین",
    "major_70": "آروم",
    "major_160": "پرانرژی",
    "major_128": "رقصی",
    "minor_110": "حماسی",
    "major_110": "معمولی"
}


def detect_request(message):

    text = message.strip()

    has_subject = any(word in text for word in SUBJECT_WORDS)
    has_verb = any(verb in text for verb in TRIGGER_VERBS)

    return has_subject and has_verb


def _pick_mood(text):

    for keywords, scale, tempo, durations in MOOD_PROFILES:

        if any(word in text for word in keywords):
            return scale, tempo, durations

    return "major", 110, [0.25, 0.25, 0.5]


def _degree_to_freq(degree, scale, octave_shift=0):

    octave, idx = divmod(degree, len(scale))

    semitone = scale[idx] + (octave + octave_shift) * 12

    return ROOT_FREQ * (2 ** (semitone / 12))


def _generate_motif(scale, length=5, center=0, spread=4):

    degree = center

    motif = []

    for i in range(length):

        step = random.choice([-2, -1, -1, 0, 1, 1, 2])

        degree = max(center - spread, min(center + spread, degree + step))

        motif.append(degree)

    return motif


def _motif_to_notes(motif, scale, duration_choices):

    notes = []

    for degree in motif:

        freq = _degree_to_freq(degree, scale)

        duration = random.choice(duration_choices)

        notes.append({
            "freq": round(freq, 2),
            "duration": duration
        })

    return notes


def generate_melody(message, motif_length=5):

    scale_name, tempo, duration_choices = _pick_mood(message)

    scale = SCALES[scale_name]

    # motif A is the "verse", motif B is the "chorus" — built around a
    # different center note so it feels like a distinct section
    motif_a = _generate_motif(scale, motif_length, center=0)
    motif_b = _generate_motif(scale, motif_length, center=4)

    # simple song form: verse, verse, chorus, verse, chorus, verse
    structure = [motif_a, motif_a, motif_b, motif_a, motif_b, motif_a]

    # chord roots (scale degrees) under each section — a I-I-V-I-V-I feel
    bass_roots = [0, 0, 4, 0, 4, 0]

    melody_notes = []
    bass_notes = []

    for section, root_degree in zip(structure, bass_roots):

        section_notes = _motif_to_notes(section, scale, duration_choices)

        melody_notes.extend(section_notes)

        section_duration = sum(n["duration"] for n in section_notes)

        bass_freq = _degree_to_freq(root_degree, scale, octave_shift=-1)

        bass_notes.append({
            "freq": round(bass_freq, 2),
            "duration": section_duration
        })

    label_key = scale_name + "_" + str(tempo)

    mood_label = MOOD_LABELS.get(label_key, scale_name)

    return {
        "scale": scale_name,
        "tempo": tempo,
        "mood": mood_label,
        "notes": melody_notes,
        "bass": bass_notes
    }
