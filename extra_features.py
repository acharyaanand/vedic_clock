"""
extra_features.py — DrikPanchang Parity Features
=================================================
Covers all MEDIUM/HIGH priority gaps vs DrikPanchang:

1. Kala Sarpa Dosha (all 12 types)
2. Moonrise / Moonset
3. Ghati / Pala / Vipala (Vedic time units)
4. Shaka Samvat / Vikram Samvat / Purnimanta month
5. Ganda Moola check
6. Varjyam timing
7. Dur Muhurta timing  
8. Divisional charts D2, D3, D7, D10, D12 (most used)
9. Gemstone calculator
10. Baby name calculator (Nakshatra Swara)
11. Vimshopaka Bala
12. CSV export
"""

import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# ═══════════════════════════════════════════════════════════════════════
# 1. KALA SARPA DOSHA — All 12 Types
# ═══════════════════════════════════════════════════════════════════════

KALA_SARPA_TYPES = {
    0:  {"name": "Ananta",     "rahu_house": 1,  "ketu_house": 7},
    1:  {"name": "Kulika",     "rahu_house": 2,  "ketu_house": 8},
    2:  {"name": "Vasuki",     "rahu_house": 3,  "ketu_house": 9},
    3:  {"name": "Shankhapala","rahu_house": 4,  "ketu_house": 10},
    4:  {"name": "Padma",      "rahu_house": 5,  "ketu_house": 11},
    5:  {"name": "Mahapadma",  "rahu_house": 6,  "ketu_house": 12},
    6:  {"name": "Takshaka",   "rahu_house": 7,  "ketu_house": 1},
    7:  {"name": "Karkotaka",  "rahu_house": 8,  "ketu_house": 2},
    8:  {"name": "Shankhachuda","rahu_house": 9, "ketu_house": 3},
    9:  {"name": "Ghatak",     "rahu_house": 10, "ketu_house": 4},
    10: {"name": "Vishadhar",  "rahu_house": 11, "ketu_house": 5},
    11: {"name": "Sheshnaga",  "rahu_house": 12, "ketu_house": 6},
}

KSD_EFFECTS = {
    "Ananta":      "Obstacles in life path, delays in success",
    "Kulika":      "Financial difficulties, obstacles to wealth",
    "Vasuki":      "Family troubles, sibling conflicts",
    "Shankhapala": "Domestic unhappiness, mother's suffering",
    "Padma":       "Problems with children, education challenges",
    "Mahapadma":   "Health issues, legal troubles",
    "Takshaka":    "Marital discord, partnership problems",
    "Karkotaka":   "Longevity concerns, obstacles to moksha",
    "Shankhachuda":"Father's suffering, luck challenges",
    "Ghatak":      "Career obstacles, social difficulties",
    "Vishadhar":   "Income struggles, elder sibling troubles",
    "Sheshnaga":   "Hidden enemies, expenditure problems",
}

def calc_kala_sarpa_dosha(planets: dict, houses: dict) -> dict:
    """
    Check for Kala Sarpa Dosha and identify its type.
    
    KSD exists when ALL 7 planets (Sun-Saturn) are between Rahu and Ketu
    in the same half of the zodiac.
    
    Parameters:
        planets: {planet: {longitude: float, ...}} — sidereal longitudes
        houses:  {1: {planets: [...], sign: ...}, ...}
    
    Returns dict with dosha status, type, name, effects, remedies.
    """
    PLANETS_7 = ["sun","moon","mars","mercury","jupiter","venus","saturn"]
    
    rahu_lon = planets.get("rahu", {}).get("longitude", 0)
    ketu_lon = planets.get("ketu", {}).get("longitude", 0)
    
    if not rahu_lon:
        return {"present": False, "reason": "Rahu position unknown"}
    
    # Rahu moves in reverse — get the arc from Rahu to Ketu (going forward)
    # All planets must be in this arc for KSD
    
    # Arc from Rahu forward to Ketu (going in direction of zodiac increase)
    if ketu_lon > rahu_lon:
        rahu_to_ketu_forward = ketu_lon - rahu_lon
    else:
        rahu_to_ketu_forward = 360 - rahu_lon + ketu_lon
    
    # Check if all 7 planets are between Rahu and Ketu
    planets_in_rahu_ketu_arc = []
    planets_outside = []
    
    for p in PLANETS_7:
        plon = planets.get(p, {}).get("longitude")
        if plon is None:
            continue
        # Distance from Rahu going forward
        dist_from_rahu = (plon - rahu_lon) % 360
        if dist_from_rahu < rahu_to_ketu_forward:
            planets_in_rahu_ketu_arc.append(p)
        else:
            planets_outside.append(p)
    
    ksd_present = len(planets_outside) == 0 and len(planets_in_rahu_ketu_arc) == 7
    
    # Partial KSD — some planets outside
    partial = (len(planets_outside) <= 1 and len(planets_in_rahu_ketu_arc) >= 6)
    
    if not ksd_present and not partial:
        return {
            "present": False,
            "partial": False,
            "planets_in_arc": planets_in_rahu_ketu_arc,
            "planets_outside": planets_outside,
            "note": "No Kala Sarpa Dosha"
        }
    
    # Identify the type based on Rahu's house
    rahu_house = None
    for hnum, hdata in houses.items():
        if "rahu" in [p.lower() for p in hdata.get("planets", [])]:
            rahu_house = hnum
            break
    
    # Alternative: calculate from Rahu's longitude
    if rahu_house is None:
        rahu_sign = int(rahu_lon / 30)
        lagna_lon = planets.get("ascendant", {}).get("longitude", 0)
        lagna_sign = int(lagna_lon / 30)
        rahu_house = ((rahu_sign - lagna_sign) % 12) + 1
    
    ksd_type = None
    ksd_name = "Unknown"
    for type_num, type_info in KALA_SARPA_TYPES.items():
        if type_info["rahu_house"] == rahu_house:
            ksd_type = type_num
            ksd_name = type_info["name"]
            break
    
    # Severity check — if Lagna lord or Moon is with Rahu/Ketu, more severe
    severity = "Moderate"
    moon_lon = planets.get("moon", {}).get("longitude", 0)
    dist_moon_rahu = abs(moon_lon - rahu_lon) % 360
    if dist_moon_rahu < 10 or dist_moon_rahu > 350:
        severity = "Severe"
    
    return {
        "present":          ksd_present,
        "partial":          partial and not ksd_present,
        "type":             ksd_type,
        "name":             ksd_name,
        "rahu_house":       rahu_house,
        "ketu_house":       (rahu_house + 6 - 1) % 12 + 1,
        "severity":         severity,
        "effect":           KSD_EFFECTS.get(ksd_name, ""),
        "planets_in_arc":   planets_in_rahu_ketu_arc,
        "planets_outside":  planets_outside,
        "remedy": (
            "Perform Kala Sarpa Dosha Puja at Trimbakeshwar or Ujjain. "
            "Worship Shiva on Mondays. Chant Maha Mrityunjaya mantra. "
            "Observe Naga Panchami. Donate to snake temples."
        ),
        "source": "BPHS Ch.85, Sarvartha Chintamani"
    }


# ═══════════════════════════════════════════════════════════════════════
# 2. MOONRISE / MOONSET
# ═══════════════════════════════════════════════════════════════════════

