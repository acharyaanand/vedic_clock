"""
AETHERIS — Navamsha (D9) Engine
Complete Navamsha calculation with classical rules.

Sources read directly from your books:
1. Laghu Jatakam | Varahamihira | Ch.1 Sl.8, 19 — Navamsha lords + Vargottama
2. Laghu Jatakam | Varahamihira | Ch.12 Pg.95 — Navamsha birth results
3. Laghu Jatakam | Varahamihira | Ch.9 Pg.68 — Vargottama doubles longevity
4. Phaldipika | Mantreswara/Ojha | Ch.2 Pg.20-25 — Divisional chart rules
5. BPHS | Parashara — Navamsha in marriage analysis

KEY TEACHING from Laghu Jatakam Ch.1 Sl.19 (Varahamihira, pg.21):
"Vargottama — a planet in its own Navamsha — gives double good results.
 Movable signs: 1st Navamsha is Vargottama.
 Fixed signs: 5th Navamsha is Vargottama.
 Dual signs: 9th Navamsha is Vargottama."

KEY TEACHING from Laghu Jatakam Ch.9 Pg.68 (Varahamihira):
"Vargottame svara-dhyaye svadrekkane svanavashmake —
 a planet in Vargottama, own Drekkana, own Navamsha
 gives DOUBLE the longevity/result."
"""

from typing import Dict, List, Tuple, Optional

# ─────────────────────────────────────────────────────────────
# NAVAMSHA CALCULATION TABLE
# Source: Laghu Jatakam Ch.1 Sl.8 | Table on pages 13-14
#
# Varahamihira gives the complete lord table:
# Each sign is divided into 9 Navamshas of 3°20' each
# Total = 30° per sign ÷ 9 = 3°20' per Navamsha
#
# Starting sign of Navamsha sequence:
# Fire signs (Aries, Leo, Sagittarius): start from Aries
# Earth signs (Taurus, Virgo, Capricorn): start from Capricorn
# Air signs (Gemini, Libra, Aquarius): start from Libra
# Water signs (Cancer, Scorpio, Pisces): start from Cancer
# ─────────────────────────────────────────────────────────────

SIGNS = [
    "aries", "taurus", "gemini", "cancer", "leo", "virgo",
    "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"
]

SIGN_INDEX = {s: i for i, s in enumerate(SIGNS)}

# Navamsha starting sign for each sign
# Fire → Aries(0), Earth → Capricorn(9), Air → Libra(6), Water → Cancer(3)
NAVAMSHA_START = {
    "aries": 0, "leo": 0, "sagittarius": 0,           # Fire → start Aries
    "taurus": 9, "virgo": 9, "capricorn": 9,           # Earth → start Capricorn
    "gemini": 6, "libra": 6, "aquarius": 6,            # Air → start Libra
    "cancer": 3, "scorpio": 3, "pisces": 3             # Water → start Cancer
}

NAVAMSHA_SIZE = 3 + 1/3  # 3°20' = 3.3333...°

# Sign types for Vargottama detection
MOVABLE_SIGNS  = ["aries", "cancer", "libra", "capricorn"]       # Chara
FIXED_SIGNS    = ["taurus", "leo", "scorpio", "aquarius"]         # Sthira
DUAL_SIGNS     = ["gemini", "virgo", "sagittarius", "pisces"]     # Dwiswabhava

# Sign lords
SIGN_LORDS = {
    "aries": "mars", "taurus": "venus", "gemini": "mercury",
    "cancer": "moon", "leo": "sun", "virgo": "mercury",
    "libra": "venus", "scorpio": "mars", "sagittarius": "jupiter",
    "capricorn": "saturn", "aquarius": "saturn", "pisces": "jupiter"
}


def calc_navamsha(sign: str, degree: float) -> Dict:
    """
    Calculate the Navamsha (D9) position of a planet.
    Source: Laghu Jatakam Ch.1 Sl.8 (Varahamihira) — pages 13-14

    Each sign = 30°, divided into 9 parts of 3°20' each.
    The Navamsha sign is determined by which 1/9th division
    the planet falls in, counted from the starting sign.
    """
    if sign not in NAVAMSHA_START:
        return {"navamsha_sign": "aries", "navamsha_num": 1}

    # Which Navamsha within the sign (1-9)
    navamsha_num = int(degree / NAVAMSHA_SIZE) + 1
    if navamsha_num > 9:
        navamsha_num = 9

    # Starting sign index for this sign's Navamsha sequence
    start_idx = NAVAMSHA_START[sign]

    # Navamsha sign = start + (navamsha_num - 1), cycling through 12 signs
    navamsha_sign_idx = (start_idx + navamsha_num - 1) % 12
    navamsha_sign = SIGNS[navamsha_sign_idx]
    navamsha_lord = SIGN_LORDS[navamsha_sign]

    # Degree within Navamsha
    navamsha_degree_start = (navamsha_num - 1) * NAVAMSHA_SIZE
    degree_in_navamsha = degree - navamsha_degree_start

    return {
        "navamsha_sign": navamsha_sign,
        "navamsha_sign_lord": navamsha_lord,
        "navamsha_num": navamsha_num,
        "navamsha_degree": round(degree_in_navamsha, 4),
        "rashi_sign": sign,
        "rashi_degree": round(degree, 4),
        "citation": "Laghu Jatakam | Varahamihira | Ch.1 | Shloka 8 (pages 13-14)"
    }


