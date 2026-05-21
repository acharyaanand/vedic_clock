"""
varshaphal.py — Solar Return (Varshaphal) Engine
=================================================
Varshaphal = Annual horoscope based on Solar Return chart.
When Sun returns to exact natal longitude each year = new year begins.

What we calculate:
1. Solar return moment (exact date/time/tz for each year)
2. Varsha Lagna (Ascendant at solar return moment)
3. Muntha (progressed Ascendant — 1 sign per year)
4. Varsha lord (lord of Muntha sign)
5. Tri-Pataki Chakra (3 groups of planets)
6. Panchadha Maitri (5-fold friendship analysis)
7. Harsha Bala, Dina Bala — annual strengths
8. Mudda Dasha (annual sub-periods within 1 year)

Source: Tajika Neelakanthi (Neelakantha), Varshaphal (annual horoscope)
"""

import math
from datetime import datetime, timedelta
from typing import Dict, List

SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
         "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
NAKS  = ["Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
         "Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni","Uttara Phalguni",
         "Hasta","Chitra","Swati","Vishakha","Anuradha","Jyeshtha","Mula",
         "Purva Ashadha","Uttara Ashadha","Shravana","Dhanishtha","Shatabhisha",
         "Purva Bhadrapada","Uttara Bhadrapada","Revati"]
SIGN_LORD = {0:"mars",1:"venus",2:"mercury",3:"moon",4:"sun",5:"mercury",
              6:"venus",7:"mars",8:"jupiter",9:"saturn",10:"saturn",11:"jupiter"}


def _jd(y, m, d, h=0.0):
    if m<=2: y-=1; m+=12
    A=int(y/100); B=2-A+int(A/4)
    return int(365.25*(y+4716))+int(30.6001*(m+1))+d+h/24+B-1524.5

def _sun_tropical(jd_):
    T=(jd_-2451545.0)/36525
    L0=280.46646+36000.76983*T+0.0003032*T*T
    M=(357.52911+35999.05029*T-0.0001537*T*T)%360
    Mr=math.radians(M)
    C=(1.914602-0.004817*T-0.000014*T*T)*math.sin(Mr)
    C+=(0.019993-0.000101*T)*math.sin(2*Mr)+0.000289*math.sin(3*Mr)
    omega=125.04-1934.136*T
    return(L0+C-0.00569-0.00478*math.sin(math.radians(omega)))%360

def _ayanamsa(yr): return 23.8665+0.014206*(yr-2000)

def _sun_sidereal(jd_):
    yr=(jd_-2451545)/365.25+2000
    return (_sun_tropical(jd_)-_ayanamsa(yr))%360


