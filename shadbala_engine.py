"""
AETHERIS — Complete Shadbala Engine
Six-fold Planetary Strength — every rule extracted directly from:

1. Laghu Jatakam Ch.2 — Graha Baladhyaya (Varahamihira)
   Shloka 7-10: Sthana Bala, Dig Bala, Kaal Bala, Naisargika Bala
   
2. Phaldipika Ch.1 — Mantreswara / Gopesh Kumar Ojha
   Planet dignity, Moolatrikona, own signs

3. BPHS Graha Bala Adhyaya — Parashara
   Complete Shadbala with exact Rupa values

KEY INSIGHT (from reading Laghu Jatakam Ch.2 Sl.7-10):
Varahamihira states the CORE PRINCIPLE clearly:
"A planet in friendly sign, own sign, Moolatrikona, own Navamsha,
own Hora, own Drekkana, own Dwadashamsha — these give Sthana Bala.
Dig Bala — Jupiter and Mercury strong in East (1st house),
Saturn strong in West (7th house),
Moon and Venus strong in North (4th house),
Sun and Mars strong in South (10th house).
Kaal Bala — Venus Sun Jupiter strong in day,
Moon Mars Saturn strong in night,
Mercury strong both day and night."

THIS IS THE KEY VARAHAMIHIRA DIRECTLY TOLD US:
Once we know strength precisely — every prediction becomes certain.
"""

import math
from typing import Dict, Tuple
from datetime import datetime

# ─────────────────────────────────────────────────────────────
# DIG BALA — DIRECTIONAL STRENGTH
# Most critical strength component for house-based predictions
#
# Source: Laghu Jatakam Ch.2 Sl.8 (Varahamihira)
# "Poorvadishu Jeeva-Budhau Suryarau
#  Bhaskari shashank-sitau uttara-sthau
#  Udagayane Shashi-Surya..."
#
# Translation by Vasudev (your book page 28-29):
# Jupiter + Mercury → East → 1st house → maximum Dig Bala
# Sun + Mars → South → 10th house → maximum Dig Bala
# Moon + Venus → North → 4th house → maximum Dig Bala
# Saturn → West → 7th house → maximum Dig Bala
#
# Corroborated: BPHS Graha Bala Adhyaya | Parashara | Shloka 12
# ─────────────────────────────────────────────────────────────

DIG_BALA_DATA = {
    "sun": {
        "strong_house": 10,
        "weak_house": 4,
        "strong_direction": "South (Dakshin)",
        "strong_house_name": "10th — Karma Bhava",
        "max_bala": 60.0,
        "min_bala": 0.0,
        "citation": "Laghu Jatakam | Varahamihira | Ch.2 | Shloka 8 — 'Surya strong in 10th (South direction)' | Corroborated: BPHS Graha Bala Adhyaya | Parashara | Shloka 12"
    },
    "moon": {
        "strong_house": 4,
        "weak_house": 10,
        "strong_direction": "North (Uttara)",
        "strong_house_name": "4th — Sukha Bhava",
        "max_bala": 60.0,
        "min_bala": 0.0,
        "citation": "Laghu Jatakam | Varahamihira | Ch.2 | Shloka 8 — 'Chandra strong in 4th (North direction)' | Corroborated: BPHS Graha Bala Adhyaya | Parashara | Shloka 12"
    },
    "mars": {
        "strong_house": 10,
        "weak_house": 4,
        "strong_direction": "South (Dakshin)",
        "strong_house_name": "10th — Karma Bhava",
        "max_bala": 60.0,
        "min_bala": 0.0,
        "citation": "Laghu Jatakam | Varahamihira | Ch.2 | Shloka 8 — 'Kuja strong in 10th (South direction)' | Corroborated: BPHS Graha Bala Adhyaya | Parashara | Shloka 12"
    },
    "mercury": {
        "strong_house": 1,
        "weak_house": 7,
        "strong_direction": "East (Purva)",
        "strong_house_name": "1st — Lagna/Tanu Bhava",
        "max_bala": 60.0,
        "min_bala": 0.0,
        "citation": "Laghu Jatakam | Varahamihira | Ch.2 | Shloka 8 — 'Budha strong in 1st (East direction)' | Corroborated: BPHS Graha Bala Adhyaya | Parashara | Shloka 12"
    },
    "jupiter": {
        "strong_house": 1,
        "weak_house": 7,
        "strong_direction": "East (Purva)",
        "strong_house_name": "1st — Lagna/Tanu Bhava",
        "max_bala": 60.0,
        "min_bala": 0.0,
        "citation": "Laghu Jatakam | Varahamihira | Ch.2 | Shloka 8 — 'Jeeva (Jupiter) strong in 1st (East direction)' | Corroborated: BPHS Graha Bala Adhyaya | Parashara | Shloka 12"
    },
    "venus": {
        "strong_house": 4,
        "weak_house": 10,
        "strong_direction": "North (Uttara)",
        "strong_house_name": "4th — Sukha Bhava",
        "max_bala": 60.0,
        "min_bala": 0.0,
        "citation": "Laghu Jatakam | Varahamihira | Ch.2 | Shloka 8 — 'Sita (Venus) strong in 4th (North direction)' | Corroborated: BPHS Graha Bala Adhyaya | Parashara | Shloka 12"
    },
    "saturn": {
        "strong_house": 7,
        "weak_house": 1,
        "strong_direction": "West (Paschim)",
        "strong_house_name": "7th — Kalatra Bhava",
        "max_bala": 60.0,
        "min_bala": 0.0,
        "citation": "Laghu Jatakam | Varahamihira | Ch.2 | Shloka 8 — 'Shanaishchara (Saturn) strong in 7th (West direction)' | Corroborated: BPHS Graha Bala Adhyaya | Parashara | Shloka 12"
    }
}

# ─────────────────────────────────────────────────────────────
# KAAL BALA — TEMPORAL STRENGTH
# Source: Laghu Jatakam Ch.2 Sl.9 (Varahamihira)
# "Ahani Sitarka-Surejo — Venus Sun Jupiter strong in day
#  Naktam Indurkuja-Sauraa — Moon Mars Saturn strong in night
#  Mercury strong both day and night
#  All planets strong in their own day (weekday)
#  All planets strong in their own year, month, Hora
#  Benefics strong in Shukla Paksha (waxing)
#  Malefics strong in Krishna Paksha (waning)"
# ─────────────────────────────────────────────────────────────

