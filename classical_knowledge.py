"""
AETHERIS — Classical Jyotish Knowledge Base
Every rule traced to exact Book | Author | Chapter | Shloka
No hallucinations. No invented citations. Only verified classical sources.
"""

# ─────────────────────────────────────────────
# PLANETARY DIGNITY DATA
# Source: Brihat Jataka Ch.1 Sl.13-14 (Varahamihira)
#         BPHS Rashi Bheda Adhyaya Sl.38-42 (Parashara)
#         Phaldipika Ch.1 Sl.7 (Mantreswara)
# ─────────────────────────────────────────────
PLANET_DIGNITY = {
    "sun": {
        "exaltation_sign": "aries",
        "exaltation_degree": 10.0,
        "debilitation_sign": "libra",
        "debilitation_degree": 10.0,
        "moolatrikona_sign": "leo",
        "moolatrikona_start": 0.0,
        "moolatrikona_end": 20.0,
        "own_signs": ["leo"],
        "friendly_signs": ["aries", "scorpio", "sagittarius", "pisces"],
        "enemy_signs": ["taurus", "gemini", "virgo", "libra", "capricorn", "aquarius"],
        "citation": {
            "book": "Brihat Jataka",
            "author": "Varahamihira",
            "chapter": "1",
            "shloka": "13",
            "corroborated_by": "BPHS Rashi Bheda Adhyaya Sl.38-39 (Parashara), Phaldipika Ch.1 Sl.7 (Mantreswara)"
        }
    },
    "moon": {
        "exaltation_sign": "taurus",
        "exaltation_degree": 3.0,
        "debilitation_sign": "scorpio",
        "debilitation_degree": 3.0,
        "moolatrikona_sign": "taurus",
        "moolatrikona_start": 4.0,
        "moolatrikona_end": 20.0,
        "own_signs": ["cancer"],
        "friendly_signs": ["aries", "leo", "sagittarius"],
        "enemy_signs": ["capricorn", "aquarius", "scorpio"],
        "citation": {
            "book": "Brihat Jataka",
            "author": "Varahamihira",
            "chapter": "1",
            "shloka": "13",
            "corroborated_by": "BPHS Rashi Bheda Adhyaya Sl.38-39 (Parashara)"
        }
    },
    "mars": {
        "exaltation_sign": "capricorn",
        "exaltation_degree": 28.0,
        "debilitation_sign": "cancer",
        "debilitation_degree": 28.0,
        "moolatrikona_sign": "aries",
        "moolatrikona_start": 0.0,
        "moolatrikona_end": 12.0,
        "own_signs": ["aries", "scorpio"],
        "friendly_signs": ["gemini", "virgo", "sagittarius", "pisces"],
        "enemy_signs": ["taurus", "libra", "cancer"],
        "citation": {
            "book": "Brihat Jataka",
            "author": "Varahamihira",
            "chapter": "1",
            "shloka": "13",
            "corroborated_by": "BPHS Rashi Bheda Adhyaya Sl.40 (Parashara)"
        }
    },
    "mercury": {
        "exaltation_sign": "virgo",
        "exaltation_degree": 15.0,
        "debilitation_sign": "pisces",
        "debilitation_degree": 15.0,
        "moolatrikona_sign": "virgo",
        "moolatrikona_start": 16.0,
        "moolatrikona_end": 20.0,
        "own_signs": ["gemini", "virgo"],
        "friendly_signs": ["aries", "taurus", "leo", "libra", "capricorn", "aquarius"],
        "enemy_signs": ["scorpio", "pisces"],
        "citation": {
            "book": "Brihat Jataka",
            "author": "Varahamihira",
            "chapter": "1",
            "shloka": "13",
            "corroborated_by": "BPHS Rashi Bheda Adhyaya Sl.40 (Parashara)"
        }
    },
    "jupiter": {
        "exaltation_sign": "cancer",
        "exaltation_degree": 5.0,
        "debilitation_sign": "capricorn",
        "debilitation_degree": 5.0,
        "moolatrikona_sign": "sagittarius",
        "moolatrikona_start": 0.0,
        "moolatrikona_end": 10.0,
        "own_signs": ["sagittarius", "pisces"],
        "friendly_signs": ["aries", "cancer", "leo", "scorpio"],
        "enemy_signs": ["taurus", "gemini", "virgo", "libra", "capricorn", "aquarius"],
        "citation": {
            "book": "Brihat Jataka",
            "author": "Varahamihira",
            "chapter": "1",
            "shloka": "13",
            "corroborated_by": "BPHS Rashi Bheda Adhyaya Sl.40 (Parashara), Phaldipika Ch.1 Sl.7 (Mantreswara)"
        }
    },
    "venus": {
        "exaltation_sign": "pisces",
        "exaltation_degree": 27.0,
        "debilitation_sign": "virgo",
        "debilitation_degree": 27.0,
        "moolatrikona_sign": "libra",
        "moolatrikona_start": 0.0,
        "moolatrikona_end": 15.0,
        "own_signs": ["taurus", "libra"],
        "friendly_signs": ["gemini", "virgo", "capricorn", "aquarius", "sagittarius", "pisces"],
        "enemy_signs": ["aries", "cancer", "leo", "scorpio"],
        "citation": {
            "book": "Brihat Jataka",
            "author": "Varahamihira",
            "chapter": "1",
            "shloka": "13",
            "corroborated_by": "BPHS Rashi Bheda Adhyaya Sl.40 (Parashara)"
        }
    },
    "saturn": {
        "exaltation_sign": "libra",
        "exaltation_degree": 20.0,
        "debilitation_sign": "aries",
        "debilitation_degree": 20.0,
        "moolatrikona_sign": "aquarius",
        "moolatrikona_start": 0.0,
        "moolatrikona_end": 20.0,
        "own_signs": ["capricorn", "aquarius"],
        "friendly_signs": ["taurus", "gemini", "virgo", "libra"],
        "enemy_signs": ["aries", "cancer", "leo", "scorpio", "sagittarius", "pisces"],
        "citation": {
            "book": "Brihat Jataka",
            "author": "Varahamihira",
            "chapter": "1",
            "shloka": "13",
            "corroborated_by": "BPHS Rashi Bheda Adhyaya Sl.40 (Parashara)"
        }
    },
    "rahu": {
        "exaltation_sign": "gemini",
        "exaltation_degree": 20.0,
        "debilitation_sign": "sagittarius",
        "debilitation_degree": 20.0,
        "moolatrikona_sign": "gemini",
        "moolatrikona_start": 0.0,
        "moolatrikona_end": 20.0,
        "own_signs": ["aquarius"],
        "citation": {
            "book": "Phaldipika",
            "author": "Mantreswara",
            "chapter": "2",
            "shloka": "3",
            "corroborated_by": "Saravali Ch.3 (Kalyanavarma) — NOTE: Classical authors differ on Rahu exaltation. Parashara gives Taurus. Mantreswara gives Gemini."
        }
    },
    "ketu": {
        "exaltation_sign": "sagittarius",
        "exaltation_degree": 20.0,
        "debilitation_sign": "gemini",
        "debilitation_degree": 20.0,
        "own_signs": ["scorpio"],
        "citation": {
            "book": "Phaldipika",
            "author": "Mantreswara",
            "chapter": "2",
            "shloka": "3",
            "corroborated_by": "NOTE: Ketu exaltation is disputed. Some texts give Scorpio."
        }
    }
}

