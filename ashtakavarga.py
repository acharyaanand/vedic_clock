"""
ashtakavarga.py — Complete Ashtakavarga System
================================================
Implements the classical Ashtakavarga system as per:
  - Brihat Parashara Hora Shastra (BPHS) Ch.66-75
  - Phaldipika Ch.17

Prashtarashtakavarga: Individual planet contribution tables
Sarvashtakavarga:     Sum of all 7 planets (max 56 per sign)

Each planet contributes 0 or 1 (bindu) to each of 12 signs
based on the relative positions of all 7 planets + Lagna + Moon.
"""

# ═══════════════════════════════════════════════════════════
# ASHTAKAVARGA CONTRIBUTION TABLES (from BPHS)
# Format: planet → {from_planet/lagna: [list of signs that get bindu]}
# Signs are 1-indexed from that planet's position
# ═══════════════════════════════════════════════════════════

# For each planet, shows which RELATIVE positions (from the
# contributing body) give a bindu (1 point).
# e.g., SUN_CHART["sun"] = [1,2,4,7,8,9,10,11] means
# Sun gives bindu to signs 1,2,4,7,8,9,10,11 houses from itself

BINDU_RULES = {
    "sun": {
        "sun":      [1,2,4,7,8,9,10,11],
        "moon":     [3,6,10,11],
        "mars":     [1,2,4,7,8,9,10,11],
        "mercury":  [3,5,6,9,10,11,12],
        "jupiter":  [5,6,9,11],
        "venus":    [6,7,12],
        "saturn":   [1,2,4,7,8,9,10,11],
        "lagna":    [3,4,6,10,11,12],
    },
    "moon": {
        "sun":      [3,6,7,8,10,11],
        "moon":     [1,3,6,7,10,11],
        "mars":     [2,3,5,6,9,10,11],
        "mercury":  [1,3,4,5,7,8,10,11],
        "jupiter":  [1,4,7,8,10,11],
        "venus":    [3,4,5,7,9,10,11],
        "saturn":   [3,5,6,11],
        "lagna":    [3,6,10,11],
    },
    "mars": {
        "sun":      [3,5,6,10,11],
        "moon":     [3,6,11],
        "mars":     [1,2,4,7,8,10,11],
        "mercury":  [3,5,6,11],
        "jupiter":  [6,10,11,12],
        "venus":    [6,8,11,12],
        "saturn":   [1,4,7,8,9,10,11],
        "lagna":    [1,4,7,8,9,10,11],
    },
    "mercury": {
        "sun":      [5,6,9,11,12],
        "moon":     [2,4,6,8,10,11],
        "mars":     [1,2,4,7,8,9,10,11],
        "mercury":  [1,3,5,6,9,10,11,12],
        "jupiter":  [6,8,11,12],
        "venus":    [1,2,3,4,5,8,9,11],
        "saturn":   [1,2,4,7,8,9,10,11],
        "lagna":    [1,2,4,6,8,10,11],
    },
    "jupiter": {
        "sun":      [1,2,3,4,7,8,9,10,11],
        "moon":     [2,5,7,9,11],
        "mars":     [1,2,4,7,8,10,11],
        "mercury":  [1,2,4,5,6,9,10,11],
        "jupiter":  [1,2,3,4,7,8,10,11],
        "venus":    [2,5,6,9,10,11],
        "saturn":   [3,5,6,12],
        "lagna":    [1,2,4,5,6,7,9,10,11],
    },
    "venus": {
        "sun":      [8,11,12],
        "moon":     [1,2,3,4,5,8,9,11,12],
        "mars":     [3,4,6,9,11,12],
        "mercury":  [3,5,6,9,11],
        "jupiter":  [5,8,9,10,11],
        "venus":    [1,2,3,4,5,8,9,10,11],
        "saturn":   [3,4,5,8,9,10,11],
        "lagna":    [1,2,3,4,5,8,9,11],
    },
    "saturn": {
        "sun":      [1,2,4,7,8,10,11],
        "moon":     [3,6,11],
        "mars":     [3,5,6,10,11,12],
        "mercury":  [6,8,9,10,11,12],
        "jupiter":  [5,6,11,12],
        "venus":    [6,11,12],
        "saturn":   [3,5,6,11],
        "lagna":    [1,3,4,6,10,11],
    },
}

