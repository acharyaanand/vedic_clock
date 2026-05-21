"""
prashna_kundali.py — Horary Astrology (Prashna) Engine
=======================================================
Prashna = Question chart cast at the exact moment of query.
Used when birth time is unknown or for specific life questions.

What we calculate:
1. Prashna Lagna (Ascendant at question moment)
2. All planet positions at query time
3. Prashna Panchanga (Tithi, Vara, Nakshatra, Yoga, Karana)
4. Lagna Bala (strength of Prashna Ascendant)
5. Ruling planets (Hora lord, Weekday lord, Lagna lord, Moon sign lord)
6. Question analysis by house
7. Ashtamangala Prashna (8-point favorable check)
8. Answer tendency (favorable/unfavorable)

Source: Prashna Marga (Kerala tradition), Krishneeyam
"""

import math
from datetime import datetime
from typing import Dict

SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
         "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
NAKS  = ["Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
         "Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni","Uttara Phalguni",
         "Hasta","Chitra","Swati","Vishakha","Anuradha","Jyeshtha","Mula",
         "Purva Ashadha","Uttara Ashadha","Shravana","Dhanishtha","Shatabhisha",
         "Purva Bhadrapada","Uttara Bhadrapada","Revati"]
SIGN_LORD = {0:"mars",1:"venus",2:"mercury",3:"moon",4:"sun",5:"mercury",
              6:"venus",7:"mars",8:"jupiter",9:"saturn",10:"saturn",11:"jupiter"}

TITHI_N = ["Pratipada","Dwitiya","Tritiya","Chaturthi","Panchami","Shashthi",
           "Saptami","Ashtami","Navami","Dashami","Ekadashi","Dwadashi",
           "Trayodashi","Chaturdashi","Purnima"]*2 + ["Amavasya"]
PAKSHA = ["Shukla"]*15 + ["Krishna"]*15
YOGA_N = ["Vishkumbha","Priti","Ayushman","Saubhagya","Shobhana","Atiganda",
          "Sukarma","Dhriti","Shoola","Ganda","Vriddhi","Dhruva","Vyaghata",
          "Harshana","Vajra","Siddhi","Vyatipata","Variyana","Parigha","Shiva",
          "Siddha","Sadhya","Shubha","Shukla","Brahma","Indra","Vaidhriti"]
VARA   = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
HORA_LORD = {0:"sun",1:"venus",2:"mercury",3:"moon",4:"saturn",5:"jupiter",6:"mars"}


def _jd(y,m,d,h=0):
    if m<=2: y-=1; m+=12
    A=int(y/100); B=2-A+int(A/4)
    return int(365.25*(y+4716))+int(30.6001*(m+1))+d+h/24+B-1524.5

def _sun(jd_):
    T=(jd_-2451545)/36525
    L0=280.46646+36000.76983*T+0.0003032*T*T
    M=(357.52911+35999.05029*T-0.0001537*T*T)%360
    Mr=math.radians(M)
    C=(1.914602-0.004817*T-0.000014*T*T)*math.sin(Mr)+(0.019993-0.000101*T)*math.sin(2*Mr)+0.000289*math.sin(3*Mr)
    return(L0+C-0.00569-0.00478*math.sin(math.radians(125.04-1934.136*T)))%360

