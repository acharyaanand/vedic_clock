"""
AETHERIS — Complete Muhurta Engine
Choghadiya, Hora, Udaya Lagna, Special Yogas, Sandhya timings
Source: Muhurta Chintamani | Brihat Samhita | Jyotish Siddhanta
"""
import math
from datetime import datetime
from typing import Dict, List

# ── Choghadiya ────────────────────────────────────────────────
# 8 day periods + 8 night periods
# Source: Muhurta Chintamani — Choghadiya Prakarana

CHOGHADIYA_NAMES = ["Udveg","Char","Labh","Amrit","Kaal","Shubh","Rog","Udveg"]
CHOGHADIYA_QUALITY = {
    "Amrit": "Excellent", "Shubh": "Good", "Labh": "Good", "Char": "Neutral",
    "Udveg": "Inauspicious", "Kaal": "Inauspicious", "Rog": "Inauspicious"
}
CHOGHADIYA_MEANING = {
    "Amrit": "Nectar — best for all auspicious work",
    "Shubh": "Auspicious — good for all work",
    "Labh":  "Profit — excellent for business, trade",
    "Char":  "Moving — good for travel and change",
    "Udveg": "Anxiety — avoid important decisions",
    "Kaal":  "Time of death — avoid new ventures",
    "Rog":   "Disease — avoid medical procedures"
}

# Day Choghadiya order by weekday (0=Sun)
DAY_CHOGHADIYA = {
    0: ["Udveg","Char","Labh","Amrit","Kaal","Shubh","Rog","Udveg"],
    1: ["Amrit","Kaal","Shubh","Rog","Udveg","Char","Labh","Amrit"],
    2: ["Rog","Udveg","Char","Labh","Amrit","Kaal","Shubh","Rog"],
    3: ["Labh","Amrit","Kaal","Shubh","Rog","Udveg","Char","Labh"],
    4: ["Shubh","Rog","Udveg","Char","Labh","Amrit","Kaal","Shubh"],
    5: ["Char","Labh","Amrit","Kaal","Shubh","Rog","Udveg","Char"],
    6: ["Kaal","Shubh","Rog","Udveg","Char","Labh","Amrit","Kaal"],
}
# NIGHT CHOGHADIYA — Verified against DrikPanchang (May 21-26 2026, New Delhi)
# Day and Night use DIFFERENT sequences — common mistake in many implementations
# Night sequence cycle: Amrit→Char→Rog→Kaal→Labh→Udveg→Shubh (different from day!)
# Day sequence cycle:   Amrit→Kaal→Shubh→Rog→Udveg→Char→Labh
NIGHT_CHOGHADIYA = {
    0: ["Shubh","Amrit","Char","Rog","Kaal","Labh","Udveg","Shubh"],   # Sunday  ✅
    1: ["Char","Rog","Kaal","Labh","Udveg","Shubh","Amrit","Char"],    # Monday  ✅
    2: ["Kaal","Labh","Udveg","Shubh","Amrit","Char","Rog","Kaal"],    # Tuesday ✅
    3: ["Udveg","Shubh","Amrit","Char","Rog","Kaal","Labh","Udveg"],   # Wednesday
    4: ["Amrit","Char","Rog","Kaal","Labh","Udveg","Shubh","Amrit"],   # Thursday ✅
    5: ["Rog","Kaal","Labh","Udveg","Shubh","Amrit","Char","Rog"],     # Friday  ✅ FIXED
    6: ["Labh","Udveg","Shubh","Amrit","Char","Rog","Kaal","Labh"],    # Saturday ✅ FIXED
}

def calc_choghadiya(weekday: int, sunrise_h: float, sunset_h: float) -> Dict:
    day_len = sunset_h - sunrise_h
    night_len = 24 - day_len
    day_period = day_len / 8
    night_period = night_len / 8

    def fmt(h):
        h = h % 24
        return f"{int(h):02d}:{int((h%1)*60):02d}"

    day_chog = []
    for i, name in enumerate(DAY_CHOGHADIYA[weekday]):
        s = sunrise_h + i * day_period
        e = s + day_period
        day_chog.append({
            "name": name, "quality": CHOGHADIYA_QUALITY[name],
            "meaning": CHOGHADIYA_MEANING[name],
            "start": fmt(s), "end": fmt(e),
            "is_current": False
        })

    night_chog = []
    for i, name in enumerate(NIGHT_CHOGHADIYA[weekday]):
        s = sunset_h + i * night_period
        e = s + night_period
        night_chog.append({
            "name": name, "quality": CHOGHADIYA_QUALITY[name],
            "meaning": CHOGHADIYA_MEANING[name],
            "start": fmt(s % 24), "end": fmt(e % 24),
            "is_current": False
        })

    return {
        "day": day_chog, "night": night_chog,
        "citation": "Muhurta Chintamani — Choghadiya Prakarana"
    }


# ── Hora ──────────────────────────────────────────────────────
# Planetary hour — each hour ruled by a planet
# Source: Jyotish Siddhanta — Hora calculation