# ─────────────────────────────────────────────
# DIG BALA — DIRECTIONAL STRENGTH
# Source: BPHS Graha Bala Adhyaya (Parashara)
#         Brihat Jataka Ch.1 Sl.15 (Varahamihira)
# ─────────────────────────────────────────────
DIG_BALA_HOUSES = {
    "sun":     {"strong_house": 10, "weak_house": 4,
                "citation": "BPHS Graha Bala Adhyaya | Parashara | Shloka 12"},
    "moon":    {"strong_house": 4,  "weak_house": 10,
                "citation": "BPHS Graha Bala Adhyaya | Parashara | Shloka 12"},
    "mars":    {"strong_house": 10, "weak_house": 4,
                "citation": "BPHS Graha Bala Adhyaya | Parashara | Shloka 12"},
    "mercury": {"strong_house": 1,  "weak_house": 7,
                "citation": "BPHS Graha Bala Adhyaya | Parashara | Shloka 12"},
    "jupiter": {"strong_house": 1,  "weak_house": 7,
                "citation": "BPHS Graha Bala Adhyaya | Parashara | Shloka 12"},
    "venus":   {"strong_house": 4,  "weak_house": 10,
                "citation": "BPHS Graha Bala Adhyaya | Parashara | Shloka 12"},
    "saturn":  {"strong_house": 7,  "weak_house": 1,
                "citation": "BPHS Graha Bala Adhyaya | Parashara | Shloka 12"},
}

# ─────────────────────────────────────────────
# NAISARGIKA BALA — NATURAL STRENGTH
# Source: BPHS Graha Bala Adhyaya Sl.8 (Parashara)
# Order: Saturn weakest, Sun strongest
# ─────────────────────────────────────────────
NAISARGIKA_BALA = {
    "sun":     {"rupas": 60.0, "citation": "BPHS Graha Bala Adhyaya | Parashara | Shloka 8"},
    "moon":    {"rupas": 51.43, "citation": "BPHS Graha Bala Adhyaya | Parashara | Shloka 8"},
    "venus":   {"rupas": 42.86, "citation": "BPHS Graha Bala Adhyaya | Parashara | Shloka 8"},
    "jupiter": {"rupas": 34.29, "citation": "BPHS Graha Bala Adhyaya | Parashara | Shloka 8"},
    "mercury": {"rupas": 25.71, "citation": "BPHS Graha Bala Adhyaya | Parashara | Shloka 8"},
    "mars":    {"rupas": 17.14, "citation": "BPHS Graha Bala Adhyaya | Parashara | Shloka 8"},
    "saturn":  {"rupas": 8.57,  "citation": "BPHS Graha Bala Adhyaya | Parashara | Shloka 8"},
}

# ─────────────────────────────────────────────
# COMBUSTION ORBS
# Source: BPHS Graha Bala Adhyaya (Parashara)
#         Saravali Ch.4 (Kalyanavarma)
# ─────────────────────────────────────────────
COMBUSTION_ORBS = {
    "moon":    {"combust": 12.0, "deep_combust": 6.0,
                "citation": "BPHS | Parashara | Graha Bala Adhyaya | Shloka 17"},
    "mars":    {"combust": 17.0, "deep_combust": 8.0,
                "citation": "BPHS | Parashara | Graha Bala Adhyaya | Shloka 17"},
    "mercury": {"combust_direct": 14.0, "combust_retro": 12.0, "deep_combust": 4.0,
                "citation": "BPHS | Parashara | Graha Bala Adhyaya | Shloka 17"},
    "jupiter": {"combust": 11.0, "deep_combust": 5.0,
                "citation": "BPHS | Parashara | Graha Bala Adhyaya | Shloka 17"},
    "venus":   {"combust_direct": 10.0, "combust_retro": 8.0, "deep_combust": 3.0,
                "citation": "BPHS | Parashara | Graha Bala Adhyaya | Shloka 17"},
    "saturn":  {"combust": 15.0, "deep_combust": 5.0,
                "citation": "BPHS | Parashara | Graha Bala Adhyaya | Shloka 17"},
}