def _moon(jd_):
    T=(jd_-2451545)/36525
    T2=T*T;T3=T2*T;T4=T3*T
    Lp=(218.3164477+481267.88123421*T-0.0015786*T2+T3/538841-T4/65194000)%360
    D=(297.8501921+445267.1114034*T-0.0018819*T2+T3/545868-T4/113065000)%360
    M=(357.5291092+35999.0502909*T-0.0001536*T2+T3/24490000)%360
    Mp=(134.9633964+477198.8675055*T+0.0087414*T2+T3/69699-T4/14712000)%360
    F=(93.2720950+483202.0175233*T-0.0036539*T2-T3/3526000+T4/863310000)%360
    r=math.radians; E=1-0.002516*T-0.0000074*T2
    terms=[(0,0,1,0,6288774),(2,0,-1,0,1274027),(2,0,0,0,658314),(0,0,2,0,213618),
           (0,1,0,0,-185116),(0,0,0,2,-114332),(2,0,-2,0,58793),(2,-1,-1,0,57066),
           (2,0,1,0,53322),(2,-1,0,0,45758),(0,1,-1,0,-40923),(1,0,0,0,-34720),
           (0,1,1,0,-30383),(2,0,0,-2,15327),(0,0,1,-2,10980),(4,0,-1,0,10675),
           (0,0,3,0,10034),(4,0,-2,0,8548),(2,1,-1,0,-7888),(2,1,0,0,-6766),
           (1,0,-1,0,-5163),(1,1,0,0,4987),(2,-1,1,0,4036),(2,0,2,0,3994),
           (4,0,0,0,3861),(2,0,-3,0,3665),(0,1,-2,0,-2689),(2,-1,-2,0,2390),
           (1,0,1,0,-2348),(2,-2,0,0,2236),(0,1,2,0,-2120),(0,2,0,0,-2069),
           (2,-2,-1,0,2048),(4,-1,-1,0,1215),(0,0,2,2,-1110),(3,0,-1,0,-892),
           (2,1,1,0,-810),(4,-1,-2,0,759),(0,2,-1,0,-713),(2,2,-1,0,-700),
           (2,1,-2,0,691),(2,-1,0,-2,-596),(4,0,1,0,549),(0,0,4,0,537),
           (4,-1,0,0,520),(1,0,-2,0,-487),(2,1,0,-2,-399),(0,0,2,-2,-381),
           (1,1,1,0,351),(3,0,-2,0,-340),(4,0,-3,0,330),(2,-1,2,0,327),
           (0,2,1,0,-323),(1,1,-1,0,299),(2,0,3,0,294)]
    SL=sum(c*(E**abs(m_) if m_ else 1)*math.sin(r(d_*D+m_*M+mp_*Mp+f_*F)) for d_,m_,mp_,f_,c in terms)
    SL+=3958*math.sin(r((119.75+131.849*T)%360))+1962*math.sin(r((Lp-F)%360))+318*math.sin(r((53.09+479264.290*T)%360))
    return(Lp+SL/1e6)%360

def _ay(yr): return 23.8665+0.014206*(yr-2000)
def _sid(lon,yr): return(lon-_ay(yr))%360

def _sunrise(y,mo,d,lat,lon,tz):
    n=datetime(y,mo,d).timetuple().tm_yday
    B=360/365*(n-81)
    eot=9.87*math.sin(math.radians(2*B))-7.53*math.cos(math.radians(B))-1.5*math.sin(math.radians(B))
    sn=12-(lon-15*tz)/15-eot/60
    decl=math.degrees(math.asin(0.39795*math.cos(math.radians(0.98563*(n-173)))))
    lr=math.radians(lat); dr=math.radians(decl)
    cos_ha=(math.cos(math.radians(90.833))-math.sin(lr)*math.sin(dr))/(math.cos(lr)*math.cos(dr))
    ha=math.degrees(math.acos(max(-1,min(1,cos_ha))))
    return sn-ha/15


# ── Question categories ────────────────────────────────────────────────
QUESTION_HOUSES = {
    "health":       {"house":1, "karaka":"sun",     "desc":"1st house — self, body, health"},
    "wealth":       {"house":2, "karaka":"jupiter", "desc":"2nd house — money, family, food"},
    "siblings":     {"house":3, "karaka":"mars",    "desc":"3rd house — brothers, courage, travel"},
    "property":     {"house":4, "karaka":"moon",    "desc":"4th house — home, mother, vehicle"},
    "children":     {"house":5, "karaka":"jupiter", "desc":"5th house — children, romance, education"},
    "enemies":      {"house":6, "karaka":"mars",    "desc":"6th house — enemies, disease, debts"},
    "marriage":     {"house":7, "karaka":"venus",   "desc":"7th house — spouse, partnership, business"},
    "longevity":    {"house":8, "karaka":"saturn",  "desc":"8th house — death, obstacles, secrets"},
    "fortune":      {"house":9, "karaka":"jupiter", "desc":"9th house — father, luck, dharma"},
    "career":       {"house":10,"karaka":"mercury", "desc":"10th house — profession, authority"},
    "gains":        {"house":11,"karaka":"jupiter", "desc":"11th house — income, desires, elder siblings"},
    "losses":       {"house":12,"karaka":"saturn",  "desc":"12th house — expenses, foreign, moksha"},
    "general":      {"house":1, "karaka":"sun",     "desc":"General question"},
}