HORA_ORDER = ["sun","venus","mercury","moon","saturn","jupiter","mars"]
HORA_MEANING = {
    "sun":     "Authority, government work, leadership",
    "moon":    "Emotions, travel, creative work, meeting women",
    "mars":    "Courage, surgery, sports, conflict resolution",
    "mercury": "Business, writing, communication, education",
    "jupiter": "Wisdom, spiritual work, teaching, expansion",
    "venus":   "Arts, romance, luxury, pleasure, beauty",
    "saturn":  "Hard work, service, discipline, old people"
}

def calc_hora(weekday: int, sunrise_h: float, sunset_h: float) -> List[Dict]:
    """Planetary hours from sunrise. Day has 12 hora, night has 12 hora."""
    day_len = sunset_h - sunrise_h
    night_len = 24 - day_len
    day_hora_len = day_len / 12
    night_hora_len = night_len / 12

    # Day lord index
    day_lord_idx = weekday  # Sun=0, Mon=1 (HORA_ORDER matches weekday order via lord)
    # Actually weekday lord: Sun=0,Mon=4,Tue=2,Wed=1,Thu=5,Fri=3,Sat=6
    WEEKDAY_TO_HORA_START = {0:0, 1:2, 2:4, 3:6, 4:1, 5:3, 6:5}
    start_idx = WEEKDAY_TO_HORA_START[weekday]

    horas = []
    for i in range(24):
        if i < 12:
            s = sunrise_h + i * day_hora_len
            e = s + day_hora_len
            period_type = "Day"
        else:
            s = sunset_h + (i-12) * night_hora_len
            e = s + night_hora_len
            period_type = "Night"
        planet = HORA_ORDER[(start_idx + i) % 7]
        def fmt(h): h=h%24; return f"{int(h):02d}:{int((h%1)*60):02d}"
        horas.append({
            "hora_num": i+1,
            "planet": planet.capitalize(),
            "period": period_type,
            "start": fmt(s),
            "end": fmt(e),
            "meaning": HORA_MEANING[planet]
        })
    return horas


# ── Udaya Lagna ───────────────────────────────────────────────
# Rising sign — changes approximately every 2 hours
# Source: Jyotish Siddhanta

SIGNS = ["Mesha","Vrishabha","Mithuna","Karka","Simha","Kanya",
         "Tula","Vrishchika","Dhanu","Makara","Kumbha","Meena"]
# Approximate rising times per sign (varies by latitude)
LAGNA_DURATION_MINS = [108,114,120,108,102,96,96,102,108,120,114,108]

def calc_udaya_lagna_schedule(sun_lon: float, sunrise_h: float) -> List[Dict]:
    lagna_at_sunrise = int(sun_lon / 30) % 12
    schedule = []
    current_h = sunrise_h
    for i in range(12):
        lagna_idx = (lagna_at_sunrise + i) % 12
        duration_h = LAGNA_DURATION_MINS[lagna_idx] / 60
        end_h = current_h + duration_h
        def fmt(h): h=h%24; return f"{int(h):02d}:{int((h%1)*60):02d}"
        schedule.append({
            "lagna": SIGNS[lagna_idx],
            "start": fmt(current_h),
            "end": fmt(end_h),
            "duration_mins": LAGNA_DURATION_MINS[lagna_idx]
        })
        current_h = end_h
    return schedule


# ── Special Yogas ─────────────────────────────────────────────
# Ravi Pushya, Guru Pushya, Sarvartha Siddhi, Amrit Siddhi, etc.