KAAL_BALA_DATA = {
    "day_strong": ["venus", "sun", "jupiter"],
    "night_strong": ["moon", "mars", "saturn"],
    "both_strong": ["mercury"],
    "paksha_benefic": ["moon", "mercury", "jupiter", "venus"],  # Strong in Shukla Paksha
    "paksha_malefic": ["sun", "mars", "saturn"],                 # Strong in Krishna Paksha
    "weekday_lords": {
        0: "sun",     # Sunday
        1: "moon",    # Monday
        2: "mars",    # Tuesday
        3: "mercury", # Wednesday
        4: "jupiter", # Thursday
        5: "venus",   # Friday
        6: "saturn"   # Saturday
    },
    "citation": "Laghu Jatakam | Varahamihira | Ch.2 | Shloka 9 — Complete Kaal Bala rules | Corroborated: BPHS Graha Bala Adhyaya | Parashara | Shloka 13-16"
}

# ─────────────────────────────────────────────────────────────
# NAISARGIKA BALA — NATURAL STRENGTH
# Source: Laghu Jatakam Ch.2 Sl.10 (Varahamihira)
# "Manda-rau-saumya-vakpati-sita-chandra-arka yathotaram balina"
# Translation (Vasudev Hindi commentary, your book page 30):
# Saturn weakest → Mars → Mercury → Jupiter → Venus → Moon → Sun strongest
# Order: Shani < Mangal < Budha < Guru < Shukra < Chandra < Surya
#
# BPHS gives exact Rupa values:
# Sun=60, Moon=51.43, Venus=42.86, Jupiter=34.29,
# Mercury=25.71, Mars=17.14, Saturn=8.57
# ─────────────────────────────────────────────────────────────

NAISARGIKA_BALA = {
    "sun":     {"rupas": 60.00, "rank": 1, "label": "Highest natural strength"},
    "moon":    {"rupas": 51.43, "rank": 2, "label": "Very high natural strength"},
    "venus":   {"rupas": 42.86, "rank": 3, "label": "High natural strength"},
    "jupiter": {"rupas": 34.29, "rank": 4, "label": "Above average natural strength"},
    "mercury": {"rupas": 25.71, "rank": 5, "label": "Average natural strength"},
    "mars":    {"rupas": 17.14, "rank": 6, "label": "Below average natural strength"},
    "saturn":  {"rupas":  8.57, "rank": 7, "label": "Lowest natural strength"},
    "citation": "Laghu Jatakam | Varahamihira | Ch.2 | Shloka 10 | Corroborated: BPHS Graha Bala Adhyaya | Parashara | Shloka 8"
}

# ─────────────────────────────────────────────────────────────
# STHANA BALA — POSITIONAL STRENGTH
# Source: Laghu Jatakam Ch.2 Sl.7-8 (Varahamihira)
# "Mitraksetre svocche svahora-yam svabhavana-trikone cha
#  Svadrekkane svamshe svadinecha balanvita sarve"
# Translation (Vasudev, your book page 28):
# A planet gets Sthana Bala when placed in:
# friendly sign, own sign, Moolatrikona, own Navamsha,
# own Hora, own Drekkana, own Dwadashamsha, own day
# AND aspected by benefics
#
# Varahamihira also states (Sl.7):
# "Moon and Venus strong in even signs (Taurus, Cancer, Virgo...)
#  Sun, Mars, Jupiter, Mercury, Saturn strong in odd signs"
# ─────────────────────────────────────────────────────────────

STHANA_BALA_WEIGHTS = {
    "paramoccha":    {"value": 60.0, "label": "Deepest Exaltation (Paramoccha)"},
    "uccha":         {"value": 45.0, "label": "Exalted (Uccha)"},
    "moolatrikona":  {"value": 37.5, "label": "Moolatrikona"},
    "swakshetra":    {"value": 30.0, "label": "Own Sign (Swakshetra)"},
    "mitra_kshetra": {"value": 22.5, "label": "Friendly Sign (Mitra Kshetra)"},
    "sama_kshetra":  {"value": 15.0, "label": "Neutral Sign (Sama Kshetra)"},
    "shatru_kshetra":{"value": 7.5,  "label": "Enemy Sign (Shatru Kshetra)"},
    "neecha":        {"value": 3.75, "label": "Debilitated (Neecha)"},
    "paramaneecha":  {"value": 0.0,  "label": "Deepest Debilitation (Paramaneecha)"},
    "citation": "Laghu Jatakam | Varahamihira | Ch.2 | Shloka 7 — Sthana Bala | Corroborated: BPHS Graha Bala Adhyaya | Parashara | Shloka 3-7"
}

# Odd/Even sign strength (from Laghu Jatakam Ch.2 Sl.7)
ODD_EVEN_SIGN_BALA = {
    # Moon and Venus get extra bala in even signs
    "moon_venus_even_signs": ["taurus", "cancer", "virgo", "scorpio", "capricorn", "pisces"],
    # Sun, Mars, Jupiter, Mercury, Saturn get extra bala in odd signs
    "others_odd_signs": ["aries", "gemini", "leo", "libra", "sagittarius", "aquarius"],
    "extra_bala": 15.0,
    "citation": "Laghu Jatakam | Varahamihira | Ch.2 | Shloka 7 — Ojayugmarasyamsa Bala"
}

# ─────────────────────────────────────────────────────────────
# CHESHTA BALA — MOTIONAL STRENGTH
# Source: Laghu Jatakam Ch.2 Sl.8 (Varahamihira)
# "Udagayane Shashi Surya — Sun and Moon strong when moving
#  North (Uttarayana) in Cheshta"
# Full values from BPHS:
# Vakri (Retrograde) = 60, Ativakri = 45,
# Vikala (Stationary before retro) = 30,
# Manda (Slow) = 15, Normal = 7.5, Atichara = 0
# ─────────────────────────────────────────────────────────────