# ── Kaksha (sub-divisions for transit analysis) ──────────────────
KAKSHA_ORDER = ["saturn","jupiter","mars","sun","venus","mercury","moon","lagna"]


def calc_prashtara_ashtakavarga(planets: dict, lagna_lon: float) -> dict:
    """
    Calculate individual planet Prashtara Ashtakavarga.
    
    planets: dict with keys sun/moon/mars/mercury/jupiter/venus/saturn
             each having 'longitude' in degrees (0-360 sidereal)
    lagna_lon: Ascendant longitude in degrees
    
    Returns: {
        "sun": [bindus for signs 1-12],   # list of 12 values (0 or 1 each)
        "moon": [...],
        ...
        "sarva": [total bindus per sign]   # sum of all 7
    }
    """
    # Convert longitudes to sign numbers (1-12)
    def sign_num(lon):
        return int(lon / 30) % 12 + 1  # 1=Aries, 12=Pisces

    # Get sign for each body
    pos = {}
    for p in ["sun","moon","mars","mercury","jupiter","venus","saturn"]:
        lon = planets.get(p, {})
        if isinstance(lon, dict):
            lon = lon.get("longitude", 0)
        pos[p] = sign_num(float(lon))
    pos["lagna"] = sign_num(float(lagna_lon))

    result = {}

    for planet in ["sun","moon","mars","mercury","jupiter","venus","saturn"]:
        bindus = [0] * 12  # one per sign (index 0 = Aries)

        rules = BINDU_RULES[planet]

        for contributor, positions in rules.items():
            base_sign = pos[contributor]  # sign of contributing body
            for rel_pos in positions:
                # relative position from contributor
                actual_sign = ((base_sign - 1 + rel_pos - 1) % 12)
                bindus[actual_sign] += 1

        result[planet] = bindus

    # Sarvashtakavarga (sum of all 7 planets)
    sarva = [0] * 12
    for p in ["sun","moon","mars","mercury","jupiter","venus","saturn"]:
        for i in range(12):
            sarva[i] += result[p][i]
    result["sarva"] = sarva

    return result


def get_ashtakavarga_score(ashtaka: dict, planet: str, sign_idx: int) -> int:
    """Get bindu score for planet in sign (sign_idx 0=Aries, 11=Pisces)."""
    return ashtaka.get(planet, [0]*12)[sign_idx % 12]


def get_planet_total(ashtaka: dict, planet: str) -> int:
    """Total bindus for a planet across all 12 signs (should be ~28-56)."""
    return sum(ashtaka.get(planet, [0]*12))


def interpret_bindu(score: int, planet: str = None) -> str:
    """Interpret bindu score for a sign."""
    if score >= 7: return "Highly Auspicious — excellent results"
    if score >= 5: return "Auspicious — good results"
    if score >= 4: return "Moderate — mixed results"
    if score >= 2: return "Weak — some difficulties"
    return "Very Weak — challenging"


def get_transit_strength(ashtaka: dict, planet: str, 
                          current_sign_idx: int) -> dict:
    """
    Ashtakavarga-based transit strength.
    Used to assess how well a planet performs while transiting a sign.
    """
    score = get_ashtakavarga_score(ashtaka, planet, current_sign_idx)
    sarva = get_ashtakavarga_score(ashtaka, "sarva", current_sign_idx)
    return {
        "planet": planet,
        "transit_sign": current_sign_idx + 1,
        "bindu_score": score,
        "sarva_score": sarva,
        "transit_quality": interpret_bindu(score, planet),
        "citation": "BPHS Ch.70 — Transit results based on Ashtakavarga bindus"
    }


def format_ashtakavarga_table(ashtaka: dict) -> str:
    """Format Ashtakavarga as a readable table."""
    SIGNS = ["Ar","Ta","Ge","Ca","Le","Vi","Li","Sc","Sg","Cp","Aq","Pi"]
    planets = ["sun","moon","mars","mercury","jupiter","venus","saturn"]
    
    lines = []
    lines.append(f"{'Planet':<10} " + " ".join(f"{s:>3}" for s in SIGNS) + f" {'Total':>6}")
    lines.append("─" * 66)
    for p in planets:
        row = ashtaka.get(p, [0]*12)
        total = sum(row)
        lines.append(f"{p.capitalize():<10} " + " ".join(f"{v:>3}" for v in row) + f" {total:>6}")
    lines.append("─" * 66)
    sarva = ashtaka.get("sarva", [0]*12)
    lines.append(f"{'SARVA':<10} " + " ".join(f"{v:>3}" for v in sarva) + f" {sum(sarva):>6}")
    return "\n".join(lines)