def calc_special_yogas(weekday: int, nakshatra_num: int,
                        tithi_num: int, yoga_name: str) -> List[Dict]:
    yogas = []
    tithi = (tithi_num-1)%30+1
    nak_name_list = [
        "Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
        "Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni",
        "Uttara Phalguni","Hasta","Chitra","Swati","Vishakha","Anuradha",
        "Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha","Shravana",
        "Dhanishtha","Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati"
    ]
    nak_name = nak_name_list[nakshatra_num-1]

    # Ravi Pushya — Sunday + Pushya
    if weekday == 0 and nakshatra_num == 8:
        yogas.append({
            "name": "Ravi Pushya Yoga",
            "quality": "Extremely Auspicious",
            "description": "Sunday + Pushya Nakshatra — rarest and most powerful yoga. Excellent for buying gold, jewellery, property, starting business",
            "citation": "Muhurta Chintamani | Pushya Yoga Prakarana"
        })

    # Guru Pushya — Thursday + Pushya
    if weekday == 4 and nakshatra_num == 8:
        yogas.append({
            "name": "Guru Pushya Yoga",
            "quality": "Extremely Auspicious",
            "description": "Thursday + Pushya Nakshatra — highly auspicious for education, spiritual initiation, guru vandana, investments",
            "citation": "Muhurta Chintamani | Pushya Yoga Prakarana"
        })

    # Sarvartha Siddhi Yoga — specific Vara + Nakshatra combinations
    SARVARTHA_COMBOS = {
        0: [1,4,6,7,10,11,13,22,24],   # Sunday
        1: [3,5,7,8,13,14,15,22,27],   # Monday
        2: [1,3,6,8,11,22,26],         # Tuesday
        3: [4,6,7,10,11,13,14,15,22],  # Wednesday
        4: [5,6,7,8,10,11,21,22,27],   # Thursday
        5: [3,5,7,8,13,15,22,25,27],   # Friday
        6: [3,8,10,14,16,22,23],       # Saturday
    }
    if nakshatra_num in SARVARTHA_COMBOS.get(weekday, []):
        yogas.append({
            "name": "Sarvartha Siddhi Yoga",
            "quality": "Highly Auspicious",
            "description": "All purposes accomplished — excellent for all auspicious activities",
            "citation": "Muhurta Chintamani | Sarvartha Siddhi Yoga"
        })

    # Amrit Siddhi Yoga — specific combos
    AMRIT_COMBOS = {
        0: [7], 1: [15], 2: [22], 3: [8], 4: [27], 5: [4], 6: [3]
    }
    if nakshatra_num in AMRIT_COMBOS.get(weekday, []):
        yogas.append({
            "name": "Amrit Siddhi Yoga",
            "quality": "Extremely Auspicious",
            "description": "Nectar of accomplishment — extremely rare and powerful",
            "citation": "Muhurta Chintamani | Amrit Siddhi Yoga"
        })

    # Dwipushkar Yoga — specific Vara + Tithi + Nakshatra
    DWI_VARA = [0, 2, 6]   # Sun, Tue, Sat
    DWI_TITHI = [2, 7, 12]  # Dwitiya, Saptami, Dwadashi
    DWI_NAK = [3,7,8,13,22,23]
    if weekday in DWI_VARA and tithi in DWI_TITHI and nakshatra_num in DWI_NAK:
        yogas.append({
            "name": "Dwipushkar Yoga",
            "quality": "Powerful — doubles effect",
            "description": "Double Pushkar — whatever is done gets doubled. Good deeds doubled, bad deeds also doubled. Avoid inauspicious activities.",
            "citation": "Muhurta Chintamani | Dwipushkar Yoga"
        })

    # Tripushkar Yoga
    TRI_VARA = [0, 2, 6]
    TRI_TITHI = [3, 8, 13]
    TRI_NAK = [3,7,8,13,22,23]
    if weekday in TRI_VARA and tithi in TRI_TITHI and nakshatra_num in TRI_NAK:
        yogas.append({
            "name": "Tripushkar Yoga",
            "quality": "Very Powerful — triples effect",
            "description": "Triple Pushkar — effects tripled. Very auspicious for giving in charity. Avoid inauspicious work.",
            "citation": "Muhurta Chintamani | Tripushkar Yoga"
        })

    # Vijay Muhurta (already in panchanga — add if relevant)
    if weekday in [0,1,2,3,4,5,6]:
        pass  # Calculated separately from solar noon

    # Bhadra / Vishti Karana — inauspicious half-tithi
    diff_approx = tithi * 12
    karana_idx = int(diff_approx / 6) % 11
    if karana_idx == 6:  # Vishti = Bhadra
        yogas.append({
            "name": "Bhadra (Vishti Karana)",
            "quality": "Inauspicious",
            "description": "Vishti Karana (Bhadra) — inauspicious half-tithi. Avoid travel, new ventures, important decisions.",
            "citation": "Muhurta Chintamani | Karana Dosha"
        })

    # Ganda Moola Nakshatras
    GANDA_MOOLA = [9, 18, 27, 1, 10, 19]  # Ashlesha, Jyeshtha, Revati, Ashwini, Magha, Mula
    if nakshatra_num in GANDA_MOOLA:
        yogas.append({
            "name": "Ganda Moola Nakshatra",
            "quality": "Inauspicious for birth",
            "description": f"Birth in {nak_name} — Ganda Moola dosha. Shanti puja recommended for newborns.",
            "citation": "Muhurta Chintamani | Ganda Moola Dosha"
        })

    return yogas


# ── Sandhya Timings ───────────────────────────────────────────
def calc_sandhya_timings(sunrise_h: float, sunset_h: float) -> Dict:
    def fmt(h): h=h%24; return f"{int(h):02d}:{int((h%1)*60):02d}"
    solar_noon = (sunrise_h + sunset_h) / 2
    return {
        "pratah_sandhya": {
            "start": fmt(sunrise_h - 24/60),
            "end":   fmt(sunrise_h + 48/60),
            "description": "Morning twilight — Surya Namaskar, Gayatri Japa"
        },
        "madhyahna_sandhya": {
            "start": fmt(solar_noon - 24/60),
            "end":   fmt(solar_noon + 24/60),
            "description": "Midday prayer — overlaps Abhijit Muhurta"
        },
        "sayahna_sandhya": {
            "start": fmt(sunset_h - 24/60),
            "end":   fmt(sunset_h + 24/60),
            "description": "Evening twilight — evening prayer and lamp lighting"
        },
        "citation": "Dharmasindhu | Sandhya Vandana Prakarana"
    }