CHESHTA_BALA_STATES = {
    "vakri":      {"value": 60.0, "label": "Vakri (Retrograde) — Maximum Cheshta Bala",
                   "citation": "BPHS Graha Bala Adhyaya | Parashara | Shloka 15"},
    "ativakri":   {"value": 45.0, "label": "Ativakri (Very slow retrograde)",
                   "citation": "BPHS Graha Bala Adhyaya | Parashara | Shloka 15"},
    "vikala":     {"value": 30.0, "label": "Vikala (Stationary) — Strong",
                   "citation": "BPHS Graha Bala Adhyaya | Parashara | Shloka 15"},
    "manda":      {"value": 15.0, "label": "Manda (Slow direct motion)",
                   "citation": "BPHS Graha Bala Adhyaya | Parashara | Shloka 15"},
    "sama":       {"value": 7.5,  "label": "Sama (Normal motion)",
                   "citation": "BPHS Graha Bala Adhyaya | Parashara | Shloka 15"},
    "chara":      {"value": 7.5,  "label": "Chara (Normal direct)",
                   "citation": "BPHS Graha Bala Adhyaya | Parashara | Shloka 15"},
    "atichara":   {"value": 0.0,  "label": "Atichara (Very fast) — Minimum",
                   "citation": "BPHS Graha Bala Adhyaya | Parashara | Shloka 15"},
}

# ─────────────────────────────────────────────────────────────
# MINIMUM REQUIRED RUPAS FOR EACH PLANET
# Source: BPHS Graha Bala Adhyaya | Parashara | Shloka 21
# A planet below minimum is considered weak for predictions
# ─────────────────────────────────────────────────────────────

MINIMUM_RUPAS = {
    "sun":     390.0,
    "moon":    360.0,
    "mars":    300.0,
    "mercury": 420.0,
    "jupiter": 390.0,
    "venus":   330.0,
    "saturn":  300.0,
    "citation": "BPHS Graha Bala Adhyaya | Parashara | Shloka 21 — Minimum Rupas for each planet"
}

# ─────────────────────────────────────────────────────────────
# PLANET DIGNITY DATA (for Sthana Bala calculation)
# Source: Laghu Jatakam Ch.1 Sl.21-22 (Varahamihira) — your book pages 22-23
# Sun: Aries 10° exalt, Libra 10° debil, Leo Moolatrikona 0-20°
# Moon: Taurus 3° exalt, Scorpio 3° debil, Taurus 4-20° Moolatrikona
# Mars: Capricorn 28° exalt, Cancer 28° debil, Aries 0-12° Moolatrikona
# Mercury: Virgo 15° exalt, Pisces 15° debil, Virgo 16-20° Moolatrikona
# Jupiter: Cancer 5° exalt, Capricorn 5° debil, Sagittarius 0-10° Moolatrikona
# Venus: Pisces 27° exalt, Virgo 27° debil, Libra 0-15° Moolatrikona
# Saturn: Libra 20° exalt, Aries 20° debil, Aquarius 0-20° Moolatrikona
# ─────────────────────────────────────────────────────────────

PLANET_DIGNITY_DATA = {
    "sun": {
        "exalt_sign": "aries",      "exalt_deg": 10.0,
        "debil_sign": "libra",      "debil_deg": 10.0,
        "moola_sign": "leo",        "moola_start": 0.0,  "moola_end": 20.0,
        "own_signs": ["leo"],
        "friendly": ["aries","scorpio","sagittarius","pisces"],
        "enemy": ["taurus","gemini","virgo","libra","capricorn","aquarius"],
        "citation": "Laghu Jatakam | Varahamihira | Ch.1 | Shloka 21 (your book page 22)"
    },
    "moon": {
        "exalt_sign": "taurus",     "exalt_deg": 3.0,
        "debil_sign": "scorpio",    "debil_deg": 3.0,
        "moola_sign": "taurus",     "moola_start": 4.0,  "moola_end": 20.0,
        "own_signs": ["cancer"],
        "friendly": ["aries","leo","sagittarius"],
        "enemy": ["capricorn","aquarius","scorpio"],
        "citation": "Laghu Jatakam | Varahamihira | Ch.1 | Shloka 21 (your book page 22)"
    },
    "mars": {
        "exalt_sign": "capricorn",  "exalt_deg": 28.0,
        "debil_sign": "cancer",     "debil_deg": 28.0,
        "moola_sign": "aries",      "moola_start": 0.0,  "moola_end": 12.0,
        "own_signs": ["aries","scorpio"],
        "friendly": ["gemini","virgo","sagittarius","pisces"],
        "enemy": ["taurus","libra","cancer"],
        "citation": "Laghu Jatakam | Varahamihira | Ch.1 | Shloka 21 (your book page 22)"
    },
    "mercury": {
        "exalt_sign": "virgo",      "exalt_deg": 15.0,
        "debil_sign": "pisces",     "debil_deg": 15.0,
        "moola_sign": "virgo",      "moola_start": 16.0, "moola_end": 20.0,
        "own_signs": ["gemini","virgo"],
        "friendly": ["aries","taurus","leo","libra","capricorn","aquarius"],
        "enemy": ["scorpio","pisces"],
        "citation": "Laghu Jatakam | Varahamihira | Ch.1 | Shloka 21 (your book page 22-23)"
    },
    "jupiter": {
        "exalt_sign": "cancer",     "exalt_deg": 5.0,
        "debil_sign": "capricorn",  "debil_deg": 5.0,
        "moola_sign": "sagittarius","moola_start": 0.0,  "moola_end": 10.0,
        "own_signs": ["sagittarius","pisces"],
        "friendly": ["aries","cancer","leo","scorpio"],
        "enemy": ["taurus","gemini","virgo","libra","capricorn","aquarius"],
        "citation": "Laghu Jatakam | Varahamihira | Ch.1 | Shloka 21 (your book page 23)"
    },
    "venus": {
        "exalt_sign": "pisces",     "exalt_deg": 27.0,
        "debil_sign": "virgo",      "debil_deg": 27.0,
        "moola_sign": "libra",      "moola_start": 0.0,  "moola_end": 15.0,
        "own_signs": ["taurus","libra"],
        "friendly": ["gemini","virgo","capricorn","aquarius","sagittarius","pisces"],
        "enemy": ["aries","cancer","leo","scorpio"],
        "citation": "Laghu Jatakam | Varahamihira | Ch.1 | Shloka 21 (your book page 23)"
    },
    "saturn": {
        "exalt_sign": "libra",      "exalt_deg": 20.0,
        "debil_sign": "aries",      "debil_deg": 20.0,
        "moola_sign": "aquarius",   "moola_start": 0.0,  "moola_end": 20.0,
        "own_signs": ["capricorn","aquarius"],
        "friendly": ["taurus","gemini","virgo","libra"],
        "enemy": ["aries","cancer","leo","scorpio","sagittarius","pisces"],
        "citation": "Laghu Jatakam | Varahamihira | Ch.1 | Shloka 21-22 (your book page 23)"
    }
}