def is_vargottama(sign: str, degree: float) -> Dict:
    """
    Vargottama — planet in its own Navamsha within its Rashi.
    Source: Laghu Jatakam Ch.1 Sl.19 (Varahamihira) — page 21

    Varahamihira's exact rule:
    Movable signs (Chara):  1st Navamsha (0°-3°20') = Vargottama
    Fixed signs (Sthira):   5th Navamsha (13°20'-16°40') = Vargottama
    Dual signs (Dwiswabhava): 9th Navamsha (26°40'-30°) = Vargottama

    Result: "Vargottama planet gives double results"
    Longevity reference: LJ Ch.9 Pg.68 — doubles longevity calculation
    """
    navamsha_num = int(degree / NAVAMSHA_SIZE) + 1

    if sign in MOVABLE_SIGNS:
        vargottama = (navamsha_num == 1)  # 1st Navamsha
    elif sign in FIXED_SIGNS:
        vargottama = (navamsha_num == 5)  # 5th Navamsha
    elif sign in DUAL_SIGNS:
        vargottama = (navamsha_num == 9)  # 9th Navamsha
    else:
        vargottama = False

    if vargottama:
        return {
            "is_vargottama": True,
            "sign_type": (
                "Movable (1st Navamsha)" if sign in MOVABLE_SIGNS else
                "Fixed (5th Navamsha)" if sign in FIXED_SIGNS else
                "Dual (9th Navamsha)"
            ),
            "effect": "Planet gives DOUBLE results — strongest Navamsha position",
            "longevity_effect": "Doubles longevity contribution in Ayurdaya calculation",
            "citation": (
                "Laghu Jatakam | Varahamihira | Ch.1 | Shloka 19 (page 21) — "
                "Vargottama definition | Ch.9 Page 68 — doubles longevity"
            )
        }
    return {
        "is_vargottama": False,
        "sign_type": "",
        "effect": "",
        "citation": "Laghu Jatakam | Varahamihira | Ch.1 | Shloka 19"
    }


def get_pushkara_navamsha(sign: str, degree: float) -> Dict:
    """
    Pushkara Navamsha — specific Navamshas of highest auspiciousness.
    Source: BPHS | Parashara — Pushkara Navamsha Adhyaya

    These are the most powerful Navamshas in the zodiac.
    A planet here is extremely strong and auspicious.
    """
    # Pushkara Navamsha degrees (sign: [navamsha_nums])
    PUSHKARA = {
        "aries":       [2],       # 3°20'-6°40'
        "taurus":      [5],       # 13°20'-16°40'
        "gemini":      [3],       # 6°40'-10°
        "cancer":      [7],       # 20°-23°20'
        "leo":         [5],       # 13°20'-16°40'
        "virgo":       [3],       # 6°40'-10°
        "libra":       [7],       # 20°-23°20'
        "scorpio":     [5],       # 13°20'-16°40'
        "sagittarius": [8],       # 23°20'-26°40'
        "capricorn":   [2],       # 3°20'-6°40'
        "aquarius":    [6],       # 16°40'-20°
        "pisces":      [7],       # 20°-23°20'
    }

    navamsha_num = int(degree / NAVAMSHA_SIZE) + 1
    pushkara_list = PUSHKARA.get(sign, [])

    if navamsha_num in pushkara_list:
        return {
            "is_pushkara": True,
            "effect": "Pushkara Navamsha — highest auspiciousness, planet gives best results",
            "citation": "BPHS | Parashara | Pushkara Navamsha Adhyaya"
        }
    return {"is_pushkara": False, "effect": "", "citation": "BPHS | Parashara"}