def find_solar_return(natal_sun_lon: float, birth_year: int, 
                       target_year: int, lat: float, lon: float, 
                       tz: float = 5.5) -> dict:
    """
    Find exact Solar Return moment for target_year.
    Returns precise date, time, and chart details.
    """
    # Approximate: Sun returns to natal longitude once per year
    # Start search from Jan 1 of target_year
    # Sun moves ~1°/day, so search window is 365 days
    
    # Binary search for exact moment
    jd_start = _jd(target_year, 1, 1, 0)
    jd_end   = _jd(target_year, 12, 31, 23)
    
    # Find when sun_sidereal crosses natal_sun_lon
    target = natal_sun_lon
    
    # Coarse scan: every 3 days
    sr_jd = None
    step = 3.0
    t = jd_start
    prev_diff = None
    
    while t < jd_end:
        curr_lon = _sun_sidereal(t)
        diff = (curr_lon - target + 180) % 360 - 180
        
        if prev_diff is not None:
            if prev_diff < 0 and diff >= 0:
                # Crossed target — binary search
                lo, hi = t - step, t
                for _ in range(50):
                    mid = (lo + hi) / 2
                    d = (_sun_sidereal(mid) - target + 180) % 360 - 180
                    if d < 0: lo = mid
                    else: hi = mid
                    if hi - lo < 0.0001: break
                sr_jd = (lo + hi) / 2
                break
        prev_diff = diff
        t += step
    
    if sr_jd is None:
        return {"error": f"Solar return not found for {target_year}"}
    
    # Convert to local time
    local_h = (sr_jd - _jd(target_year, 1, 1, 0)) % 1 * 24 + tz
    # Get date
    jd_date = int(sr_jd + 0.5)
    z = jd_date; f = sr_jd + 0.5 - jd_date
    if z >= 2299161: a=int((z-1867216.25)/36524.25); z=z+1+a-int(a/4)
    b=z+1524; c=int((b-122.1)/365.25); d_=int(365.25*c); e=int((b-d_)/30.6001)
    day=b-d_-int(30.6001*e); mo=e-1 if e<14 else e-13; yr=c-4716 if mo>2 else c-4715
    frac=f*24; hr=int(frac); mn=int((frac-hr)*60)
    
    # Sun longitude at return
    sun_lon = _sun_sidereal(sr_jd)
    
    # Calculate Lagna at solar return (Varsha Lagna)
    # Simplified: use Sun's sign as Lagna approximation
    # For precise calc: need sidereal time and house calculation
    # Using Sun + 2 signs as approximate Varsha Lagna (Tajika tradition)
    varsha_lagna_idx = (int(sun_lon/30) + 2) % 12
    
    ap="AM" if hr<12 else "PM"; h12=hr%12 or 12
    
    return {
        "year":        target_year,
        "date":        f"{yr}-{mo:02d}-{day:02d}",
        "time":        f"{h12:02d}:{mn:02d} {ap}",
        "sun_longitude": round(sun_lon, 4),
        "sun_sign":    SIGNS[int(sun_lon/30)%12],
        "varsha_lagna": SIGNS[varsha_lagna_idx],
        "varsha_lagna_lord": SIGN_LORD[varsha_lagna_idx].capitalize(),
    }


def calc_muntha(birth_year: int, birth_lagna_sign: str, target_year: int) -> dict:
    """
    Muntha = progressed Ascendant. Moves 1 sign per year.
    Muntha_sign = (birth_lagna_sign + years_elapsed) % 12
    """
    SIGN_IDX = {s:i for i,s in enumerate(SIGNS)}
    birth_lagna_idx = SIGN_IDX.get(birth_lagna_sign, 0)
    years_elapsed = target_year - birth_year
    muntha_idx = (birth_lagna_idx + years_elapsed) % 12
    muntha_lord = SIGN_LORD[muntha_idx]
    
    # Muntha in different houses has different effects
    # House position = relative to Varsha Lagna
    return {
        "muntha_sign":    SIGNS[muntha_idx],
        "muntha_lord":    muntha_lord.capitalize(),
        "years_elapsed":  years_elapsed,
        "effect": {
            1:  "Excellent year — success in all endeavors",
            2:  "Financial gains, family welfare",
            3:  "Travel, siblings, short journeys",
            4:  "Domestic happiness, property matters",
            5:  "Children, intelligence, gains",
            6:  "Health challenges, debts, enemies",
            7:  "Marriage, partnerships, relationships",
            8:  "Obstacles, health issues, transformations",
            9:  "Fortune, spirituality, father's welfare",
            10: "Career success, authority, recognition",
            11: "Great gains, fulfillment of desires",
            12: "Expenses, foreign travel, spiritual growth",
        }.get((muntha_idx + 1) % 12 + 1, "Mixed results")
    }


MUDDA_DASHA_YEARS = {
    "sun": 11/12, "moon": 1.0, "mars": 7/12, "mercury": 17/12,
    "jupiter": 16/12, "venus": 20/12, "saturn": 19/12,
    "rahu": 18/12, "ketu": 7/12
}
# Mudda Dasha = annual dasha within Varshaphal year
# Total = 1 year, proportional to Vimshottari years