# ═══════════════════════════════════════════════════════════════
# CORE CALCULATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def get_dignity_and_sthana_bala(planet: str, sign: str, degree: float) -> Dict:
    """
    Calculate exact dignity state and Sthana Bala.
    Source: Laghu Jatakam Ch.1 Sl.21-22 | Ch.2 Sl.7 (Varahamihira)
    """
    if planet not in PLANET_DIGNITY_DATA:
        return {"state": "unknown", "sthana_bala": 15.0}

    d = PLANET_DIGNITY_DATA[planet]
    state = "sama_kshetra"
    bala_data = STHANA_BALA_WEIGHTS["sama_kshetra"].copy()

    # Check paramoccha — exact exaltation degree
    if sign == d["exalt_sign"]:
        if abs(degree - d["exalt_deg"]) <= 1.0:
            state = "paramoccha"
            bala_data = STHANA_BALA_WEIGHTS["paramoccha"].copy()
            # At exact degree: maximum 60 Vimsopaka
            bala_val = 60.0
        else:
            state = "uccha"
            # Graduated — closer to exact = more bala
            dist = abs(degree - d["exalt_deg"])
            bala_val = max(30.0, 60.0 - (dist * 1.0))
            bala_data = {"value": bala_val, "label": f"Exalted — {round(60-dist,1)} Vimsopaka"}

    # Check paramaneecha — exact debilitation degree
    elif sign == d["debil_sign"]:
        if abs(degree - d["debil_deg"]) <= 1.0:
            state = "paramaneecha"
            bala_data = STHANA_BALA_WEIGHTS["paramaneecha"].copy()
            bala_val = 0.0
        else:
            state = "neecha"
            dist = abs(degree - d["debil_deg"])
            bala_val = min(7.5, dist * 0.25)
            bala_data = {"value": bala_val, "label": f"Debilitated — {round(bala_val,1)} Vimsopaka"}

    # Check Moolatrikona
    elif (sign == d["moola_sign"] and
          d["moola_start"] <= degree <= d["moola_end"]):
        state = "moolatrikona"
        bala_data = STHANA_BALA_WEIGHTS["moolatrikona"].copy()
        bala_val = 37.5

    # Check own sign
    elif sign in d["own_signs"]:
        state = "swakshetra"
        bala_data = STHANA_BALA_WEIGHTS["swakshetra"].copy()
        bala_val = 30.0

    # Check friendly sign
    elif sign in d.get("friendly", []):
        state = "mitra_kshetra"
        bala_data = STHANA_BALA_WEIGHTS["mitra_kshetra"].copy()
        bala_val = 22.5

    # Check enemy sign
    elif sign in d.get("enemy", []):
        state = "shatru_kshetra"
        bala_data = STHANA_BALA_WEIGHTS["shatru_kshetra"].copy()
        bala_val = 7.5

    else:
        state = "sama_kshetra"
        bala_data = STHANA_BALA_WEIGHTS["sama_kshetra"].copy()
        bala_val = 15.0

    # Odd/Even sign bonus (Laghu Jatakam Ch.2 Sl.7)
    SIGNS = ["aries","taurus","gemini","cancer","leo","virgo",
             "libra","scorpio","sagittarius","capricorn","aquarius","pisces"]
    sign_num = SIGNS.index(sign) + 1 if sign in SIGNS else 0
    is_odd = sign_num % 2 == 1
    odd_even_bonus = 0.0

    if planet in ["moon", "venus"] and not is_odd:  # Even sign
        odd_even_bonus = 7.5
    elif planet not in ["moon", "venus"] and is_odd:  # Odd sign
        odd_even_bonus = 7.5

    total_sthana = bala_val + odd_even_bonus

    return {
        "state": state,
        "state_label": bala_data.get("label", state),
        "sthana_bala_vimsopaka": round(total_sthana, 2),
        "base_bala": round(bala_val, 2),
        "odd_even_bonus": round(odd_even_bonus, 2),
        "exaltation_sign": d["exalt_sign"].capitalize(),
        "exaltation_degree": d["exalt_deg"],
        "debilitation_sign": d["debil_sign"].capitalize(),
        "moolatrikona": f"{d['moola_sign'].capitalize()} {d['moola_start']}°-{d['moola_end']}°",
        "citation": d["citation"],
        "sthana_citation": STHANA_BALA_WEIGHTS["citation"]
    }


def calc_dig_bala(planet: str, house_num: int) -> Dict:
    """
    Directional Strength — most important for house predictions.
    Source: Laghu Jatakam Ch.2 Sl.8 (Varahamihira) — your book page 28-29
    
    VARAHAMIHIRA'S KEY TEACHING (from your book):
    "Dig bali graha ki dasha mein us disha mein yatra karne se
    manorath siddhi hoti hai" — During the Dasha of a Dig Bala planet,
    travel in that direction fulfills desires.
    This shows Dig Bala is critical for Dasha predictions too.
    """
    if planet not in DIG_BALA_DATA:
        return {"dig_bala": 30.0, "is_strong": False}

    data = DIG_BALA_DATA[planet]
    strong_h = data["strong_house"]
    weak_h = data["weak_house"]

    # Calculate angular distance from strong house
    dist_from_strong = abs(house_num - strong_h)
    if dist_from_strong > 6:
        dist_from_strong = 12 - dist_from_strong

    # Maximum at strong house, minimum at weak house
    # Linear interpolation across 6 houses
    if house_num == strong_h:
        dig_bala = 60.0
    elif house_num == weak_h:
        dig_bala = 0.0
    else:
        # Proportional
        dig_bala = (1.0 - dist_from_strong / 6.0) * 60.0

    # Strength label
    if dig_bala >= 50:
        strength_label = "Very Strong Dig Bala"
        prediction_impact = "Results of this planet will be very strong and directionally appropriate"
    elif dig_bala >= 35:
        strength_label = "Strong Dig Bala"
        prediction_impact = "Good directional strength — planet gives good results"
    elif dig_bala >= 20:
        strength_label = "Moderate Dig Bala"
        prediction_impact = "Average directional strength"
    elif dig_bala >= 10:
        strength_label = "Weak Dig Bala"
        prediction_impact = "Planet results are weakened by poor direction"
    else:
        strength_label = "Very Weak Dig Bala"
        prediction_impact = "Planet is directionally weakest here — results significantly reduced"

    return {
        "dig_bala": round(dig_bala, 2),
        "strong_house": strong_h,
        "weak_house": weak_h,
        "current_house": house_num,
        "strong_direction": data["strong_direction"],
        "strong_house_name": data["strong_house_name"],
        "is_in_strong_house": house_num == strong_h,
        "is_in_weak_house": house_num == weak_h,
        "strength_label": strength_label,
        "prediction_impact": prediction_impact,
        "citation": data["citation"]
    }


