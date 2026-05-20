"""
AETHERIS — Vimshottari Dasha Engine
Complete Mahadasha/Antardasha calculation
Source: BPHS Vimshottari Dasha Adhyaya (Parashara)
        Phaldipika Ch.17 (Mantreswara)
"""
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from app.classical_knowledge import (
    VIMSHOTTARI_YEARS, NAKSHATRA_DASHA_LORD, DASHA_ORDER, NAKSHATRAS
)


TOTAL_YEARS = 120


def get_nakshatra_number(longitude: float) -> int:
    """Get Nakshatra number (1-27) from longitude."""
    return int((longitude * 27) / 360) % 27 + 1


def get_dasha_balance_at_birth(moon_lon: float, birth_jd: float) -> Dict:
    """
    Calculate remaining Dasha balance at birth from Moon's Nakshatra.
    Source: BPHS Vimshottari Dasha Adhyaya | Parashara | Shloka 4-6
    """
    nak_num = get_nakshatra_number(moon_lon)
    nak_data = NAKSHATRAS[nak_num]
    dasha_lord = NAKSHATRA_DASHA_LORD[nak_num]
    total_dasha_years = VIMSHOTTARI_YEARS[dasha_lord]["years"]

    # Position within Nakshatra (0 to 1)
    nak_start = nak_data["start_deg"]
    nak_end = nak_data["end_deg"]
    nak_span = nak_end - nak_start
    pos_in_nak = (moon_lon - nak_start) / nak_span  # 0 = start, 1 = end

    # Remaining fraction of Nakshatra = remaining Dasha balance
    remaining_fraction = 1.0 - pos_in_nak
    balance_years = total_dasha_years * remaining_fraction

    return {
        "nakshatra": nak_data["name"],
        "nakshatra_number": nak_num,
        "nakshatra_lord": dasha_lord.capitalize(),
        "current_dasha_lord": dasha_lord,
        "balance_years": round(balance_years, 4),
        "balance_days": round(balance_years * 365.25, 0),
        "moon_longitude": round(moon_lon, 4),
        "position_in_nakshatra_percent": round(pos_in_nak * 100, 2),
        "citation": "BPHS Vimshottari Dasha Adhyaya | Parashara | Shloka 4-6"
    }


def calculate_vimshottari_dashas(moon_lon: float, birth_date: datetime,
                                  years_to_compute: int = 120) -> List[Dict]:
    """
    Calculate complete Vimshottari Dasha sequence with Antardasha.
    Source: BPHS Vimshottari Dasha Adhyaya | Parashara | Shloka 3-12
    """
    balance = get_dasha_balance_at_birth(moon_lon, 0)
    start_lord = balance["current_dasha_lord"]
    balance_years = balance["balance_years"]

    # Find starting position in Dasha order
    start_idx = DASHA_ORDER.index(start_lord)

    dashas = []
    current_date = birth_date

    for i in range(len(DASHA_ORDER)):
        idx = (start_idx + i) % len(DASHA_ORDER)
        maha_lord = DASHA_ORDER[idx]
        maha_years = VIMSHOTTARI_YEARS[maha_lord]["years"]

        # First Mahadasha uses remaining balance
        if i == 0:
            actual_years = balance_years
        else:
            actual_years = maha_years

        maha_start = current_date
        maha_end = current_date + timedelta(days=actual_years * 365.25)

        # Calculate Antardashas within this Mahadasha
        antardashas = _calc_antardashas(
            maha_lord, maha_start, actual_years, DASHA_ORDER, idx
        )

        dasha_entry = {
            "mahadasha_lord": maha_lord.capitalize(),
            "mahadasha_years": round(actual_years, 4),
            "start_date": maha_start.strftime("%d %b %Y"),
            "end_date": maha_end.strftime("%d %b %Y"),
            "antardashas": antardashas,
            "general_results": _maha_results(maha_lord),
            "citation": VIMSHOTTARI_YEARS[maha_lord]["citation"]
        }

        dashas.append(dasha_entry)
        current_date = maha_end

        # Stop after computing enough years
        if (current_date - birth_date).days > years_to_compute * 365:
            break

    return dashas


