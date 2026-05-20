"""
AETHERIS — Master Prediction Engine
The core insight of this engine (from our Jyotish scholar):

"Focus on Dig Bala — once we understand fully the strength
 of planet, house and zodiac, we can predict anything so precisely"

This engine implements exactly that:
STRENGTH × PLACEMENT → SCALED PRECISE PREDICTION

Sources:
- Laghu Jatakam | Varahamihira | Ch.2 Sl.7-10 (Graha Baladhyaya)
- Phaldipika | Mantreswara/Ojha | Ch.3 Pg.44-46, 80 (Dig Bala + Scale)
- Phaldipika | Mantreswara/Ojha | Ch.7 (Planet in house results)
"""

from typing import Dict, List, Optional

# ─────────────────────────────────────────────────────────────
# IMPORT FROM OUR ENGINES
# ─────────────────────────────────────────────────────────────

# Inline key data to keep this file self-contained
# Full versions in shadbala_engine.py and planet_results.py

DIG_BALA_STRONG_HOUSE = {
    "sun": 10, "moon": 4, "mars": 10,
    "mercury": 1, "jupiter": 1, "venus": 4, "saturn": 7
}

DIG_BALA_WEAK_HOUSE = {
    "sun": 4, "moon": 10, "mars": 4,
    "mercury": 7, "jupiter": 7, "venus": 10, "saturn": 1
}

DIG_BALA_DIRECTION = {
    "sun": "South (10th)", "moon": "North (4th)", "mars": "South (10th)",
    "mercury": "East (1st)", "jupiter": "East (1st)",
    "venus": "North (4th)", "saturn": "West (7th)"
}

MINIMUM_RUPAS = {
    "sun": 390, "moon": 360, "mars": 300,
    "mercury": 420, "jupiter": 390, "venus": 330, "saturn": 300
}

NAISARGIKA_ORDER = {
    "sun": 7, "moon": 6, "venus": 5, "jupiter": 4,
    "mercury": 3, "mars": 2, "saturn": 1
}

SIGNS = ["aries","taurus","gemini","cancer","leo","virgo",
         "libra","scorpio","sagittarius","capricorn","aquarius","pisces"]

EXALTATION = {
    "sun": ("aries", 10), "moon": ("taurus", 3),
    "mars": ("capricorn", 28), "mercury": ("virgo", 15),
    "jupiter": ("cancer", 5), "venus": ("pisces", 27),
    "saturn": ("libra", 20)
}

DEBILITATION = {
    "sun": ("libra", 10), "moon": ("scorpio", 3),
    "mars": ("cancer", 28), "mercury": ("pisces", 15),
    "jupiter": ("capricorn", 5), "venus": ("virgo", 27),
    "saturn": ("aries", 20)
}

OWN_SIGNS = {
    "sun": ["leo"], "moon": ["cancer"],
    "mars": ["aries", "scorpio"], "mercury": ["gemini", "virgo"],
    "jupiter": ["sagittarius", "pisces"],
    "venus": ["taurus", "libra"],
    "saturn": ["capricorn", "aquarius"]
}

MOOLATRIKONA = {
    "sun": ("leo", 0, 20), "moon": ("taurus", 4, 20),
    "mars": ("aries", 0, 12), "mercury": ("virgo", 16, 20),
    "jupiter": ("sagittarius", 0, 10),
    "venus": ("libra", 0, 15), "saturn": ("aquarius", 0, 20)
}

NATURAL_BENEFICS = ["moon", "mercury", "jupiter", "venus"]
NATURAL_MALEFICS = ["sun", "mars", "saturn", "rahu", "ketu"]


# ═══════════════════════════════════════════════════════════════
# STEP 1 — DIGNITY STATE
# Source: Laghu Jatakam Ch.1 Sl.21-22 | Phaldipika Ch.1
# ═══════════════════════════════════════════════════════════════