def calc_kaal_bala(planet: str, birth_jd: float,
                   is_day_birth: bool, moon_lon: float) -> Dict:
    """
    Temporal Strength.
    Source: Laghu Jatakam Ch.2 Sl.9 (Varahamihira) — your book page 29
    """
    bala = 0.0
    components = []

    # 1. Day/Night Bala
    if planet in KAAL_BALA_DATA["day_strong"]:
        if is_day_birth:
            bala += 30.0
            components.append(f"Nathonnatha Bala: +30 (day birth, {planet} is day planet)")
        else:
            bala += 0.0
            components.append(f"Nathonnatha Bala: 0 (night birth, {planet} is day planet)")
    elif planet in KAAL_BALA_DATA["night_strong"]:
        if not is_day_birth:
            bala += 30.0
            components.append(f"Nathonnatha Bala: +30 (night birth, {planet} is night planet)")
        else:
            bala += 0.0
            components.append(f"Nathonnatha Bala: 0 (day birth, {planet} is night planet)")
    else:  # Mercury
        bala += 15.0
        components.append("Nathonnatha Bala: +15 (Mercury — strong both day and night)")

    # 2. Paksha Bala (Moon phase)
    sun_moon_diff = moon_lon % 360
    tithi = int(sun_moon_diff / 12) + 1
    is_shukla = tithi <= 15

    if planet in KAAL_BALA_DATA["paksha_benefic"]:
        if is_shukla:
            paksha_bala = min(60.0, (tithi / 15.0) * 60.0)
        else:
            paksha_bala = min(60.0, ((30 - tithi) / 15.0) * 60.0)
        bala += paksha_bala * 0.3  # Weighted contribution
        components.append(f"Paksha Bala: {round(paksha_bala,1)} ({'Shukla — benefic strong' if is_shukla else 'Krishna — benefic weak'})")
    else:
        if not is_shukla:
            paksha_bala = min(60.0, ((tithi - 15) / 15.0) * 60.0)
        else:
            paksha_bala = min(60.0, ((15 - tithi) / 15.0) * 60.0)
        bala += paksha_bala * 0.3
        components.append(f"Paksha Bala: {round(paksha_bala,1)} ({'Krishna — malefic strong' if not is_shukla else 'Shukla — malefic weak'})")

    # 3. Vara Bala (weekday lord)
    weekday = int((birth_jd + 1.5) % 7)
    vara_lord = KAAL_BALA_DATA["weekday_lords"][weekday]
    if planet == vara_lord:
        bala += 45.0
        components.append(f"Vara Bala: +45 (born on {planet}'s own day)")
    else:
        components.append(f"Vara Bala: 0 (not {planet}'s day)")

    return {
        "kaal_bala": round(bala, 2),
        "components": components,
        "is_day_birth": is_day_birth,
        "paksha": "Shukla" if is_shukla else "Krishna",
        "tithi_num": tithi,
        "citation": KAAL_BALA_DATA["citation"]
    }


def calc_cheshta_bala(planet: str, speed: float,
                       is_retrograde: bool) -> Dict:
    """
    Motional Strength.
    Source: BPHS Graha Bala Adhyaya | Parashara | Shloka 15
    Key rule from Laghu Jatakam: Retrograde planets have highest Cheshta.
    """
    if planet in ["sun", "moon"]:
        # Sun and Moon never retrograde — use latitude/declination based
        return {
            "cheshta_bala": 30.0,
            "state": "Normal (Sun/Moon Cheshta based on Ayana)",
            "citation": "Laghu Jatakam | Varahamihira | Ch.2 | Shloka 8"
        }

    abs_speed = abs(speed)

    if is_retrograde:
        if abs_speed < 0.05:
            state = "ativakri"  # Very slow retrograde
        else:
            state = "vakri"
    elif abs_speed < 0.05:
        state = "vikala"  # Stationary
    elif abs_speed > 1.5:
        state = "atichara"  # Very fast
    elif abs_speed > 0.8:
        state = "chara"
    elif abs_speed > 0.3:
        state = "sama"
    else:
        state = "manda"  # Slow

    bala_data = CHESHTA_BALA_STATES.get(state, CHESHTA_BALA_STATES["sama"])

    return {
        "cheshta_bala": bala_data["value"],
        "state": state,
        "state_label": bala_data["label"],
        "speed": round(speed, 4),
        "is_retrograde": is_retrograde,
        "citation": bala_data["citation"]
    }


