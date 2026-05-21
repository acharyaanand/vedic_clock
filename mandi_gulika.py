"""
mandi_gulika.py — Exact Mandi & Gulika Position Calculator
===========================================================
Mandi (also called Maandi) = upagraha of Saturn
Gulika = upagraha of Saturn (slightly different timing)

Classical source: BPHS Chapter 4, Muhurta Chintamani

Method:
  Day is divided into 8 equal parts (each = day_duration/8)
  Night is divided into 8 equal parts (each = night_duration/8)
  
  For each weekday, Mandi occupies a specific part of the day/night
  The exact longitude = start of that part + half the part duration
  converted to ecliptic longitude based on Sun's motion
  
  Mandi period order (day): Sun=1,Venus=2,Mercury=3,Moon=4,
                              Saturn=5,Jupiter=6,Mars=7,(Rahu=8=none)
  Day of week mapping to which part Saturn (Mandi's lord) rules:
  
  Weekday  Day-Mandi-Part  Night-Mandi-Part
  Sunday       8                4
  Monday       7                3  
  Tuesday      1                7
  Wednesday    6                2
  Thursday     5                1
  Friday       4                6
  Saturday     3                5
"""

import math
from datetime import datetime, timedelta

def calc_mandi_gulika(year, month, day, lat, lon, tz_offset=5.5):
    """
    Calculate exact Mandi and Gulika positions.
    
    Returns: dict with longitude, sign, nakshatra, pada, degree
    """
    from datetime import date as _date
    import math

    # ── Sunrise/Sunset calculation ────────────────────────────────────
    n = _date(year, month, day).timetuple().tm_yday
    B = 360/365 * (n - 81)
    eot = (9.87*math.sin(math.radians(2*B))
           - 7.53*math.cos(math.radians(B))
           - 1.5*math.sin(math.radians(B)))
    solar_noon = 12 - (lon - 15*tz_offset)/15 - eot/60
    decl = math.degrees(math.asin(0.39795*math.cos(math.radians(0.98563*(n-173)))))
    lr = math.radians(lat); dr = math.radians(decl)
    cos_ha = ((math.cos(math.radians(90.833)) - math.sin(lr)*math.sin(dr))
              / (math.cos(lr)*math.cos(dr)))
    ha = math.degrees(math.acos(max(-1.0, min(1.0, cos_ha))))
    sunrise = solar_noon - ha/15   # local hours
    sunset  = solar_noon + ha/15

    # Next day sunrise
    n2 = n + 1
    B2 = 360/365 * (n2 - 81)
    eot2 = (9.87*math.sin(math.radians(2*B2))
            - 7.53*math.cos(math.radians(B2))
            - 1.5*math.sin(math.radians(B2)))
    solar_noon2 = 12 - (lon - 15*tz_offset)/15 - eot2/60
    decl2 = math.degrees(math.asin(0.39795*math.cos(math.radians(0.98563*(n2-173)))))
    cos_ha2 = ((math.cos(math.radians(90.833)) - math.sin(math.radians(lat))*math.sin(math.radians(decl2)))
               / (math.cos(math.radians(lat))*math.cos(math.radians(decl2))))
    ha2 = math.degrees(math.acos(max(-1.0, min(1.0, cos_ha2))))
    next_sunrise = solar_noon2 - ha2/15

    day_duration   = sunset - sunrise         # hours
    night_duration = next_sunrise - sunset    # hours

    # ── Weekday (0=Sunday...6=Saturday) ──────────────────────────────
    from datetime import date as _d
    weekday_iso = _d(year, month, day).weekday()  # Mon=0..Sun=6
    # Convert to Sun=0..Sat=6
    weekday = (weekday_iso + 1) % 7  # Sun=0,Mon=1..Sat=6

    # ── Mandi period numbers (1-8, 8=no planet = no Mandi) ───────────
    # Which period of the day does Mandi (Saturn's upagraha) occupy?
    # BPHS: Mandi day periods by weekday (Sun=0..Sat=6)
    MANDI_DAY_PART  = {0:8, 1:7, 2:1, 3:6, 4:5, 5:4, 6:3}
    MANDI_NIGHT_PART= {0:4, 1:3, 2:7, 3:2, 4:1, 5:6, 6:5}

    # Gulika occupies the part AFTER Mandi (next part)
    # BPHS: Gulika day periods
    GULIKA_DAY_PART  = {0:7, 1:6, 2:8, 3:5, 4:4, 5:3, 6:2}
    GULIKA_NIGHT_PART= {0:3, 1:2, 2:6, 3:1, 4:8, 5:5, 6:4}

    # ── Calculate times ───────────────────────────────────────────────
    def calc_time(is_day: bool, part_num: int) -> float:
        """Returns local time (hours) of start of part_num (1-8)."""
        if part_num == 8:
            return None  # No Mandi on this day
        if is_day:
            period = day_duration / 8
            start_time = sunrise
        else:
            period = night_duration / 8
            start_time = sunset
        return start_time + (part_num - 1) * period

    # Mandi start time (beginning of its period, day)
    mandi_day_part = MANDI_DAY_PART[weekday]
    gulika_day_part = GULIKA_DAY_PART[weekday]

    mandi_start_h = calc_time(True, mandi_day_part)
    gulika_start_h = calc_time(True, gulika_day_part)

    # ── Sun longitude at given time → Mandi longitude ─────────────────
    # Mandi's longitude = Sun's ecliptic longitude at the start of its period
    # This is the traditional method from BPHS

    def jd(y, m, d, h_ut):
        if m <= 2: y -= 1; m += 12
        A = int(y/100); B_j = 2 - A + int(A/4)
        return int(365.25*(y+4716)) + int(30.6001*(m+1)) + d + h_ut/24 + B_j - 1524.5

    def sun_lon_tropical(jd_):
        T = (jd_ - 2451545.0) / 36525.0
        L0 = 280.46646 + 36000.76983*T + 0.0003032*T*T
        M = (357.52911 + 35999.05029*T - 0.0001537*T*T) % 360
        Mr = math.radians(M)
        C = ((1.914602 - 0.004817*T - 0.000014*T*T)*math.sin(Mr)
             + (0.019993 - 0.000101*T)*math.sin(2*Mr)
             + 0.000289*math.sin(3*Mr))
        omega = 125.04 - 1934.136*T
        return (L0 + C - 0.00569 - 0.00478*math.sin(math.radians(omega))) % 360

    def ayanamsa(yr):
        return 23.8665 + 0.014206*(yr - 2000)

    yr_dec = year + month/12

    def get_sidereal_sun(h_local):
        if h_local is None:
            return None
        h_ut = h_local - tz_offset
        jd_ = jd(year, month, day, h_ut)
        trop = sun_lon_tropical(jd_)
        return (trop - ayanamsa(yr_dec)) % 360

    mandi_lon  = get_sidereal_sun(mandi_start_h)
    gulika_lon = get_sidereal_sun(gulika_start_h)

    # ── Format output ─────────────────────────────────────────────────
    SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
             "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
    NAKS  = ["Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
             "Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni",
             "Uttara Phalguni","Hasta","Chitra","Swati","Vishakha","Anuradha",
             "Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha","Shravana",
             "Dhanishtha","Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada",
             "Revati"]

    def format_planet(lon, name, start_h):
        if lon is None or start_h is None:
            return {
                "name": name,
                "longitude": None,
                "sign": None, "degree": None,
                "nakshatra": None, "pada": None,
                "period_start": None,
                "note": "Void period — not active on this weekday"
            }
        sign_idx = int(lon / 30) % 12
        deg_in_sign = lon % 30
        nak_idx = int(lon * 27 / 360) % 27
        pada = int((lon % (360/27)) / (360/27/4)) + 1
        h = int(start_h); mn = int((start_h-h)*60)
        ap = "AM" if h < 12 else "PM"; h12 = h%12 or 12
        return {
            "name":       name,
            "longitude":  round(lon, 4),
            "sign":       SIGNS[sign_idx],
            "degree":     round(deg_in_sign, 2),
            "nakshatra":  NAKS[nak_idx],
            "pada":       min(pada, 4),
            "period_start": f"{h12:02d}:{mn:02d} {ap}",
        }

    # ── Day period duration ───────────────────────────────────────────
    period_min = int(day_duration / 8 * 60)

    return {
        "mandi":   format_planet(mandi_lon,  "Mandi",  mandi_start_h),
        "gulika":  format_planet(gulika_lon, "Gulika", gulika_start_h),
        "sunrise": f"{int(sunrise):02d}:{int((sunrise%1)*60):02d}",
        "sunset":  f"{int(sunset):02d}:{int((sunset%1)*60):02d}",
        "day_duration_h": round(day_duration, 2),
        "period_duration_min": period_min,
        "source": "BPHS Ch.4 — Mandi/Gulika upagrahas",
    }


if __name__ == "__main__":
    # Test cases — verify against known ClickAstro reports
    tests = [
        ("Harshit Parakh", 2005,12,20, 28.02,73.19),
        ("Vedanth",        1996, 5,19, 12.58,77.33),
        ("Delhi today",    2026, 5,21, 28.61,77.21),
    ]
    for name, y,mo,d,lat,lon in tests:
        r = calc_mandi_gulika(y,mo,d,lat,lon)
        print(f"\n{name} ({y}-{mo:02d}-{d:02d})")
        print(f"  Sunrise: {r['sunrise']}  Sunset: {r['sunset']}")
        print(f"  Period:  {r['period_duration_min']}min each")
        m = r['mandi']
        g = r['gulika']
        print(f"  Mandi:   {m['sign']} {m['degree']:.2f}°  "
              f"[{m['nakshatra']}]  starts {m['period_start']}")
        print(f"  Gulika:  {g['sign']} {g['degree']:.2f}°  "
              f"[{g['nakshatra']}]  starts {g['period_start']}")