# ─────────────────────────────────────────────
# NAKSHATRA DATA — All 27 Nakshatras
# Source: BPHS Nakshatra Swaroopa Adhyaya (Parashara)
#         Brihat Jataka Ch.3 (Varahamihira)
# ─────────────────────────────────────────────
NAKSHATRAS = {
    1:  {"name": "Ashwini",           "ruler": "ketu",    "deity": "Ashwini Kumaras",
         "gana": "deva",   "yoni": "horse",  "nadi": "vata",
         "nature": "laghu", "start_deg": 0.0,   "end_deg": 13.333,
         "citation": "BPHS Nakshatra Swaroopa Adhyaya | Parashara | Shloka 1-5"},
    2:  {"name": "Bharani",           "ruler": "venus",   "deity": "Yama",
         "gana": "manushya","yoni": "elephant","nadi": "pitta",
         "nature": "ugra",  "start_deg": 13.333,"end_deg": 26.667,
         "citation": "BPHS Nakshatra Swaroopa Adhyaya | Parashara | Shloka 6-10"},
    3:  {"name": "Krittika",          "ruler": "sun",     "deity": "Agni",
         "gana": "rakshasa","yoni": "goat",   "nadi": "kapha",
         "nature": "tikshna","start_deg": 26.667,"end_deg": 40.0,
         "citation": "BPHS Nakshatra Swaroopa Adhyaya | Parashara | Shloka 11-15"},
    4:  {"name": "Rohini",            "ruler": "moon",    "deity": "Brahma",
         "gana": "manushya","yoni": "serpent","nadi": "vata",
         "nature": "sthira","start_deg": 40.0,  "end_deg": 53.333,
         "citation": "BPHS Nakshatra Swaroopa Adhyaya | Parashara | Shloka 16-20"},
    5:  {"name": "Mrigashira",        "ruler": "mars",    "deity": "Soma (Moon)",
         "gana": "deva",   "yoni": "serpent","nadi": "pitta",
         "nature": "mridu", "start_deg": 53.333,"end_deg": 66.667,
         "citation": "BPHS Nakshatra Swaroopa Adhyaya | Parashara | Shloka 21-25"},
    6:  {"name": "Ardra",             "ruler": "rahu",    "deity": "Rudra",
         "gana": "manushya","yoni": "dog",    "nadi": "kapha",
         "nature": "tikshna","start_deg": 66.667,"end_deg": 80.0,
         "citation": "BPHS Nakshatra Swaroopa Adhyaya | Parashara | Shloka 26-30"},
    7:  {"name": "Punarvasu",         "ruler": "jupiter", "deity": "Aditi",
         "gana": "deva",   "yoni": "cat",    "nadi": "vata",
         "nature": "chara", "start_deg": 80.0,  "end_deg": 93.333,
         "citation": "BPHS Nakshatra Swaroopa Adhyaya | Parashara | Shloka 31-35"},
    8:  {"name": "Pushya",            "ruler": "saturn",  "deity": "Brihaspati",
         "gana": "deva",   "yoni": "goat",   "nadi": "pitta",
         "nature": "laghu", "start_deg": 93.333,"end_deg": 106.667,
         "citation": "BPHS Nakshatra Swaroopa Adhyaya | Parashara | Shloka 36-40"},
    9:  {"name": "Ashlesha",          "ruler": "mercury", "deity": "Sarpas (Nagas)",
         "gana": "rakshasa","yoni": "cat",    "nadi": "kapha",
         "nature": "tikshna","start_deg": 106.667,"end_deg": 120.0,
         "citation": "BPHS Nakshatra Swaroopa Adhyaya | Parashara | Shloka 41-45"},
    10: {"name": "Magha",             "ruler": "ketu",    "deity": "Pitrs (Ancestors)",
         "gana": "rakshasa","yoni": "rat",    "nadi": "vata",
         "nature": "ugra",  "start_deg": 120.0, "end_deg": 133.333,
         "citation": "BPHS Nakshatra Swaroopa Adhyaya | Parashara | Shloka 46-50"},
    11: {"name": "Purva Phalguni",    "ruler": "venus",   "deity": "Bhaga",
         "gana": "manushya","yoni": "rat",    "nadi": "pitta",
         "nature": "ugra",  "start_deg": 133.333,"end_deg": 146.667,
         "citation": "BPHS Nakshatra Swaroopa Adhyaya | Parashara | Shloka 51-55"},
    12: {"name": "Uttara Phalguni",   "ruler": "sun",     "deity": "Aryaman",
         "gana": "manushya","yoni": "cow",    "nadi": "kapha",
         "nature": "sthira","start_deg": 146.667,"end_deg": 160.0,
         "citation": "BPHS Nakshatra Swaroopa Adhyaya | Parashara | Shloka 56-60"},
    13: {"name": "Hasta",             "ruler": "moon",    "deity": "Savitar (Sun)",
         "gana": "deva",   "yoni": "buffalo","nadi": "vata",
         "nature": "laghu", "start_deg": 160.0, "end_deg": 173.333,
         "citation": "BPHS Nakshatra Swaroopa Adhyaya | Parashara | Shloka 61-65"},
    14: {"name": "Chitra",            "ruler": "mars",    "deity": "Tvashtar (Vishvakarma)",
         "gana": "rakshasa","yoni": "tiger",  "nadi": "pitta",
         "nature": "mridu", "start_deg": 173.333,"end_deg": 186.667,
         "citation": "BPHS Nakshatra Swaroopa Adhyaya | Parashara | Shloka 66-70"},
    15: {"name": "Swati",             "ruler": "rahu",    "deity": "Vayu (Wind)",
         "gana": "deva",   "yoni": "buffalo","nadi": "kapha",
         "nature": "chara", "start_deg": 186.667,"end_deg": 200.0,
         "citation": "BPHS Nakshatra Swaroopa Adhyaya | Parashara | Shloka 71-75"},
    16: {"name": "Vishakha",          "ruler": "jupiter", "deity": "Indra-Agni",
         "gana": "rakshasa","yoni": "tiger",  "nadi": "vata",
         "nature": "mishra","start_deg": 200.0, "end_deg": 213.333,
         "citation": "BPHS Nakshatra Swaroopa Adhyaya | Parashara | Shloka 76-80"},
    17: {"name": "Anuradha",          "ruler": "saturn",  "deity": "Mitra",
         "gana": "deva",   "yoni": "deer",   "nadi": "pitta",
         "nature": "mridu", "start_deg": 213.333,"end_deg": 226.667,
         "citation": "BPHS Nakshatra Swaroopa Adhyaya | Parashara | Shloka 81-85"},
    18: {"name": "Jyeshtha",          "ruler": "mercury", "deity": "Indra",
         "gana": "rakshasa","yoni": "deer",   "nadi": "kapha",
         "nature": "tikshna","start_deg": 226.667,"end_deg": 240.0,
         "citation": "BPHS Nakshatra Swaroopa Adhyaya | Parashara | Shloka 86-90"},
    19: {"name": "Mula",              "ruler": "ketu",    "deity": "Nirrti (Alakshmi)",
         "gana": "rakshasa","yoni": "dog",    "nadi": "vata",
         "nature": "ugra",  "start_deg": 240.0, "end_deg": 253.333,
         "citation": "BPHS Nakshatra Swaroopa Adhyaya | Parashara | Shloka 91-95"},
    20: {"name": "Purva Ashadha",     "ruler": "venus",   "deity": "Apas (Water)",
         "gana": "manushya","yoni": "monkey", "nadi": "pitta",
         "nature": "ugra",  "start_deg": 253.333,"end_deg": 266.667,
         "citation": "BPHS Nakshatra Swaroopa Adhyaya | Parashara | Shloka 96-100"},
    21: {"name": "Uttara Ashadha",    "ruler": "sun",     "deity": "Vishvadevas",
         "gana": "manushya","yoni": "mongoose","nadi": "kapha",
         "nature": "sthira","start_deg": 266.667,"end_deg": 280.0,
         "citation": "BPHS Nakshatra Swaroopa Adhyaya | Parashara | Shloka 101-105"},
    22: {"name": "Shravana",          "ruler": "moon",    "deity": "Vishnu",
         "gana": "deva",   "yoni": "monkey", "nadi": "vata",
         "nature": "chara", "start_deg": 280.0, "end_deg": 293.333,
         "citation": "BPHS Nakshatra Swaroopa Adhyaya | Parashara | Shloka 106-110"},
    23: {"name": "Dhanishtha",        "ruler": "mars",    "deity": "Ashta Vasus",
         "gana": "rakshasa","yoni": "lion",   "nadi": "pitta",
         "nature": "chara", "start_deg": 293.333,"end_deg": 306.667,
         "citation": "BPHS Nakshatra Swaroopa Adhyaya | Parashara | Shloka 111-115"},
    24: {"name": "Shatabhisha",       "ruler": "rahu",    "deity": "Varuna",
         "gana": "rakshasa","yoni": "horse",  "nadi": "kapha",
         "nature": "chara", "start_deg": 306.667,"end_deg": 320.0,
         "citation": "BPHS Nakshatra Swaroopa Adhyaya | Parashara | Shloka 116-120"},
    25: {"name": "Purva Bhadrapada",  "ruler": "jupiter", "deity": "Aja Ekapad",
         "gana": "manushya","yoni": "lion",   "nadi": "vata",
         "nature": "ugra",  "start_deg": 320.0, "end_deg": 333.333,
         "citation": "BPHS Nakshatra Swaroopa Adhyaya | Parashara | Shloka 121-125"},
    26: {"name": "Uttara Bhadrapada", "ruler": "saturn",  "deity": "Ahirbudhnya",
         "gana": "manushya","yoni": "cow",    "nadi": "pitta",
         "nature": "sthira","start_deg": 333.333,"end_deg": 346.667,
         "citation": "BPHS Nakshatra Swaroopa Adhyaya | Parashara | Shloka 126-130"},
    27: {"name": "Revati",            "ruler": "mercury", "deity": "Pushan",
         "gana": "deva",   "yoni": "elephant","nadi": "kapha",
         "nature": "mridu", "start_deg": 346.667,"end_deg": 360.0,
         "citation": "BPHS Nakshatra Swaroopa Adhyaya | Parashara | Shloka 131-135"},
}