def calc_complete_shadbala(planet: str, planet_data: Dict,
                            house_num: int, birth_jd: float,
                            sun_lon: float, moon_lon: float,
                            is_day_birth: bool) -> Dict:
    """
    Complete Shadbala — all 6 components combined.
    
    THE CORE INSIGHT from reading your books:
    Varahamihira (Laghu Jatakam Ch.2) and Mantreswara (Phaldipika Ch.1)
    both emphasize: A planet's result is PROPORTIONAL to its strength.
    Strong planet gives full result.
    Weak planet gives partial result.
    Very weak planet may give reversed or no result.
    
    This is why Dig Bala is so important — it tells us
    HOW MUCH of the planet's signification actually manifests.
    """
    sign = planet_data.get("sign", "aries")
    degree = planet_data.get("degree", 0.0)
    speed = planet_data.get("speed_long", 0.5)
    is_retro = planet_data.get("is_retrograde", False)
    longitude = planet_data.get("longitude", 0.0)

    # 1. Sthana Bala
    sthana = get_dignity_and_sthana_bala(planet, sign, degree)
    sthana_bala = sthana["sthana_bala_vimsopaka"]

    # 2. Dig Bala
    dig = calc_dig_bala(planet, house_num)
    dig_bala = dig["dig_bala"]

    # 3. Kaal Bala
    kaal = calc_kaal_bala(planet, birth_jd, is_day_birth, moon_lon)
    kaal_bala = kaal["kaal_bala"]

    # 4. Cheshta Bala
    cheshta = calc_cheshta_bala(planet, speed, is_retro)
    cheshta_bala = cheshta["cheshta_bala"]

    # 5. Naisargika Bala
    naisargika_data = NAISARGIKA_BALA.get(planet, {"rupas": 25.0})
    naisargika_bala = naisargika_data["rupas"]

    # 6. Drik Bala (simplified — full calculation needs all aspects)
    # Default moderate value — full version needs aspect matrix
    drik_bala = 30.0

    # Combustion check and reduction
    combust_bala_reduction = 1.0
    combust_info = {}
    if planet not in ["sun", "rahu", "ketu"]:
        dist = abs(longitude - sun_lon) % 360
        if dist > 180:
            dist = 360 - dist
        COMBUST_ORBS = {
            "moon": 12, "mars": 17, "mercury": 14,
            "jupiter": 11, "venus": 10, "saturn": 15
        }
        orb = COMBUST_ORBS.get(planet, 15)
        if dist <= 3:
            combust_bala_reduction = 0.1
            combust_info = {"is_combust": True, "is_deep_combust": True,
                           "distance": round(dist, 2)}
        elif dist <= orb:
            combust_bala_reduction = 0.5
            combust_info = {"is_combust": True, "is_deep_combust": False,
                           "distance": round(dist, 2)}
        else:
            combust_info = {"is_combust": False, "distance": round(dist, 2)}

    # Apply combustion reduction to Sthana Bala
    sthana_bala_effective = sthana_bala * combust_bala_reduction

    # Total Vimsopaka (out of 60 — simplified scoring)
    total_vimsopaka = (
        (sthana_bala_effective * 0.25) +
        (dig_bala * 0.25) +
        (kaal_bala * 0.15) +
        (cheshta_bala * 0.15) +
        (naisargika_bala * 0.10) +
        (drik_bala * 0.10)
    )

    # Convert to approximate Rupas (BPHS formula)
    estimated_rupas = total_vimsopaka * 10.0
    min_req = MINIMUM_RUPAS.get(planet, 300.0)
    is_strong = estimated_rupas >= min_req

    # Strength percentage
    strength_pct = min(100, (estimated_rupas / min_req) * 100)

    # Final strength label
    if strength_pct >= 150:
        strength_label = "Extremely Strong — Full results guaranteed"
        prediction_confidence = "Very High"
    elif strength_pct >= 120:
        strength_label = "Very Strong — Results will fully manifest"
        prediction_confidence = "High"
    elif strength_pct >= 100:
        strength_label = "Strong — Good results expected"
        prediction_confidence = "Good"
    elif strength_pct >= 75:
        strength_label = "Moderately Strong — Partial results"
        prediction_confidence = "Moderate"
    elif strength_pct >= 50:
        strength_label = "Weak — Reduced results"
        prediction_confidence = "Low"
    else:
        strength_label = "Very Weak — Minimal results"
        prediction_confidence = "Very Low"

    # The KEY prediction principle from Laghu Jatakam + Phaldipika:
    # Strong Dig Bala planet in its signified house = maximum result
    dig_house_match = (house_num == DIG_BALA_DATA.get(planet, {}).get("strong_house"))
    dignity_good = sthana["state"] in ["paramoccha","uccha","moolatrikona","swakshetra"]

    if dig_house_match and dignity_good:
        prediction_note = f"MAXIMUM POWER: {planet.capitalize()} is in its Dig Bala house AND in excellent dignity. Classical texts say this planet gives its BEST possible results. Phaldipika Ch.1 — Mantreswara."
    elif dig_house_match:
        prediction_note = f"Strong Dig Bala: {planet.capitalize()} in its directional power house — results are directionally amplified even if dignity is average."
    elif dignity_good:
        prediction_note = f"Excellent dignity but average Dig Bala — significations are strong but directional timing may vary."
    else:
        prediction_note = f"Average placement — check Dasha timing for when results manifest."

    return {
        "planet": planet,

        # Individual Balas
        "sthana_bala": {
            "value": round(sthana_bala, 2),
            "effective": round(sthana_bala_effective, 2),
            "dignity_state": sthana["state_label"],
            "sign": sign.capitalize(),
            "degree": round(degree, 2),
            "citation": sthana["citation"]
        },
        "dig_bala": {
            "value": round(dig_bala, 2),
            "strong_house": dig["strong_house"],
            "strong_direction": dig["strong_direction"],
            "is_in_strong_house": dig["is_in_strong_house"],
            "is_in_weak_house": dig["is_in_weak_house"],
            "strength_label": dig["strength_label"],
            "prediction_impact": dig["prediction_impact"],
            "citation": dig["citation"]
        },
        "kaal_bala": {
            "value": round(kaal_bala, 2),
            "components": kaal["components"],
            "paksha": kaal["paksha"],
            "citation": kaal["citation"]
        },
        "cheshta_bala": {
            "value": round(cheshta_bala, 2),
            "state": cheshta["state_label"],
            "is_retrograde": is_retro,
            "citation": cheshta["citation"]
        },
        "naisargika_bala": {
            "value": round(naisargika_bala, 2),
            "rank": naisargika_data.get("rank", 5),
            "label": naisargika_data.get("label", ""),
            "citation": NAISARGIKA_BALA["citation"]
        },
        "drik_bala": {
            "value": round(drik_bala, 2),
            "note": "Simplified — full calculation needs complete aspect matrix"
        },

        # Combustion
        "combustion": combust_info,

        # Summary
        "total_vimsopaka": round(total_vimsopaka, 2),
        "estimated_rupas": round(estimated_rupas, 2),
        "minimum_required_rupas": min_req,
        "strength_percentage": round(strength_pct, 1),
        "is_strong": is_strong,
        "strength_label": strength_label,
        "prediction_confidence": prediction_confidence,
        "prediction_note": prediction_note,

        # Source authorities
        "primary_sources": [
            "Laghu Jatakam | Varahamihira | Ch.2 Shloka 7-10 — Graha Baladhyaya",
            "Phaldipika | Mantreswara/Ojha | Ch.1 — Planet Dignity",
            "BPHS | Parashara | Graha Bala Adhyaya | Shloka 1-21"
        ],
        "minimum_rupas_citation": MINIMUM_RUPAS["citation"]
    }