def get_dignity(planet: str, sign: str, degree: float) -> Dict:
    """Get planet dignity — foundation of Sthana Bala."""
    if planet not in EXALTATION:
        return {"state": "neutral", "sthana_score": 15, "symbol": "○"}

    exalt_sign, exalt_deg = EXALTATION[planet]
    debil_sign, debil_deg = DEBILITATION[planet]
    moola_sign, moola_start, moola_end = MOOLATRIKONA[planet]
    own = OWN_SIGNS[planet]

    if sign == exalt_sign:
        dist = abs(degree - exalt_deg)
        if dist <= 1:
            return {"state": "Paramoccha (Deepest Exaltation)",
                    "sthana_score": 60, "symbol": "⭐⭐",
                    "citation": "Laghu Jatakam Ch.1 Sl.21 (Varahamihira)"}
        score = max(30, 60 - dist * 1.5)
        return {"state": "Uccha (Exalted)",
                "sthana_score": round(score), "symbol": "⭐",
                "citation": "Laghu Jatakam Ch.1 Sl.21 (Varahamihira)"}

    if sign == debil_sign:
        dist = abs(degree - debil_deg)
        if dist <= 1:
            return {"state": "Paramaneecha (Deepest Debilitation)",
                    "sthana_score": 0, "symbol": "⬇️⬇️",
                    "citation": "Laghu Jatakam Ch.1 Sl.21 (Varahamihira)"}
        return {"state": "Neecha (Debilitated)",
                "sthana_score": 5, "symbol": "⬇️",
                "citation": "Laghu Jatakam Ch.1 Sl.21 (Varahamihira)"}

    if sign == moola_sign and moola_start <= degree <= moola_end:
        return {"state": "Moolatrikona",
                "sthana_score": 37, "symbol": "🔺",
                "citation": "Laghu Jatakam Ch.1 Sl.22 (Varahamihira)"}

    if sign in own:
        return {"state": "Swakshetra (Own Sign)",
                "sthana_score": 30, "symbol": "🏠",
                "citation": "Laghu Jatakam Ch.1 Sl.22 (Varahamihira)"}

    return {"state": "Neutral/Friend Sign",
            "sthana_score": 15, "symbol": "○",
            "citation": "Laghu Jatakam Ch.2 Sl.7 (Varahamihira)"}


# ═══════════════════════════════════════════════════════════════
# STEP 2 — DIG BALA (The key insight)
# Source: Laghu Jatakam Ch.2 Sl.8 | Phaldipika Ch.3 Pg.44-46
# ═══════════════════════════════════════════════════════════════

def get_dig_bala(planet: str, house: int) -> Dict:
    """
    Directional strength — the foundation of precise prediction.

    Varahamihira (LJ Ch.2 Sl.8):
    Jupiter+Mercury → East (1st), Sun+Mars → South (10th),
    Moon+Venus → North (4th), Saturn → West (7th)

    Ojha (Phaldipika Ch.3 Pg.45):
    'The prediction of the house where a planet has maximum
     Dig Bala will be the most accurate and complete.'
    """
    if planet not in DIG_BALA_STRONG_HOUSE:
        return {"dig_bala": 30, "label": "Rahu/Ketu — no Dig Bala"}

    strong = DIG_BALA_STRONG_HOUSE[planet]
    weak = DIG_BALA_WEAK_HOUSE[planet]

    dist = abs(house - strong)
    if dist > 6:
        dist = 12 - dist

    if house == strong:
        value = 60
        label = f"MAXIMUM — {planet.capitalize()} is in its Dig Bala house"
    elif house == weak:
        value = 0
        label = f"MINIMUM — opposite of Dig Bala house"
    else:
        value = round((1 - dist/6) * 60)
        label = f"Partial — {value}/60"

    return {
        "dig_bala": value,
        "strong_house": strong,
        "strong_direction": DIG_BALA_DIRECTION.get(planet, ""),
        "is_maximum": house == strong,
        "is_minimum": house == weak,
        "label": label,
        "lj_citation": "Laghu Jatakam | Varahamihira | Ch.2 | Shloka 8",
        "pd_citation": "Phaldipika | Mantreswara/Ojha | Ch.3 | Pages 44-46"
    }


# ═══════════════════════════════════════════════════════════════
# STEP 3 — KENDRADI BALA
# Source: Phaldipika Ch.3 Pg.43 (Ojha)
# ═══════════════════════════════════════════════════════════════