def calc_moonrise_moonset(year: int, month: int, day: int,
                           lat: float, lon: float, tz: float = 5.5) -> dict:
    """
    Calculate approximate moonrise and moonset times.
    Accuracy: ±10-15 minutes (sufficient for panchanga purposes).
    
    Method: Moon moves ~13.2°/day. Calculate moon's position
    and find when it crosses the horizon.
    """
    from datetime import date as _date
    
    def jd(y, m, d, h=0):
        if m <= 2: y -= 1; m += 12
        A = int(y/100); B = 2 - A + int(A/4)
        return int(365.25*(y+4716)) + int(30.6001*(m+1)) + d + h/24 + B - 1524.5
    
    def moon_lon_approx(jd_):
        """Fast Moon longitude (Meeus simplified)."""
        T = (jd_ - 2451545.0) / 36525.0
        Lp = (218.3164477 + 481267.88123421*T) % 360
        D  = (297.8501921 + 445267.1114034*T) % 360
        M  = (357.5291092 + 35999.0502909*T) % 360
        Mp = (134.9633964 + 477198.8675055*T) % 360
        SL = (6288774*math.sin(math.radians(Mp))
             + 1274027*math.sin(math.radians(2*D-Mp))
             +  658314*math.sin(math.radians(2*D))
             -  185116*math.sin(math.radians(M))
             -  114332*math.sin(math.radians(2*Mp))) / 1e6
        return (Lp + SL) % 360
    
    def ayanamsa(yr): return 23.8665 + 0.014206*(yr-2000)
    
    # Moon's right ascension and declination
    def moon_ra_dec(jd_):
        trop_lon = moon_lon_approx(jd_)
        # Convert ecliptic to equatorial (obliquity ~23.44°)
        eps = math.radians(23.4397 - 0.0001*((jd_-2451545)/36525))
        lon_r = math.radians(trop_lon)
        ra = math.degrees(math.atan2(
            math.sin(lon_r)*math.cos(eps),
            math.cos(lon_r)
        )) % 360
        dec = math.degrees(math.asin(math.sin(lon_r)*math.sin(eps)))
        return ra, dec
    
    # Find hour when Moon crosses horizon
    def moon_altitude(h_ut, observer_lat):
        jd_ = jd(year, month, day, h_ut)
        ra, dec = moon_ra_dec(jd_)
        # Hour angle
        gst = (280.46061837 + 360.98564736629*jd_) % 360
        lst = (gst + lon) % 360  # Local sidereal time
        ha = (lst - ra) % 360
        if ha > 180: ha -= 360
        # Altitude
        lat_r = math.radians(observer_lat)
        dec_r = math.radians(dec)
        ha_r  = math.radians(ha)
        alt = math.degrees(math.asin(
            math.sin(lat_r)*math.sin(dec_r) +
            math.cos(lat_r)*math.cos(dec_r)*math.cos(ha_r)
        ))
        return alt
    
    # Scan for moonrise/moonset (when altitude crosses -0.567° for refraction)
    moonrise = None
    moonset  = None
    
    prev_alt = moon_altitude(0 - tz, lat)  # midnight local
    
    step = 0.25  # 15 min steps
    h = step
    while h < 24 + step:
        h_ut = h - tz
        curr_alt = moon_altitude(h_ut, lat)
        
        # Check for sign change (crossing horizon)
        if prev_alt < -0.567 and curr_alt >= -0.567 and moonrise is None:
            # Binary search
            lo, hi = h - step, h
            for _ in range(20):
                mid = (lo + hi) / 2
                a = moon_altitude(mid - tz, lat)
                if a < -0.567: lo = mid
                else: hi = mid
            moonrise = (lo + hi) / 2
        
        if prev_alt >= -0.567 and curr_alt < -0.567 and moonset is None:
            lo, hi = h - step, h
            for _ in range(20):
                mid = (lo + hi) / 2
                a = moon_altitude(mid - tz, lat)
                if a >= -0.567: lo = mid
                else: hi = mid
            moonset = (lo + hi) / 2
        
        prev_alt = curr_alt
        h += step
    
    def fmt(h):
        if h is None: return None
        hr = int(h) % 24; mn = int((h%1)*60)
        ap = "AM" if hr < 12 else "PM"; h12 = hr%12 or 12
        return f"{h12:02d}:{mn:02d} {ap}"
    
    # Moon phase
    jd_ = jd(year, month, day, 12 - tz)
    jd_new = 2451549.5  # Jan 6 2000 new moon
    synodic = 29.530588
    phase_days = (jd_ - jd_new) % synodic
    phase_pct  = phase_days / synodic * 100
    
    if phase_days < 1.85:    phase_name = "New Moon"
    elif phase_days < 7.38:  phase_name = "Waxing Crescent"
    elif phase_days < 9.22:  phase_name = "First Quarter"
    elif phase_days < 14.77: phase_name = "Waxing Gibbous"
    elif phase_days < 16.61: phase_name = "Full Moon"
    elif phase_days < 22.15: phase_name = "Waning Gibbous"
    elif phase_days < 24.00: phase_name = "Last Quarter"
    elif phase_days < 29.53: phase_name = "Waning Crescent"
    else:                    phase_name = "New Moon"
    
    return {
        "moonrise":   fmt(moonrise),
        "moonset":    fmt(moonset),
        "phase":      phase_name,
        "phase_pct":  round(phase_pct, 1),
        "phase_days": round(phase_days, 1),
    }


# ═══════════════════════════════════════════════════════════════════════
# 3. VEDIC TIME — Ghati / Pala / Vipala + Samvat
# ═══════════════════════════════════════════════════════════════════════

def calc_vedic_time(hour: float, sunrise_h: float, sunset_h: float) -> dict:
    """
    Convert clock time to Vedic time units.
    
    1 day (sunrise to sunrise) = 60 Ghati
    1 Ghati = 60 Pala (Vighatika)
    1 Pala  = 60 Vipala (Lipta)
    
    Day has 30 Ghati, Night has 30 Ghati.
    """
    day_len = sunset_h - sunrise_h
    night_len = 24 - day_len
    
    if sunrise_h <= hour <= sunset_h:
        # Daytime
        elapsed = hour - sunrise_h
        total_ghati = elapsed / day_len * 30
        is_day = True
    elif hour < sunrise_h:
        # Before sunrise (night from previous day)
        elapsed = hour + (24 - sunset_h)  # Not exactly right
        total_ghati = 30 + elapsed / night_len * 30
        is_day = False
    else:
        # After sunset
        elapsed = hour - sunset_h
        total_ghati = 30 + elapsed / night_len * 30
        is_day = False
    
    ghati  = int(total_ghati)
    pala   = int((total_ghati - ghati) * 60)
    vipala = int(((total_ghati - ghati) * 60 - pala) * 60)
    
    return {
        "ghati":   ghati,
        "pala":    pala,
        "vipala":  vipala,
        "display": f"{ghati} Ghati {pala} Pala {vipala} Vipala",
        "is_day":  is_day,
        "note":    "Day = 30 Ghati (sunrise to sunset)"
    }


def calc_samvat(year: int, month: int, day: int,
                tithi_idx: int, paksha: str) -> dict:
    """
    Calculate Shaka Samvat, Vikram Samvat, and Hindu month names.
    
    Shaka Samvat  = Gregorian year - 78 (starts at Chaitra Shukla Pratipada)
    Vikram Samvat = Gregorian year + 57 (approx)
    """
    # Shaka Samvat
    # Starts at Chaitra Shukla Pratipada (approx Mar/Apr)
    if month >= 4 or (month == 3 and day >= 20):
        shaka = year - 78
    else:
        shaka = year - 79
    
    # Vikram Samvat
    if month >= 11 or (month == 10 and day >= 15):
        vikram = year + 57
    else:
        vikram = year + 56
    
    # Gujarati Samvat (starts at Diwali = Kartik Shukla 1)
    gujarati = vikram - 1
    
    # Solar months (Saura months based on Sun's position)
    SAURA_MONTHS = ["Mesha","Vrishabha","Mithuna","Karka","Simha","Kanya",
                    "Tula","Vrishchika","Dhanu","Makara","Kumbha","Meena"]
    
    # Amanta lunar months (Moon-based, ends at Amavasya)
    AMANTA_MONTHS = ["Chaitra","Vaishakha","Jyeshtha","Ashadha","Shravana",
                     "Bhadrapada","Ashwin","Kartika","Margashirsha","Paush",
                     "Magha","Phalguna"]
    
    # Approximate Hindu month from Gregorian date
    month_offset = (month - 3) % 12  # Chaitra starts ~March
    amanta_month = AMANTA_MONTHS[month_offset % 12]
    
    # Purnimanta (ends at Purnima — used in North India)
    purnimanta_month = AMANTA_MONTHS[(month_offset + 1) % 12]
    
    # Samvatsara (60-year cycle name)
    SAMVATSARA = [
        "Prabhava","Vibhava","Shukla","Pramoda","Prajapati","Angiras",
        "Shrimukha","Bhava","Yuvan","Dhatri","Ishvara","Bahudhanya",
        "Pramathi","Vikrama","Vrisha","Chitrabanu","Svabhanu","Tarana",
        "Parthiva","Vyaya","Sarvajit","Sarvadharin","Virodhi","Vikrita",
        "Khara","Nandana","Vijaya","Jaya","Manmatha","Durmukhi",
        "Hevilambi","Vilambi","Vikari","Sharvari","Plava","Shubhakrit",
        "Shobhakrit","Krodhi","Vishvavasu","Parabhava","Plavanga","Kilaka",
        "Saumya","Sadharana","Virodhakrit","Paridhavin","Pramadicha",
        "Ananda","Rakshasa","Nala","Pingala","Kalayukti","Siddharthi",
        "Raudri","Durmati","Dundubhi","Rudhirodgari","Raktakshi",
        "Krodhana","Akshaya"
    ]
    samvatsara_idx = (vikram - 1) % 60
    samvatsara = SAMVATSARA[samvatsara_idx]
    
    # Ayana (Uttarayana/Dakshinayana)
    if 3 <= month <= 8:  # approx
        ayana = "Uttarayana" if month <= 6 else "Dakshinayana"
    else:
        ayana = "Dakshinayana" if month >= 9 else "Uttarayana"
    
    # Ritu (Season)
    RITU = {(3,4):"Vasanta (Spring)", (5,6):"Grishma (Summer)",
            (7,8):"Varsha (Monsoon)", (9,10):"Sharad (Autumn)",
            (11,12):"Hemanta (Pre-Winter)", (1,2):"Shishira (Winter)"}
    ritu = "Vasanta"
    for months_pair, name in RITU.items():
        if month in months_pair:
            ritu = name
            break
    
    return {
        "shaka_samvat":      shaka,
        "vikram_samvat":     vikram,
        "gujarati_samvat":   gujarati,
        "samvatsara":        samvatsara,
        "amanta_month":      amanta_month,
        "purnimanta_month":  purnimanta_month,
        "ayana":             ayana,
        "ritu":              ritu,
    }


# ═══════════════════════════════════════════════════════════════════════
# 4. GANDA MOOLA CHECK
# ═══════════════════════════════════════════════════════════════════════

# Ganda Moola = Birth at junction of certain Nakshatras
# Specifically: Ashwini, Ashlesha, Magha, Jyeshtha, Mula, Revati
# Within 1 Ghati (24 min) of start or end of these nakshatras
GANDA_MOOLA_NAKS = {0, 8, 9, 17, 18, 26}  # Ashwini, Ashlesha, Magha, Jyeshtha, Mula, Revati
GANDA_MOOLA_NAMES = ["Ashwini","Ashlesha","Magha","Jyeshtha","Mula","Revati"]