def _calc_antardashas(maha_lord: str, maha_start: datetime,
                       maha_years: float, order: List, start_idx: int) -> List[Dict]:
    """
    Calculate Antardashas within a Mahadasha.
    Formula: Antardasha years = (Maha years × Antar years) / 120
    Source: BPHS Vimshottari Dasha Adhyaya | Parashara | Shloka 7
    """
    antardashas = []
    current = maha_start

    for i in range(len(order)):
        antar_idx = (start_idx + i) % len(order)
        antar_lord = order[antar_idx]
        antar_total_years = VIMSHOTTARI_YEARS[antar_lord]["years"]

        # Core formula from BPHS
        antar_duration_years = (maha_years * antar_total_years) / TOTAL_YEARS
        antar_end = current + timedelta(days=antar_duration_years * 365.25)

        antardashas.append({
            "antardasha_lord": antar_lord.capitalize(),
            "duration_years": round(antar_duration_years, 4),
            "duration_months": round(antar_duration_years * 12, 1),
            "start_date": current.strftime("%d %b %Y"),
            "end_date": antar_end.strftime("%d %b %Y"),
            "results_hint": _antar_results_hint(maha_lord, antar_lord),
            "formula_citation": "BPHS Vimshottari Dasha Adhyaya | Parashara | Shloka 7 — Formula: (Maha years × Antar years) ÷ 120"
        })
        current = antar_end

    return antardashas


def _maha_results(lord: str) -> Dict:
    """
    General Mahadasha results.
    Source: BPHS Vimshottari Dasha Adhyaya (Parashara)
            Phaldipika Ch.17 (Mantreswara)
    """
    results = {
        "sun": {
            "positive": "Authority, government favour, father's blessings, good health, leadership",
            "negative": "Ego conflicts, separation from family, father's health issues",
            "citation": "BPHS Vimshottari Dasha Adhyaya | Parashara | Sun Dasha | Shloka 15"
        },
        "moon": {
            "positive": "Emotional happiness, mother's blessings, travel, wealth from trade",
            "negative": "Mental instability, health issues related to fluids, mother's health",
            "citation": "BPHS Vimshottari Dasha Adhyaya | Parashara | Moon Dasha | Shloka 20"
        },
        "mars": {
            "positive": "Courage, land/property gains, victory over enemies, brother's support",
            "negative": "Accidents, conflicts, blood-related diseases, disputes over property",
            "citation": "BPHS Vimshottari Dasha Adhyaya | Parashara | Mars Dasha | Shloka 25"
        },
        "rahu": {
            "positive": "Foreign travel, unconventional gains, political rise, worldly success",
            "negative": "Confusion, health issues, unexpected obstacles, family separation",
            "citation": "BPHS Vimshottari Dasha Adhyaya | Parashara | Rahu Dasha | Shloka 30"
        },
        "jupiter": {
            "positive": "Wisdom, children, wealth, religious activities, guru's blessings, fame",
            "negative": "Overconfidence, weight gain, liver issues if afflicted",
            "citation": "BPHS Vimshottari Dasha Adhyaya | Parashara | Jupiter Dasha | Shloka 35"
        },
        "saturn": {
            "positive": "Hard work rewarded, discipline, longevity, property, service gains",
            "negative": "Depression, delays, chronic illness, separation, losses if afflicted",
            "citation": "BPHS Vimshottari Dasha Adhyaya | Parashara | Saturn Dasha | Shloka 40"
        },
        "mercury": {
            "positive": "Intelligence, business, communication, education, writing, trade",
            "negative": "Nervous system issues, skin problems, speech issues if afflicted",
            "citation": "BPHS Vimshottari Dasha Adhyaya | Parashara | Mercury Dasha | Shloka 45"
        },
        "ketu": {
            "positive": "Spiritual growth, occult knowledge, liberation, moksha tendency",
            "negative": "Health issues, accidents, unexpected losses, confusion",
            "citation": "BPHS Vimshottari Dasha Adhyaya | Parashara | Ketu Dasha | Shloka 50"
        },
        "venus": {
            "positive": "Marriage, luxury, vehicles, arts, wealth, pleasure, beauty",
            "negative": "Overindulgence, marital issues if afflicted, kidney problems",
            "citation": "BPHS Vimshottari Dasha Adhyaya | Parashara | Venus Dasha | Shloka 55"
        }
    }
    return results.get(lord, {"positive": "General results", "negative": "Depends on placement"})