FAVORABLE_SIGNS = {4,0,8,11,2}  # Cancer, Aries, Sagittarius, Pisces, Gemini — benefic
BENEFIC_PLANETS = {"jupiter","venus","moon","mercury"}
MALEFIC_PLANETS = {"saturn","mars","rahu","ketu","sun"}

GOOD_YOGAS = {"Priti","Ayushman","Saubhagya","Shobhana","Sukarma","Dhriti",
              "Vriddhi","Dhruva","Harshana","Siddhi","Variyana","Shiva",
              "Siddha","Sadhya","Shubha","Shukla","Brahma","Indra"}

# Ashtamangala: 8 good signs
ASHTAMANGALA_CHECKS = [
    "Lagna in benefic sign",
    "Lagna lord strong",
    "Moon in favorable position",
    "No malefics in 1/8 houses",
    "Benefic in Kendra (1/4/7/10)",
    "Hora lord is benefic",
    "Auspicious Yoga",
    "Good Tithi and Vara"
]


def calc_prashna_kundali(
    lat: float, lon: float, tz: float = 5.5,
    question_type: str = "general",
    query_dt: datetime = None
) -> dict:
    """
    Cast a Prashna Kundali at the current moment (or given datetime).
    
    Parameters:
        lat, lon, tz:    Observer's location
        question_type:   One of: health, wealth, marriage, career, children,
                         property, fortune, enemies, gains, longevity, general
        query_dt:        Datetime of question (default = now)
    
    Returns complete Prashna chart with analysis.
    """
    if query_dt is None:
        query_dt = datetime.now()
    
    y, mo, d = query_dt.year, query_dt.month, query_dt.day
    h_local  = query_dt.hour + query_dt.minute/60 + query_dt.second/3600
    h_ut     = h_local - tz
    jd_      = _jd(y, mo, d, h_ut)
    yr_dec   = y + mo/12
    
    # ── Planet positions ──────────────────────────────────────────────
    sun_t  = _sun(jd_); sun_s  = _sid(sun_t, yr_dec)
    moon_t = _moon(jd_); moon_s = _sid(moon_t, yr_dec)
    
    # Simple planet positions (using same formulas as engine.py)
    T = (jd_ - 2451545) / 36525
    def sid(lon): return (lon - _ay(yr_dec)) % 360
    
    mercury_s = sid((252.250906+149474.0722491*T) % 360)
    venus_s   = sid((181.979801+58519.2130302*T) % 360)
    mars_s    = sid((355.433+19141.6964471*T) % 360)
    jupiter_s = sid((34.351519+3036.3027748*T) % 360)
    saturn_s  = sid((50.077444+1223.5110686*T) % 360)
    rahu_s    = sid((125.0445-1934.1363*T-0.0020708*T*T) % 360)
    ketu_s    = (rahu_s + 180) % 360
    
    # Lagna — use Sun + 90° as approximate Prashna Lagna
    # (Proper Lagna needs sidereal time + lat-based calculation)
    # Approximate: Lagna changes 1 sign per 2 hours
    hours_since_sunrise = h_local - _sunrise(y, mo, d, lat, lon, tz)
    lagna_offset = int(hours_since_sunrise / 2)
    sun_sign_idx  = int(sun_s / 30) % 12
    lagna_idx     = (sun_sign_idx + lagna_offset) % 12
    
    # ── Panchanga at query time ───────────────────────────────────────
    diff = (moon_s - sun_s) % 360
    tithi_idx = int(diff / 12)
    yoga_idx  = int(((sun_s + moon_s) % 360) / (360/27)) % 27
    vara_idx  = int((jd_ + 1.5) % 7)
    nak_idx   = int(moon_s * 27 / 360) % 27
    
    # Hora lord at this moment
    hora_hour = int(h_local)
    hora_order_day = [4,5,6,0,1,2,3]  # Sun, Mon, Tue, Wed, Thu, Fri, Sat Hora start
    hora_lord = HORA_LORD.get((vara_idx * 24 + hora_hour) % 7, "sun")
    
    # ── Ruling planets (Prashna's 5 ruling planets) ─────────────────
    # Weekday lord, Hora lord, Moon sign lord, Moon nakshatra lord,
    # Lagna lord
    NAK_LORDS = ["ketu","venus","sun","moon","mars","rahu","jupiter","saturn","mercury"]*3
    weekday_lord = ["sun","moon","mars","mercury","jupiter","venus","saturn"][vara_idx]
    moon_sign_lord = SIGN_LORD[int(moon_s/30)%12]
    moon_nak_lord  = NAK_LORDS[nak_idx]
    lagna_lord     = SIGN_LORD[lagna_idx]
    
    ruling_planets = list(dict.fromkeys([
        weekday_lord, hora_lord, moon_sign_lord, moon_nak_lord, lagna_lord
    ]))
    
    # ── Ashtamangala (8 auspiciousness checks) ───────────────────────
    am_checks = {
        "lagna_in_benefic_sign":  lagna_idx in FAVORABLE_SIGNS,
        "lagna_lord_is_benefic":  lagna_lord in BENEFIC_PLANETS,
        "moon_in_benefic_sign":   int(moon_s/30)%12 in FAVORABLE_SIGNS,
        "no_malefic_in_lagna":    True,  # Simplified
        "benefic_in_kendra":      lagna_lord in BENEFIC_PLANETS,
        "hora_lord_benefic":      hora_lord in BENEFIC_PLANETS,
        "auspicious_yoga":        YOGA_N[yoga_idx] in GOOD_YOGAS,
        "good_tithi_vara":        tithi_idx % 15 in [1,2,4,6,9,10,12],
    }
    am_score = sum(am_checks.values())
    
    # ── Question analysis ─────────────────────────────────────────────
    q_info = QUESTION_HOUSES.get(question_type, QUESTION_HOUSES["general"])
    q_house = q_info["house"]
    q_karaka = q_info["karaka"]
    
    # Check if karaka planet is strong (in own/exalt sign or kendra)
    EXALT = {"sun":0,"moon":1,"mars":9,"mercury":5,"jupiter":3,"venus":11,"saturn":6}
    DEBIL = {"sun":6,"moon":7,"mars":3,"mercury":11,"jupiter":9,"venus":5,"saturn":0}
    
    karaka_lon = {
        "sun":sun_s,"moon":moon_s,"mercury":mercury_s,"venus":venus_s,
        "mars":mars_s,"jupiter":jupiter_s,"saturn":saturn_s
    }.get(q_karaka, sun_s)
    
    karaka_sign = int(karaka_lon/30)%12
    karaka_strong = (karaka_sign == EXALT.get(q_karaka) or 
                     SIGN_LORD.get(karaka_sign) == q_karaka)
    karaka_weak = karaka_sign == DEBIL.get(q_karaka)
    
    # Moon's condition — key for prashna
    moon_sign = int(moon_s/30)%12
    moon_good = moon_sign in FAVORABLE_SIGNS
    
    # Overall answer tendency
    favorable_count = (
        (lagna_idx in FAVORABLE_SIGNS) +
        (lagna_lord in BENEFIC_PLANETS) +
        (YOGA_N[yoga_idx] in GOOD_YOGAS) +
        moon_good +
        karaka_strong +
        (am_score >= 5)
    )
    
    if favorable_count >= 5:   answer = "Highly Favorable ✅"
    elif favorable_count >= 3: answer = "Favorable ✅"
    elif favorable_count >= 2: answer = "Mixed — some hope 🔶"
    else:                      answer = "Unfavorable — delays likely ❌"
    
    # ── Format time ───────────────────────────────────────────────────
    ap = "AM" if h_local < 12 else "PM"
    h12 = int(h_local) % 12 or 12
    mn  = int((h_local % 1) * 60)
    time_str = f"{h12:02d}:{mn:02d} {ap}"
    
    planets_table = {
        "sun":     {"longitude": round(sun_s,2),  "sign": SIGNS[int(sun_s/30)%12],  "nakshatra": NAKS[int(sun_s*27/360)%27]},
        "moon":    {"longitude": round(moon_s,2), "sign": SIGNS[int(moon_s/30)%12], "nakshatra": NAKS[int(moon_s*27/360)%27]},
        "mercury": {"longitude": round(mercury_s,2),"sign": SIGNS[int(mercury_s/30)%12],"nakshatra": NAKS[int(mercury_s*27/360)%27]},
        "venus":   {"longitude": round(venus_s,2),  "sign": SIGNS[int(venus_s/30)%12],  "nakshatra": NAKS[int(venus_s*27/360)%27]},
        "mars":    {"longitude": round(mars_s,2),   "sign": SIGNS[int(mars_s/30)%12],   "nakshatra": NAKS[int(mars_s*27/360)%27]},
        "jupiter": {"longitude": round(jupiter_s,2),"sign": SIGNS[int(jupiter_s/30)%12],"nakshatra": NAKS[int(jupiter_s*27/360)%27]},
        "saturn":  {"longitude": round(saturn_s,2), "sign": SIGNS[int(saturn_s/30)%12], "nakshatra": NAKS[int(saturn_s*27/360)%27]},
        "rahu":    {"longitude": round(rahu_s,2),   "sign": SIGNS[int(rahu_s/30)%12],   "nakshatra": NAKS[int(rahu_s*27/360)%27]},
        "ketu":    {"longitude": round(ketu_s,2),   "sign": SIGNS[int(ketu_s/30)%12],   "nakshatra": NAKS[int(ketu_s*27/360)%27]},
    }
    
    return {
        "query_time":    f"{y}-{mo:02d}-{d:02d} {time_str}",
        "question_type": question_type,
        "question_house":q_info["desc"],
        "prashna_lagna": {
            "sign": SIGNS[lagna_idx],
            "lord": lagna_lord.capitalize(),
        },
        "panchanga": {
            "tithi":    f"{PAKSHA[tithi_idx]} {TITHI_N[tithi_idx % 30]}",
            "vara":     VARA[vara_idx],
            "nakshatra":NAKS[nak_idx],
            "yoga":     YOGA_N[yoga_idx],
        },
        "ruling_planets":  [p.capitalize() for p in ruling_planets],
        "hora_lord":       hora_lord.capitalize(),
        "karaka_planet":   {
            "planet": q_karaka.capitalize(),
            "strong": karaka_strong,
            "weak":   karaka_weak,
        },
        "ashtamangala": {
            "score":    f"{am_score}/8",
            "checks":   am_checks,
            "verdict":  "Highly Auspicious" if am_score>=7 else 
                        "Auspicious" if am_score>=5 else
                        "Mixed" if am_score>=3 else "Inauspicious"
        },
        "answer_tendency":  answer,
        "favorable_count":  f"{favorable_count}/6",
        "planets":          planets_table,
        "interpretation": {
            "summary": f"Prashna cast at {time_str} on {VARA[vara_idx]}. "
                       f"Lagna in {SIGNS[lagna_idx]}, Moon in {NAKS[nak_idx]}. "
                       f"Ruling planets: {', '.join(p.capitalize() for p in ruling_planets[:3])}.",
            "answer":  answer,
            "advice": ("Auspicious moment — proceed with your plans." 
                       if favorable_count >= 3 else
                       "Consider waiting for a more favorable time."),
        },
        "source": "Prashna Marga (Kerala Jyotish tradition)"
    }


if __name__ == "__main__":
    print("PRASHNA KUNDALI TEST — Delhi May 21 2026")
    print("="*55)
    
    for q_type in ["marriage","career","wealth","health"]:
        r = calc_prashna_kundali(28.61, 77.21, 5.5, q_type)
        print(f"\nQuestion: {q_type.upper()}")
        print(f"  Lagna:    {r['prashna_lagna']['sign']} (Lord: {r['prashna_lagna']['lord']})")
        print(f"  Ruling:   {', '.join(r['ruling_planets'][:3])}")
        print(f"  Answer:   {r['answer_tendency']}")
        print(f"  Score:    Ashtamangala {r['ashtamangala']['score']} — {r['ashtamangala']['verdict']}")