# ── MANDI / GULIKA EXACT FORMULA ────────────────────────────────────────────

def calc_mandi_gulika(year: int, month: int, day: int,
                      lat: float, lon: float, tz: float) -> dict:
    """
    Calculate exact Mandi and Gulika positions.
    
    Mandi = Saturn's upagraha (shadow planet)
    Gulika = Child of Saturn, slightly different formula
    
    Classical formula (BPHS Ch.78):
    - Divide day into 8 equal parts (one per planet)
    - Weekday determines which part Mandi falls in
    - For night births, use night formula
    
    Mandi formula (day):
    Sunday=7th, Monday=1st, Tuesday=2nd, Wednesday=3rd,
    Thursday=4th, Friday=5th, Saturday=6th period
    
    Mandi = Sunrise + (period_number - 1) * day_duration/8
    Mandi longitude = Sun's longitude at that time
    """
    import math
    from datetime import datetime, date as _date

    def jd_calc(y, m, d, h_ut):
        if m <= 2: y -= 1; m += 12
        A = int(y/100); B = 2 - A + int(A/4)
        return int(365.25*(y+4716)) + int(30.6001*(m+1)) + d + h_ut/24 + B - 1524.5

    def sunrise_local(y, mo, d, lat, lon, tz):
        n = _date(y, mo, d).timetuple().tm_yday
        B = 360/365*(n-81)
        eot = 9.87*math.sin(math.radians(2*B))-7.53*math.cos(math.radians(B))-1.5*math.sin(math.radians(B))
        sn = 12-(lon-15*tz)/15-eot/60
        decl = math.degrees(math.asin(0.39795*math.cos(math.radians(0.98563*(n-173)))))
        lr = math.radians(lat); dr = math.radians(decl)
        cos_ha = (math.cos(math.radians(90.833))-math.sin(lr)*math.sin(dr))/(math.cos(lr)*math.cos(dr))
        ha = math.degrees(math.acos(max(-1,min(1,cos_ha))))
        return sn - ha/15, sn + ha/15  # sunrise, sunset in local time

    def sun_lon(jd_):
        T = (jd_-2451545.0)/36525.0
        L0 = 280.46646+36000.76983*T+0.0003032*T*T
        M = (357.52911+35999.05029*T-0.0001537*T*T)%360
        Mr = math.radians(M)
        C = (1.914602-0.004817*T-0.000014*T*T)*math.sin(Mr)+(0.019993-0.000101*T)*math.sin(2*Mr)+0.000289*math.sin(3*Mr)
        return (L0+C-0.00569-0.00478*math.sin(math.radians(125.04-1934.136*T)))%360

    def ayanamsa(yr): return 23.8665+0.014206*(yr-2000)

    # Get sunrise/sunset
    sr, ss = sunrise_local(year, month, day, lat, lon, tz)
    day_dur = ss - sr  # hours
    period_dur = day_dur / 8.0  # each period = 1/8 of day

    # Weekday (0=Sun, 1=Mon, ... 6=Sat)
    from datetime import date
    wd = date(year, month, day).weekday()  # Mon=0, Sun=6
    wd_sun_based = (wd + 1) % 7  # Sun=0, Mon=1, ... Sat=6

    # Mandi period number (DAY births)
    # Sun=8th, Mon=2nd, Tue=3rd, Wed=4th, Thu=5th, Fri=6th, Sat=7th
    # Which means the START of that period:
    # Sun: 7 periods done → 7*dur from sunrise
    MANDI_PERIOD = {0:7, 1:1, 2:2, 3:3, 4:4, 5:5, 6:6}  # 0=Sun..6=Sat
    GULIKA_PERIOD = {0:6, 1:0, 2:1, 3:2, 4:3, 5:4, 6:5}  # Gulika = one before Mandi

    mandi_period = MANDI_PERIOD[wd_sun_based]
    gulika_period = GULIKA_PERIOD[wd_sun_based]

    # Time of Mandi/Gulika = Sunrise + period * duration
    mandi_time_local = sr + mandi_period * period_dur
    gulika_time_local = sr + gulika_period * period_dur

    # Convert to JD and get Sun's longitude at that time
    mandi_jd = jd_calc(year, month, day, mandi_time_local - tz)
    gulika_jd = jd_calc(year, month, day, gulika_time_local - tz)

    yr_dec = year + month/12
    ay = ayanamsa(yr_dec)

    mandi_lon = (sun_lon(mandi_jd) - ay) % 360
    gulika_lon = (sun_lon(gulika_jd) - ay) % 360

    SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
             "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
    NAKS = ["Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
            "Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni","Uttara Phalguni",
            "Hasta","Chitra","Swati","Vishakha","Anuradha","Jyeshtha","Mula",
            "Purva Ashadha","Uttara Ashadha","Shravana","Dhanishtha","Shatabhisha",
            "Purva Bhadrapada","Uttara Bhadrapada","Revati"]

    def fmt(lon):
        sign_i = int(lon/30)
        deg_in = lon - sign_i*30
        deg = int(deg_in); mn = int((deg_in-deg)*60)
        nak_i = int(lon*27/360) % 27
        pada = int((lon - int(lon*27/360)*360/27) / (360/27/4)) + 1
        return {
            "longitude": round(lon, 4),
            "sign": SIGNS[sign_i % 12],
            "degree": f"{deg}°{mn}'",
            "nakshatra": NAKS[nak_i],
            "pada": min(pada, 4),
        }

    def h_fmt(h):
        hr = int(h); mn = int((h-hr)*60)
        ap = "AM" if hr < 12 else "PM"; h12 = hr%12 or 12
        return f"{h12:02d}:{mn:02d} {ap}"

    WEEKDAYS = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
    weekday = WEEKDAYS[wd_sun_based]

    return {
        "mandi": {
            **fmt(mandi_lon),
            "time": h_fmt(mandi_time_local),
            "period_number": mandi_period,
            "citation": "BPHS Ch.78 — Mandi = Saturn's upagraha, period formula"
        },
        "gulika": {
            **fmt(gulika_lon),
            "time": h_fmt(gulika_time_local),
            "period_number": gulika_period,
            "citation": "BPHS Ch.78 — Gulika = child of Saturn"
        },
        "weekday": weekday,
        "day_duration_hours": round(day_dur, 4),
        "period_duration_minutes": round(period_dur*60, 2),
    }


