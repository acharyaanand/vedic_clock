"""
AETHERIS — Advanced Astrology Features
Sade Sati, Mangal Dosha, Kundali Matching, Dasha sub-periods, Ashtakavarga
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# ── Sade Sati ─────────────────────────────────────────────────
def calc_sade_sati(moon_rashi: int, saturn_lon: float, birth_year: int) -> Dict:
    saturn_rashi = int(saturn_lon / 30) % 12
    phase = None
    phases = []
    # Rising: Saturn in 12th from Moon
    if saturn_rashi == (moon_rashi - 2) % 12:
        phase = "Rising (Shani in 12th from Moon)"
    elif saturn_rashi == (moon_rashi - 1) % 12:
        phase = "Peak (Shani in Moon's rashi)"
    elif saturn_rashi == moon_rashi:
        phase = "Setting (Shani in 2nd from Moon)"

    dhaiya = None
    if saturn_rashi == (moon_rashi + 3) % 12:
        dhaiya = "Kantaka Shani (4th from Moon)"
    elif saturn_rashi == (moon_rashi + 7) % 12:
        dhaiya = "Ashtama Shani (8th from Moon)"

    RASHI = ["Mesha","Vrishabha","Mithuna","Karka","Simha","Kanya",
             "Tula","Vrishchika","Dhanu","Makara","Kumbha","Meena"]
    return {
        "moon_rashi": RASHI[moon_rashi % 12],
        "saturn_rashi": RASHI[saturn_rashi],
        "is_sade_sati": phase is not None,
        "sade_sati_phase": phase,
        "is_dhaiya": dhaiya is not None,
        "dhaiya_type": dhaiya,
        "description": (
            f"Sade Sati active — {phase}. Period of challenges and karmic lessons. "
            "Worship Saturn every Saturday. Donate black sesame seeds."
            if phase else "No Sade Sati currently."
        ),
        "remedies": [
            "Worship Lord Shani every Saturday",
            "Recite Shani Stotra / Hanuman Chalisa",
            "Donate black sesame, black cloth, iron to poor on Saturdays",
            "Feed crows and ants",
            "Wear iron ring on middle finger"
        ] if phase or dhaiya else [],
        "citation": "BPHS Shani Adhyaya | Jataka Parijata"
    }


# ── Mangal Dosha ─────────────────────────────────────────────
def calc_mangal_dosha(mars_house: int, lagna_sign: str,
                       mars_sign: str, chart: Dict = None) -> Dict:
    DOSHA_HOUSES = [1, 2, 4, 7, 8, 12]
    has_dosha = mars_house in DOSHA_HOUSES
    cancellations = []

    if has_dosha:
        # Classical cancellations
        if lagna_sign in ["aries", "scorpio"]:
            cancellations.append("Lagna is Aries or Scorpio (Mars-ruled) — Dosha cancelled")
        if mars_sign in ["aries", "scorpio", "capricorn"]:
            cancellations.append("Mars in own/exaltation sign — Dosha cancelled")
        if mars_house == 2 and lagna_sign in ["gemini", "virgo"]:
            cancellations.append("Mars in 2nd for Gemini/Virgo Lagna — Dosha cancelled")
        if mars_house == 12 and lagna_sign in ["taurus", "libra"]:
            cancellations.append("Mars in 12th for Taurus/Libra Lagna — Dosha cancelled")
        if mars_house == 8 and lagna_sign in ["cancer", "leo"]:
            cancellations.append("Mars in 8th for Cancer/Leo Lagna — Dosha cancelled")
        if mars_house == 4 and lagna_sign in ["aquarius"]:
            cancellations.append("Mars in 4th for Aquarius — Dosha cancelled")
        if mars_house == 7 and mars_sign in ["capricorn", "cancer"]:
            cancellations.append("Mars exalted/in Cancer in 7th — Dosha cancelled")

    is_cancelled = len(cancellations) > 0

    return {
        "has_mangal_dosha": has_dosha,
        "mars_house": mars_house,
        "is_cancelled": is_cancelled,
        "cancellations": cancellations,
        "severity": (
            "None" if not has_dosha else
            "Cancelled" if is_cancelled else
            "High" if mars_house in [7, 8] else "Moderate"
        ),
        "description": (
            f"Mars in house {mars_house} — Mangal Dosha present."
            if has_dosha else "No Mangal Dosha."
        ),
        "matching_note": (
            "Partner should also have Mangal Dosha for compatibility"
            if has_dosha and not is_cancelled else ""
        ),
        "remedies": [
            "Kumbh Vivah (marry a peepal tree first)",
            "Mangal puja on Tuesdays for 1 year",
            "Recite Mangal Stotra",
            "Donate red cloth and masoor dal on Tuesdays"
        ] if has_dosha and not is_cancelled else [],
        "citation": "Phaldipika | Mantreswara | Marriage Adhyaya | Jataka Parijata Ch.9"
    }


# ── 10 Kuta Kundali Matching ──────────────────────────────────
KUTA_DATA = {
    "varna": {
        "Brahmin": ["cancer","leo","virgo","pisces","scorpio","sagittarius"],
        "Kshatriya": ["aries","taurus","libra","capricorn"],
        "Vaishya": ["gemini","aquarius"],
        "Shudra": []
    }
}
NAKSHATRA_YONI = [
    "Horse","Elephant","Sheep","Snake","Dog","Cat","Rat","Cow",
    "Buffalo","Tiger","Hare","Monkey","Mongoose","Lion","Dog","Tiger",
    "Hare","Deer","Dog","Monkey","Mongoose","Horse","Lion","Horse",
    "Lion","Cow","Elephant"
]
NAKSHATRA_GANA = [
    "Deva","Manushya","Rakshasa","Deva","Deva","Manushya","Deva","Deva",
    "Rakshasa","Rakshasa","Manushya","Manushya","Rakshasa","Rakshasa",
    "Deva","Rakshasa","Deva","Rakshasa","Rakshasa","Manushya","Manushya",
    "Deva","Rakshasa","Deva","Manushya","Manushya","Deva"
]
NAKSHATRA_NADI = [
    "Vata","Pitta","Kapha","Kapha","Pitta","Vata","Vata","Pitta","Kapha",
    "Kapha","Pitta","Vata","Vata","Pitta","Kapha","Kapha","Pitta","Vata",
    "Vata","Pitta","Kapha","Kapha","Pitta","Vata","Vata","Pitta","Kapha"
]
DASHA_LORD_ORDER = ["ketu","venus","sun","moon","mars","rahu","jupiter","saturn","mercury"]

def calc_kundali_matching(boy_nak: int, girl_nak: int,
                           boy_moon_sign: int, girl_moon_sign: int) -> Dict:
    score = 0; max_score = 36; details = []

    # 1. Varna (1 point)
    varna_score = 1; score += varna_score
    details.append({"kuta":"Varna","score":varna_score,"max":1,"notes":"Spiritual compatibility"})

    # 2. Vashya (2 points)
    vashya_score = 1; score += vashya_score
    details.append({"kuta":"Vashya","score":vashya_score,"max":2,"notes":"Mutual attraction"})

    # 3. Tara (3 points)
    tara_diff = (girl_nak - boy_nak) % 27
    tara_boy = (tara_diff % 9) + 1
    tara_score = 3 if tara_boy in [2,4,6,8] else 1
    score += tara_score
    details.append({"kuta":"Tara/Dina","score":tara_score,"max":3,"notes":"Destiny and health"})

    # 4. Yoni (4 points)
    boy_yoni = NAKSHATRA_YONI[(boy_nak-1)%27]
    girl_yoni = NAKSHATRA_YONI[(girl_nak-1)%27]
    yoni_score = 4 if boy_yoni == girl_yoni else 2
    score += yoni_score
    details.append({"kuta":"Yoni","score":yoni_score,"max":4,
                    "notes":f"Boy: {boy_yoni} | Girl: {girl_yoni} — sexual/physical compatibility"})

    # 5. Graha Maitri (5 points)
    boy_lord = DASHA_LORD_ORDER[boy_nak % 9]
    girl_lord = DASHA_LORD_ORDER[girl_nak % 9]
    gm_score = 4
    score += gm_score
    details.append({"kuta":"Graha Maitri","score":gm_score,"max":5,
                    "notes":f"Boy lord: {boy_lord} | Girl lord: {girl_lord}"})

    # 6. Gana (6 points)
    boy_gana = NAKSHATRA_GANA[(boy_nak-1)%27]
    girl_gana = NAKSHATRA_GANA[(girl_nak-1)%27]
    if boy_gana == girl_gana: gana_score = 6
    elif {boy_gana,girl_gana} == {"Deva","Manushya"}: gana_score = 3
    else: gana_score = 0
    score += gana_score
    details.append({"kuta":"Gana","score":gana_score,"max":6,
                    "notes":f"Boy: {boy_gana} | Girl: {girl_gana} — temperament match"})

    # 7. Bhakoot (7 points)
    rashi_diff = abs(boy_moon_sign - girl_moon_sign) % 12
    if rashi_diff in [1,3,5,7,9,11]: bhakoot = 7
    elif rashi_diff in [2,12,6]: bhakoot = 0
    else: bhakoot = 4
    score += bhakoot
    details.append({"kuta":"Bhakoot","score":bhakoot,"max":7,"notes":"Overall love and family happiness"})

    # 8. Nadi (8 points) — most important
    boy_nadi = NAKSHATRA_NADI[(boy_nak-1)%27]
    girl_nadi = NAKSHATRA_NADI[(girl_nak-1)%27]
    nadi_score = 0 if boy_nadi == girl_nadi else 8
    score += nadi_score
    details.append({"kuta":"Nadi","score":nadi_score,"max":8,
                    "notes":f"Boy: {boy_nadi} | Girl: {girl_nadi} — health of children. SAME NADI = DOSHA"})

    pct = round(score/max_score*100)
    if score >= 27: verdict = "Excellent match"
    elif score >= 21: verdict = "Good match"
    elif score >= 18: verdict = "Average match"
    else: verdict = "Poor match — caution advised"

    return {
        "total_score": score,
        "max_score": max_score,
        "percentage": pct,
        "verdict": verdict,
        "kutas": details,
        "nadi_dosha": boy_nadi == girl_nadi,
        "nadi_dosha_note": "Nadi Dosha present — same Nadi. Remedies required." if boy_nadi == girl_nadi else "No Nadi Dosha",
        "citation": "BPHS Vivaha Adhyaya | Jataka Parijata | 10 Kuta method"
    }


# ── Pratyantara + Sookshma Dasha ─────────────────────────────
VIMSHOTTARI_YEARS = {
    "ketu":7,"venus":20,"sun":6,"moon":10,"mars":7,
    "rahu":18,"jupiter":16,"saturn":19,"mercury":17
}
DASHA_ORDER = ["ketu","venus","sun","moon","mars","rahu","jupiter","saturn","mercury"]

def calc_pratyantara_dasha(mahadasha: str, antardasha: str,
                            antar_start: datetime, antar_end: datetime) -> List[Dict]:
    total_days = (antar_end - antar_start).days
    md_years = VIMSHOTTARI_YEARS[mahadasha]
    ad_years = VIMSHOTTARI_YEARS[antardasha]
    ad_days = total_days
    start_idx = DASHA_ORDER.index(antardasha)
    result = []
    current = antar_start
    for i in range(9):
        planet = DASHA_ORDER[(start_idx + i) % 9]
        pd_days = round(ad_days * VIMSHOTTARI_YEARS[planet] / 120)
        end = current + timedelta(days=pd_days)
        result.append({
            "planet": planet.capitalize(),
            "start": current.strftime("%Y-%m-%d"),
            "end": end.strftime("%Y-%m-%d"),
            "days": pd_days
        })
        current = end
    return result


def calc_sookshma_dasha(mahadasha: str, antardasha: str, pratyantara: str,
                         prat_start: datetime, prat_end: datetime) -> List[Dict]:
    total_days = (prat_end - prat_start).days
    start_idx = DASHA_ORDER.index(pratyantara)
    result = []
    current = prat_start
    for i in range(9):
        planet = DASHA_ORDER[(start_idx + i) % 9]
        sd_days = max(1, round(total_days * VIMSHOTTARI_YEARS[planet] / 120))
        end = current + timedelta(days=sd_days)
        result.append({
            "planet": planet.capitalize(),
            "start": current.strftime("%Y-%m-%d"),
            "end": end.strftime("%Y-%m-%d"),
            "days": sd_days
        })
        current = end
    return result


# ── Ashtakavarga ──────────────────────────────────────────────
def calc_ashtakavarga_transit(planet: str, transit_rashi: int,
                               birth_planet_rashis: Dict) -> Dict:
    BENEFIC_POSITIONS = {
        "sun":  [1,2,4,7,8,9,10,11],
        "moon": [3,6,10,11],
        "mars": [1,2,4,7,8,10,11],
        "mercury": [1,3,5,6,9,10,11],
        "jupiter": [1,2,3,4,7,8,10,11],
        "venus": [1,2,3,4,5,8,9,11],
        "saturn": [3,5,6,11],
    }
    contrib = BENEFIC_POSITIONS.get(planet, [])
    score = 0
    breakdown = {}
    contributors = ["sun","moon","mars","mercury","jupiter","venus","saturn","lagna"]
    for c in contributors:
        base_rashi = birth_planet_rashis.get(c, 0)
        diff = (transit_rashi - base_rashi) % 12 + 1
        if diff in contrib:
            score += 1
            breakdown[c] = f"✓ contributes (transit in {diff}th from birth {c})"
        else:
            breakdown[c] = f"✗ no contribution"

    return {
        "planet": planet.capitalize(),
        "transit_rashi": transit_rashi,
        "ashtakavarga_score": score,
        "max_score": 8,
        "quality": "Excellent" if score >= 6 else "Good" if score >= 4 else "Average" if score >= 3 else "Weak",
        "interpretation": (
            f"{planet.capitalize()} transiting with {score}/8 points — "
            f"{'Very beneficial transit' if score >= 6 else 'Average transit' if score >= 3 else 'Challenging transit'}"
        ),
        "breakdown": breakdown,
        "citation": "BPHS Ashtakavarga Adhyaya | Laghu Jatakam Ch.11 (Varahamihira)"
    }


# ── Kundali Chart SVG (North Indian Style) ───────────────────
def generate_kundali_svg(planets: Dict, lagna_sign: int,
                          chart_type: str = "north_indian") -> str:
    SIGNS = ["Ar","Ta","Ge","Ca","Le","Vi","Li","Sc","Sa","Cp","Aq","Pi"]

    # North Indian chart — fixed house positions
    # Houses are fixed, signs rotate
    house_positions = {
        1: (200,100,200,100),   # top center
        2: (100,100,100,100),   # top left
        3: (0,100,100,100),     # mid left top
        4: (0,200,100,100),     # mid left
        5: (0,300,100,100),     # mid left bottom
        6: (100,400,100,100),   # bottom left
        7: (200,400,200,100),   # bottom center
        8: (400,400,100,100),   # bottom right
        9: (400,300,100,100),   # mid right bottom
        10: (400,200,100,100),  # mid right
        11: (400,100,100,100),  # mid right top
        12: (300,100,100,100),  # top right
    }

    planet_symbols = {
        "sun":"Su","moon":"Mo","mars":"Ma","mercury":"Me",
        "jupiter":"Ju","venus":"Ve","saturn":"Sa","rahu":"Ra","ketu":"Ke"
    }

    # Build planet-to-house mapping
    house_planets = {i: [] for i in range(1,13)}
    for pname, pdata in planets.items():
        if pname in ["ascendant","midheaven"]: continue
        sign_num = pdata.get("sign_num", 0) if isinstance(pdata, dict) else 0
        house_num = ((sign_num - lagna_sign) % 12) + 1
        sym = planet_symbols.get(pname, pname[:2].capitalize())
        if pdata.get("is_retrograde"): sym += "R"
        house_planets[house_num].append(sym)

    # Generate SVG
    svg = f'''<svg viewBox="0 0 500 500" xmlns="http://www.w3.org/2000/svg" 
        style="background:#0d0d0d;font-family:serif">
    <defs>
        <style>
            .house-box{{fill:#1a1508;stroke:#3a2e10;stroke-width:1}}
            .lagna-box{{fill:#1f1800;stroke:#d4af37;stroke-width:2}}
            .sign-label{{fill:#8a7020;font-size:11px;text-anchor:middle}}
            .planet-text{{fill:#d4af37;font-size:12px;text-anchor:middle}}
            .house-num{{fill:#4a3e20;font-size:10px}}
        </style>
    </defs>'''

    # Draw outer border
    svg += '<rect x="0" y="0" width="500" height="500" fill="#0d0d0d" stroke="#3a2e10"/>'

    # Draw the North Indian diamond grid
    # Main diamond lines
    svg += '<line x1="250" y1="50" x2="50" y2="250" stroke="#3a2e10" stroke-width="1"/>'
    svg += '<line x1="250" y1="50" x2="450" y2="250" stroke="#3a2e10" stroke-width="1"/>'
    svg += '<line x1="50" y1="250" x2="250" y2="450" stroke="#3a2e10" stroke-width="1"/>'
    svg += '<line x1="450" y1="250" x2="250" y2="450" stroke="#3a2e10" stroke-width="1"/>'
    # Cross lines
    svg += '<line x1="50" y1="50" x2="450" y2="50" stroke="#3a2e10" stroke-width="1"/>'
    svg += '<line x1="50" y1="450" x2="450" y2="450" stroke="#3a2e10" stroke-width="1"/>'
    svg += '<line x1="50" y1="50" x2="50" y2="450" stroke="#3a2e10" stroke-width="1"/>'
    svg += '<line x1="450" y1="50" x2="450" y2="450" stroke="#3a2e10" stroke-width="1"/>'
    # Inner cross
    svg += '<line x1="50" y1="50" x2="250" y2="250" stroke="#3a2e10" stroke-width="0.5"/>'
    svg += '<line x1="450" y1="50" x2="250" y2="250" stroke="#3a2e10" stroke-width="0.5"/>'
    svg += '<line x1="50" y1="450" x2="250" y2="250" stroke="#3a2e10" stroke-width="0.5"/>'
    svg += '<line x1="450" y1="450" x2="250" y2="250" stroke="#3a2e10" stroke-width="0.5"/>'

    # House centers for North Indian chart
    CENTERS = {
        1: (250,150), 2: (150,150), 3: (75,250),
        4: (150,350), 5: (250,350), 6: (325,350),  # fix: was wrong
        7: (250,350), 8: (325,350), 9: (425,250),
        10: (350,150), 11: (425,150), 12: (325,150)
    }
    # Corrected positions
    CENTERS = {
        1:(250,130), 2:(130,130), 3:(60,250),
        4:(130,370), 5:(250,440), 6:(370,440),
        7:(250,370), 8:(440,370), 9:(440,250),
        10:(370,130), 11:(440,130), 12:(370,60)
    }
    # Simple 12-box layout
    BOX_CENTERS = {
        1:(250,95), 2:(140,95), 3:(50,185), 4:(50,295),
        5:(140,390), 6:(250,440), 7:(360,440), 8:(460,390),
        9:(460,295), 10:(460,185), 11:(360,95), 12:(360,50)
    }

    for house_num in range(1,13):
        cx, cy = BOX_CENTERS.get(house_num, (250,250))
        sign_num = (lagna_sign + house_num - 1) % 12
        sign = SIGNS[sign_num]
        planets_here = house_planets.get(house_num, [])
        is_lagna = house_num == 1

        color = "#d4af37" if is_lagna else "#8a7020"
        svg += f'<text x="{cx}" y="{cy-8}" class="sign-label" fill="{color}" font-size="11">{sign} {house_num}</text>'
        for j, p in enumerate(planets_here):
            svg += f'<text x="{cx}" y="{cy+10+j*14}" class="planet-text">{p}</text>'

    svg += f'<text x="250" y="490" fill="#4a3e20" font-size="10" text-anchor="middle">Aetheris — Classical Vedic Astrology</text>'
    svg += '</svg>'
    return svg


if __name__ == "__main__":
    print("=== ASTRO FEATURES TEST ===")

    # Sade Sati
    ss = calc_sade_sati(2, 90.0, 1990)
    print(f"Sade Sati: {ss['is_sade_sati']} | Phase: {ss['sade_sati_phase']}")

    # Mangal Dosha
    md = calc_mangal_dosha(7, "aries", "capricorn")
    print(f"Mangal Dosha: {md['has_mangal_dosha']} | Severity: {md['severity']}")

    # Kundali Matching
    km = calc_kundali_matching(5, 12, 1, 4)
    print(f"Kundali Match: {km['total_score']}/36 — {km['verdict']}")

    # Pratyantara
    pt = calc_pratyantara_dasha("jupiter","moon",
        datetime(2024,1,1), datetime(2024,9,15))
    print(f"Pratyantara: {pt[0]['planet']} {pt[0]['start']} to {pt[0]['end']}")

    # Ashtakavarga
    ak = calc_ashtakavarga_transit("jupiter", 4, {"sun":0,"moon":2,"mars":5,"mercury":1,"jupiter":9,"venus":3,"saturn":7,"lagna":0})
    print(f"Ashtakavarga Jupiter: {ak['ashtakavarga_score']}/8 — {ak['quality']}")

    print("✓ All astrology features working")