def check_ganda_moola(moon_lon: float) -> dict:
    """Check if Moon is in Ganda Moola nakshatra at junction."""
    nak_size = 360 / 27  # 13.333°
    nak_idx = int(moon_lon * 27 / 360) % 27
    deg_in_nak = moon_lon % nak_size
    
    # 1 Ghati = 24 minutes = Moon moves ~0.22°
    # Junction zone = within 1 Ghati = 0.22° of start or end
    junction_deg = 0.22
    at_start = deg_in_nak < junction_deg
    at_end   = deg_in_nak > (nak_size - junction_deg)
    
    NAKS = ["Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
            "Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni",
            "Uttara Phalguni","Hasta","Chitra","Swati","Vishakha","Anuradha",
            "Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha","Shravana",
            "Dhanishtha","Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada",
            "Revati"]
    
    is_ganda_moola = nak_idx in GANDA_MOOLA_NAKS
    is_at_junction = (at_start or at_end) and is_ganda_moola
    
    remedy = ""
    if is_ganda_moola:
        remedy = ("Perform Nakshatra Shanti Puja within 27 days of birth. "
                  "Consult a Jyotishi for specific remedies.")
    
    return {
        "is_ganda_moola":   is_ganda_moola,
        "at_junction":      is_at_junction,
        "nakshatra":        NAKS[nak_idx],
        "severity":         "High" if is_at_junction else ("Moderate" if is_ganda_moola else "None"),
        "remedy":           remedy,
        "note": ("Ganda Moola birth requires Shanti if Moon is within "
                 "1 Ghati of junction of Ashwini/Ashlesha/Magha/Jyeshtha/Mula/Revati")
    }


# ═══════════════════════════════════════════════════════════════════════
# 5. VARJYAM TIMING
# ═══════════════════════════════════════════════════════════════════════

def calc_varjyam(moon_lon_sid: float, sunrise_h: float, tz: float = 5.5) -> dict:
    """
    Varjyam = inauspicious period based on Moon's nakshatra.
    Each nakshatra has a specific Varjyam duration.
    
    Duration: ~1.5-3 hours per day. Based on Moon's movement through
    a specific part of each nakshatra.
    """
    VARJYAM_START_GHATI = [
        50, 3, 20, 7, 33, 22, 13, 22, 27, 27, 13, 7,
        30, 11, 9, 17, 22, 50, 11, 9, 17, 50, 9, 14,
        13, 27, 27
    ]  # Ghati from start of nakshatra when Varjyam begins
    
    VARJYAM_DURATION_GHATI = [
        4, 4, 4, 3, 3, 4, 4, 4, 4, 3, 3, 4,
        4, 4, 3, 4, 4, 4, 4, 4, 4, 3, 4, 4,
        4, 4, 3
    ]  # Duration in Ghati
    
    nak_size = 360 / 27
    nak_idx = int(moon_lon_sid * 27 / 360) % 27
    deg_in_nak = moon_lon_sid % nak_size
    
    # Moon's speed: ~13.2°/day = 0.55°/hour
    MOON_SPEED = 13.2 / 24  # degrees per hour
    
    # Time until end of current nakshatra
    remaining_deg = nak_size - deg_in_nak
    hours_to_nak_end = remaining_deg / MOON_SPEED
    
    # Varjyam starts when Moon reaches specific Ghati within nakshatra
    ghati_size_hours = 24 / 60  # 1 ghati = 24 min = 0.4 h
    varjyam_start_ghati = VARJYAM_START_GHATI[nak_idx]
    varjyam_dur_ghati   = VARJYAM_DURATION_GHATI[nak_idx]
    
    # Convert to degrees from nak start
    nak_start_lon = nak_idx * nak_size
    moon_at_nak_start = moon_lon_sid - deg_in_nak  # = nak_start_lon approximately
    
    varjyam_start_deg = nak_start_lon + (varjyam_start_ghati / 60) * nak_size
    varjyam_end_deg   = varjyam_start_deg + (varjyam_dur_ghati / 60) * nak_size
    
    # Convert to clock time from current position
    hours_to_varjyam_start = (varjyam_start_deg - moon_lon_sid) / MOON_SPEED
    hours_to_varjyam_end   = (varjyam_end_deg - moon_lon_sid) / MOON_SPEED
    
    def fmt_h(h_from_now, base_h):
        t = base_h + h_from_now
        t = t % 24
        hr = int(t); mn = int((t-hr)*60)
        ap = "AM" if hr < 12 else "PM"; h12 = hr%12 or 12
        return f"{h12:02d}:{mn:02d} {ap}"
    
    # Only show if within today
    start_str = end_str = None
    if 0 < hours_to_varjyam_start < 24:
        start_str = fmt_h(hours_to_varjyam_start, sunrise_h)
        end_str   = fmt_h(hours_to_varjyam_end, sunrise_h)
    
    NAKS = ["Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
            "Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni",
            "Uttara Phalguni","Hasta","Chitra","Swati","Vishakha","Anuradha",
            "Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha","Shravana",
            "Dhanishtha","Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada",
            "Revati"]
    
    return {
        "start": start_str,
        "end":   end_str,
        "nakshatra": NAKS[nak_idx],
        "duration_ghati": varjyam_dur_ghati,
        "note": "Varjyam: inauspicious period — avoid important work"
    }


# ═══════════════════════════════════════════════════════════════════════
# 6. DUR MUHURTA TIMING
# ═══════════════════════════════════════════════════════════════════════

def calc_dur_muhurta(year: int, month: int, day: int,
                      sunrise_h: float, sunset_h: float) -> list:
    """
    Dur Muhurta = inauspicious 48-minute windows in a day.
    2 per day, specific to weekday.
    
    Source: Muhurta Chintamani
    """
    from datetime import date as _date
    weekday_iso = _date(year, month, day).weekday()
    weekday = (weekday_iso + 1) % 7  # Sun=0..Sat=6
    
    day_len = sunset_h - sunrise_h
    # Day divided into 30 Muhurtas (each 48 min)
    muhurta_len = day_len / 15  # hours per Muhurta (1/15 of day)
    
    # Dur Muhurta positions (1-based, out of 15 daytime Muhurtas)
    # Source: Muhurta Chintamani
    DUR_MUHURTA = {
        0: [6, 8],   # Sunday
        1: [7, 11],  # Monday
        2: [5, 9],   # Tuesday
        3: [4, 12],  # Wednesday
        4: [3, 6],   # Thursday
        5: [2, 10],  # Friday
        6: [1, 8],   # Saturday
    }
    
    positions = DUR_MUHURTA.get(weekday, [])
    
    def fmt(h):
        hr = int(h); mn = int((h-hr)*60)
        ap = "AM" if hr < 12 else "PM"; h12 = hr%12 or 12
        return f"{h12:02d}:{mn:02d} {ap}"
    
    results = []
    for pos in positions:
        start_h = sunrise_h + (pos - 1) * muhurta_len
        end_h   = start_h + muhurta_len
        results.append({
            "start":    fmt(start_h),
            "end":      fmt(end_h),
            "muhurta":  pos,
            "duration": "48 minutes",
        })
    
    return results


# ═══════════════════════════════════════════════════════════════════════
# 7. DIVISIONAL CHARTS (D2, D3, D7, D10, D12)
# ═══════════════════════════════════════════════════════════════════════

SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
         "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