# ─────────────────────────────────────────────────────────────
# NAVAMSHA LAGNA RESULTS
# Source: Laghu Jatakam Ch.12 Pg.95 (Varahamihira)
# "Navamsha birth results" — what Navamsha Lagna gives
#
# Varahamihira's exact words (LJ Ch.12 Sl.1, page 95):
# Aries Navamsha  → Thief (Taskara)
# Taurus          → Enjoyer (Bhoktru)
# Gemini          → Intelligent/Skilled (Vichakshana)
# Cancer          → Wealthy (Dhani)
# Leo             → King/Ruler (Raja)
# Virgo           → Eunuch/Neuter (Napumsaka)
# Libra           → Brave/Warrior (Shura)
# Scorpio         → Poor (Daridra)
# Sagittarius     → Wicked/Cruel (Khala/Dushta)
# Capricorn       → Sinful/Troubled (Papa)
# Aquarius        → Aggressive (Ugra)
# Pisces          → Excellent/Noble (Utkrishta)
# ─────────────────────────────────────────────────────────────

NAVAMSHA_LAGNA_RESULTS = {
    "aries": {
        "type": "Taskara (Risk-taker)",
        "result": "Bold, enterprising, risk-taking nature. May be involved in secret or daring activities. Active and courageous.",
        "citation": "Laghu Jatakam | Varahamihira | Ch.12 | Shloka 1 (page 95)"
    },
    "taurus": {
        "type": "Bhoktru (Enjoyer)",
        "result": "Fond of pleasures and comforts. Good food, wealth, and material enjoyments. Sensuous and comfort-loving.",
        "citation": "Laghu Jatakam | Varahamihira | Ch.12 | Shloka 1 (page 95)"
    },
    "gemini": {
        "type": "Vichakshana (Skilled/Intelligent)",
        "result": "Highly intelligent, skilled in multiple arts and crafts. Good at analysis, writing, and communication.",
        "citation": "Laghu Jatakam | Varahamihira | Ch.12 | Shloka 1 (page 95)"
    },
    "cancer": {
        "type": "Dhani (Wealthy)",
        "result": "Wealth and prosperity. Good family life, emotional richness, property and inheritance.",
        "citation": "Laghu Jatakam | Varahamihira | Ch.12 | Shloka 1 (page 95)"
    },
    "leo": {
        "type": "Raja (King/Leader)",
        "result": "Leadership qualities, authority, fame. Natural ruler or person of high position in society.",
        "citation": "Laghu Jatakam | Varahamihira | Ch.12 | Shloka 1 (page 95)"
    },
    "virgo": {
        "type": "Napumsaka (Neutral)",
        "result": "Meticulous, analytical, service-oriented. May have reduced romantic inclinations. Scholarly nature.",
        "citation": "Laghu Jatakam | Varahamihira | Ch.12 | Shloka 1 (page 95)"
    },
    "libra": {
        "type": "Shura (Brave/Just)",
        "result": "Brave, just, and fair-minded. Good at resolving conflicts. Social and diplomatic.",
        "citation": "Laghu Jatakam | Varahamihira | Ch.12 | Shloka 1 (page 95)"
    },
    "scorpio": {
        "type": "Daridra (Struggles)",
        "result": "Faces financial struggles and obstacles. Life has challenges but also depth and transformation.",
        "citation": "Laghu Jatakam | Varahamihira | Ch.12 | Shloka 1 (page 95)"
    },
    "sagittarius": {
        "type": "Khala (Daring/Harsh)",
        "result": "Direct, blunt, sometimes harsh in speech. Independent, philosophical, and adventurous.",
        "citation": "Laghu Jatakam | Varahamihira | Ch.12 | Shloka 1 (page 95)"
    },
    "capricorn": {
        "type": "Papa (Troubled)",
        "result": "Life has karmic challenges and hardships. Strong discipline and endurance. Late success.",
        "citation": "Laghu Jatakam | Varahamihira | Ch.12 | Shloka 1 (page 95)"
    },
    "aquarius": {
        "type": "Ugra (Intense/Fierce)",
        "result": "Intense, determined, sometimes aggressive. Strong will and unconventional approach to life.",
        "citation": "Laghu Jatakam | Varahamihira | Ch.12 | Shloka 1 (page 95)"
    },
    "pisces": {
        "type": "Utkrishta (Excellent/Noble)",
        "result": "Noble, spiritual, excellent qualities. Compassionate and wise. Good fortune and spiritual elevation.",
        "citation": "Laghu Jatakam | Varahamihira | Ch.12 | Shloka 1 (page 95)"
    }
}