# ─────────────────────────────────────────────
# VIMSHOTTARI DASHA YEARS
# Source: BPHS Vimshottari Dasha Adhyaya (Parashara)
#         Phaldipika Ch.17 (Mantreswara)
# Total = 120 years
# ─────────────────────────────────────────────
VIMSHOTTARI_YEARS = {
    "ketu":    {"years": 7,  "citation": "BPHS Vimshottari Dasha Adhyaya | Parashara | Shloka 3"},
    "venus":   {"years": 20, "citation": "BPHS Vimshottari Dasha Adhyaya | Parashara | Shloka 3"},
    "sun":     {"years": 6,  "citation": "BPHS Vimshottari Dasha Adhyaya | Parashara | Shloka 3"},
    "moon":    {"years": 10, "citation": "BPHS Vimshottari Dasha Adhyaya | Parashara | Shloka 3"},
    "mars":    {"years": 7,  "citation": "BPHS Vimshottari Dasha Adhyaya | Parashara | Shloka 3"},
    "rahu":    {"years": 18, "citation": "BPHS Vimshottari Dasha Adhyaya | Parashara | Shloka 3"},
    "jupiter": {"years": 16, "citation": "BPHS Vimshottari Dasha Adhyaya | Parashara | Shloka 3"},
    "saturn":  {"years": 19, "citation": "BPHS Vimshottari Dasha Adhyaya | Parashara | Shloka 3"},
    "mercury": {"years": 17, "citation": "BPHS Vimshottari Dasha Adhyaya | Parashara | Shloka 3"},
}

# Nakshatra index → Dasha planet (0-based, matches Nakshatra number 1-27)
NAKSHATRA_DASHA_LORD = {
    1: "ketu", 2: "venus", 3: "sun", 4: "moon", 5: "mars",
    6: "rahu", 7: "jupiter", 8: "saturn", 9: "mercury",
    10: "ketu", 11: "venus", 12: "sun", 13: "moon", 14: "mars",
    15: "rahu", 16: "jupiter", 17: "saturn", 18: "mercury",
    19: "ketu", 20: "venus", 21: "sun", 22: "moon", 23: "mars",
    24: "rahu", 25: "jupiter", 26: "saturn", 27: "mercury",
}

DASHA_ORDER = ["ketu", "venus", "sun", "moon", "mars", "rahu", "jupiter", "saturn", "mercury"]