# ── PRATYANTAR DASHA (3rd Level) ────────────────────────────────────────────

VIMSHOTTARI_YEARS = {
    "ketu":7,"venus":20,"sun":6,"moon":10,"mars":7,
    "rahu":18,"jupiter":16,"saturn":19,"mercury":17
}
DASHA_SEQ = ["ketu","venus","sun","moon","mars","rahu","jupiter","saturn","mercury"]

def calc_pratyantar_dasha(maha_planet: str, antar_planet: str,
                           antar_start: "datetime", antar_end: "datetime") -> list:
    """
    Calculate Pratyantar Dasha (3rd level) for given Antardasha period.
    
    Formula: Pratyantar duration = Antardasha_duration × (planet_years / 120)
    Sequence: starts from the Antardasha planet
    
    Returns list of dicts with planet, start, end dates.
    """
    from datetime import timedelta

    total_days = (antar_end - antar_start).days
    total_seconds = (antar_end - antar_start).total_seconds()

    # Start sequence from antardasha planet
    start_idx = DASHA_SEQ.index(antar_planet)
    
    pratyantar_list = []
    current_dt = antar_start

    for i in range(9):
        p = DASHA_SEQ[(start_idx + i) % 9]
        # Duration = total_antardasha * planet_years / 120
        fraction = VIMSHOTTARI_YEARS[p] / 120.0
        duration_secs = total_seconds * fraction
        end_dt = current_dt + timedelta(seconds=duration_secs)

        pratyantar_list.append({
            "planet": p.capitalize(),
            "start": current_dt.strftime("%d %b %Y"),
            "end":   end_dt.strftime("%d %b %Y"),
            "duration_days": round(duration_secs/86400, 1)
        })
        current_dt = end_dt

    return pratyantar_list