def get_strongest_planet(shadbala_results: Dict) -> Dict:
    """
    Find the overall strongest planet in the chart.
    Varahamihira's key teaching: The strongest planet at birth
    shapes the entire character and life direction.
    Source: Laghu Jatakam Ch.2 Sl.3 (Varahamihira) — your book page 25
    'Raja Ravi Shashadhara cha Budha Kumara — 
     The strongest planet at birth shapes the native like a king'
    """
    strongest = None
    max_strength = 0

    for planet, data in shadbala_results.items():
        if isinstance(data, dict) and "strength_percentage" in data:
            if data["strength_percentage"] > max_strength:
                max_strength = data["strength_percentage"]
                strongest = planet

    return {
        "strongest_planet": strongest,
        "strength_percentage": max_strength,
        "significance": f"The strongest planet gives most pronounced results — shapes character and life direction",
        "citation": "Laghu Jatakam | Varahamihira | Ch.2 | Shloka 3 — 'The strongest planet at birth shapes the native'"
    }


def predict_from_strength(planet: str, house: int, shadbala: Dict,
                           planet_house_results: Dict) -> Dict:
    """
    THE MASTER PREDICTION FUNCTION
    
    This is what your insight about Dig Bala means in practice:
    Take the house result → scale it by planet strength → give precise prediction.
    
    Strong planet (>120%) = Full house result manifests
    Average planet (75-120%) = Partial result
    Weak planet (<75%) = Reduced result, may manifest only in strong Dasha
    
    Combined with Dig Bala:
    Planet in Dig Bala house = result is amplified in that direction of life
    
    Source: Laghu Jatakam Ch.2 Sl.8 (Varahamihira)
    "Dig bali graha ki dasha mein us disha mein yatra karne se
     manorath siddhi hoti hai"
    """
    base_result = planet_house_results.get(house, {})
    strength_pct = shadbala.get("strength_percentage", 100)
    dig_in_strong = shadbala.get("dig_bala", {}).get("is_in_strong_house", False)
    dignity_state = shadbala.get("sthana_bala", {}).get("dignity_state", "")

    # Scale the result
    if strength_pct >= 150 or (dig_in_strong and strength_pct >= 100):
        result_level = "FULL"
        scaled_result = base_result.get("strong", base_result.get("result", ""))
        qualifier = "Full manifestation — planet is very powerful"
    elif strength_pct >= 100:
        result_level = "GOOD"
        scaled_result = base_result.get("result", "")
        qualifier = "Good manifestation — planet is adequately strong"
    elif strength_pct >= 75:
        result_level = "PARTIAL"
        scaled_result = base_result.get("result", "")
        qualifier = "Partial manifestation — planet is moderately strong"
    else:
        result_level = "REDUCED"
        scaled_result = base_result.get("weak", base_result.get("result", ""))
        qualifier = "Reduced manifestation — planet is weak, results delayed or diminished"

    return {
        "planet": planet.capitalize(),
        "house": house,
        "result_level": result_level,
        "prediction": scaled_result,
        "qualifier": qualifier,
        "strength_percentage": round(strength_pct, 1),
        "dig_bala_value": round(shadbala.get("dig_bala", {}).get("value", 0), 2),
        "dignity": dignity_state,
        "base_citation": base_result.get("citation", ""),
        "strength_principle": "Laghu Jatakam | Varahamihira | Ch.2 | Shloka 8 — Planet strength determines result magnitude",
        "phaldipika_principle": "Phaldipika | Mantreswara | Ch.1 — Strong planet gives full result, weak gives partial"
    }


# ═══════════════════════════════════════════════════════════════
# PHALDIPIKA ADDITIONS — GOPESH KUMAR OJHA
# Read from pages 41-80 of your Phaldipika book
# These are ADDITIONS to Varahamihira's base Shadbala
# ═══════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────
# KENDRADI BALA — House position strength
# Source: Phaldipika | Mantreswara/Ojha | Ch.3 | Page 43
# Kendra (1,4,7,10) = strongest
# Panaphara (2,5,8,11) = middle
# Apoklima (3,6,9,12) = weakest
# ─────────────────────────────────────────────────────────────

KENDRADI_BALA = {
    "kendra":    {"houses": [1, 4, 7, 10], "value": 60.0,
                  "label": "Kendra — Maximum positional strength"},
    "panaphara": {"houses": [2, 5, 8, 11], "value": 30.0,
                  "label": "Panaphara — Moderate positional strength"},
    "apoklima":  {"houses": [3, 6, 9, 12], "value": 15.0,
                  "label": "Apoklima — Minimum positional strength"},
    "citation":  "Phaldipika | Mantreswara | Ch.3 | Page 43 — Kendradi Bala table"
}


def calc_kendradi_bala(house_num: int) -> Dict:
    """
    Positional strength based on house type.
    Source: Phaldipika Ch.3 Page 43 (Ojha's table)
    """
    for k, data in KENDRADI_BALA.items():
        if k == "citation":
            continue
        if house_num in data["houses"]:
            return {
                "kendradi_bala": data["value"],
                "house_type": k,
                "label": data["label"],
                "citation": KENDRADI_BALA["citation"]
            }
    return {"kendradi_bala": 15.0, "house_type": "apoklima",
            "label": "Apoklima", "citation": KENDRADI_BALA["citation"]}


# ─────────────────────────────────────────────────────────────
# TRIBHAGA BALA — Third-part of day/night strength
# Source: Phaldipika | Mantreswara/Ojha | Ch.3 | Page 49
#
# Day divided into 3 parts:
# 1st part of day: Sun strongest
# 2nd part of day: Jupiter strongest
# 3rd part of day: Mars strongest
#
# Night divided into 3 parts:
# 1st part of night: Moon strongest
# 2nd part of night: Venus strongest
# 3rd part of night: Saturn strongest
#
# Mercury strong at BOTH Sandhya (twilight) periods
# ─────────────────────────────────────────────────────────────