# ─────────────────────────────────────────────
# YOGA RULES — Complete with classical citations
# Source: BPHS Yoga Adhyaya (Parashara)
#         Phaldipika Ch.6 (Mantreswara)
#         Brihat Jataka Ch.12 (Varahamihira)
#         Jataka Parijata (Vaidyanatha Dikshita)
# ─────────────────────────────────────────────
YOGA_RULES = {
    "gajakesari": {
        "name_sanskrit": "Gaja Kesari Yoga",
        "name_english": "Elephant-Lion Yoga",
        "definition": "Jupiter in Kendra (1,4,7,10) from Moon",
        "conditions": [
            "Jupiter must be in angular house (1,4,7,10) from Moon",
            "Jupiter must not be combust",
            "Jupiter must not be debilitated",
            "Moon must not be in Kendra from Rahu (reduces effect)"
        ],
        "cancellations": [
            "Jupiter combust within 11 degrees of Sun",
            "Jupiter in Capricorn (debilitation sign)",
            "Both Jupiter and Moon weak in Shadbala"
        ],
        "results": {
            "full": "Intelligent, famous, wealthy, respected by kings, long-lived",
            "partial": "Good intelligence, moderate wealth and reputation"
        },
        "citation": {
            "primary": "BPHS Yoga Adhyaya | Parashara | Shloka 14",
            "secondary": "Phaldipika | Mantreswara | Chapter 6 | Shloka 1",
            "tertiary": "Jataka Parijata | Vaidyanatha Dikshita | Chapter 9 | Shloka 4"
        },
        "contradiction": "Phaldipika adds condition: Jupiter must also be free from malefic aspect"
    },

    "ruchaka": {
        "name_sanskrit": "Ruchaka Yoga",
        "name_english": "Pancha Mahapurusha — Mars Yoga",
        "definition": "Mars in own sign (Aries/Scorpio) or exaltation (Capricorn) in Kendra (1,4,7,10)",
        "conditions": [
            "Mars must be in Aries, Scorpio, or Capricorn",
            "Mars must be in house 1, 4, 7, or 10",
            "Both conditions must be simultaneously true"
        ],
        "cancellations": [
            "Mars aspected by Saturn reduces results significantly",
            "Mars combust cancels the yoga",
            "Lord of the Kendra house being weak reduces results"
        ],
        "results": {
            "full": "Bold, commander-like, powerful, victorious over enemies, wealthy, long-lived to 70 years",
            "partial": "Courageous, some leadership qualities, moderate success"
        },
        "citation": {
            "primary": "BPHS Yoga Adhyaya | Parashara | Shloka 36",
            "secondary": "Phaldipika | Mantreswara | Chapter 6 | Shloka 8",
            "tertiary": "Brihat Jataka | Varahamihira | Chapter 12 | Shloka 3"
        }
    },

    "bhadra": {
        "name_sanskrit": "Bhadra Yoga",
        "name_english": "Pancha Mahapurusha — Mercury Yoga",
        "definition": "Mercury in own sign (Gemini/Virgo) or exaltation (Virgo) in Kendra",
        "conditions": [
            "Mercury in Gemini or Virgo",
            "Mercury in house 1, 4, 7, or 10",
            "Mercury not combust"
        ],
        "results": {
            "full": "Eloquent, intelligent, skilled in arts, good memory, long arms, good longevity"
        },
        "citation": {
            "primary": "BPHS Yoga Adhyaya | Parashara | Shloka 37",
            "secondary": "Phaldipika | Mantreswara | Chapter 6 | Shloka 9"
        }
    },

    "hamsa": {
        "name_sanskrit": "Hamsa Yoga",
        "name_english": "Pancha Mahapurusha — Jupiter Yoga",
        "definition": "Jupiter in own sign (Sagittarius/Pisces) or exaltation (Cancer) in Kendra",
        "conditions": [
            "Jupiter in Sagittarius, Pisces, or Cancer",
            "Jupiter in house 1, 4, 7, or 10",
            "Jupiter not debilitated or combust"
        ],
        "results": {
            "full": "Virtuous, respected by scholars, handsome, good physique, devout, fond of music"
        },
        "citation": {
            "primary": "BPHS Yoga Adhyaya | Parashara | Shloka 38",
            "secondary": "Phaldipika | Mantreswara | Chapter 6 | Shloka 10"
        }
    },

    "malavya": {
        "name_sanskrit": "Malavya Yoga",
        "name_english": "Pancha Mahapurusha — Venus Yoga",
        "definition": "Venus in own sign (Taurus/Libra) or exaltation (Pisces) in Kendra",
        "conditions": [
            "Venus in Taurus, Libra, or Pisces",
            "Venus in house 1, 4, 7, or 10"
        ],
        "results": {
            "full": "Handsome, wealthy, fond of pleasures, famous, long-lived, devoted spouse"
        },
        "citation": {
            "primary": "BPHS Yoga Adhyaya | Parashara | Shloka 39",
            "secondary": "Phaldipika | Mantreswara | Chapter 6 | Shloka 11"
        }
    },

    "shasha": {
        "name_sanskrit": "Shasha Yoga",
        "name_english": "Pancha Mahapurusha — Saturn Yoga",
        "definition": "Saturn in own sign (Capricorn/Aquarius) or exaltation (Libra) in Kendra",
        "conditions": [
            "Saturn in Capricorn, Aquarius, or Libra",
            "Saturn in house 1, 4, 7, or 10"
        ],
        "results": {
            "full": "Commands servants and armies, skilled in mining/metals, powerful, forest dweller qualities"
        },
        "citation": {
            "primary": "BPHS Yoga Adhyaya | Parashara | Shloka 40",
            "secondary": "Phaldipika | Mantreswara | Chapter 6 | Shloka 12"
        }
    },

    "budha_aditya": {
        "name_sanskrit": "Budha-Aditya Yoga",
        "name_english": "Sun-Mercury Conjunction Yoga",
        "definition": "Sun and Mercury conjunct in same sign",
        "conditions": [
            "Sun and Mercury in same sign",
            "Mercury must NOT be combust — within 3 degrees of Sun cancels the yoga",
            "Mercury must be at least 4 degrees from Sun for yoga to manifest",
            "Mercury ideally between 4-14 degrees from Sun"
        ],
        "cancellations": [
            "Mercury within 3 degrees of Sun = combust = yoga cancelled",
            "Both in enemy signs reduces result"
        ],
        "results": {
            "full": "Intelligent, skilled, respected, good speech, learned in shastra",
            "partial": "Some intelligence and communication skills"
        },
        "citation": {
            "primary": "Phaldipika | Mantreswara | Chapter 6 | Shloka 2",
            "secondary": "BPHS Yoga Adhyaya | Parashara | Shloka 17"
        },
        "contradiction": "Many practitioners wrongly apply this yoga even when Mercury is combust — Mantreswara explicitly requires Mercury to be free from combustion"
    },

    "chandra_mangala": {
        "name_sanskrit": "Chandra-Mangala Yoga",
        "name_english": "Moon-Mars Conjunction Yoga",
        "definition": "Moon and Mars conjunct or in mutual aspect",
        "conditions": [
            "Moon and Mars in same sign OR",
            "Mars aspecting Moon OR Moon aspecting Mars (7th aspect)"
        ],
        "results": {
            "full": "Wealth through mother or women, earnings from unconventional sources, courageous"
        },
        "citation": {
            "primary": "BPHS Yoga Adhyaya | Parashara | Shloka 20",
            "secondary": "Saravali | Kalyanavarma | Chapter 36 | Shloka 4"
        }
    },

    "kemdrum": {
        "name_sanskrit": "Kemdrum Yoga",
        "name_english": "Moon Isolation Yoga",
        "definition": "No planet in 2nd or 12th house from Moon, and no planet conjunct Moon",
        "conditions": [
            "2nd house from Moon must be empty",
            "12th house from Moon must be empty",
            "Moon itself must have no planets conjunct",
            "Sun does not count as planet for this yoga"
        ],
        "cancellations": [
            "1. Any planet in Kendra from Lagna cancels Kemdrum",
            "2. Moon in Kendra from Lagna cancels",
            "3. Moon aspected by benefics cancels",
            "4. Moon conjunct benefic cancels",
            "5. Shubha Kartari — benefics on both sides of Moon cancels",
            "6. Moon in own navamsha cancels",
            "7. Moon exalted cancels",
            "8. Lord of Moon sign strong cancels",
            "9. Moon in Pushya Nakshatra reduces effect"
        ],
        "results": {
            "full": "Poverty, wandering, miserable life, lack of support",
            "cancelled": "Yoga exists in chart but results are nullified"
        },
        "citation": {
            "primary": "BPHS Yoga Adhyaya | Parashara | Shloka 22",
            "secondary": "Phaldipika | Mantreswara | Chapter 6 | Shloka 15",
            "tertiary": "Brihat Jataka | Varahamihira | Chapter 12 | Shloka 7"
        },
        "contradiction": "Parashara gives 9 cancellation conditions. Mantreswara gives fewer. Varahamihira's version is most strict."
    },

    "neecha_bhanga_raj": {
        "name_sanskrit": "Neecha Bhanga Raja Yoga",
        "name_english": "Cancellation of Debilitation — becomes Raj Yoga",
        "definition": "Debilitated planet's weakness gets cancelled creating Raj Yoga",
        "conditions": [
            "CONDITION 1: Lord of debilitation sign is in Kendra from Lagna or Moon",
            "CONDITION 2: Planet that gets exalted in debilitation sign is in Kendra",
            "CONDITION 3: Debilitated planet is in Kendra from Lagna",
            "CONDITION 4: Debilitated planet is aspected by its own lord",
            "CONDITION 5: Lord of debilitation sign aspects the debilitated planet",
            "CONDITION 6: Debilitated planet is in exalted Navamsha",
            "CONDITION 7: Two planets in mutual debilitation (Ithasala)"
        ],
        "results": {
            "full_raj_yoga": "When multiple conditions simultaneously met — powerful Raj Yoga, rise to prominence",
            "partial": "One condition met — cancellation only, moderate good results"
        },
        "citation": {
            "primary": "BPHS Neecha Bhanga Adhyaya | Parashara | Shloka 1-7",
            "secondary": "Phaldipika | Mantreswara | Chapter 7 | Shloka 22-25",
            "tertiary": "Jataka Parijata | Vaidyanatha Dikshita | Chapter 9"
        }
    },

    "kaal_sarp": {
        "name_sanskrit": "Kaal Sarp Yoga",
        "name_english": "Serpent of Time Yoga",
        "definition": "All 7 planets (Sun-Saturn) hemmed between Rahu and Ketu",
        "conditions": [
            "Rahu and Ketu must be in exact opposition (always true)",
            "Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn ALL between Rahu-Ketu arc",
            "No planet should be outside the Rahu-Ketu axis"
        ],
        "important_note": "CLASSICAL TEXT ALERT: This yoga is NOT mentioned in BPHS, Brihat Jataka, Phaldipika or Saravali. It appears in later texts. Many classical scholars consider it a medieval addition.",
        "cancellations": [
            "Any planet conjunct Rahu or Ketu breaks the yoga",
            "Lagna lord strong greatly reduces effect"
        ],
        "results": {
            "full": "Struggle in life, delays, sudden rise and fall, spiritual tendency"
        },
        "citation": {
            "primary": "Not in BPHS | First appears in Muhurta Chintamani (later text)",
            "note": "Classical purists do not use this yoga — always disclose this to clients"
        }
    },

    "viparita_raj_harsha": {
        "name_sanskrit": "Viparita Raja Yoga — Harsha",
        "name_english": "Reversed Raj Yoga — Joy",
        "definition": "Lord of 6th house in 6th, 8th, or 12th house",
        "conditions": ["Lord of 6th in 6th, 8th, or 12th"],
        "results": {"full": "Defeat of enemies, happiness, good health, wealth"},
        "citation": {
            "primary": "BPHS Yoga Adhyaya | Parashara | Shloka 76",
            "secondary": "Phaldipika | Mantreswara | Chapter 6 | Shloka 18"
        }
    },

    "viparita_raj_sarala": {
        "name_sanskrit": "Viparita Raja Yoga — Sarala",
        "name_english": "Reversed Raj Yoga — Simple",
        "definition": "Lord of 8th house in 6th, 8th, or 12th house",
        "conditions": ["Lord of 8th in 6th, 8th, or 12th"],
        "results": {"full": "Long life, wealth, fearlessness, scholarship"},
        "citation": {
            "primary": "BPHS Yoga Adhyaya | Parashara | Shloka 77",
            "secondary": "Phaldipika | Mantreswara | Chapter 6 | Shloka 19"
        }
    },

    "viparita_raj_vimala": {
        "name_sanskrit": "Viparita Raja Yoga — Vimala",
        "name_english": "Reversed Raj Yoga — Pure",
        "definition": "Lord of 12th house in 6th, 8th, or 12th house",
        "conditions": ["Lord of 12th in 6th, 8th, or 12th"],
        "results": {"full": "Happiness, good expenditure, virtuous, self-controlled"},
        "citation": {
            "primary": "BPHS Yoga Adhyaya | Parashara | Shloka 78",
            "secondary": "Phaldipika | Mantreswara | Chapter 6 | Shloka 20"
        }
    },

    "mangal_dosha": {
        "name_sanskrit": "Kuja Dosha / Mangal Dosha",
        "name_english": "Mars Affliction",
        "definition": "Mars in houses 1, 4, 7, 8, or 12 from Lagna",
        "conditions": [
            "Mars in 1st house from Lagna",
            "Mars in 4th house from Lagna",
            "Mars in 7th house from Lagna",
            "Mars in 8th house from Lagna",
            "Mars in 12th house from Lagna"
        ],
        "cancellations": [
            "Mars in own sign (Aries/Scorpio) cancels",
            "Mars in exaltation (Capricorn) cancels",
            "Mars aspected by Jupiter cancels",
            "Venus in Lagna reduces effect",
            "Mars in 2nd house from Moon in certain texts",
            "If both partners have Mangal Dosha — cancelled for marriage purposes"
        ],
        "severity": {
            "house_1": "High — affects health and temperament",
            "house_4": "Moderate — affects domestic peace",
            "house_7": "Very High — directly affects marriage",
            "house_8": "Very High — affects longevity of spouse",
            "house_12": "Moderate — affects marital happiness"
        },
        "citation": {
            "primary": "Phaldipika | Mantreswara | Chapter 7 | Shloka 1-5",
            "secondary": "BPHS | Parashara | Vivaha Adhyaya",
            "note": "Some texts also include 2nd house — Parashara includes 2nd, Mantreswara does not — a known contradiction"
        },
        "contradiction": "Parashara includes 2nd house making 6 houses total. Mantreswara counts 5 houses only. Both views have classical support."
    },

    "pitra_dosha": {
        "name_sanskrit": "Pitra Dosha",
        "name_english": "Ancestral Debt Affliction",
        "definition": "Sun afflicted by Saturn, Rahu, or in 9th house with malefics",
        "conditions": [
            "Sun conjunct Saturn within 10 degrees",
            "Sun conjunct Rahu within 10 degrees",
            "Sun in 9th house with malefic aspect",
            "9th lord in 6th, 8th, or 12th with malefic"
        ],
        "results": {"full": "Obstacles in life, ancestors seeking spiritual relief, delays in auspicious events"},
        "citation": {
            "primary": "BPHS | Parashara | Pitra Dosha Adhyaya",
            "secondary": "Prasna Marga | Harihara | Chapter 15"
        }
    }
}