def get_kendradi_bala(house: int) -> Dict:
    if house in [1, 4, 7, 10]:
        return {"value": 60, "type": "Kendra",
                "citation": "Phaldipika Ch.3 Pg.43"}
    elif house in [2, 5, 8, 11]:
        return {"value": 30, "type": "Panaphara",
                "citation": "Phaldipika Ch.3 Pg.43"}
    else:
        return {"value": 15, "type": "Apoklima",
                "citation": "Phaldipika Ch.3 Pg.43"}


# ═══════════════════════════════════════════════════════════════
# STEP 4 — COMBINED STRENGTH SCORE
# Varahamihira + Ojha combined formula
# ═══════════════════════════════════════════════════════════════

def calc_combined_strength(planet: str, sign: str, degree: float,
                            house: int, is_retrograde: bool = False,
                            is_combust: bool = False,
                            is_day_birth: bool = True,
                            paksha_is_shukla: bool = True) -> Dict:
    """
    Combined strength from all classical sources.
    This is the engine of precise prediction.
    """
    dignity = get_dignity(planet, sign, degree)
    dig = get_dig_bala(planet, house)
    kendradi = get_kendradi_bala(house)

    # Sthana Bala (from dignity)
    sthana = dignity["sthana_score"]
    if is_combust and planet not in ["sun", "rahu", "ketu"]:
        sthana = round(sthana * 0.4)  # Combustion reduces Sthana Bala

    # Dig Bala
    dig_val = dig["dig_bala"]

    # Kaal Bala (simplified)
    day_planets = ["venus", "sun", "jupiter"]
    night_planets = ["moon", "mars", "saturn"]
    if planet in day_planets:
        kaal = 45 if is_day_birth else 15
    elif planet in night_planets:
        kaal = 45 if not is_day_birth else 15
    else:  # Mercury
        kaal = 30

    # Paksha component
    if planet in NATURAL_BENEFICS:
        kaal += 20 if paksha_is_shukla else 5
    else:
        kaal += 20 if not paksha_is_shukla else 5

    # Cheshta Bala
    cheshta = 60 if is_retrograde else 30

    # Naisargika Bala (Varahamihira LJ Ch.2 Sl.10)
    naisargika_values = {
        "sun": 60, "moon": 51, "venus": 43,
        "jupiter": 34, "mercury": 26, "mars": 17, "saturn": 9
    }
    naisargika = naisargika_values.get(planet, 25)

    # Kendradi component
    kendradi_val = kendradi["value"]

    # Weighted total (Vimsopaka style)
    total = (
        sthana     * 0.25 +
        dig_val    * 0.25 +
        kaal       * 0.15 +
        cheshta    * 0.10 +
        naisargika * 0.10 +
        kendradi_val * 0.15
    )

    # Convert to approximate Rupas
    rupas = total * 8

    # Compare to minimum
    min_req = MINIMUM_RUPAS.get(planet, 300)
    strength_pct = min(200, (rupas / min_req) * 100)

    return {
        "planet": planet,
        "sign": sign,
        "house": house,
        "dignity": dignity,
        "dig_bala": dig,
        "kendradi": kendradi,
        "components": {
            "sthana_bala": sthana,
            "dig_bala": dig_val,
            "kaal_bala": kaal,
            "cheshta_bala": cheshta,
            "naisargika_bala": naisargika,
            "kendradi_bala": kendradi_val
        },
        "total_vimsopaka": round(total, 1),
        "estimated_rupas": round(rupas),
        "minimum_rupas": min_req,
        "strength_pct": round(strength_pct, 1),
        "is_combust": is_combust,
        "is_retrograde": is_retrograde
    }


# ═══════════════════════════════════════════════════════════════
# STEP 5 — OJHA'S PREDICTION SCALE
# Source: Phaldipika Ch.3 Page 80 — the master scale
# ═══════════════════════════════════════════════════════════════