# ─────────────────────────────────────────────────────────────
# NAVAMSHA IN MARRIAGE ANALYSIS
# Source: BPHS | Parashara — Vivaha Adhyaya
# The 7th Navamsha lord is the most important for marriage timing
# Venus Navamsha position shows spouse nature
# ─────────────────────────────────────────────────────────────

def analyze_navamsha_for_marriage(
    venus_d1_sign: str, venus_d1_deg: float,
    venus_d9_sign: str,
    lagna_d9_sign: str,
    seventh_lord_d9_sign: str
) -> Dict:
    """
    Marriage analysis from Navamsha.
    Source: BPHS Vivaha Adhyaya | Phaldipika Ch.16 (Ojha)

    Phaldipika page 22-23 (Ojha's rules):
    1. Venus in exaltation/own sign in D9 → excellent marriage
    2. 7th lord of D9 in good position → happy marriage
    3. D9 Lagna lord strong → strong marriage foundation
    4. Venus in enemy sign in D9 → marital difficulties
    """
    insights = []

    # Venus dignity in D9
    venus_exalt_signs = ["pisces"]  # Venus exalted in Pisces
    venus_own_signs = ["taurus", "libra"]
    venus_enemy_signs = ["aries", "scorpio", "virgo"]

    if venus_d9_sign in venus_exalt_signs:
        insights.append({
            "factor": "Venus exalted in D9",
            "result": "Excellent marriage — very beautiful, loving, devoted spouse",
            "strength": "Very Strong",
            "citation": "Phaldipika | Mantreswara/Ojha | Ch.16 | Page 22"
        })
    elif venus_d9_sign in venus_own_signs:
        insights.append({
            "factor": "Venus in own sign in D9",
            "result": "Good marriage — comfortable, pleasant, harmonious partnership",
            "strength": "Strong",
            "citation": "Phaldipika | Mantreswara/Ojha | Ch.16 | Page 22"
        })
    elif venus_d9_sign in venus_enemy_signs:
        insights.append({
            "factor": "Venus in enemy sign in D9",
            "result": "Marital challenges possible — differences with spouse, requires effort",
            "strength": "Challenging",
            "citation": "Phaldipika | Mantreswara/Ojha | Ch.16 | Page 23"
        })

    # Vargottama Venus check
    if venus_d1_sign == venus_d9_sign:
        insights.append({
            "factor": "Venus Vargottama (same sign in D1 and D9)",
            "result": "Very strong Venus — marriage is central to life, great comfort and beauty",
            "strength": "Exceptional",
            "citation": "Laghu Jatakam | Varahamihira | Ch.1 | Shloka 19"
        })

    return {
        "marriage_insights": insights,
        "venus_d9": venus_d9_sign,
        "lagna_d9": lagna_d9_sign,
        "primary_citation": "BPHS | Parashara | Vivaha Adhyaya"
    }


# ─────────────────────────────────────────────────────────────
# COMPLETE D9 CHART CALCULATION
# ─────────────────────────────────────────────────────────────

def calc_full_navamsha_chart(planets_d1: Dict) -> Dict:
    """
    Calculate complete Navamsha (D9) chart from D1 positions.
    Returns all planet positions in D9 with Vargottama analysis.

    Source: Laghu Jatakam Ch.1 Sl.8-9, 19 (Varahamihira)
    """
    d9_chart = {}

    for planet, data in planets_d1.items():
        if planet in ["ascendant", "midheaven"]:
            continue

        sign = data.get("sign", "aries")
        degree = data.get("degree", 0.0)

        # Calculate D9 position
        d9 = calc_navamsha(sign, degree)

        # Check Vargottama
        vargo = is_vargottama(sign, degree)

        # Check Pushkara
        pushkara = get_pushkara_navamsha(sign, degree)

        d9_chart[planet] = {
            "d1_sign": sign.capitalize(),
            "d1_degree": round(degree, 2),
            "d9_sign": d9["navamsha_sign"].capitalize(),
            "d9_sign_lord": d9["navamsha_sign_lord"].capitalize(),
            "navamsha_num": d9["navamsha_num"],
            "is_vargottama": vargo["is_vargottama"],
            "vargottama_effect": vargo.get("effect", ""),
            "is_pushkara": pushkara["is_pushkara"],
            "pushkara_effect": pushkara.get("effect", ""),
            "citations": {
                "navamsha": d9["citation"],
                "vargottama": vargo["citation"],
                "pushkara": pushkara["citation"]
            }
        }

    return {
        "d9_chart": d9_chart,
        "vargottama_planets": [
            p for p, d in d9_chart.items()
            if d.get("is_vargottama")
        ],
        "pushkara_planets": [
            p for p, d in d9_chart.items()
            if d.get("is_pushkara")
        ],
        "primary_citation": (
            "Laghu Jatakam | Varahamihira | Ch.1 | Shloka 8-9, 19 — "
            "Complete Navamsha calculation"
        )
    }