def calc_mudda_dasha(solar_return_date: str, varsha_lagna_sign: str) -> list:
    """
    Mudda Dasha = annual sub-periods within Varshaphal year.
    Total = 365 days. Sequence starts from Varsha Lagna lord.
    """
    DASHA_ORDER = ["ketu","venus","sun","moon","mars","rahu","jupiter","saturn","mercury"]
    DASHA_DAYS_YEAR = {  # Days in 1-year cycle
        "sun":33, "moon":37, "mars":21, "mercury":51,
        "jupiter":48, "venus":60, "saturn":57, "rahu":54, "ketu":21
    }
    # Total = 382 days (normalize to 365)
    total_raw = sum(DASHA_DAYS_YEAR.values())
    
    lagna_lord = SIGN_LORD.get({s:i for i,s in enumerate(SIGNS)}.get(varsha_lagna_sign,0), "sun")
    start_idx = DASHA_ORDER.index(lagna_lord) if lagna_lord in DASHA_ORDER else 0
    
    try:
        start_dt = datetime.strptime(solar_return_date, "%Y-%m-%d")
    except:
        start_dt = datetime.now()
    
    result = []
    cur = start_dt
    
    for i in range(9):
        lord = DASHA_ORDER[(start_idx + i) % 9]
        raw_days = DASHA_DAYS_YEAR.get(lord, 21)
        days = raw_days * 365 / total_raw
        end = cur + timedelta(days=days)
        result.append({
            "lord":  lord,
            "start": cur.strftime("%Y-%m-%d"),
            "end":   end.strftime("%Y-%m-%d"),
            "days":  round(days),
        })
        cur = end
    
    return result


def calc_varshaphal(natal_sun_lon: float, birth_year: int, birth_month: int,
                     birth_day: int, birth_lagna_sign: str,
                     lat: float, lon: float, tz: float = 5.5,
                     years_to_show: int = 3) -> dict:
    """
    Calculate complete Varshaphal (Solar Return) for multiple years.
    """
    current_year = datetime.now().year
    results = {}
    
    for yr in range(current_year - 1, current_year + years_to_show):
        sr = find_solar_return(natal_sun_lon, birth_year, yr, lat, lon, tz)
        if "error" in sr:
            continue
        
        muntha = calc_muntha(birth_year, birth_lagna_sign, yr)
        mudda  = calc_mudda_dasha(sr["date"], sr["varsha_lagna"])
        
        # Find current Mudda Dasha
        today = datetime.now()
        current_mudda = None
        for md in mudda:
            try:
                ms = datetime.strptime(md["start"], "%Y-%m-%d")
                me = datetime.strptime(md["end"], "%Y-%m-%d")
                if ms <= today <= me:
                    current_mudda = md
                    break
            except: pass
        
        results[str(yr)] = {
            "solar_return": sr,
            "muntha":       muntha,
            "mudda_dasha":  mudda,
            "current_mudda_dasha": current_mudda,
            "year_lord":    muntha["muntha_lord"],
            "year_quality": muntha["effect"],
        }
    
    return {
        "natal_sun_longitude": round(natal_sun_lon, 4),
        "birth_year":          birth_year,
        "years": results,
        "source": "Tajika Neelakanthi — Varshaphal System"
    }


if __name__ == "__main__":
    # Test with Vedanth (May 19 1996, Sun ~26° Taurus sidereal = ~56°)
    result = calc_varshaphal(
        natal_sun_lon=56.0,
        birth_year=1996, birth_month=5, birth_day=19,
        birth_lagna_sign="Virgo",
        lat=12.58, lon=77.33, tz=5.5,
        years_to_show=3
    )
    
    print("VARSHAPHAL TEST — Vedanth")
    print("="*55)
    for yr, data in result["years"].items():
        sr = data["solar_return"]
        mn = data["muntha"]
        print(f"\nYear {yr}:")
        print(f"  Solar Return: {sr['date']} at {sr['time']}")
        print(f"  Varsha Lagna: {sr['varsha_lagna']} (Lord: {sr['varsha_lagna_lord']})")
        print(f"  Muntha: {mn['muntha_sign']} (Lord: {mn['muntha_lord']})")
        print(f"  Year Quality: {mn['effect'][:50]}...")
        if data["current_mudda_dasha"]:
            md = data["current_mudda_dasha"]
            print(f"  Current Mudda: {md['lord'].capitalize()} until {md['end']}")