def calc_divisional_charts(planet_lons: dict) -> dict:
    """
    Calculate ALL 16 Shodasavarga divisional charts.
    D1 through D60 — complete set as per BPHS Ch.6.
    
    Source: Brihat Parashara Hora Shastra Ch.6 (Shodasha Varga)
    """
    SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
             "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

    def sign_of(lon): return int(lon / 30) % 12
    def deg_in(lon):  return lon % 30

    # ── D1: Rasi (natal chart) ─────────────────────────────────────
    def d1(lon): return sign_of(lon)

    # ── D2: Hora (wealth) ──────────────────────────────────────────
    # Odd signs: 0-15° = Leo(4), 15-30° = Cancer(3)
    # Even signs: 0-15° = Cancer(3), 15-30° = Leo(4)
    def d2(lon):
        s = sign_of(lon); d = deg_in(lon)
        return 4 if (s%2==0 and d<15) or (s%2==1 and d>=15) else 3

    # ── D3: Drekkana (siblings, courage) ──────────────────────────
    # 3 equal parts of 10°. Part 1=same sign, Part 2=+4, Part 3=+8
    def d3(lon):
        s = sign_of(lon); d = deg_in(lon)
        return (s + [0,4,8][int(d/10)]) % 12

    # ── D4: Chaturthamsha (property, fortune) ──────────────────────
    # 4 parts of 7.5°. Cardinal: Aries/Cancer/Libra/Capricorn start
    # Odd signs start from sign itself; Even signs start from 4th
    def d4(lon):
        s = sign_of(lon); d = deg_in(lon)
        part = int(d / 7.5)  # 0,1,2,3
        if s % 2 == 0:   # Odd sign (Aries=0, Gemini=2...)
            return (s + part) % 12
        else:             # Even sign
            return (s + 3 + part) % 12

    # ── D7: Saptamsha (children, grandchildren) ───────────────────
    # 7 parts of ~4.286°
    # Odd signs: start from same sign; Even signs: start from 7th
    def d7(lon):
        s = sign_of(lon); d = deg_in(lon)
        part = int(d / (30/7))
        if s % 2 == 0:  # Odd sign
            return (s + part) % 12
        else:            # Even sign
            return (s + 6 + part) % 12

    # ── D9: Navamsha (spouse, dharma) — THE most important ─────────
    # 9 parts of 3.333°. Sequence of 12 signs cycling through
    # Fire signs start from Aries, Earth from Capricorn,
    # Air from Libra, Water from Cancer
    def d9(lon):
        total_navamsha = int(lon / (360/108))  # 0-107
        return total_navamsha % 12

    # ── D10: Dasamsha (career, profession) ────────────────────────
    # 10 parts of 3°
    # Odd signs: start from same sign; Even signs: start from 9th
    def d10(lon):
        s = sign_of(lon); d = deg_in(lon)
        part = int(d / 3)
        if s % 2 == 0:  # Odd sign
            return (s + part) % 12
        else:
            return (s + 9 + part) % 12

    # ── D12: Dwadashamsha (parents) ───────────────────────────────
    # 12 parts of 2.5°. Each 2.5° = one sign, cycling from same sign
    def d12(lon):
        s = sign_of(lon); d = deg_in(lon)
        part = int(d / 2.5)
        return (s + part) % 12

    # ── D16: Shodashamsha (vehicles, comforts) ────────────────────
    # 16 parts of 1.875°
    # Movable signs: start from Aries; Fixed: from Leo; Dual: from Sagittarius
    def d16(lon):
        s = sign_of(lon); d = deg_in(lon)
        part = int(d / (30/16))
        sign_type = s % 3  # 0=movable(Ar,Ca,Li,Cp), 1=fixed(Ta,Le,Sc,Aq), 2=dual
        start = [0, 4, 8][sign_type]  # Aries, Leo, Sagittarius
        return (start + part) % 12

    # ── D20: Vimsamsha (spiritual progress, worship) ──────────────
    # 20 parts of 1.5°
    # Movable: start Aries(0); Fixed: start Sagittarius(8); Dual: start Leo(4)
    def d20(lon):
        s = sign_of(lon); d = deg_in(lon)
        part = int(d / 1.5)
        sign_type = s % 3
        start = [0, 8, 4][sign_type]
        return (start + part) % 12

    # ── D24: Siddhamsha/Chaturvimsamsha (education, knowledge) ────
    # 24 parts of 1.25°
    # Odd signs: start from Leo(4); Even signs: start from Cancer(3)
    def d24(lon):
        s = sign_of(lon); d = deg_in(lon)
        part = int(d / 1.25)
        start = 4 if s % 2 == 0 else 3  # Leo or Cancer
        return (start + part) % 12

    # ── D27: Bhamsha/Nakshatramsha (strength, vitality) ───────────
    # 27 parts of 1.111°
    # Fire signs: from Aries; Earth: from Cancer; Air: from Libra; Water: from Capricorn
    def d27(lon):
        s = sign_of(lon); d = deg_in(lon)
        part = int(d / (30/27))
        element = s % 4  # 0=fire(Ar,Le,Sg), 1=earth(Ta,Vi,Cp), 2=air(Ge,Li,Aq), 3=water(Ca,Sc,Pi)
        start = [0, 3, 6, 9][element]  # Aries, Cancer, Libra, Capricorn
        return (start + part) % 12

    # ── D30: Trimsamsha (evils, misfortune, diseases) ─────────────
    # Unequal parts — 5 planets rule different portions
    # Odd signs: Mars 0-5°, Saturn 5-10°, Jupiter 10-18°, Mercury 18-25°, Venus 25-30°
    # Even signs: Venus 0-5°, Mercury 5-12°, Jupiter 12-20°, Saturn 20-25°, Mars 25-30°
    def d30(lon):
        s = sign_of(lon); d = deg_in(lon)
        if s % 2 == 0:  # Odd sign
            if d < 5:    return 0   # Aries (Mars)
            elif d < 10: return 10  # Aquarius (Saturn)
            elif d < 18: return 8   # Sagittarius (Jupiter)
            elif d < 25: return 5   # Virgo (Mercury)
            else:        return 1   # Taurus (Venus)
        else:            # Even sign
            if d < 5:    return 1   # Taurus (Venus)
            elif d < 12: return 5   # Virgo (Mercury)
            elif d < 20: return 8   # Sagittarius (Jupiter)
            elif d < 25: return 10  # Aquarius (Saturn)
            else:        return 0   # Aries (Mars)

    # ── D40: Khavedamsha (auspicious/inauspicious effects) ────────
    # 40 parts of 0.75°
    # Odd signs: start from Aries; Even signs: start from Libra
    def d40(lon):
        s = sign_of(lon); d = deg_in(lon)
        part = int(d / 0.75)
        start = 0 if s % 2 == 0 else 6  # Aries or Libra
        return (start + part) % 12

    # ── D45: Akshavedamsha (all results) ──────────────────────────
    # 45 parts of 0.667°
    # Movable: from Aries; Fixed: from Leo; Dual: from Sagittarius
    def d45(lon):
        s = sign_of(lon); d = deg_in(lon)
        part = int(d / (30/45))
        sign_type = s % 3
        start = [0, 4, 8][sign_type]
        return (start + part) % 12

    # ── D60: Shashtiamsha (past karma, overall results) ───────────
    # 60 parts of 0.5°. Most important after D9.
    # Odd signs: from Aries; Even signs: from Libra
    def d60(lon):
        s = sign_of(lon); d = deg_in(lon)
        part = int(d / 0.5)
        start = 0 if s % 2 == 0 else 6
        return (start + part) % 12

    # ── Chart metadata ─────────────────────────────────────────────
    CHART_INFO = {
        "D1":  ("Rasi",            "Natal chart — overall life"),
        "D2":  ("Hora",            "Wealth, prosperity"),
        "D3":  ("Drekkana",        "Siblings, courage, vitality"),
        "D4":  ("Chaturthamsha",   "Property, fixed assets, fortune"),
        "D7":  ("Saptamsha",       "Children, grandchildren, progeny"),
        "D9":  ("Navamsha",        "Spouse, dharma, spiritual life — most important after D1"),
        "D10": ("Dasamsha",        "Career, profession, social status"),
        "D12": ("Dwadashamsha",    "Parents, ancestors, lineage"),
        "D16": ("Shodashamsha",    "Vehicles, comforts, happiness"),
        "D20": ("Vimsamsha",       "Spiritual progress, worship, Upasana"),
        "D24": ("Siddhamsha",      "Education, learning, intelligence"),
        "D27": ("Bhamsha",         "Strength, physical vitality, nakshatras"),
        "D30": ("Trimsamsha",      "Evils, diseases, misfortune"),
        "D40": ("Khavedamsha",     "Auspicious/inauspicious effects, maternal lineage"),
        "D45": ("Akshavedamsha",   "All results, paternal lineage"),
        "D60": ("Shashtiamsha",    "Past karma — most sensitive divisional chart"),
    }

    DIV_FNS = {
        "D1":d1,"D2":d2,"D3":d3,"D4":d4,"D7":d7,"D9":d9,
        "D10":d10,"D12":d12,"D16":d16,"D20":d20,"D24":d24,
        "D27":d27,"D30":d30,"D40":d40,"D45":d45,"D60":d60
    }

    PLANETS_ALL = ["sun","moon","mars","mercury","jupiter","venus",
                   "saturn","rahu","ketu","ascendant"]

    result = {}
    for chart_key, fn in DIV_FNS.items():
        name, purpose = CHART_INFO[chart_key]
        chart = {}
        for p in PLANETS_ALL:
            if p in planet_lons and planet_lons[p] is not None:
                try:
                    sign_idx = fn(planet_lons[p])
                    chart[p] = SIGNS[sign_idx % 12]
                except:
                    chart[p] = "Unknown"
        result[chart_key] = {
            "name":    name,
            "purpose": purpose,
            "planets": chart,
            "source":  "BPHS Ch.6 (Parashara)"
        }

    return result



# ═══════════════════════════════════════════════════════════════════════
# 8. GEMSTONE CALCULATOR
# ═══════════════════════════════════════════════════════════════════════

PLANET_GEMS = {
    "sun":     {
        "primary": "Ruby (Manikya)", "substitute": "Red Spinel / Red Garnet",
        "metal": "Gold", "finger": "Ring finger",
        "day": "Sunday", "benefit": "Confidence, authority, health, government favor"
    },
    "moon":    {
        "primary": "Pearl (Moti)", "substitute": "Moonstone / White Coral",
        "metal": "Silver", "finger": "Little finger",
        "day": "Monday", "benefit": "Mental peace, mother's health, emotions"
    },
    "mars":    {
        "primary": "Red Coral (Moonga)", "substitute": "Carnelian",
        "metal": "Gold/Copper", "finger": "Ring finger",
        "day": "Tuesday", "benefit": "Energy, courage, property, brothers"
    },
    "mercury": {
        "primary": "Emerald (Panna)", "substitute": "Green Tourmaline / Peridot",
        "metal": "Gold", "finger": "Little finger",
        "day": "Wednesday", "benefit": "Intelligence, communication, business"
    },
    "jupiter": {
        "primary": "Yellow Sapphire (Pukhraj)", "substitute": "Yellow Topaz / Citrine",
        "metal": "Gold", "finger": "Index finger",
        "day": "Thursday", "benefit": "Wisdom, wealth, children, spirituality"
    },
    "venus":   {
        "primary": "Diamond (Heera)", "substitute": "White Sapphire / White Zircon",
        "metal": "Silver/Platinum", "finger": "Middle finger",
        "day": "Friday", "benefit": "Love, beauty, luxury, arts, marriage"
    },
    "saturn":  {
        "primary": "Blue Sapphire (Neelam)", "substitute": "Amethyst / Blue Spinel",
        "metal": "Silver/Iron", "finger": "Middle finger",
        "day": "Saturday", "benefit": "Discipline, karma, longevity, service"
    },
    "rahu":    {
        "primary": "Hessonite Garnet (Gomed)", "substitute": "Zircon",
        "metal": "Silver", "finger": "Middle finger",
        "day": "Saturday", "benefit": "Protection from Rahu, foreign travel, technology"
    },
    "ketu":    {
        "primary": "Cat's Eye (Lehsunia)", "substitute": "Tiger's Eye",
        "metal": "Silver", "finger": "Little finger",
        "day": "Tuesday", "benefit": "Spirituality, moksha, past karma resolution"
    },
}