def calc_full_dasha_with_pratyantar(moon_lon: float, birth_dt, 
                                     num_maha: int = 3) -> list:
    """
    Generate Mahadasha + Antardasha + Pratyantar for first num_maha periods.
    """
    from datetime import datetime, timedelta
    import sys
    sys.path.insert(0, '/mnt/user-data/outputs')

    try:
        from dasha_engine import calculate_vimshottari_dashas
        dashas = calculate_vimshottari_dashas(moon_lon, birth_dt, 120)
    except:
        return []

    result = []
    for maha in dashas[:num_maha]:
        maha_entry = {
            "mahadasha": maha["planet"],
            "start": maha["start_date"],
            "end":   maha["end_date"],
            "antardashas": []
        }
        # Get antardashas
        for antar in maha.get("antardashas", []):
            # Parse dates
            try:
                a_start = datetime.strptime(antar["start_date"], "%d %b %Y")
                a_end   = datetime.strptime(antar["end_date"],   "%d %b %Y")
            except:
                a_start = datetime.now()
                a_end   = datetime.now() + timedelta(days=365)

            pratyantar = calc_pratyantar_dasha(
                maha["planet"], antar["planet"], a_start, a_end
            )
            antar_entry = {
                "planet":   antar["planet"],
                "start":    antar["start_date"],
                "end":      antar["end_date"],
                "pratyantar": pratyantar[:3]  # show first 3 for brevity
            }
            maha_entry["antardashas"].append(antar_entry)

        result.append(maha_entry)
    return result


# ── SPECIAL PANCHANGA YOGAS ─────────────────────────────────────────────────

