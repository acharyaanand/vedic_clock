"""
AETHERIS — Shadbala Engine
Six-fold planetary strength calculation
Source: BPHS Graha Bala Adhyaya (Parashara)
        Brihat Jataka Ch.1 Sl.15 (Varahamihira)
"""
import math
from typing import Dict
from classical_knowledge import (
    PLANET_DIGNITY, DIG_BALA_HOUSES, NAISARGIKA_BALA, COMBUSTION_ORBS
)


SIGNS = ["aries","taurus","gemini","cancer","leo","virgo",
         "libra","scorpio","sagittarius","capricorn","aquarius","pisces"]

SIGN_INDEX = {s: i for i, s in enumerate(SIGNS)}


def get_dignity_state(planet: str, sign: str, degree: float) -> Dict:
    """
    Determine exact dignity state of a planet.
    Source: BPHS Rashi Bheda Adhyaya (Parashara) Sl.38-42
            Brihat Jataka Ch.1 Sl.13 (Varahamihira)
            Phaldipika Ch.1 Sl.7 (Mantreswara)
    """
    if planet not in PLANET_DIGNITY:
        return {"state": "unknown", "sthana_bala": 0, "citation": "N/A"}

    d = PLANET_DIGNITY[planet]
    state = "enemy"
    sthana_bala = 7.5  # minimum

    # Exaltation — BPHS Sl.38
    if sign == d.get("exaltation_sign"):
        if abs(degree - d.get("exaltation_degree", 0)) <= 1:
            state = "paramoccha"    # deepest exaltation
            sthana_bala = 60.0
        else:
            state = "uccha"
            # Graduated: closer to exact degree = more bala
            dist = abs(degree - d.get("exaltation_degree", 0))
            sthana_bala = max(30.0, 60.0 - dist * 1.5)

    # Debilitation — BPHS Sl.39
    elif sign == d.get("debilitation_sign"):
        if abs(degree - d.get("debilitation_degree", 0)) <= 1:
            state = "paramaneecha"  # deepest debilitation
            sthana_bala = 0.0
        else:
            state = "neecha"
            dist = abs(degree - d.get("debilitation_degree", 0))
            sthana_bala = min(15.0, dist * 0.5)

    # Moolatrikona — BPHS Sl.40
    elif (sign == d.get("moolatrikona_sign") and
          d.get("moolatrikona_start", 0) <= degree <= d.get("moolatrikona_end", 0)):
        state = "moolatrikona"
        sthana_bala = 45.0

    # Own sign — BPHS Sl.41
    elif sign in d.get("own_signs", []):
        state = "swakshetra"
        sthana_bala = 30.0

    # Friendly sign
    elif sign in d.get("friendly_signs", []):
        state = "mitra_kshetra"
        sthana_bala = 22.5

    # Enemy sign
    elif sign in d.get("enemy_signs", []):
        state = "shatru_kshetra"
        sthana_bala = 7.5

    else:
        state = "sama_kshetra"  # neutral
        sthana_bala = 15.0

    return {
        "state": state,
        "state_label": _dignity_label(state),
        "sthana_bala_vimsopaka": sthana_bala,
        "citation": d.get("citation", {})
    }


def _dignity_label(state: str) -> str:
    labels = {
        "paramoccha":    "Deepest Exaltation (Paramoccha) — Maximum strength",
        "uccha":         "Exalted (Uccha) — Very strong",
        "moolatrikona":  "Moolatrikona — Strong",
        "swakshetra":    "Own Sign (Swakshetra) — Strong",
        "mitra_kshetra": "Friendly Sign — Moderate",
        "sama_kshetra":  "Neutral Sign — Average",
        "shatru_kshetra":"Enemy Sign — Weak",
        "neecha":        "Debilitated (Neecha) — Very weak",
        "paramaneecha":  "Deepest Debilitation (Paramaneecha) — Minimum strength",
    }
    return labels.get(state, state)


def calc_dig_bala(planet: str, house_num: int) -> Dict:
    """
    Directional Strength calculation.
    Source: BPHS Graha Bala Adhyaya | Parashara | Shloka 12
    """
    if planet not in DIG_BALA_HOUSES:
        return {"dig_bala": 0, "citation": "N/A"}

    strong_house = DIG_BALA_HOUSES[planet]["strong_house"]
    weak_house = DIG_BALA_HOUSES[planet]["weak_house"]

    # Distance from strong house determines strength
    strong_dist = abs(house_num - strong_house)
    if strong_dist > 6:
        strong_dist = 12 - strong_dist
    weak_dist = abs(house_num - weak_house)
    if weak_dist > 6:
        weak_dist = 12 - weak_dist

    # Maximum 60 Vimsopaka at strong house, 0 at weak house
    dig_bala = (strong_dist / 6.0) * 60.0
    if house_num == strong_house:
        dig_bala = 60.0
    elif house_num == weak_house:
        dig_bala = 0.0

    return {
        "dig_bala": round(dig_bala, 2),
        "strong_house": strong_house,
        "is_in_strong_house": house_num == strong_house,
        "is_in_weak_house": house_num == weak_house,
        "citation": DIG_BALA_HOUSES[planet]["citation"]
    }