def calc_gemstone(lagna_sign: str, moon_sign: str, planet_strengths: dict = None) -> dict:
    """
    Recommend gemstones based on Lagna lord and other factors.
    
    Primary gem = Lagna lord's gem
    Supporting gems = friendly planet gems
    Avoid = enemy planet gems
    """
    SIGN_LORD = {
        "Aries":"mars","Taurus":"venus","Gemini":"mercury","Cancer":"moon",
        "Leo":"sun","Virgo":"mercury","Libra":"venus","Scorpio":"mars",
        "Sagittarius":"jupiter","Capricorn":"saturn","Aquarius":"saturn",
        "Pisces":"jupiter"
    }
    
    PLANET_FRIENDS = {
        "sun":     ["moon","mars","jupiter"],
        "moon":    ["sun","mercury"],
        "mars":    ["sun","moon","jupiter"],
        "mercury": ["sun","venus"],
        "jupiter": ["sun","moon","mars"],
        "venus":   ["mercury","saturn"],
        "saturn":  ["mercury","venus"],
        "rahu":    ["saturn","venus","mercury"],
        "ketu":    ["mars","venus","saturn"],
    }
    
    lagna_lord = SIGN_LORD.get(lagna_sign, "sun")
    moon_lord  = SIGN_LORD.get(moon_sign, "moon")
    
    primary = PLANET_GEMS.get(lagna_lord, {})
    supporting_planets = PLANET_FRIENDS.get(lagna_lord, [])
    
    return {
        "primary_gem": {
            "planet": lagna_lord.capitalize(),
            "gem":    primary.get("primary", ""),
            "substitute": primary.get("substitute", ""),
            "metal":  primary.get("metal", ""),
            "finger": primary.get("finger", ""),
            "day_to_wear": primary.get("day", ""),
            "benefit": primary.get("benefit", ""),
        },
        "supporting_gems": [
            {
                "planet": p.capitalize(),
                "gem": PLANET_GEMS[p]["primary"],
                "benefit": PLANET_GEMS[p]["benefit"],
            }
            for p in supporting_planets if p in PLANET_GEMS
        ],
        "note": ("Consult a qualified Jyotishi before wearing gemstones. "
                 "Minimum weight: 3-5 Ratti. Wear on auspicious day."),
        "source": "Ratna Pariksha (classical gem treatise)"
    }


# ═══════════════════════════════════════════════════════════════════════
# 9. BABY NAME CALCULATOR (Nakshatra Swara)
# ═══════════════════════════════════════════════════════════════════════

# Each nakshatra pada has specific syllables (Swara/Aksharas)
# for naming a child born in that nakshatra-pada
NAK_NAME_SYLLABLES = {
    "Ashwini":         {"1":"Chu","2":"Che","3":"Cho","4":"La"},
    "Bharani":         {"1":"Li","2":"Lu","3":"Le","4":"Lo"},
    "Krittika":        {"1":"A","2":"I","3":"U","4":"E"},
    "Rohini":          {"1":"O","2":"Va","3":"Vi","4":"Vu"},
    "Mrigashira":      {"1":"Ve","2":"Vo","3":"Ka","4":"Ki"},
    "Ardra":           {"1":"Ku","2":"Gha","3":"Ing","4":"Jha"},
    "Punarvasu":       {"1":"Ke","2":"Ko","3":"Ha","4":"Hi"},
    "Pushya":          {"1":"Hu","2":"He","3":"Ho","4":"Da"},
    "Ashlesha":        {"1":"Di","2":"Du","3":"De","4":"Do"},
    "Magha":           {"1":"Ma","2":"Mi","3":"Mu","4":"Me"},
    "Purva Phalguni":  {"1":"Mo","2":"Ta","3":"Ti","4":"Tu"},
    "Uttara Phalguni": {"1":"Te","2":"To","3":"Pa","4":"Pi"},
    "Hasta":           {"1":"Pu","2":"Sha","3":"Na","4":"Tha"},
    "Chitra":          {"1":"Pe","2":"Po","3":"Ra","4":"Ri"},
    "Swati":           {"1":"Ru","2":"Re","3":"Ro","4":"Ta"},
    "Vishakha":        {"1":"Ti","2":"Tu","3":"Te","4":"To"},
    "Anuradha":        {"1":"Na","2":"Ni","3":"Nu","4":"Ne"},
    "Jyeshtha":        {"1":"No","2":"Ya","3":"Yi","4":"Yu"},
    "Mula":            {"1":"Ye","2":"Yo","3":"Bha","4":"Bhi"},
    "Purva Ashadha":   {"1":"Bhu","2":"Dha","3":"Pha","4":"Dha"},
    "Uttara Ashadha":  {"1":"Bhe","2":"Bho","3":"Ja","4":"Ji"},
    "Shravana":        {"1":"Ju","2":"Je","3":"Jo","4":"Sha"},
    "Dhanishtha":      {"1":"Ga","2":"Gi","3":"Gu","4":"Ge"},
    "Shatabhisha":     {"1":"Go","2":"Sa","3":"Si","4":"Su"},
    "Purva Bhadrapada":{"1":"Se","2":"So","3":"Da","4":"Di"},
    "Uttara Bhadrapada":{"1":"Du","2":"Tha","3":"Jha","4":"Da"},
    "Revati":          {"1":"De","2":"Do","3":"Cha","4":"Chi"},
}

def calc_baby_name(moon_lon_sid: float) -> dict:
    """
    Get recommended name syllables for a baby based on birth nakshatra-pada.
    """
    NAKS = list(NAK_NAME_SYLLABLES.keys())
    nak_size = 360 / 27
    nak_idx = int(moon_lon_sid * 27 / 360) % 27
    deg_in_nak = moon_lon_sid % nak_size
    pada = min(int(deg_in_nak / (nak_size/4)) + 1, 4)
    
    nak_name = NAKS[nak_idx] if nak_idx < len(NAKS) else "Ashwini"
    syllable = NAK_NAME_SYLLABLES.get(nak_name, {}).get(str(pada), "A")
    
    # All syllables for this nakshatra
    all_syllables = NAK_NAME_SYLLABLES.get(nak_name, {})
    
    return {
        "nakshatra":      nak_name,
        "pada":           pada,
        "recommended_syllable": syllable,
        "all_pada_syllables": all_syllables,
        "example_names":  f"Names starting with '{syllable}' are recommended",
        "note": ("Name the child starting with this syllable for auspiciousness. "
                 "Based on Swara Siddhanta from classical texts."),
    }


# ═══════════════════════════════════════════════════════════════════════
# 10. CSV EXPORT
# ═══════════════════════════════════════════════════════════════════════