def get_navamsha_lagna_result(navamsha_lagna_sign: str) -> Dict:
    """
    Get the birth type result from Navamsha Lagna.
    Source: Laghu Jatakam Ch.12 Sl.1 (Varahamihira) — page 95
    """
    result = NAVAMSHA_LAGNA_RESULTS.get(
        navamsha_lagna_sign.lower(),
        {"type": "Unknown", "result": "Calculate Navamsha Lagna", "citation": "LJ Ch.12"}
    )
    return result


def get_planet_d9_strength(planet: str,
                            d9_sign: str,
                            is_vargottama: bool = False,
                            is_pushkara: bool = False) -> Dict:
    """
    Assess planet strength in D9 chart.
    Used for marriage timing and spouse analysis.
    Source: Phaldipika Ch.2 Pg.20-25 (Ojha's divisional chart rules)
    """
    from prediction_engine import get_dignity

    dignity = get_dignity(planet, d9_sign.lower(), 15.0)
    base_score = dignity["sthana_score"]

    # Vargottama doubles the score
    if is_vargottama:
        base_score = min(60, base_score * 2)

    # Pushkara adds 15
    if is_pushkara:
        base_score = min(60, base_score + 15)

    if base_score >= 50:
        label = "Very Strong in D9"
    elif base_score >= 35:
        label = "Strong in D9"
    elif base_score >= 20:
        label = "Moderate in D9"
    else:
        label = "Weak in D9"

    return {
        "planet": planet,
        "d9_sign": d9_sign,
        "d9_dignity": dignity["state"],
        "d9_score": base_score,
        "is_vargottama": is_vargottama,
        "is_pushkara": is_pushkara,
        "strength_label": label,
        "citation": "Phaldipika | Mantreswara/Ojha | Ch.2 | Pages 20-25"
    }


# ─────────────────────────────────────────────────────────────
# QUICK TEST
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("NAVAMSHA D9 ENGINE — TEST")
    print("=" * 60)

    # Test 1: Sun at Aries 10° (exaltation) — what Navamsha?
    d9 = calc_navamsha("aries", 10.0)
    vargo = is_vargottama("aries", 10.0)
    print(f"\nSun in Aries 10° (Paramoccha):")
    print(f"  D9 Sign: {d9['navamsha_sign'].capitalize()}")
    print(f"  D9 Lord: {d9['navamsha_sign_lord'].capitalize()}")
    print(f"  Navamsha #: {d9['navamsha_num']}")
    print(f"  Vargottama: {vargo['is_vargottama']}")

    # Test 2: Moon at Taurus 3° (Paramoccha) — Vargottama check
    d9_moon = calc_navamsha("taurus", 3.0)
    vargo_moon = is_vargottama("taurus", 3.0)
    push_moon = get_pushkara_navamsha("taurus", 3.0)
    print(f"\nMoon in Taurus 3° (Paramoccha):")
    print(f"  D9 Sign: {d9_moon['navamsha_sign'].capitalize()}")
    print(f"  Navamsha #: {d9_moon['navamsha_num']}")
    print(f"  Vargottama: {vargo_moon['is_vargottama']} — {vargo_moon.get('sign_type','')}")
    print(f"  Pushkara: {push_moon['is_pushkara']}")

    # Test 3: Vargottama examples
    print("\nVargottama examples:")
    print(f"  Aries 1° (movable, 1st navamsha): {is_vargottama('aries', 1.0)['is_vargottama']}")
    print(f"  Leo 14° (fixed, 5th navamsha): {is_vargottama('leo', 14.0)['is_vargottama']}")
    print(f"  Gemini 27° (dual, 9th navamsha): {is_vargottama('gemini', 27.0)['is_vargottama']}")

    # Test 4: Navamsha Lagna results
    print("\nNavamsha Lagna results (Varahamihira LJ Ch.12 Sl.1):")
    for sign in ["aries", "leo", "cancer", "pisces"]:
        r = get_navamsha_lagna_result(sign)
        print(f"  {sign.capitalize():12} → {r['type']:25} — {r['result'][:50]}")

    print(f"\nSource: Laghu Jatakam | Varahamihira | Ch.1 Sl.8,19 + Ch.12 Sl.1")
    print(f"        Phaldipika | Mantreswara/Ojha | Ch.2 Pages 20-25")
    print("=" * 60)