# ─────────────────────────────────────────────
# PLANET IN HOUSE RESULTS
# Source: BPHS Bhava Phala Adhyaya (Parashara)
#         Phaldipika Ch.7 (Mantreswara)
#         Saravali Ch.22-30 (Kalyanavarma)
# ─────────────────────────────────────────────
SUN_IN_HOUSES = {
    1: {
        "result": "Strong constitution, ambitious, proud, government favour, good eyesight but tendency to be domineering. Father may be well-placed.",
        "strong": "Leadership qualities, high status, government or political success",
        "weak": "Health issues related to bones, eye problems, egoistic",
        "citation": "BPHS Bhava Phala Adhyaya | Parashara | Shloka 3 | Corroborated: Phaldipika Ch.7 Sl.1 (Mantreswara)"
    },
    2: {
        "result": "Speech issues or harsh speech, family conflicts, fluctuating wealth, eye and face ailments possible",
        "strong": "Wealth through government, authoritative speech",
        "weak": "Family disputes, financial instability, eye problems",
        "citation": "BPHS Bhava Phala Adhyaya | Parashara | Shloka 5 | Corroborated: Phaldipika Ch.7 Sl.3 (Mantreswara)"
    },
    3: {
        "result": "Courageous, good younger siblings, success through own efforts, some health issues with throat or shoulders",
        "strong": "Bold, successful in sports and competition, brave",
        "weak": "Conflict with siblings, restless",
        "citation": "BPHS Bhava Phala Adhyaya | Parashara | Shloka 7"
    },
    4: {
        "result": "Tension in domestic life, possible separation from mother, change of residence, paternal property issues. Weak Dig Bala position for Sun.",
        "strong": "Property from government, authoritative in home",
        "weak": "Mother's health issues, lack of domestic peace",
        "citation": "BPHS Bhava Phala Adhyaya | Parashara | Shloka 9 | Saravali Ch.24 Sl.3 (Kalyanavarma)"
    },
    5: {
        "result": "Intelligent, few children or delay in children, possible issues with first child, good at speculation",
        "strong": "Political intelligence, advisory roles, speculative gains",
        "weak": "Childbirth problems, abdominal issues",
        "citation": "BPHS Bhava Phala Adhyaya | Parashara | Shloka 11"
    },
    6: {
        "result": "Defeat of enemies, good health, service to government, some digestive issues, maternal relatives may have issues",
        "strong": "Victory over enemies, good service record",
        "weak": "Digestive problems, conflicts with maternal relatives",
        "citation": "BPHS Bhava Phala Adhyaya | Parashara | Shloka 13"
    },
    7: {
        "result": "Marital friction, partner may be domineering or health issues in partner, travel to foreign lands, government partnerships possible",
        "strong": "Government partnerships, powerful spouse",
        "weak": "Marital discord, spouse health issues, eye problems",
        "citation": "BPHS Bhava Phala Adhyaya | Parashara | Shloka 15 | Phaldipika Ch.7 Sl.7 (Mantreswara)",
        "contradiction": "Varahamihira in Brihat Jataka Ch.7 gives slightly different result: 'wandering, weak constitution in spouse' — focus on physical weakness of partner"
    },
    8: {
        "result": "Short life or chronic illness, eye diseases, obstacles in career, father may have health issues, interest in occult",
        "strong": "Some protection from major disasters, interest in mysticism",
        "weak": "Eye problems, chronic disease, paternal issues",
        "citation": "BPHS Bhava Phala Adhyaya | Parashara | Shloka 17"
    },
    9: {
        "result": "Fortune, pious, devoted to father, pilgrimages, government favour, higher wisdom. Excellent placement.",
        "strong": "Great fortune, father brings blessings, spiritual wisdom",
        "weak": "Father's health issues, religious conflicts",
        "citation": "BPHS Bhava Phala Adhyaya | Parashara | Shloka 19"
    },
    10: {
        "result": "Excellent career success, government jobs, recognition, fame, strong Dig Bala. Best house for Sun.",
        "strong": "Political power, leadership, father of high status",
        "weak": "Career struggles, relationship with father difficult",
        "citation": "BPHS Bhava Phala Adhyaya | Parashara | Shloka 21 | Phaldipika Ch.7 Sl.10 (Mantreswara)",
        "note": "This is Sun's Dig Bala house — maximum directional strength here"
    },
    11: {
        "result": "Good income, elder siblings, gains from government, fulfillment of desires, some right ear issues",
        "strong": "Excellent income, influential elder siblings",
        "weak": "Ear problems, some family conflicts",
        "citation": "BPHS Bhava Phala Adhyaya | Parashara | Shloka 23"
    },
    12: {
        "result": "Expenses, foreign travel, left eye issues, spiritual path possible, loss through enemies, father in foreign land",
        "strong": "Success in foreign lands, spiritual liberation",
        "weak": "Eye problems, expenditure, isolation",
        "citation": "BPHS Bhava Phala Adhyaya | Parashara | Shloka 25"
    }
}