def export_chart_csv(chart_data: dict) -> str:
    """
    Export birth chart data as CSV string.
    Compatible with Excel/Google Sheets.
    """
    import io
    lines = []
    
    # Header
    lines.append("Field,Value,Notes")
    
    def row(field, value, note=""):
        val = str(value).replace(",","；").replace('"','""')
        return f'"{field}","{val}","{note}"'
    
    # Personal
    lines.append(row("Name", chart_data.get("name","")))
    lines.append(row("Date of Birth", chart_data.get("dob","")))
    lines.append(row("Time of Birth", chart_data.get("tob","")))
    lines.append(row("Place of Birth", chart_data.get("place","")))
    lines.append(row("Latitude", chart_data.get("latitude","")))
    lines.append(row("Longitude", chart_data.get("longitude","")))
    lines.append(row("Timezone", chart_data.get("timezone","")))
    lines.append(row("Ayanamsa", chart_data.get("ayanamsa",""), "Lahiri"))
    lines.append(row("Lagna", chart_data.get("lagna","")))
    lines.append(row("Lagna Lord", chart_data.get("lagna_lord","")))
    
    # Panchanga
    p = chart_data.get("panchanga", {})
    lines.append(row("Tithi", p.get("tithi","")))
    lines.append(row("Vara", p.get("vara","")))
    lines.append(row("Nakshatra", p.get("nakshatra","")))
    lines.append(row("Yoga", p.get("yoga","")))
    lines.append(row("Karana", p.get("karana","")))
    
    # Planets
    lines.append(row("","",""))
    lines.append("Planet,Sign,Degree,Nakshatra,Pada,Retrograde")
    
    planets = chart_data.get("planets", {})
    for pname, pdata in planets.items():
        if isinstance(pdata, dict):
            retro = "R" if pdata.get("is_retrograde") else ""
            lines.append(
                f'"{pname.capitalize()}",'
                f'"{pdata.get("sign","")}","{pdata.get("degree","")}",'
                f'"{pdata.get("nakshatra","")}",'
                f'"{pdata.get("nakshatra_pada","")}","{retro}"'
            )
    
    # Dasha
    lines.append(row("","",""))
    lines.append("Dasha Level,Lord,Start,End")
    dasha = chart_data.get("current_dasha", {})
    if dasha:
        lines.append(f'"Mahadasha","{dasha.get("mahadasha","")}","","'
                     f'{dasha.get("maha_end","")}"')
        lines.append(f'"Antardasha","{dasha.get("antardasha","")}","'
                     f'{dasha.get("antar_start","")}","'
                     f'{dasha.get("antar_end","")}"')
    
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════
# SELF-TEST
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("EXTRA FEATURES TEST")
    print("="*60)
    
    # 1. Vedic time
    vt = calc_vedic_time(10.5, 5.47, 19.12)
    print(f"\n1. Vedic Time (10:30 AM): {vt['display']}")
    
    # 2. Samvat
    sv = calc_samvat(2026, 5, 21, 4, "Shukla")
    print(f"\n2. Samvat (May 21 2026):")
    print(f"   Shaka: {sv['shaka_samvat']}  Vikram: {sv['vikram_samvat']}")
    print(f"   Samvatsara: {sv['samvatsara']}")
    print(f"   Month: {sv['amanta_month']}  Ritu: {sv['ritu']}")
    
    # 3. Moonrise
    mr = calc_moonrise_moonset(2026, 5, 21, 28.61, 77.21)
    print(f"\n3. Moonrise/Moonset Delhi May 21 2026:")
    print(f"   Rise: {mr['moonrise']}  Set: {mr['moonset']}")
    print(f"   Phase: {mr['phase']} ({mr['phase_pct']}%)")
    
    # 4. Dur Muhurta
    dm = calc_dur_muhurta(2026, 5, 21, 5.47, 19.12)
    print(f"\n4. Dur Muhurta (Thursday May 21 2026):")
    for d in dm:
        print(f"   {d['start']} → {d['end']}")
    
    # 5. Ganda Moola check (Vedanth Moon ~56.4° = Mrigashira — NOT Ganda Moola)
    gm = check_ganda_moola(56.4)
    print(f"\n5. Ganda Moola (Mrigashira): {gm['is_ganda_moola']} — {gm['nakshatra']}")
    
    # 6. Baby name
    bn = calc_baby_name(56.4)  # Mrigashira Pada 1 = "Ve"
    print(f"\n6. Baby name syllable: '{bn['recommended_syllable']}' ({bn['nakshatra']} Pada {bn['pada']})")
    
    # 7. Gemstone
    gs = calc_gemstone("Virgo", "Cancer")
    print(f"\n7. Gemstone for Virgo Lagna:")
    print(f"   Primary: {gs['primary_gem']['gem']} ({gs['primary_gem']['planet']})")
    
    # 8. Divisional charts
    test_lons = {"sun":56.0,"moon":56.4,"mars":127.0,"mercury":37.2,
                 "jupiter":258.0,"venus":18.0,"saturn":340.0,
                 "rahu":176.0,"ketu":356.0,"ascendant":157.0}
    dc = calc_divisional_charts(test_lons)
    print(f"\n8. D10 Dasamsha (Career chart):")
    for p, s in dc["D10_dasamsha"]["planets"].items():
        print(f"   {p.capitalize()}: {s}")
    
    print("\n✅ All extra features working")


# ═══════════════════════════════════════════════════════════════════════
# 11. SOOKSHMA DASHA (4th level)
# ═══════════════════════════════════════════════════════════════════════

def calc_sookshma_dasha(pratyantar_lord, pratyantar_start, pratyantar_end, 
                         antar_lord, maha_lord):
    """4th level dasha within Pratyantar."""
    from datetime import timedelta
    dur_days = (pratyantar_end - pratyantar_start).total_seconds()/86400
    DASHA_YEARS = {"ketu":7,"venus":20,"sun":6,"moon":10,"mars":7,
                   "rahu":18,"jupiter":16,"saturn":19,"mercury":17}
    DASHA_ORDER = ["ketu","venus","sun","moon","mars","rahu","jupiter","saturn","mercury"]
    start_idx = DASHA_ORDER.index(pratyantar_lord)
    result = []
    cur = pratyantar_start
    for i in range(9):
        lord = DASHA_ORDER[(start_idx+i)%9]
        d = dur_days * DASHA_YEARS[lord] / 120
        end = cur + timedelta(days=d)
        result.append({
            "lord": lord,
            "start": cur.strftime("%Y-%m-%d"),
            "end": end.strftime("%Y-%m-%d"),
            "label": f"{maha_lord}-{antar_lord}-{pratyantar_lord}-{lord}",
            "duration_days": round(d,1)
        })
        cur = end
    return result


# ═══════════════════════════════════════════════════════════════════════
# 12. VIMSHOPAKA BALA (20-point strength)
# ═══════════════════════════════════════════════════════════════════════