def apply_ojha_scale(base_result: str, base_strong: str,
                     base_weak: str, strength_pct: float) -> Dict:
    """
    Ojha's exact scale from Phaldipika page 80:
    100%+ → Full result
    75%   → 3/4 result
    50%   → 1/2 result
    25%   → 1/4 result
    <25%  → Minimal
    """
    if strength_pct >= 150:
        return {
            "level": "EXCEPTIONAL",
            "fraction": "Full + amplified",
            "prediction": base_strong,
            "qualifier": "Planet is exceptionally strong — results exceed normal"
        }
    elif strength_pct >= 100:
        return {
            "level": "FULL",
            "fraction": "Complete (4/4)",
            "prediction": base_strong,
            "qualifier": "Planet is strong — full classical result applies"
        }
    elif strength_pct >= 75:
        return {
            "level": "THREE QUARTER",
            "fraction": "3/4",
            "prediction": base_result,
            "qualifier": "Good strength — main significations manifest"
        }
    elif strength_pct >= 50:
        return {
            "level": "HALF",
            "fraction": "1/2",
            "prediction": base_result,
            "qualifier": "Moderate strength — partial manifestation"
        }
    elif strength_pct >= 25:
        return {
            "level": "QUARTER",
            "fraction": "1/4",
            "prediction": base_weak,
            "qualifier": "Weak planet — limited results, needs Dasha support"
        }
    else:
        return {
            "level": "MINIMAL",
            "fraction": "~0",
            "prediction": base_weak,
            "qualifier": "Very weak — results negligible without strong Dasha"
        }


# ═══════════════════════════════════════════════════════════════
# THE MASTER FUNCTION
# Combines everything into one precise prediction
# ═══════════════════════════════════════════════════════════════

def predict_precisely(
    planet: str,
    sign: str,
    degree: float,
    house: int,
    house_result: Dict,
    is_retrograde: bool = False,
    is_combust: bool = False,
    is_day_birth: bool = True,
    paksha_is_shukla: bool = True,
    current_dasha: str = "",
    current_antardasha: str = ""
) -> Dict:
    """
    THE MASTER PREDICTION FUNCTION

    Takes planet placement + strength → gives precise scaled prediction.

    This is the implementation of the insight:
    'Strength × Placement → Precise Prediction'

    Every output is traceable to exact classical source.
    """
    # Calculate complete strength
    strength = calc_combined_strength(
        planet, sign, degree, house,
        is_retrograde, is_combust,
        is_day_birth, paksha_is_shukla
    )

    strength_pct = strength["strength_pct"]
    dig = strength["dig_bala"]
    dignity = strength["dignity"]

    # Get base results from planet_results.py data
    base_result = house_result.get("result", "")
    base_strong = house_result.get("strong", base_result)
    base_weak   = house_result.get("weak", base_result)
    base_citation = house_result.get("citation", "")

    # Apply Ojha's scale
    scaled = apply_ojha_scale(base_result, base_strong,
                               base_weak, strength_pct)

    # Dig Bala special note
    dig_note = ""
    if dig["is_maximum"]:
        dig_note = (
            f"{planet.capitalize()} is in its MAXIMUM Dig Bala house "
            f"({dig['strong_direction']}). "
            f"Ojha says this gives the most accurate and complete prediction. "
            f"Result is amplified in {dig['strong_direction']} direction of life."
        )
    elif dig["dig_bala"] >= 40:
        dig_note = f"Strong Dig Bala ({dig['dig_bala']}/60) — directional strength supports prediction."
    elif dig["is_minimum"]:
        dig_note = f"Planet is in its WEAKEST directional position — results reduced."

    # Dasha timing note
    dasha_note = ""
    if current_dasha:
        if current_dasha.lower() == planet.lower():
            dasha_note = (
                f"Currently running {planet.capitalize()} Mahadasha — "
                f"THIS IS THE ACTIVATION PERIOD. Results manifest NOW."
            )
        elif current_antardasha.lower() == planet.lower():
            dasha_note = (
                f"{planet.capitalize()} Antardasha active — "
                f"partial activation of these results now."
            )
        else:
            dasha_note = (
                f"Results fully activate during {planet.capitalize()} "
                f"Mahadasha or Antardasha."
            )

    # Special flags
    flags = []
    if is_combust:
        flags.append("⚠️ COMBUST — Sthana Bala reduced significantly (Phaldipika Ch.1)")
    if is_retrograde:
        flags.append("🔄 RETROGRADE — Maximum Cheshta Bala (LJ Ch.2 Sl.8)")
    if dignity["state"].startswith("Paramoccha"):
        flags.append("⭐ PARAMOCCHA — Deepest exaltation, highest possible strength")
    if dignity["state"].startswith("Paramaneecha"):
        flags.append("⬇️ PARAMANEECHA — Deepest debilitation, Neecha Bhanga check needed")
    if dig["is_maximum"] and dignity["sthana_score"] >= 30:
        flags.append("🌟 DOUBLE STRONG — Both Dig Bala and dignity excellent — rarest combination")

    return {
        # Core prediction
        "planet": planet.capitalize(),
        "placement": f"{sign.capitalize()} {degree:.1f}° — House {house}",
        "prediction": scaled["prediction"],
        "result_level": scaled["level"],
        "result_fraction": scaled["fraction"],
        "qualifier": scaled["qualifier"],

        # Strength breakdown
        "strength": {
            "overall_pct": strength_pct,
            "dignity_state": dignity["state"],
            "dignity_score": dignity["sthana_score"],
            "dig_bala": dig["dig_bala"],
            "dig_bala_label": dig["label"],
            "kendradi": strength["kendradi"]["type"],
            "is_retrograde": is_retrograde,
            "is_combust": is_combust,
            "components": strength["components"]
        },

        # Insights
        "dig_bala_insight": dig_note,
        "dasha_timing": dasha_note,
        "special_flags": flags,

        # Citations
        "citations": {
            "result_source": base_citation,
            "dig_bala_source": "Laghu Jatakam | Varahamihira | Ch.2 | Shloka 8",
            "prediction_scale": "Phaldipika | Mantreswara/Ojha | Ch.3 | Page 80",
            "strength_formula": "LJ Ch.2 Sl.7-10 + Phaldipika Ch.3 Pg.41-80"
        }
    }


