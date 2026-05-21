"""
pratyantar_dasha.py — 3-Level Vimshottari Dasha Engine
=======================================================
Extends dasha_engine.py to add Pratyantar (sub-sub) dasha.

3 levels:
  Level 1: Mahadasha       (major period)
  Level 2: Antardasha      (sub period / Bhukti)
  Level 3: Pratyantar      (sub-sub period / Sookshma intro)

Formula:
  Pratyantar duration = Antardasha_duration × (pratyantar_planet_years / 120)

Each Antardasha has 9 Pratyantar dashas running in the
same sequence starting from the Antardasha lord.

Source: Phaldipika Ch.4, BPHS Ch.46
"""

from datetime import datetime, timedelta
from typing import List, Dict

# Vimshottari Dasha periods (years)
DASHA_YEARS = {
    "ketu":    7, "venus":  20, "sun":     6, "moon":    10,
    "mars":    7, "rahu":   18, "jupiter": 16, "saturn":  19,
    "mercury": 17
}

DASHA_ORDER = ["ketu","venus","sun","moon","mars","rahu","jupiter","saturn","mercury"]
DASHA_TOTAL = 120  # years

# Nakshatra to dasha lord mapping
NAKSHATRA_LORD = [
    "ketu","venus","sun","moon","mars","rahu","jupiter","saturn","mercury",  # 1-9
    "ketu","venus","sun","moon","mars","rahu","jupiter","saturn","mercury",  # 10-18
    "ketu","venus","sun","moon","mars","rahu","jupiter","saturn","mercury",  # 19-27
]

def get_dasha_lord_from_moon(moon_lon_sid: float):
    """Get dasha lord and balance from Moon's sidereal longitude."""
    nak_idx = int(moon_lon_sid * 27 / 360) % 27
    nak_start = nak_idx * (360/27)
    deg_in_nak = moon_lon_sid - nak_start
    fraction_traversed = deg_in_nak / (360/27)
    
    lord = NAKSHATRA_LORD[nak_idx]
    years_total = DASHA_YEARS[lord]
    years_remaining = years_total * (1 - fraction_traversed)
    
    return lord, years_remaining, nak_idx


def days_to_ymd(total_days: float):
    """Convert days to (years, months, days) tuple."""
    years = int(total_days / 365.25)
    rem = total_days - years * 365.25
    months = int(rem / 30.4375)
    days = int(rem - months * 30.4375)
    return years, months, days


def add_years_precise(dt: datetime, years_float: float) -> datetime:
    """Add decimal years to a datetime precisely."""
    days = years_float * 365.25
    return dt + timedelta(days=days)


def calc_pratyantar_dashas(
    antardasha_lord: str,
    antardasha_start: datetime,
    antardasha_end: datetime,
    mahadasha_lord: str
) -> List[Dict]:
    """
    Calculate all 9 Pratyantar dashas within one Antardasha.
    
    Returns list of dicts with start, end, lord, duration for each Pratyantar.
    """
    antardasha_duration_days = (antardasha_end - antardasha_start).total_seconds() / 86400
    
    # Sequence starts from the Antardasha lord
    start_idx = DASHA_ORDER.index(antardasha_lord)
    sequence = [DASHA_ORDER[(start_idx + i) % 9] for i in range(9)]
    
    pratyantars = []
    current_start = antardasha_start
    
    for p_lord in sequence:
        # Duration = antardasha_duration × (p_lord_years / 120)
        duration_days = antardasha_duration_days * (DASHA_YEARS[p_lord] / DASHA_TOTAL)
        current_end = current_start + timedelta(days=duration_days)
        
        y, m, d = days_to_ymd(duration_days)
        
        pratyantars.append({
            "lord":     p_lord,
            "start":    current_start.strftime("%Y-%m-%d"),
            "end":      current_end.strftime("%Y-%m-%d"),
            "duration": {"years": y, "months": m, "days": d},
            "duration_days": round(duration_days, 1),
            "label":    f"{mahadasha_lord}-{antardasha_lord}-{p_lord}",
        })
        
        current_start = current_end
    
    return pratyantars