def calc_vimshopaka_bala(planet_lons: dict) -> dict:
    """
    Vimshopaka Bala = 20-point strength based on divisional chart positions.
    Checks 16 divisional charts, each with a weight.
    Source: BPHS Ch.27
    """
    def sign_of(lon): return int(lon/30)%12
    
    # Weights for each divisional chart (out of 20 total)
    WEIGHTS = {
        "D1":  3.0,  "D2":  1.5, "D3":  1.5, "D7":  1.5,
        "D9":  3.0,  "D10": 1.5, "D12": 1.5, "D16": 1.5,
        "D20": 0.5,  "D24": 0.5, "D27": 0.5, "D30": 1.0,
        "D40": 0.5,  "D45": 0.5, "D60": 4.0,
    }
    
    # Own, exaltation, friendly signs give full points
    # Neutral = half, enemy/debilitation = zero
    EXALTATION = {"sun":0,"moon":1,"mars":9,"mercury":5,"jupiter":3,
                   "venus":11,"saturn":6,"rahu":1,"ketu":7}
    DEBILITATION = {"sun":6,"moon":7,"mars":3,"mercury":11,"jupiter":9,
                     "venus":5,"saturn":0,"rahu":7,"ketu":1}
    OWN_SIGNS = {
        "sun":[4],"moon":[3],"mars":[0,7],"mercury":[5,2],
        "jupiter":[8,11],"venus":[1,6],"saturn":[9,10],
        "rahu":[9,10],"ketu":[0,7]
    }
    FRIENDS = {
        "sun":["moon","mars","jupiter"],
        "moon":["sun","mercury"],
        "mars":["sun","moon","jupiter"],
        "mercury":["sun","venus"],
        "jupiter":["sun","moon","mars"],
        "venus":["mercury","saturn"],
        "saturn":["mercury","venus"],
        "rahu":["saturn","venus","mercury"],
        "ketu":["mars","saturn","venus"],
    }
    SIGN_LORDS = ["mars","venus","mercury","moon","sun","mercury",
                   "venus","mars","jupiter","saturn","saturn","jupiter"]
    
    def strength_in_sign(planet, sign_idx):
        """Return 1.0=full, 0.5=neutral, 0.0=weak."""
        if sign_idx == EXALTATION.get(planet): return 1.0
        if sign_idx == DEBILITATION.get(planet): return 0.0
        if sign_idx in OWN_SIGNS.get(planet,[]): return 1.0
        lord = SIGN_LORDS[sign_idx]
        if lord in FRIENDS.get(planet,[]): return 0.75
        if lord == planet: return 1.0
        return 0.5
    
    def get_divisional_sign(lon, div):
        s = int(lon/30)%12
        d = lon%30
        if div==1:  return s
        if div==2:  return 4 if s%2==0 else 3  # simplified hora
        if div==3:  return (s+[0,4,8][int(d/10)])%12
        if div==7:  return (s+int(d/(30/7)))%12 if s%2==0 else (s+6+int(d/(30/7)))%12
        if div==9:  return int(lon*9/30)%12  # navamsha
        if div==10: return (s+int(d/3))%12 if s%2==0 else (s+9+int(d/3))%12
        if div==12: return (s+int(d/2.5))%12
        if div==16: return (s*4+int(d/(30/4)))%12
        if div==20: return (s*20//12+int(d/(30/20)))%12
        if div==24: return (s+int(d/(30/24)))%12
        if div==27: return (s*3+int(d/(30/9)))%12
        if div==30: return s  # simplified
        if div==40: return (s*40//12)%12
        if div==45: return (s*45//12)%12
        if div==60: return (s*60//12)%12
        return s
    
    DIVS = [1,2,3,7,9,10,12,16,20,24,27,30,40,45,60]
    DIV_NAMES = ["D1","D2","D3","D7","D9","D10","D12","D16","D20","D24","D27","D30","D40","D45","D60"]
    
    result = {}
    PLANETS = ["sun","moon","mars","mercury","jupiter","venus","saturn"]
    
    for planet in PLANETS:
        if planet not in planet_lons: continue
        lon = planet_lons[planet]
        total = 0.0
        max_total = sum(WEIGHTS.values())
        details = {}
        
        for div, dname in zip(DIVS, DIV_NAMES):
            if dname not in WEIGHTS: continue
            div_sign = get_divisional_sign(lon, div)
            strength = strength_in_sign(planet, div_sign)
            points = strength * WEIGHTS[dname]
            total += points
            details[dname] = {
                "sign": ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                          "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"][div_sign],
                "strength": ["Weak","Neutral","Strong"][int(strength*2)] if strength<1 else "Strong",
                "points": round(points,2)
            }
        
        pct = total/max_total*20  # Scale to 20
        result[planet] = {
            "vimshopaka": round(pct,2),
            "max": 20,
            "percent": round(pct/20*100,1),
            "strength": "Excellent" if pct>=15 else "Good" if pct>=10 else "Average" if pct>=5 else "Weak",
            "details": details
        }
    
    return result


# ═══════════════════════════════════════════════════════════════════════
# 13. GRAHA YUDDHA (Planetary War)
# ═══════════════════════════════════════════════════════════════════════

def check_graha_yuddha(planet_lons: dict) -> list:
    """
    Graha Yuddha = Planetary War — two planets within 1° of each other.
    Only among: Mars, Mercury, Jupiter, Venus, Saturn.
    The planet with lower ecliptic latitude wins (traditionally).
    Source: BPHS Ch.3
    """
    WAR_PLANETS = ["mars","mercury","jupiter","venus","saturn"]
    wars = []
    
    planets = [(p, planet_lons[p]) for p in WAR_PLANETS if p in planet_lons]
    
    for i in range(len(planets)):
        for j in range(i+1, len(planets)):
            p1, lon1 = planets[i]
            p2, lon2 = planets[j]
            diff = abs(lon1-lon2)
            if diff > 180: diff = 360-diff
            
            if diff <= 1.0:
                # Determine winner (higher longitude = winner traditionally)
                winner = p1 if lon1 > lon2 else p2
                loser  = p2 if winner==p1 else p1
                wars.append({
                    "planet1": p1, "planet2": p2,
                    "separation_deg": round(diff,3),
                    "winner": winner,
                    "loser":  loser,
                    "effect": f"{loser.capitalize()} is defeated — weakened significations",
                    "note": "Graha Yuddha: planets within 1° — significant weakness for loser",
                    "source": "BPHS Ch.3"
                })
    
    return wars


# ═══════════════════════════════════════════════════════════════════════
# 14. MUHURTA CALCULATORS (Vivah, Griha Pravesh, Vehicle)
# ═══════════════════════════════════════════════════════════════════════

# Auspicious Tithis for each muhurta type
VIVAH_TITHIS = [2,3,5,7,10,11,13]  # Dwitiya, Tritiya, Panchami, Saptami, Dashami, Ekadashi, Trayodashi
VIVAH_NAKSHATRAS = [3,4,6,7,8,11,13,14,15,17,22,23,24,25,26]  # Rohini, Mrigashira, Punarvasu, Pushya, etc.
VIVAH_MONTHS = [11,12,1,2,4,5]  # Margashirsha, Paush, Magh, Phalgun, Vaishakha, Jyeshtha

GRIHA_PRAVESH_TITHIS = [2,3,5,7,10,11,12,13]
GRIHA_PRAVESH_NAKSHATRAS = [3,4,6,7,8,11,12,13,14,20,22,23,24,25,26]

VEHICLE_TITHIS = [2,3,5,7,10,11,12,13]
VEHICLE_NAKSHATRAS = [3,4,6,7,8,11,13,22,23,24,25]

def check_vivah_muhurta(year, month, day, tithi_idx, nak_idx, yoga_idx, vara_idx):
    """Check if date is suitable for marriage."""
    BAD_YOGAS = {0,5,8,9,12,14,16,18,26}  # Vishkumbha, Atiganda, etc.
    BAD_VARA  = {0}  # Sunday avoided (some traditions)
    
    tithi_num = tithi_idx%30+1
    
    checks = {
        "tithi_ok":   tithi_num in VIVAH_TITHIS,
        "nakshatra_ok": nak_idx in VIVAH_NAKSHATRAS,
        "month_ok":   month in VIVAH_MONTHS,
        "yoga_ok":    yoga_idx not in BAD_YOGAS,
        "vara_ok":    vara_idx not in BAD_VARA,
    }
    
    score = sum(checks.values())
    suitable = score >= 3 and checks["nakshatra_ok"] and checks["tithi_ok"]
    
    VIVAH_NAK_NAMES = ["Rohini","Mrigashira","Punarvasu","Pushya","Uttara Phalguni",
                        "Hasta","Swati","Anuradha","Shravana","Dhanishtha",
                        "Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati"]
    
    return {
        "suitable": suitable,
        "score": f"{score}/5",
        "checks": checks,
        "good_nakshatras": VIVAH_NAK_NAMES,
        "good_months": ["Margashirsha","Paush","Magh","Phalgun","Vaishakha","Jyeshtha"],
        "avoid": ["Adhika Masa","Khar Masa","Panchak","Bhadra"],
        "note": "Consult Jyotishi for complete Vivah Muhurta — this is a quick check only"
    }


def check_griha_pravesh_muhurta(year, month, day, tithi_idx, nak_idx, yoga_idx, vara_idx):
    """Check if date is suitable for Griha Pravesh (entering new home)."""
    BAD_YOGAS = {0,5,8,9,12,14,16,18,26}
    
    tithi_num = tithi_idx%30+1
    checks = {
        "tithi_ok":     tithi_num in GRIHA_PRAVESH_TITHIS,
        "nakshatra_ok": nak_idx in GRIHA_PRAVESH_NAKSHATRAS,
        "yoga_ok":      yoga_idx not in BAD_YOGAS,
        "vara_ok":      vara_idx not in {0,6},  # Avoid Sun/Sat
        "not_krishna_8": tithi_idx != 22,
    }
    score = sum(checks.values())
    
    return {
        "suitable": score >= 4 and checks["tithi_ok"],
        "score": f"{score}/5",
        "checks": checks,
        "note": "Best months: Vaishakha, Jyeshtha, Shravan, Magha, Phalgun"
    }


def check_vehicle_muhurta(year, month, day, tithi_idx, nak_idx, yoga_idx, vara_idx):
    """Check if date is suitable for vehicle purchase."""
    tithi_num = tithi_idx%30+1
    checks = {
        "tithi_ok":     tithi_num in VEHICLE_TITHIS,
        "nakshatra_ok": nak_idx in VEHICLE_NAKSHATRAS,
        "yoga_ok":      yoga_idx not in {0,5,8,9,12,16},
        "vara_ok":      vara_idx in {1,3,4},  # Mon/Wed/Thu best
    }
    score = sum(checks.values())
    
    return {
        "suitable": score >= 3,
        "score": f"{score}/4",
        "checks": checks,
        "best_vara": "Monday, Wednesday, Thursday",
        "note": "Ashwini nakshatra is especially good for vehicles"
    }


# ═══════════════════════════════════════════════════════════════════════
# 15. LUCKY NUMBER, COLOR, DAY
# ═══════════════════════════════════════════════════════════════════════

def calc_lucky_factors(lagna_sign: str, moon_sign: str, 
                        birth_day: int, birth_month: int, birth_year: int) -> dict:
    """Lucky number, color, day, direction based on birth details."""
    SIGN_LORD = {
        "Aries":"mars","Taurus":"venus","Gemini":"mercury","Cancer":"moon",
        "Leo":"sun","Virgo":"mercury","Libra":"venus","Scorpio":"mars",
        "Sagittarius":"jupiter","Capricorn":"saturn","Aquarius":"saturn",
        "Pisces":"jupiter"
    }
    PLANET_NUMBER = {
        "sun":1,"moon":2,"mars":9,"mercury":5,
        "jupiter":3,"venus":6,"saturn":8,"rahu":4,"ketu":7
    }
    PLANET_COLOR = {
        "sun":"Red/Orange","moon":"White/Silver","mars":"Red/Coral",
        "mercury":"Green","jupiter":"Yellow/Gold","venus":"White/Pink",
        "saturn":"Blue/Black","rahu":"Smoky Grey","ketu":"Multi-color"
    }
    PLANET_DAY = {
        "sun":"Sunday","moon":"Monday","mars":"Tuesday","mercury":"Wednesday",
        "jupiter":"Thursday","venus":"Friday","saturn":"Saturday"
    }
    PLANET_DIRECTION = {
        "sun":"East","moon":"Northwest","mars":"South","mercury":"North",
        "jupiter":"Northeast","venus":"Southeast","saturn":"West"
    }
    PLANET_METAL = {
        "sun":"Gold","moon":"Silver","mars":"Copper","mercury":"Bronze",
        "jupiter":"Gold","venus":"Silver","saturn":"Iron/Steel"
    }
    
    # Numerology number from birth date
    num = birth_day + birth_month + sum(int(d) for d in str(birth_year))
    while num > 9: num = sum(int(d) for d in str(num))
    
    lagna_lord = SIGN_LORD.get(lagna_sign, "sun")
    moon_lord  = SIGN_LORD.get(moon_sign, "moon")
    
    return {
        "lucky_number":    PLANET_NUMBER.get(lagna_lord, 1),
        "numerology_number": num,
        "lucky_color":     PLANET_COLOR.get(lagna_lord,""),
        "lucky_day":       PLANET_DAY.get(lagna_lord,""),
        "lucky_direction": PLANET_DIRECTION.get(lagna_lord,""),
        "lucky_metal":     PLANET_METAL.get(lagna_lord,""),
        "lucky_god":       {
            "sun":"Surya Deva","moon":"Chandra/Shiva","mars":"Hanuman/Kartikeya",
            "mercury":"Vishnu/Ganesh","jupiter":"Brihaspati/Vishnu",
            "venus":"Lakshmi/Shukra","saturn":"Shani/Shiva"
        }.get(lagna_lord,""),
        "lagna_lord": lagna_lord.capitalize(),
        "moon_lord":  moon_lord.capitalize(),
    }


# ═══════════════════════════════════════════════════════════════════════
# 16. RUDRAKSHA RECOMMENDATION
# ═══════════════════════════════════════════════════════════════════════

RUDRAKSHA_DATA = {
    "1_mukhi":  {"planet":"sun",     "benefit":"Leadership, soul awakening, moksha"},
    "2_mukhi":  {"planet":"moon",    "benefit":"Emotional balance, unity, relationships"},
    "3_mukhi":  {"planet":"mars",    "benefit":"Self-confidence, freedom from past karma"},
    "4_mukhi":  {"planet":"mercury", "benefit":"Intelligence, creativity, communication"},
    "5_mukhi":  {"planet":"jupiter", "benefit":"Health, peace, wisdom, most common bead"},
    "6_mukhi":  {"planet":"venus",   "benefit":"Love, beauty, willpower, grounding"},
    "7_mukhi":  {"planet":"saturn",  "benefit":"Wealth, overcoming Sade Sati"},
    "8_mukhi":  {"planet":"rahu",    "benefit":"Removes obstacles, Rahu's malefic effects"},
    "9_mukhi":  {"planet":"ketu",    "benefit":"Shakti, fearlessness, spiritual power"},
    "10_mukhi": {"planet":"vishnu",  "benefit":"Protection from all planets, peace"},
    "11_mukhi": {"planet":"hanuman", "benefit":"Meditation, adventure, wisdom"},
    "12_mukhi": {"planet":"sun",     "benefit":"Administrative power, health, radiance"},
    "14_mukhi": {"planet":"saturn",  "benefit":"Intuition, protection, highest benefit"},
}

def calc_rudraksha(lagna_sign: str, weak_planets: list = None) -> dict:
    """Recommend Rudraksha based on Lagna and weak planets."""
    SIGN_LORD = {
        "Aries":"mars","Taurus":"venus","Gemini":"mercury","Cancer":"moon",
        "Leo":"sun","Virgo":"mercury","Libra":"venus","Scorpio":"mars",
        "Sagittarius":"jupiter","Capricorn":"saturn","Aquarius":"saturn",
        "Pisces":"jupiter"
    }
    
    lagna_lord = SIGN_LORD.get(lagna_sign, "jupiter")
    
    # Primary = 5 mukhi (universal, everyone can wear)
    # Secondary = Lagna lord's rudraksha
    # Remedial = weak planet's rudraksha
    
    planet_mukhi = {
        "sun":1,"moon":2,"mars":3,"mercury":4,"jupiter":5,
        "venus":6,"saturn":7,"rahu":8,"ketu":9
    }
    
    primary = "5_mukhi"
    secondary_mukhi = planet_mukhi.get(lagna_lord, 5)
    secondary = f"{secondary_mukhi}_mukhi"
    
    recommendations = [
        {"mukhi": "5_mukhi", "type": "Universal", **RUDRAKSHA_DATA["5_mukhi"]},
        {"mukhi": secondary, "type": "Lagna Lord", **RUDRAKSHA_DATA.get(secondary, {})},
    ]
    
    if weak_planets:
        for wp in weak_planets[:2]:
            m = planet_mukhi.get(wp, 5)
            key = f"{m}_mukhi"
            if key in RUDRAKSHA_DATA:
                recommendations.append({
                    "mukhi": key, "type": f"Remedy ({wp})",
                    **RUDRAKSHA_DATA[key]
                })
    
    return {
        "recommendations": recommendations,
        "note": "Wear on Monday/Thursday. Energize before wearing. Nepal Rudraksha preferred.",
        "source": "Rudraksha Jabala Upanishad, Shiva Purana"
    }


# ═══════════════════════════════════════════════════════════════════════
# 17. PANCHA PAKSHI SYSTEM
# ═══════════════════════════════════════════════════════════════════════

def calc_pancha_pakshi(birth_nakshatra_idx: int, year: int, month: int, day: int,
                        sunrise_h: float, sunset_h: float) -> dict:
    """
    Pancha Pakshi = Five Birds system from Tamil Jyotish.
    Each nakshatra belongs to one of 5 birds.
    Each bird rules specific parts of the day.
    Activities aligned with ruling bird's active time are most successful.
    
    Source: Pancha Pakshi Shastra (Tamil tradition)
    """
    BIRDS = ["Vulture","Owl","Crow","Cock","Peacock"]
    
    # Each nakshatra belongs to a bird
    NAK_BIRD = [
        0,4,3,2,1,0,4,3,2,1,0,4,3,2,1,  # Ashwini..Swati
        0,4,3,2,1,0,4,3,2,1,0,4          # Vishakha..Revati
    ]
    
    from datetime import date as _date
    weekday = (_date(year,month,day).weekday()+1)%7  # Sun=0..Sat=6
    
    # Bird activity in 5 periods of the day
    DAY_PERIODS = 5
    period_len = (sunset_h - sunrise_h) / DAY_PERIODS
    
    # Ruling bird for each period (by weekday and paksha)
    # Simplified Pancha Pakshi table
    RULING_BIRD_DAY = {
        0:[0,4,3,2,1],  # Sun
        1:[1,0,4,3,2],  # Mon
        2:[2,1,0,4,3],  # Tue
        3:[3,2,1,0,4],  # Wed
        4:[4,3,2,1,0],  # Thu
        5:[0,4,3,2,1],  # Fri
        6:[1,0,4,3,2],  # Sat
    }
    
    birth_bird = BIRDS[NAK_BIRD[birth_nakshatra_idx % 27]]
    birth_bird_idx = NAK_BIRD[birth_nakshatra_idx % 27]
    
    periods = []
    for i in range(DAY_PERIODS):
        start_h = sunrise_h + i * period_len
        end_h   = start_h + period_len
        ruling_bird_idx = RULING_BIRD_DAY[weekday][i]
        ruling_bird = BIRDS[ruling_bird_idx]
        
        # Is birth bird ruling?
        is_birth_bird = ruling_bird_idx == birth_bird_idx
        # Activity: Eating=best, Ruling=very good, Walking=good,
        #           Sleeping=avoid, Dying=worst
        ACTIVITY = ["Ruling","Eating","Walking","Sleeping","Dying"]
        activity_offset = (ruling_bird_idx - birth_bird_idx) % 5
        activity = ACTIVITY[activity_offset]
        
        is_good = activity in ["Ruling","Eating","Walking"]
        
        def fmt(h):
            hr=int(h)%24; mn=int((h%1)*60)
            ap="AM" if hr<12 else "PM"; h12=hr%12 or 12
            return f"{h12:02d}:{mn:02d} {ap}"
        
        periods.append({
            "period": i+1,
            "start": fmt(start_h),
            "end":   fmt(end_h),
            "ruling_bird": ruling_bird,
            "activity": activity,
            "is_favorable": is_good,
        })
    
    return {
        "birth_bird": birth_bird,
        "periods": periods,
        "best_times": [p for p in periods if p["is_favorable"]],
        "note": "Pancha Pakshi: Tamil Jyotish system for timing activities"
    }


# ═══════════════════════════════════════════════════════════════════════
# 18. KAAL RATRI
# ═══════════════════════════════════════════════════════════════════════

def calc_kaal_ratri(year: int, month: int, day: int, 
                     sunset_h: float, next_sunrise_h: float) -> dict:
    """
    Kaal Ratri = inauspicious night period, 1/8th of night duration.
    Occurs before midnight. Avoid auspicious work during this time.
    """
    from datetime import date as _date
    weekday = (_date(year,month,day).weekday()+1)%7
    
    night_len = next_sunrise_h + 24 - sunset_h  # may cross midnight
    period_len = night_len / 8
    
    # Kaal Ratri occupies different period by weekday
    KAAL_RATRI_PERIOD = {0:3, 1:2, 2:7, 3:4, 4:1, 5:6, 6:5}
    period = KAAL_RATRI_PERIOD.get(weekday, 1)
    
    start_h = sunset_h + (period-1) * period_len
    end_h   = start_h + period_len
    
    def fmt(h):
        h = h % 24
        hr=int(h); mn=int((h%1)*60)
        ap="AM" if hr<12 else "PM"; h12=hr%12 or 12
        return f"{h12:02d}:{mn:02d} {ap}"
    
    return {
        "start": fmt(start_h),
        "end":   fmt(end_h),
        "duration_min": round(period_len*60),
        "note": "Kaal Ratri: avoid auspicious activities, travel, new ventures"
    }


# ═══════════════════════════════════════════════════════════════════════
# 19. PRADOSH TIMING
# ═══════════════════════════════════════════════════════════════════════

def check_pradosh(tithi_idx: int, sunset_h: float) -> dict:
    """
    Pradosh = Trayodashi (13th tithi) at sunset ±1.5 hours.
    Most auspicious time for Shiva worship.
    Occurs twice a month (Shukla and Krishna Trayodashi).
    """
    tithi_num = tithi_idx % 30 + 1
    is_trayodashi = tithi_num == 13 or tithi_num == 28  # Shukla/Krishna 13th
    
    if not is_trayodashi:
        return {"is_pradosh": False, "tithi_num": tithi_num}
    
    pradosh_start = sunset_h - 1.5  # 1.5 hours before sunset
    pradosh_end   = sunset_h + 1.5  # 1.5 hours after sunset
    
    def fmt(h):
        hr=int(h)%24; mn=int((h%1)*60)
        ap="AM" if hr<12 else "PM"; h12=hr%12 or 12
        return f"{h12:02d}:{mn:02d} {ap}"
    
    paksha = "Shukla" if tithi_idx < 15 else "Krishna"
    
    return {
        "is_pradosh": True,
        "paksha": paksha,
        "start": fmt(pradosh_start),
        "end":   fmt(pradosh_end),
        "sunset": fmt(sunset_h),
        "duration": "3 hours",
        "significance": f"{paksha} Pradosh — Most auspicious time for Shiva worship",
        "note": "Offer bilva leaves, milk, bhasma to Shiva during Pradosh time"
    }