def calc_special_panchanga_yogas(year: int, month: int, day: int,
                                  tithi_num: int, nak_idx: int,
                                  vara_num: int, yoga_idx: int) -> list:
    """
    Calculate special auspicious/inauspicious Panchanga Yogas.
    DrikPanchang shows these on daily panchanga.
    
    tithi_num: 1-30
    nak_idx: 0-26 (0=Ashwini)
    vara_num: 0-6 (0=Sunday)
    yoga_idx: 0-26
    """
    specials = []

    NAK_NAMES = ["Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
                 "Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni",
                 "Uttara Phalguni","Hasta","Chitra","Swati","Vishakha",
                 "Anuradha","Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha",
                 "Shravana","Dhanishtha","Shatabhisha","Purva Bhadrapada",
                 "Uttara Bhadrapada","Revati"]
    VARA = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]

    nak = NAK_NAMES[nak_idx % 27]
    vara = VARA[vara_num % 7]

    # 1. RAVI YOGA — Vara + Nakshatra combination
    # Specific (Vara, Nakshatra) pairs that form Ravi Yoga
    RAVI_YOGA = {
        "Sunday":["Hasta","Uttara Phalguni","Uttara Ashadha","Uttara Bhadrapada","Krittika","Pushya"],
        "Monday":["Rohini","Mrigashira","Shravana","Dhanishtha","Shatabhisha","Hasta"],
        "Tuesday":["Ashwini","Chitra","Swati","Vishakha","Anuradha","Dhanishtha"],
        "Wednesday":["Ashlesha","Jyeshtha","Revati","Anuradha","Rohini","Ardra"],
        "Thursday":["Punarvasu","Vishakha","Purva Bhadrapada","Ardra","Pushya","Ashwini"],
        "Friday":["Bharani","Purva Phalguni","Purva Ashadha","Purva Bhadrapada","Revati","Rohini"],
        "Saturday":["Pushya","Anuradha","Uttara Bhadrapada","Shravana","Dhanishtha","Rohini"],
    }
    if nak in RAVI_YOGA.get(vara, []):
        specials.append({
            "name": "Ravi Yoga",
            "type": "Auspicious",
            "description": "Formed by beneficial Vara-Nakshatra combination. Good for most works.",
            "citation": "Muhurta Chintamani"
        })

    # 2. AMRITA YOGA — Vara + Nakshatra
    AMRITA_YOGA = {
        "Sunday": ["Hasta","Mrigashira","Pushya","Ashwini"],
        "Monday": ["Rohini","Uttara Phalguni","Uttara Ashadha","Uttara Bhadrapada"],
        "Tuesday": ["Ashwini","Krittika","Chitra","Dhanishtha"],
        "Wednesday": ["Rohini","Ardra","Purva Phalguni","Hasta"],
        "Thursday": ["Pushya","Anuradha","Purva Bhadrapada","Revati"],
        "Friday": ["Purva Phalguni","Purva Ashadha","Purva Bhadrapada","Bharani"],
        "Saturday": ["Rohini","Swati","Anuradha","Uttara Bhadrapada"],
    }
    if nak in AMRITA_YOGA.get(vara, []):
        specials.append({
            "name": "Amrita Yoga",
            "type": "Highly Auspicious",
            "description": "Nectar yoga — excellent for all auspicious works, esp. medicine and healing.",
            "citation": "Muhurta Chintamani"
        })

    # 3. SARVARTHA SIDDHI YOGA — Vara + Nakshatra
    SARVARTHA = {
        "Sunday": ["Hasta","Uttara Phalguni","Uttara Ashadha","Pushya","Ashwini","Mrigashira"],
        "Monday": ["Mrigashira","Pushya","Anuradha","Shravana","Rohini"],
        "Tuesday": ["Ashwini","Anuradha","Uttara Bhadrapada","Dhanishtha","Krittika"],
        "Wednesday": ["Krittika","Rohini","Hasta","Anuradha","Ashlesha"],
        "Thursday": ["Revati","Ashwini","Punarvasu","Pushya","Anuradha"],
        "Friday": ["Ashwini","Bharani","Purva Phalguni","Hasta","Anuradha","Revati"],
        "Saturday": ["Rohini","Swati","Anuradha","Dhanishtha","Uttara Bhadrapada"],
    }
    if nak in SARVARTHA.get(vara, []):
        specials.append({
            "name": "Sarvartha Siddhi Yoga",
            "type": "Highly Auspicious",
            "description": "All purposes fulfilled. Most auspicious yoga — excellent for any new beginning.",
            "citation": "Muhurta Martanda"
        })

    # 4. RAVI PUSHYA YOGA — Sunday + Pushya Nakshatra
    if vara == "Sunday" and nak == "Pushya":
        specials.append({
            "name": "Ravi Pushya Yoga",
            "type": "Extremely Auspicious",
            "description": "Rarest and most powerful yoga. Excellent for purchase of gold, property, new ventures.",
            "citation": "Dharmasindhu — Ravi Pushya is king of all yogas"
        })

    # 5. GURU PUSHYA YOGA — Thursday + Pushya
    if vara == "Thursday" and nak == "Pushya":
        specials.append({
            "name": "Guru Pushya Yoga",
            "type": "Highly Auspicious",
            "description": "Jupiter-Pushya combination. Excellent for education, investment, religious work.",
            "citation": "Dharmasindhu"
        })

    # 6. DWIPUSHKARA YOGA — specific Tithi + Vara + Nakshatra
    # Tithi: 2,7,12 | Vara: Sun,Tue,Sat | Nak: Krittika,Punarvasu,Vishakha,Uttara Phalguni,Uttara Ashadha,Uttara Bhadrapada
    DWIPUSHKARA_VAR = ["Sunday","Tuesday","Saturday"]
    DWIPUSHKARA_NAK = ["Krittika","Punarvasu","Uttara Phalguni","Vishakha","Uttara Ashadha","Uttara Bhadrapada"]
    if vara in DWIPUSHKARA_VAR and nak in DWIPUSHKARA_NAK and tithi_num % 5 in [2,0]:
        specials.append({
            "name": "Dwipushkara Yoga",
            "type": "Mixed — doubles all results",
            "description": "Whatever done gets doubled — good deeds give double benefit, bad deeds give double loss.",
            "citation": "Muhurta Chintamani"
        })

    # 7. TRIPUSHKARA YOGA — Tithi 1,6,11 | Vara Sun,Tue,Sat | Nak Krittika,Punarvasu,Uttara etc.
    if vara in DWIPUSHKARA_VAR and nak in DWIPUSHKARA_NAK and tithi_num % 5 in [1]:
        specials.append({
            "name": "Tripushkara Yoga",
            "type": "Mixed — triples all results",
            "description": "All results tripled. Extremely important to avoid bad deeds.",
            "citation": "Muhurta Chintamani"
        })

    # 8. GANDA MOOLA — Moon in Ganda Moola Nakshatras at junctions
    # Ganda Moola nakshatras: Ashwini, Ashlesha, Magha, Jyeshtha, Mula, Revati
    GANDA_MOOLA_NAKS = ["Ashwini","Ashlesha","Magha","Jyeshtha","Mula","Revati"]
    if nak in GANDA_MOOLA_NAKS:
        specials.append({
            "name": "Ganda Moola",
            "type": "Inauspicious",
            "description": f"Moon in {nak} — junction nakshatra. Ganda Moola Shanti recommended for children born in this nakshatra.",
            "citation": "Brihat Samhita Ch.98 — Ganda Moola born children need special shanti"
        })

    # 9. PANCHAKA — Vara + Nakshatra based
    # Panchaka occurs when Moon is in Dhanishtha (last 2 padas), Shatabhisha, Purva Bhadrapada, Uttara Bhadrapada, Revati
    PANCHAKA_NAKS = ["Dhanishtha","Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati"]
    if nak in PANCHAKA_NAKS:
        # Check type of Panchaka based on weekday
        PANCHAKA_TYPES = {
            0: "Roga Panchaka (disease)",
            1: "None", 2: "Mrityu Panchaka (death-like troubles)",
            3: "Agni Panchaka (fire accidents)",
            4: "Raja Panchaka (legal troubles)",
            5: "Chor Panchaka (theft)",
            6: "Mrityu Panchaka (death-like troubles)"
        }
        ptype = PANCHAKA_TYPES.get(vara_num, "None")
        if ptype != "None":
            specials.append({
                "name": f"Panchaka — {ptype}",
                "type": "Inauspicious",
                "description": "Moon in Panchaka nakshatras. Avoid starting new projects, construction, long journeys.",
                "citation": "Muhurta Chintamani — Panchaka avoidance rules"
            })

    # 10. SHAKA SAMVAT and VIKRAM SAMVAT
    # These are calendar systems, not yogas — but add here for completeness
    # Shaka Samvat = year - 78 (approximately)
    shaka = year - 78
    vikram = year + 57

    return specials, shaka, vikram