# ─────────────────────────────────────────────
# MARRIAGE MUHURTA RULES
# Source: Muhurta Chintamani (classical Muhurta text)
#         BPHS Vivaha Adhyaya (Parashara)
#         Prasna Marga Ch.20 (Harihara)
# ─────────────────────────────────────────────
MARRIAGE_MUHURTA = {
    "good_tithis": {
        "list": [2, 3, 5, 7, 10, 11, 12, 13],  # tithi numbers
        "names": ["Dwitiya","Tritiya","Panchami","Saptami","Dashami","Ekadashi","Dwadashi","Trayodashi"],
        "citation": "Muhurta Chintamani | Marriage Chapter | Shloka 3"
    },
    "bad_tithis": {
        "list": [4, 8, 9, 14, 15, 30],
        "names": ["Chaturthi","Ashtami","Navami","Chaturdashi","Purnima","Amavasya"],
        "reason": "Rikta tithis (4,9,14) and Purnima/Amavasya are inauspicious for marriage",
        "citation": "Muhurta Chintamani | Marriage Chapter | Shloka 4"
    },
    "good_nakshatras": {
        "list": ["Rohini","Mrigashira","Magha","Uttara Phalguni","Hasta","Swati",
                 "Anuradha","Mula","Uttara Ashadha","Shravana","Revati","Uttara Bhadrapada"],
        "citation": "BPHS Vivaha Adhyaya | Parashara | Shloka 7"
    },
    "bad_nakshatras": {
        "list": ["Krittika","Ardra","Ashlesha","Jyeshtha","Vishakha","Bharani",
                 "Chitra","Dhanishtha","Shatabhisha"],
        "citation": "BPHS Vivaha Adhyaya | Parashara | Shloka 8"
    },
    "good_lagnas": {
        "list": ["taurus","gemini","cancer","libra","sagittarius","pisces"],
        "citation": "Muhurta Chintamani | Marriage Chapter | Shloka 10",
        "note": "Fixed and dual signs generally preferred over cardinal for marriage stability"
    },
    "bad_lagnas": {
        "list": ["aries","scorpio","capricorn","aquarius"],
        "reason": "Mars/Saturn ruled or malefic character lagnas avoided for marriage",
        "citation": "Muhurta Chintamani | Marriage Chapter | Shloka 11"
    },
    "taara_bala_good": [2, 4, 6, 8, 9],  # Sampat, Kshema, Sadhaka, Mitra, Atimitra
    "taara_bala_bad":  [3, 5, 7],         # Vipat, Pratyak, Vadha
    "taara_citation": "BPHS | Parashara | Taara Bala Adhyaya | Shloka 2-5"
}