def calc_full_3level_dasha(moon_lon_sid: float, birth_dt: datetime, years: int = 120) -> List[Dict]:
    """
    Calculate complete 3-level Vimshottari Dasha.
    Returns list of Mahadashas, each containing Antardashas,
    each containing Pratyantars.
    """
    lord, balance_years, nak_idx = get_dasha_lord_from_moon(moon_lon_sid)
    
    # Start of first dasha
    dasha_start = add_years_precise(birth_dt, -DASHA_YEARS[lord] + balance_years)
    
    # Get starting position in sequence
    start_idx = DASHA_ORDER.index(lord)
    
    result = []
    current_maha_start = dasha_start
    end_limit = birth_dt + timedelta(days=years*365.25)
    
    for i in range(9):  # Up to 9 full mahadashas (covers 120 years)
        maha_lord = DASHA_ORDER[(start_idx + i) % 9]
        maha_years = DASHA_YEARS[maha_lord]
        maha_end = add_years_precise(current_maha_start, maha_years)
        
        if current_maha_start > end_limit:
            break
        
        y, m, d = days_to_ymd(maha_years * 365.25)
        
        # ── Build Antardashas ──────────────────────────────────────────
        antardashas = []
        antar_start_idx = DASHA_ORDER.index(maha_lord)
        current_antar_start = current_maha_start
        
        for j in range(9):
            antar_lord = DASHA_ORDER[(antar_start_idx + j) % 9]
            # Antardasha duration = Maha_years × (antar_years / 120)
            antar_duration_years = maha_years * DASHA_YEARS[antar_lord] / DASHA_TOTAL
            antar_end = add_years_precise(current_antar_start, antar_duration_years)
            
            ay, am, ad = days_to_ymd(antar_duration_years * 365.25)
            
            # ── Build Pratyantars ──────────────────────────────────────
            pratyantars = calc_pratyantar_dashas(
                antar_lord, current_antar_start, antar_end, maha_lord
            )
            
            antardashas.append({
                "lord":         antar_lord,
                "start":        current_antar_start.strftime("%Y-%m-%d"),
                "end":          antar_end.strftime("%Y-%m-%d"),
                "duration":     {"years": ay, "months": am, "days": ad},
                "label":        f"{maha_lord}-{antar_lord}",
                "pratyantars":  pratyantars,
            })
            
            current_antar_start = antar_end
        
        result.append({
            "lord":       maha_lord,
            "start":      current_maha_start.strftime("%Y-%m-%d"),
            "end":        maha_end.strftime("%Y-%m-%d"),
            "duration":   {"years": y, "months": m, "days": d},
            "antardashas": antardashas,
        })
        
        current_maha_start = maha_end
    
    return result


def get_current_3level_dasha(moon_lon_sid: float, birth_dt: datetime) -> Dict:
    """
    Get the current running Mahadasha + Antardasha + Pratyantar.
    """
    from datetime import date
    today = datetime.now()
    
    full = calc_full_3level_dasha(moon_lon_sid, birth_dt, years=120)
    
    for maha in full:
        ms = datetime.strptime(maha["start"], "%Y-%m-%d")
        me = datetime.strptime(maha["end"], "%Y-%m-%d")
        if ms <= today <= me:
            for antar in maha["antardashas"]:
                as_ = datetime.strptime(antar["start"], "%Y-%m-%d")
                ae  = datetime.strptime(antar["end"], "%Y-%m-%d")
                if as_ <= today <= ae:
                    # Find current pratyantar
                    for prat in antar["pratyantars"]:
                        ps = datetime.strptime(prat["start"], "%Y-%m-%d")
                        pe = datetime.strptime(prat["end"], "%Y-%m-%d")
                        if ps <= today <= pe:
                            return {
                                "mahadasha":   maha["lord"],
                                "antardasha":  antar["lord"],
                                "pratyantar":  prat["lord"],
                                "maha_end":    maha["end"],
                                "antar_end":   antar["end"],
                                "prat_end":    prat["end"],
                                "label":       prat["label"],
                                "maha_start":  maha["start"],
                                "antar_start": antar["start"],
                                "prat_start":  prat["start"],
                            }
    return {}


if __name__ == "__main__":
    # Test: Vedanth — Moon in Taurus 26.4° = Mrigashira, Dwitiya Shukla
    # Moon lon approx 56.4°
    moon_lon = 56.4
    birth_dt = datetime(1996, 5, 19, 14, 25)  # 2:25 PM IST
    
    print("PRATYANTAR DASHA TEST — Vedanth (May 19 1996)")
    print("="*65)
    
    lord, bal, nak = get_dasha_lord_from_moon(moon_lon)
    print(f"Birth Nakshatra idx: {nak} → Dasha lord: {lord}")
    print(f"Balance at birth:    {bal:.2f} years")
    print()
    
    current = get_current_3level_dasha(moon_lon, birth_dt)
    if current:
        print(f"CURRENT DASHA (May 2026):")
        print(f"  Mahadasha:  {current['mahadasha'].capitalize():<12} until {current['maha_end']}")
        print(f"  Antardasha: {current['antardasha'].capitalize():<12} until {current['antar_end']}")
        print(f"  Pratyantar: {current['pratyantar'].capitalize():<12} until {current['prat_end']}")
        print(f"  Label:      {current['label']}")
    
    print()
    full = calc_full_3level_dasha(moon_lon, birth_dt, years=40)
    print(f"Showing first 2 Mahadashas with Antardashas + Pratyantars:")
    for maha in full[:2]:
        print(f"\n  MAHADASHA: {maha['lord'].upper():<10} {maha['start']} → {maha['end']}")
        for antar in maha['antardashas'][:3]:
            print(f"    ANTAR: {antar['lord']:<10} {antar['start']} → {antar['end']}")
            for prat in antar['pratyantars'][:3]:
                dur = prat['duration']
                print(f"      PRAT: {prat['lord']:<10} {prat['start']} → {prat['end']}  ({dur['months']}m {dur['days']}d)")
        print(f"    ... (9 antardashas total, 81 pratyantars total)")