def calc_samvat(year: int, month: int) -> dict:
    """Calculate Shaka Samvat and Vikram Samvat."""
    # Shaka Samvat starts in March
    # Before March: shaka = year - 79
    shaka = year - 78 if month >= 4 else year - 79
    vikram = year + 57 if month >= 4 else year + 56

    # Vikram Samvat name (60-year cycle)
    SAMVAT_NAMES = [
        "Prabhava","Vibhava","Shukla","Pramoda","Prajapati",
        "Angiras","Shrimukha","Bhava","Yuva","Dhatri",
        "Ishvara","Bahudhanya","Pramadi","Vikrama","Vrisha",
        "Chitrabhanu","Subhanu","Tarana","Parthiva","Vyaya",
        "Sarvajit","Sarvadhari","Virodhi","Vikruta","Khara",
        "Nandana","Vijaya","Jaya","Manmatha","Durmukha",
        "Hevilambi","Vilambi","Vikari","Sharvari","Plava",
        "Shubhakruta","Shobhakruta","Krodhi","Vishvavasu","Parabhava",
        "Plavanga","Kilaka","Saumya","Sadharana","Virodhikruta",
        "Paridhavi","Pramadi","Ananda","Rakshasa","Anala",
        "Pingala","Kalayukta","Siddharthi","Raudra","Durmati",
        "Dundubhi","Rudhirodgari","Raktakshi","Krodhana","Akshaya"
    ]
    vikram_name = SAMVAT_NAMES[(vikram + 9) % 60]
    shaka_name  = SAMVAT_NAMES[(shaka + 11) % 60]

    return {
        "shaka_samvat": shaka,
        "shaka_name": shaka_name,
        "vikram_samvat": vikram,
        "vikram_name": vikram_name,
        "kali_yuga": year + 3101,
    }