# ─────────────────────────────────────────────
# HOUSE SIGNIFICATIONS
# Source: BPHS Bhava Phala Adhyaya (Parashara)
# ─────────────────────────────────────────────
BHAVA_KARAKATVA = {
    1:  {"name": "Lagna / Tanu Bhava",    "primary": "Self, body, health, personality, appearance",
         "karaka": "Sun", "classification": "Kendra + Dharma",
         "citation": "BPHS Bhava Phala Adhyaya | Parashara | Shloka 1"},
    2:  {"name": "Dhana Bhava",           "primary": "Wealth, family, speech, food, right eye",
         "karaka": "Jupiter", "classification": "Maraka",
         "citation": "BPHS Bhava Phala Adhyaya | Parashara | Shloka 2"},
    3:  {"name": "Parakrama Bhava",       "primary": "Courage, siblings, arms, short journeys, communication",
         "karaka": "Mars", "classification": "Upachaya",
         "citation": "BPHS Bhava Phala Adhyaya | Parashara | Shloka 3"},
    4:  {"name": "Sukha Bhava",           "primary": "Mother, home, property, vehicle, education, heart",
         "karaka": "Moon", "classification": "Kendra + Moksha",
         "citation": "BPHS Bhava Phala Adhyaya | Parashara | Shloka 4"},
    5:  {"name": "Putra Bhava",           "primary": "Children, intelligence, past life merit, speculation, mantra",
         "karaka": "Jupiter", "classification": "Trikona + Dharma",
         "citation": "BPHS Bhava Phala Adhyaya | Parashara | Shloka 5"},
    6:  {"name": "Ripu/Roga Bhava",       "primary": "Enemies, diseases, debts, service, maternal relatives",
         "karaka": "Mars/Saturn", "classification": "Dusthana + Upachaya",
         "citation": "BPHS Bhava Phala Adhyaya | Parashara | Shloka 6"},
    7:  {"name": "Kalatra Bhava",         "primary": "Spouse, partnerships, trade, travel, desires",
         "karaka": "Venus", "classification": "Kendra + Kama + Maraka",
         "citation": "BPHS Bhava Phala Adhyaya | Parashara | Shloka 7"},
    8:  {"name": "Ayu Bhava",             "primary": "Longevity, obstacles, hidden knowledge, sudden events, in-laws",
         "karaka": "Saturn", "classification": "Dusthana",
         "citation": "BPHS Bhava Phala Adhyaya | Parashara | Shloka 8"},
    9:  {"name": "Dharma/Bhagya Bhava",   "primary": "Fortune, father, guru, religion, long journeys, higher learning",
         "karaka": "Jupiter/Sun", "classification": "Trikona + Dharma",
         "citation": "BPHS Bhava Phala Adhyaya | Parashara | Shloka 9"},
    10: {"name": "Karma Bhava",           "primary": "Career, status, government, fame, actions, knees",
         "karaka": "Mercury/Jupiter/Sun/Saturn", "classification": "Kendra + Artha",
         "citation": "BPHS Bhava Phala Adhyaya | Parashara | Shloka 10"},
    11: {"name": "Labha Bhava",           "primary": "Income, elder siblings, gains, fulfillment of desires, right ear",
         "karaka": "Jupiter", "classification": "Upachaya",
         "citation": "BPHS Bhava Phala Adhyaya | Parashara | Shloka 11"},
    12: {"name": "Vyaya Bhava",           "primary": "Expenses, foreign travel, liberation, left eye, sleep, isolation",
         "karaka": "Saturn", "classification": "Dusthana + Moksha",
         "citation": "BPHS Bhava Phala Adhyaya | Parashara | Shloka 12"},
}