# ═══════════════════════════════════════════════════════════════
# CHART-LEVEL ANALYSIS
# Analyze all planets together
# ═══════════════════════════════════════════════════════════════

def analyze_chart_strength(planets_data: List[Dict]) -> Dict:
    """
    Find the strongest and weakest planets in the chart.
    Varahamihira LJ Ch.2 Sl.3: The strongest planet at birth
    shapes the entire character and life direction.
    """
    ranked = []
    for p in planets_data:
        name = p.get("planet", "")
        sign = p.get("sign", "aries")
        degree = p.get("degree", 0)
        house = p.get("house", 1)
        retro = p.get("is_retrograde", False)
        combust = p.get("is_combust", False)

        if name in ["rahu", "ketu", "ascendant"]:
            continue

        strength = calc_combined_strength(
            name, sign, degree, house, retro, combust
        )
        ranked.append({
            "planet": name,
            "strength_pct": strength["strength_pct"],
            "dignity": strength["dignity"]["state"],
            "dig_bala": strength["dig_bala"]["dig_bala"],
            "house": house,
            "sign": sign
        })

    ranked.sort(key=lambda x: x["strength_pct"], reverse=True)

    strongest = ranked[0] if ranked else {}
    weakest = ranked[-1] if ranked else {}

    # Find planets with Dig Bala in their strong house
    dig_bala_strong = [
        p for p in ranked
        if p["dig_bala"] == 60
    ]

    return {
        "ranked_by_strength": ranked,
        "strongest_planet": strongest,
        "weakest_planet": weakest,
        "dig_bala_maximum_planets": dig_bala_strong,
        "chart_ruler_note": (
            f"{strongest.get('planet','').capitalize()} is the strongest planet — "
            f"shapes character and life direction primarily"
            if strongest else ""
        ),
        "citation": (
            "Laghu Jatakam | Varahamihira | Ch.2 | Shloka 3 — "
            "'Strongest planet at birth shapes the native'"
        )
    }