def _antar_results_hint(maha: str, antar: str) -> str:
    """
    Key Antardasha combinations.
    Source: BPHS Vimshottari Dasha Adhyaya (Parashara)
    """
    key_combos = {
        ("jupiter", "venus"):   "Excellent — both benefics — wealth, marriage, happiness | BPHS Dasha Adhyaya Sl.36",
        ("venus", "jupiter"):   "Excellent — wealth, auspicious events, spiritual progress | BPHS Dasha Adhyaya Sl.56",
        ("saturn", "rahu"):     "Difficult — Shani-Rahu Antardasha — obstacles, confusion, delays | BPHS Dasha Adhyaya Sl.42",
        ("rahu", "saturn"):     "Difficult — delays, health issues, unexpected problems | BPHS Dasha Adhyaya Sl.31",
        ("saturn", "ketu"):     "Spiritually intense — detachment, losses, moksha tendency | BPHS Dasha Adhyaya Sl.43",
        ("jupiter", "saturn"):  "Mixed — discipline meets wisdom — service, hard work with rewards | BPHS Dasha Adhyaya Sl.37",
        ("sun", "moon"):        "Family focus, emotional matters, mother and father interactions | BPHS Dasha Adhyaya Sl.16",
        ("moon", "rahu"):       "Mental turbulence, unexpected events, travel | BPHS Dasha Adhyaya Sl.21",
        ("mars", "saturn"):     "Accident prone, conflicts, property disputes — caution needed | BPHS Dasha Adhyaya Sl.27",
    }
    hint = key_combos.get((maha, antar), "")
    if not hint:
        # General rule based on natural relationship
        benefics = ["jupiter", "venus", "moon", "mercury"]
        malefics = ["saturn", "mars", "sun", "rahu", "ketu"]
        if maha in benefics and antar in benefics:
            hint = "Both planets are natural benefics — generally favourable period"
        elif maha in malefics and antar in malefics:
            hint = "Both planets are natural malefics — challenging period, depends on chart"
        else:
            hint = "Mixed period — depends on house lordship and natal strength"
    return hint


def get_current_dasha(moon_lon: float, birth_date: datetime) -> Dict:
    """
    Find the current active Mahadasha and Antardasha.
    """
    all_dashas = calculate_vimshottari_dashas(moon_lon, birth_date, 120)
    today = datetime.now()

    for dasha in all_dashas:
        start = datetime.strptime(dasha["start_date"], "%d %b %Y")
        end = datetime.strptime(dasha["end_date"], "%d %b %Y")
        if start <= today <= end:
            # Find current Antardasha
            current_antar = None
            for antar in dasha["antardashas"]:
                a_start = datetime.strptime(antar["start_date"], "%d %b %Y")
                a_end = datetime.strptime(antar["end_date"], "%d %b %Y")
                if a_start <= today <= a_end:
                    current_antar = antar
                    break

            return {
                "current_mahadasha": dasha["mahadasha_lord"],
                "mahadasha_ends": dasha["end_date"],
                "current_antardasha": current_antar["antardasha_lord"] if current_antar else "N/A",
                "antardasha_ends": current_antar["end_date"] if current_antar else "N/A",
                "mahadasha_results": dasha["general_results"],
                "antardasha_results_hint": current_antar["results_hint"] if current_antar else "",
                "citation": "BPHS Vimshottari Dasha Adhyaya | Parashara | Shloka 3-12"
            }

    return {"error": "Could not determine current dasha"}