def calc_cheshta_bala(planet: str, speed: float, is_retrograde: bool) -> Dict:
    """
    Motional Strength.
    Source: BPHS Graha Bala Adhyaya | Parashara | Shloka 15
    """
    # Retrograde planets get enhanced Cheshta Bala
    # Source: BPHS Graha Bala Adhyaya Sl.15
    if is_retrograde:
        bala = 60.0
        state = "Vakri (Retrograde) — Maximum Cheshta Bala"
        citation = "BPHS Graha Bala Adhyaya | Parashara | Shloka 15 — Retrograde planets have highest motional strength"
    elif abs(speed) < 0.1:
        bala = 0.0
        state = "Vikala (Stationary) — Minimum Cheshta Bala"
        citation = "BPHS Graha Bala Adhyaya | Parashara | Shloka 15"
    elif abs(speed) > 1.0:
        bala = 15.0
        state = "Atichara (Very fast) — Low Cheshta Bala"
        citation = "BPHS Graha Bala Adhyaya | Parashara | Shloka 15"
    else:
        bala = 30.0
        state = "Normal motion — Average Cheshta Bala"
        citation = "BPHS Graha Bala Adhyaya | Parashara | Shloka 15"

    return {"cheshta_bala": bala, "state": state, "citation": citation}


def check_combustion(planet: str, planet_lon: float, sun_lon: float,
                     is_retrograde: bool = False) -> Dict:
    """
    Combustion check.
    Source: BPHS Graha Bala Adhyaya | Parashara | Shloka 17
    """
    if planet == "sun" or planet not in COMBUSTION_ORBS:
        return {"is_combust": False, "is_deep_combust": False, "citation": "N/A"}

    orb_data = COMBUSTION_ORBS[planet]
    dist = abs(planet_lon - sun_lon) % 360
    if dist > 180:
        dist = 360 - dist

    # Mercury and Venus have different orbs when retrograde
    if planet in ["mercury", "venus"] and is_retrograde:
        combust_orb = orb_data.get("combust_retro", orb_data.get("combust", 15))
    else:
        combust_orb = orb_data.get("combust_direct", orb_data.get("combust", 15))

    deep_orb = orb_data.get("deep_combust", 3)

    is_combust = dist <= combust_orb
    is_deep_combust = dist <= deep_orb

    return {
        "is_combust": is_combust,
        "is_deep_combust": is_deep_combust,
        "distance_from_sun": round(dist, 2),
        "combust_orb": combust_orb,
        "effect": "Planet severely weakened — classical predictions significantly reduced" if is_combust else "Normal",
        "citation": orb_data.get("citation", "BPHS Graha Bala Adhyaya | Parashara | Shloka 17")
    }


def calc_complete_shadbala(planet: str, planet_data: Dict, house_num: int,
                            sun_lon: float, birth_details: Dict) -> Dict:
    """
    Complete Shadbala — all 6 components.
    Source: BPHS Graha Bala Adhyaya (Parashara)
    Minimum required Rupas (from BPHS):
    Sun=390, Moon=360, Mars=300, Mercury=420,
    Jupiter=390, Venus=330, Saturn=300
    """
    MIN_REQUIRED = {
        "sun": 390, "moon": 360, "mars": 300,
        "mercury": 420, "jupiter": 390, "venus": 330, "saturn": 300,
        "citation": "BPHS Graha Bala Adhyaya | Parashara | Shloka 21"
    }

    # 1. Sthana Bala (Positional)
    dignity = get_dignity_state(
        planet, planet_data.get("sign", ""), planet_data.get("degree", 0)
    )
    sthana_bala = dignity["sthana_bala_vimsopaka"]

    # 2. Dig Bala (Directional)
    dig = calc_dig_bala(planet, house_num)
    dig_bala = dig["dig_bala"]

    # 3. Kaal Bala (simplified — full version needs birth time)
    naisargika = NAISARGIKA_BALA.get(planet, {}).get("rupas", 30.0)

    # 4. Cheshta Bala (Motional)
    cheshta = calc_cheshta_bala(
        planet, planet_data.get("speed_long", 0.5),
        planet_data.get("is_retrograde", False)
    )
    cheshta_bala = cheshta["cheshta_bala"]

    # 5. Naisargika Bala
    naisargika_bala = naisargika

    # 6. Drik Bala (aspectual — simplified)
    drik_bala = 30.0  # Default — full calculation needs all aspects

    # Combustion check
    combust = check_combustion(
        planet, planet_data.get("longitude", 0), sun_lon,
        planet_data.get("is_retrograde", False)
    )

    # Reduce Sthana Bala if combust
    if combust["is_deep_combust"]:
        sthana_bala *= 0.1
    elif combust["is_combust"]:
        sthana_bala *= 0.5

    total_vimsopaka = (
        sthana_bala + dig_bala + cheshta_bala + naisargika_bala + drik_bala
    ) / 5  # Average for simplified score out of 60

    min_req = MIN_REQUIRED.get(planet, 300)
    total_rupas_est = total_vimsopaka * 7  # Rough conversion to Rupas
    is_strong = total_rupas_est >= min_req

    return {
        "planet": planet,
        "sthana_bala": round(sthana_bala, 2),
        "dig_bala": round(dig_bala, 2),
        "cheshta_bala": round(cheshta_bala, 2),
        "naisargika_bala": round(naisargika_bala, 2),
        "drik_bala": round(drik_bala, 2),
        "total_vimsopaka": round(total_vimsopaka, 2),
        "estimated_rupas": round(total_rupas_est, 2),
        "minimum_required_rupas": min_req,
        "is_strong": is_strong,
        "strength_label": "Strong" if is_strong else "Weak",
        "dignity_state": dignity["state_label"],
        "combustion": combust,
        "dig_bala_detail": dig,
        "cheshta_detail": cheshta,
        "shadbala_citation": "BPHS Graha Bala Adhyaya | Parashara | Shloka 1-21",
        "minimum_rupas_citation": "BPHS Graha Bala Adhyaya | Parashara | Shloka 21"
    }