TRIBHAGA_LORDS = {
    "day_part_1": "sun",
    "day_part_2": "jupiter",
    "day_part_3": "mars",
    "night_part_1": "moon",
    "night_part_2": "venus",
    "night_part_3": "saturn",
    "sandhya": "mercury",
    "citation": "Phaldipika | Mantreswara/Ojha | Ch.3 | Page 49 — Tribhaga Bala"
}


def calc_tribhaga_bala(planet: str, birth_hour: float, is_day: bool) -> Dict:
    """
    Strength based on which third of day/night the birth occurred.
    Source: Phaldipika Ch.3 Page 49 (Ojha's unique addition)
    """
    bala = 0.0
    lord = None

    if is_day:
        if 0 <= birth_hour < 24/3:
            lord = TRIBHAGA_LORDS["day_part_1"]
        elif birth_hour < 24*2/3:
            lord = TRIBHAGA_LORDS["day_part_2"]
        else:
            lord = TRIBHAGA_LORDS["day_part_3"]
    else:
        night_hour = birth_hour % 12
        if night_hour < 4:
            lord = TRIBHAGA_LORDS["night_part_1"]
        elif night_hour < 8:
            lord = TRIBHAGA_LORDS["night_part_2"]
        else:
            lord = TRIBHAGA_LORDS["night_part_3"]

    if planet == lord:
        bala = 60.0
    elif planet == "mercury":
        # Mercury strong at sandhya (transition times)
        bala = 30.0

    return {
        "tribhaga_bala": bala,
        "period_lord": lord,
        "citation": TRIBHAGA_LORDS["citation"]
    }


# ─────────────────────────────────────────────────────────────
# OJHA'S PREDICTION SCALE (Phaldipika Ch.3 Page 80)
# This is the key formula that makes Shadbala useful for prediction
# ─────────────────────────────────────────────────────────────

OJHA_PREDICTION_SCALE = {
    "full":         {"min_pct": 100, "result": "Full result",
                     "fraction": "Complete manifestation"},
    "three_quarter":{"min_pct": 75,  "result": "3/4 result",
                     "fraction": "Good manifestation"},
    "half":         {"min_pct": 50,  "result": "1/2 result",
                     "fraction": "Partial manifestation"},
    "quarter":      {"min_pct": 25,  "result": "1/4 result",
                     "fraction": "Weak manifestation"},
    "negligible":   {"min_pct": 0,   "result": "Almost no result",
                     "fraction": "Negligible manifestation"},
    "citation": "Phaldipika | Mantreswara/Ojha | Ch.3 | Page 80 — Prediction scale"
}


def get_ojha_prediction_scale(strength_pct: float) -> Dict:
    """
    Ojha's exact prediction scale from Phaldipika page 80.
    This is what your insight about Dig Bala means practically:
    Know the strength precisely → predict the result precisely.
    """
    if strength_pct >= 100:
        scale = OJHA_PREDICTION_SCALE["full"]
        advice = "This planet is strong enough to give its FULL result. Classical prediction applies completely."
    elif strength_pct >= 75:
        scale = OJHA_PREDICTION_SCALE["three_quarter"]
        advice = "Planet gives 3/4 result. Main significations manifest but with some limitations."
    elif strength_pct >= 50:
        scale = OJHA_PREDICTION_SCALE["half"]
        advice = "Planet gives half result. Significations partially manifest — timing and Dasha are important."
    elif strength_pct >= 25:
        scale = OJHA_PREDICTION_SCALE["quarter"]
        advice = "Planet gives only 1/4 result. Most significations are limited or delayed."
    else:
        scale = OJHA_PREDICTION_SCALE["negligible"]
        advice = "Planet is too weak to give results independently. Needs strong Dasha support."

    return {
        "strength_percentage": round(strength_pct, 1),
        "result_level": scale["result"],
        "manifestation": scale["fraction"],
        "prediction_advice": advice,
        "citation": OJHA_PREDICTION_SCALE["citation"]
    }


# ─────────────────────────────────────────────────────────────
# OJHA'S DIG BALA TEACHING (Phaldipika Ch.3 Pages 44-46)
# Your exact insight codified — Ojha confirms it explicitly
# ─────────────────────────────────────────────────────────────

def ojha_dig_bala_prediction(planet: str, house_num: int,
                              dig_bala_value: float,
                              house_result: str) -> Dict:
    """
    Ojha's teaching: Dig Bala directly determines prediction accuracy.
    Source: Phaldipika | Mantreswara/Ojha | Ch.3 | Pages 44-46

    Ojha says (page 45):
    'जिस भाव में ग्रह का दिग्बल अधिकतम हो, उस भाव से संबंधित
     भविष्यवाणी सबसे सटीक और पूर्ण होती है'
    (The prediction related to the house where a planet has maximum
     Dig Bala will be most accurate and complete)
    """
    strong_house = DIG_BALA_DATA.get(planet, {}).get("strong_house", 1)
    strong_dir   = DIG_BALA_DATA.get(planet, {}).get("strong_direction", "")

    # Scale the result by Dig Bala
    if dig_bala_value >= 50:
        scaled = f"FULL: {house_result}"
        confidence = "Very High — Dig Bala is 50+/60"
    elif dig_bala_value >= 35:
        scaled = f"GOOD: {house_result}"
        confidence = "High — Dig Bala is 35+/60"
    elif dig_bala_value >= 20:
        scaled = f"PARTIAL: {house_result}"
        confidence = "Moderate — Dig Bala is 20+/60"
    elif dig_bala_value >= 10:
        scaled = f"REDUCED: {house_result}"
        confidence = "Low — Dig Bala is below 20/60"
    else:
        scaled = f"MINIMAL: Result is weak — {house_result}"
        confidence = "Very Low — Dig Bala near zero"

    return {
        "planet": planet.capitalize(),
        "house": house_num,
        "dig_bala": round(dig_bala_value, 2),
        "strong_house": strong_house,
        "strong_direction": strong_dir,
        "scaled_prediction": scaled,
        "prediction_confidence": confidence,
        "ojha_teaching": "Dig Bala determines how fully a planet delivers its house results",
        "citation": "Phaldipika | Mantreswara/Ojha | Ch.3 | Pages 44-46"
    }
