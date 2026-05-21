"""
ashtakavarga.py — Complete Ashtakavarga Engine
================================================
Ashtakavarga = 7 individual planet tables + Sarvashtakavarga total.
Each planet contributes bindus (0 or 1) to each of 12 signs.

Three outputs:
  1. Bhinna Ashtakavarga — per-planet bindu count in each sign
  2. Sarvashtakavarga    — grand total across all 7 planets (max 56/sign)
  3. Transit strength   — signs with >=25 bindus are favorable

Source: BPHS Ch.66-73 (Parashara)
"""

# ═══════════════════════════════════════════════════════════════════════
# CLASSICAL CONTRIBUTION TABLES (BPHS Ch.66-73)
# For planet P: which houses counted FROM P's sign give bindus
# ═══════════════════════════════════════════════════════════════════════

CONTRIBUTION_TABLES = {
    "sun": {
        "sun":     [1,2,4,7,8,9,10,11],
        "moon":    [3,6,10,11],
        "mars":    [1,2,4,7,8,9,10,11],
        "mercury": [3,5,6,9,10,11,12],
        "jupiter": [5,6,9,11],
        "venus":   [6,7,12],
        "saturn":  [1,2,4,7,8,9,10,11],
        "lagna":   [3,4,6,10,11,12],
    },
    "moon": {
        "sun":     [3,6,7,8,10,11],
        "moon":    [1,3,6,7,10,11],
        "mars":    [2,3,5,6,9,10,11],
        "mercury": [1,3,4,5,7,8,10,11],
        "jupiter": [1,4,7,8,10,11,12],
        "venus":   [3,4,5,7,9,10,11],
        "saturn":  [3,5,6,11],
        "lagna":   [3,6,10,11],
    },
    "mars": {
        "sun":     [3,5,6,10,11],
        "moon":    [3,6,11],
        "mars":    [1,2,4,7,8,10,11],
        "mercury": [3,5,6,11],
        "jupiter": [6,10,11,12],
        "venus":   [6,8,11,12],
        "saturn":  [1,4,7,8,9,10,11],
        "lagna":   [1,3,6,10,11],
    },
    "mercury": {
        "sun":     [5,6,9,11,12],
        "moon":    [2,4,6,8,10,11],
        "mars":    [1,2,4,7,8,9,10,11],
        "mercury": [1,3,5,6,9,10,11,12],
        "jupiter": [6,8,11,12],
        "venus":   [1,2,3,4,5,8,9,11],
        "saturn":  [1,2,4,7,8,9,10,11],
        "lagna":   [1,2,4,6,8,10,11],
    },
    "jupiter": {
        "sun":     [1,2,3,4,7,8,9,10,11],
        "moon":    [2,5,7,9,11],
        "mars":    [1,2,4,7,8,10,11],
        "mercury": [1,2,4,5,6,9,10,11],
        "jupiter": [1,2,3,4,7,8,10,11],
        "venus":   [2,5,6,9,10,11],
        "saturn":  [3,5,6,12],
        "lagna":   [1,2,4,5,6,7,9,10,11],
    },
    "venus": {
        "sun":     [8,11,12],
        "moon":    [1,2,3,4,5,8,9,11,12],
        "mars":    [3,5,6,9,11,12],
        "mercury": [3,5,6,9,11],
        "jupiter": [5,8,9,10,11],
        "venus":   [1,2,3,4,5,8,9,10,11],
        "saturn":  [3,4,5,8,9,10,11],
        "lagna":   [1,2,3,4,5,8,9,11],
    },
    "saturn": {
        "sun":     [1,2,4,7,8,10,11],
        "moon":    [3,6,11],
        "mars":    [3,5,6,10,11,12],
        "mercury": [6,8,9,10,11,12],
        "jupiter": [5,6,11,12],
        "venus":   [6,11,12],
        "saturn":  [3,5,6,11],
        "lagna":   [1,3,4,6,10,11],
    },
}

SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
         "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
PLANETS_7 = ["sun","moon","mars","mercury","jupiter","venus","saturn"]