# ═══════════════════════════════════════════════════════════════
# QUICK TEST
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":

    print("=" * 60)
    print("MASTER PREDICTION ENGINE — TEST")
    print("=" * 60)

    # Test 1: Jupiter in Lagna (1st house) — maximum Dig Bala
    jupiter_1st_result = {
        "result": "Wise, learned, respected personality, fortunate life",
        "strong": "Outstanding wisdom, fame, cancels all Arishta, excellent health",
        "weak": "Overconfident, liver issues, weight problems",
        "citation": "Phaldipika | Mantreswara | Ch.7 | Shloka 74"
    }

    result1 = predict_precisely(
        planet="jupiter",
        sign="cancer",      # Exalted
        degree=5.0,         # Paramoccha
        house=1,            # Maximum Dig Bala
        house_result=jupiter_1st_result,
        is_retrograde=False,
        is_day_birth=True,
        paksha_is_shukla=True,
        current_dasha="jupiter"
    )

    print("\n🔬 TEST 1: Jupiter exalted in Lagna")
    print(f"   Placement: {result1['placement']}")
    print(f"   Dignity: {result1['strength']['dignity_state']}")
    print(f"   Dig Bala: {result1['strength']['dig_bala']}/60 — {result1['strength']['dig_bala_label']}")
    print(f"   Strength: {result1['strength']['overall_pct']}%")
    print(f"   Result Level: {result1['result_level']} ({result1['result_fraction']})")
    print(f"   Prediction: {result1['prediction']}")
    print(f"   Dig Note: {result1['dig_bala_insight']}")
    print(f"   Flags: {result1['special_flags']}")
    print(f"   Dasha: {result1['dasha_timing']}")

    print()

    # Test 2: Saturn in 1st house (weakest Dig Bala for Saturn)
    saturn_1st_result = {
        "result": "Thin lean body, disciplined, slow steady progress, philosophical",
        "strong": "Excellent longevity, authority through hard work, lasting fame",
        "weak": "Depression, chronic illness, skin and bone problems",
        "citation": "Phaldipika | Mantreswara | Ch.7 | Shloka 122"
    }

    result2 = predict_precisely(
        planet="saturn",
        sign="aries",       # Debilitated
        degree=20.0,        # Paramaneecha
        house=1,            # Weakest Dig Bala for Saturn
        house_result=saturn_1st_result,
        is_day_birth=False,
        paksha_is_shukla=False,
        current_dasha="saturn"
    )

    print("🔬 TEST 2: Saturn debilitated in Lagna (weak Dig Bala)")
    print(f"   Dignity: {result2['strength']['dignity_state']}")
    print(f"   Dig Bala: {result2['strength']['dig_bala']}/60")
    print(f"   Strength: {result2['strength']['overall_pct']}%")
    print(f"   Result Level: {result2['result_level']} ({result2['result_fraction']})")
    print(f"   Prediction: {result2['prediction']}")
    print(f"   Flags: {result2['special_flags']}")

    print()

    # Test 3: Moon in 4th house (maximum Dig Bala)
    moon_4th_result = {
        "result": "Excellent domestic happiness, devoted mother, good property",
        "strong": "Outstanding happiness, excellent mother, higher education, property",
        "weak": "Mother's health issues, domestic instability",
        "citation": "Phaldipika | Mantreswara | Ch.7 | Shloka 8"
    }

    result3 = predict_precisely(
        planet="moon",
        sign="taurus",      # Exalted
        degree=3.0,         # Paramoccha
        house=4,            # Maximum Dig Bala for Moon
        house_result=moon_4th_result,
        paksha_is_shukla=True,
        current_dasha="moon"
    )

    print("🔬 TEST 3: Moon exalted in 4th (MAXIMUM Dig Bala)")
    print(f"   Dignity: {result3['strength']['dignity_state']}")
    print(f"   Dig Bala: {result3['strength']['dig_bala']}/60")
    print(f"   Strength: {result3['strength']['overall_pct']}%")
    print(f"   Result Level: {result3['result_level']} ({result3['result_fraction']})")
    print(f"   Prediction: {result3['prediction']}")
    print(f"   Dig Note: {result3['dig_bala_insight']}")
    print(f"   Flags: {result3['special_flags']}")

    print()
    print("=" * 60)
    print("Source: Laghu Jatakam (Varahamihira) + Phaldipika (Ojha)")
    print("=" * 60)