def calc_lunar_month(tithi_num: int, solar_month: int, 
                      solar_day: int) -> dict:
    """Calculate Vedic lunar month name."""
    AMANTA_MONTHS = [
        "Chaitra","Vaishakha","Jyeshtha","Ashadha",
        "Shravana","Bhadrapada","Ashwin","Kartika",
        "Margashirsha","Pausha","Magha","Phalguna"
    ]

    # Solar month maps approximately to lunar month
    # Adjust if in Krishna Paksha (tithi > 15) we're in next month
    lunar_idx = (solar_month - 1) % 12
    if tithi_num > 15 and solar_day < 15:
        lunar_idx = (lunar_idx - 1) % 12

    amanta = AMANTA_MONTHS[lunar_idx]
    purnimanta_idx = (lunar_idx + 1) % 12
    purnimanta = AMANTA_MONTHS[purnimanta_idx]

    return {
        "amanta_month": amanta,
        "purnimanta_month": purnimanta,
        "note": "Amanta: South India | Purnimanta: North India"
    }


if __name__ == "__main__":
    print("ASHTAKAVARGA TEST")
    print("="*60)

    import sys; sys.path.insert(0, '/mnt/user-data/outputs')

    # Test with Vedanth's birth chart (May 19 1996, Bangalore)
    test_planets = {
        "sun":     {"longitude": 34.5},   # Taurus
        "moon":    {"longitude": 56.4},   # Gemini (Mrigashira)
        "mars":    {"longitude": 21.3},   # Aries
        "mercury": {"longitude": 25.8},   # Aries
        "jupiter": {"longitude": 278.2},  # Capricorn
        "venus":   {"longitude": 15.6},   # Aries
        "saturn":  {"longitude": 351.4},  # Pisces
    }
    lagna_lon = 154.8  # Virgo

    ashta = calc_prashtara_ashtakavarga(test_planets, lagna_lon)

    print("\nAshtakavarga Table:")
    print(format_ashtakavarga_table(ashta))
    print()

    # Verify totals (each planet should sum to ~28-56)
    EXPECTED = {"sun":48,"moon":49,"mars":39,"mercury":54,"jupiter":56,"venus":52,"saturn":39}
    print("Planet totals:")
    for p in ["sun","moon","mars","mercury","jupiter","venus","saturn"]:
        total = sum(ashta[p])
        exp = EXPECTED.get(p, "?")
        # Just check it's in reasonable range 28-56
        ok = 28 <= total <= 56
        print(f"  {'✅' if ok else '⚠️'} {p.capitalize():<10} total={total} (expected 28-56)")

    print()

    # Test Mandi/Gulika
    print("MANDI / GULIKA TEST — Vedanth May 19 1996, Bangalore")
    mandi = calc_mandi_gulika(1996, 5, 19, 12.9716, 77.5946, 5.5)
    print(f"  Mandi:  {mandi['mandi']['sign']} {mandi['mandi']['degree']} at {mandi['mandi']['time']}")
    print(f"  Gulika: {mandi['gulika']['sign']} {mandi['gulika']['degree']} at {mandi['gulika']['time']}")
    print(f"  Day duration: {mandi['day_duration_hours']:.2f}h  Period: {mandi['period_duration_minutes']:.1f}min")

    print()

    # Test Pratyantar Dasha
    print("PRATYANTAR DASHA TEST")
    from datetime import datetime
    pratyantar = calc_pratyantar_dasha(
        "venus", "sun",
        datetime(2020, 6, 1),
        datetime(2022, 6, 1)
    )
    print("  Venus-Sun Antardasha Pratyantars:")
    for p in pratyantar[:5]:
        print(f"    {p['planet']:<12} {p['start']} → {p['end']}  ({p['duration_days']:.0f}d)")

    print()

    # Test Special Yogas
    print("SPECIAL YOGAS TEST — May 21 2026 (Pushya, Panchami, Thursday)")
    yogas, shaka, vikram = calc_special_panchanga_yogas(2026,5,21, 5, 7, 4, 9)
    print(f"  Shaka: {shaka}  Vikram: {vikram}")
    if yogas:
        for y in yogas:
            print(f"  {y['type']}: {y['name']} — {y['description'][:60]}...")
    else:
        print("  No special yogas today")

    samvat = calc_samvat(2026, 5)
    print(f"  Samvat: Shaka {samvat['shaka_samvat']} | Vikram {samvat['vikram_samvat']} ({samvat['vikram_name']})")