def calc_ashtakavarga(planet_lons: dict) -> dict:
    """
    Calculate complete Ashtakavarga for a birth chart.

    Parameters:
        planet_lons: dict with sidereal longitudes for:
            sun, moon, mars, mercury, jupiter, venus, saturn,
            rahu, ketu, ascendant (or lagna)

    Returns:
        bhinna_ashtakavarga: per-planet bindu count per sign
        sarvashtakavarga:    total bindus per sign
        sarva_total:         grand total (should be ~337)
        planet_totals:       each planet's total across 12 signs
        planet_analysis:     per-planet natal sign strength
        transit_strength:    which signs are strong (>=25) for transit
        strength_map:        quality rating per sign
        source:              classical reference
    """
    def sign_of(lon): return int(lon / 30) % 12
    def house_dist(from_sign, to_sign):
        return ((to_sign - from_sign) % 12) + 1

    positions = {}
    for p in PLANETS_7:
        if p in planet_lons:
            positions[p] = sign_of(planet_lons[p])
    lagna_key = "ascendant" if "ascendant" in planet_lons else "lagna"
    if lagna_key in planet_lons:
        positions["lagna"] = sign_of(planet_lons[lagna_key])

    bhinna = {}
    for planet in PLANETS_7:
        if planet not in positions:
            continue
        p_sign = positions[planet]
        table  = CONTRIBUTION_TABLES[planet]
        planet_bindus = [0] * 12

        for contributor, good_houses in table.items():
            if contributor not in positions:
                continue
            for s in range(12):
                h = house_dist(p_sign, s)
                if h in good_houses:
                    planet_bindus[s] += 1

        bhinna[planet] = {i: planet_bindus[i] for i in range(12)}

    # Sarvashtakavarga
    sarva = [0] * 12
    for planet in PLANETS_7:
        if planet in bhinna:
            for s in range(12):
                sarva[s] += bhinna[planet].get(s, 0)

    # Planet totals
    planet_totals = {p: sum(bhinna[p].values()) for p in PLANETS_7 if p in bhinna}

    # Strength map
    strength_map = {}
    for s in range(12):
        b = sarva[s]
        if b >= 30:   strength_map[s] = "Very Strong"
        elif b >= 25: strength_map[s] = "Strong"
        elif b >= 20: strength_map[s] = "Average"
        else:         strength_map[s] = "Weak"

    # Transit strength
    transit_strength = {
        SIGNS[s]: {
            "bindus": sarva[s],
            "strength": strength_map[s],
            "favorable_transit": sarva[s] >= 25,
        }
        for s in range(12)
    }

    # Planet analysis
    planet_analysis = {}
    for planet in PLANETS_7:
        if planet not in positions or planet not in bhinna:
            continue
        p_sign  = positions[planet]
        p_bindus = bhinna[planet].get(p_sign, 0)
        planet_analysis[planet] = {
            "natal_sign":          SIGNS[p_sign],
            "bindus_in_natal_sign": p_bindus,
            "total_bindus":        planet_totals.get(planet, 0),
            "strength":            "Strong" if p_bindus >= 4 else "Average" if p_bindus >= 3 else "Weak",
            "all_signs":           {SIGNS[s]: bhinna[planet][s] for s in range(12)},
        }

    return {
        "bhinna_ashtakavarga": {
            p: {SIGNS[s]: bhinna[p][s] for s in range(12)}
            for p in PLANETS_7 if p in bhinna
        },
        "sarvashtakavarga":    {SIGNS[s]: sarva[s] for s in range(12)},
        "sarva_total":         sum(sarva),
        "planet_totals":       {p: planet_totals.get(p,0) for p in PLANETS_7},
        "planet_analysis":     planet_analysis,
        "transit_strength":    transit_strength,
        "strength_map":        {SIGNS[s]: strength_map[s] for s in range(12)},
        "source":              "BPHS Ch.66-73 (Parashara)",
    }


def format_ashtakavarga_table(result: dict) -> str:
    """Pretty-print Ashtakavarga as a table."""
    signs_short = ["Ar","Ta","Ge","Ca","Le","Vi","Li","Sc","Sg","Cp","Aq","Pi"]
    lines = []
    lines.append("\nSARVASHTAKAVARGA:")
    lines.append("  " + "  ".join(f"{s:>3}" for s in signs_short))
    sarva = result["sarvashtakavarga"]
    lines.append("  " + "  ".join(f"{sarva[SIGNS[i]]:>3}" for i in range(12)))
    lines.append(f"  Total = {result['sarva_total']}")
    lines.append("")
    lines.append("BHINNA ASHTAKAVARGA:")
    lines.append("       " + "  ".join(f"{s:>3}" for s in signs_short) + "  Total")
    for planet in PLANETS_7:
        if planet in result["bhinna_ashtakavarga"]:
            row = result["bhinna_ashtakavarga"][planet]
            total = result["planet_totals"][planet]
            vals = "  ".join(f"{row[SIGNS[i]]:>3}" for i in range(12))
            lines.append(f"  {planet:<8} {vals}  {total:>5}")
    return "\n".join(lines)


if __name__ == "__main__":
    test_chart = {
        "sun":56.0,"moon":56.4,"mars":127.0,"mercury":37.2,
        "jupiter":258.0,"venus":18.0,"saturn":340.0,
        "rahu":176.0,"ketu":356.0,"ascendant":157.0,
    }
    result = calc_ashtakavarga(test_chart)
    print("ASHTAKAVARGA TEST")
    print(f"Sarvashtakavarga total: {result['sarva_total']} (expected ~337)")
    print()
    print("Strong signs for transit (>=25 bindus):")
    for sign, data in result["transit_strength"].items():
        if data["favorable_transit"]:
            print(f"  ✅ {sign}: {data['bindus']} bindus")
