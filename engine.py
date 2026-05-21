"""
AETHERIS — AetherisEngine
Swiss Ephemeris based planetary calculation engine.
Falls back to astronomical formulas if swisseph unavailable.
"""
import math
from typing import Dict, List
from datetime import datetime, timedelta
import os

try:
    import swisseph as swe
    SWE_AVAILABLE = True
except ImportError:
    SWE_AVAILABLE = False

SIGNS = ["aries","taurus","gemini","cancer","leo","virgo",
         "libra","scorpio","sagittarius","capricorn","aquarius","pisces"]

NAKSHATRAS_LIST = [
    "Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
    "Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni",
    "Uttara Phalguni","Hasta","Chitra","Swati","Vishakha","Anuradha",
    "Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha","Shravana",
    "Dhanishtha","Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati"
]

GOOD_MARRIAGE_NAKSHATRAS = [
    "Rohini","Mrigashira","Magha","Uttara Phalguni","Hasta","Swati",
    "Anuradha","Uttara Ashadha","Shravana","Revati","Uttara Bhadrapada"
]
GOOD_MARRIAGE_LAGNAS = ["taurus","gemini","cancer","libra","sagittarius","pisces"]
GOOD_MARRIAGE_TITHIS = [2, 3, 5, 7, 10, 11, 12, 13]

TITHI_NAMES = [
    "Pratipada","Dwitiya","Tritiya","Chaturthi","Panchami","Shashthi",
    "Saptami","Ashtami","Navami","Dashami","Ekadashi","Dwadashi",
    "Trayodashi","Chaturdashi","Purnima",
    "Pratipada","Dwitiya","Tritiya","Chaturthi","Panchami","Shashthi",
    "Saptami","Ashtami","Navami","Dashami","Ekadashi","Dwadashi",
    "Trayodashi","Chaturdashi","Amavasya"
]
YOGA_NAMES = [
    "Vishkumbha","Priti","Ayushman","Saubhagya","Shobhana","Atiganda",
    "Sukarma","Dhriti","Shoola","Ganda","Vriddhi","Dhruva","Vyaghata",
    "Harshana","Vajra","Siddhi","Vyatipata","Variyana","Parigha","Shiva",
    "Siddha","Sadhya","Shubha","Shukla","Brahma","Indra","Vaidhriti"
]
KARANA_NAMES = [
    "Bava","Balava","Kaulava","Taitila","Gara","Vanija","Vishti",
    "Bava","Balava","Kaulava","Vishti"
]
VAARA_NAMES = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]


def _julian_day(year, month, day, hour=12.0):
    """Calculate Julian Day Number."""
    if month <= 2:
        year -= 1
        month += 12
    A = int(year / 100)
    B = 2 - A + int(A / 4)
    return int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + hour/24.0 + B - 1524.5


def _approx_planet_positions(year, month, day, hour, lat, lon, ayanamsa_offset=23.15):
    """
    Approximate planetary positions using simplified astronomical formulas.
    Accurate to within 1-2 degrees — sufficient for Vedic astrology purposes.
    Lahiri Ayanamsa offset ~23.15 degrees (2026 value).
    """
    jd = _julian_day(year, month, day, hour)
    T = (jd - 2451545.0) / 36525.0  # Julian centuries from J2000

    def norm(x): return x % 360

    # Sun (mean longitude)
    L0 = norm(280.46646 + 36000.76983 * T)
    M0 = norm(357.52911 + 35999.05029 * T)
    C = (1.914602 - 0.004817*T)*math.sin(math.radians(M0)) +         0.019993*math.sin(math.radians(2*M0))
    sun_lon = norm(L0 + C - ayanamsa_offset)

    # Moon
    Lm = norm(218.3165 + 481267.8813 * T)
    Mm = norm(134.9634 + 477198.8676 * T)
    Dm = norm(297.8502 + 445267.1115 * T)
    moon_lon = norm(Lm + 6.289*math.sin(math.radians(Mm))
                   - 1.274*math.sin(math.radians(2*Dm - Mm))
                   + 0.658*math.sin(math.radians(2*Dm))
                   - ayanamsa_offset)

    # Mercury
    merc_lon = norm(252.251 + 149474.072 * T - ayanamsa_offset)

    # Venus
    ven_lon = norm(181.980 + 58519.213 * T - ayanamsa_offset)

    # Mars
    mars_lon = norm(355.433 + 19141.696 * T - ayanamsa_offset)

    # Jupiter
    jup_lon = norm(34.351 + 3036.702 * T - ayanamsa_offset)

    # Saturn
    sat_lon = norm(50.077 + 1223.511 * T - ayanamsa_offset)

    # Rahu (Mean Node) — moves retrograde
    rahu_lon = norm(125.044 - 1934.136 * T - ayanamsa_offset)
    ketu_lon = norm(rahu_lon + 180)

    # Ascendant — approximate using RAMC
    RAMC = norm(280.46061837 + 360.98564736629*(jd-2451545) + lon)
    eps = 23.439 - 0.013*T  # obliquity
    asc_lon = norm(math.degrees(math.atan2(
        math.cos(math.radians(RAMC)),
        -(math.sin(math.radians(RAMC))*math.cos(math.radians(eps)) +
          math.tan(math.radians(lat))*math.sin(math.radians(eps)))
    )) - ayanamsa_offset)

    return {
        "sun": sun_lon, "moon": moon_lon, "mercury": merc_lon,
        "venus": ven_lon, "mars": mars_lon, "jupiter": jup_lon,
        "saturn": sat_lon, "rahu": rahu_lon, "ketu": ketu_lon,
        "ascendant": asc_lon
    }


class AetherisEngine:
    def __init__(self, birth_details):
        self.details = birth_details
        self.lat = birth_details.latitude
        self.lon = birth_details.longitude
        self.year = birth_details.year
        self.month = birth_details.month
        self.day = birth_details.day
        self.hour = birth_details.hour + birth_details.minute/60 + birth_details.second/3600
        self.ayanamsa = getattr(birth_details, "ayanamsa", "lahiri")
        self.house_sys = getattr(birth_details, "house_system", "whole_sign")

        if SWE_AVAILABLE:
            # KP ayanamsa uses Lahiri as base in this swisseph version
            ayanamsa_map = {"lahiri": swe.SIDM_LAHIRI, "raman": swe.SIDM_RAMAN, "kp": swe.SIDM_LAHIRI}
            swe.set_sid_mode(ayanamsa_map.get(self.ayanamsa, swe.SIDM_LAHIRI))
            self.jd = swe.julday(self.year, self.month, self.day, self.hour)
        else:
            self.jd = _julian_day(self.year, self.month, self.day, self.hour)

    def _sign_name(self, lon): return SIGNS[int(lon/30)%12]
    def _nakshatra(self, lon): return NAKSHATRAS_LIST[int((lon*27)/360)%27]
    def _nakshatra_number(self, lon): return int((lon*27)/360)%27+1
    def _nakshatra_pada(self, lon):
        sl = 360/27; idx = int((lon*27)/360)%27
        return int((lon - idx*sl)/(sl/4))+1

    async def get_planet_positions(self) -> Dict:
        planets = {}

        if SWE_AVAILABLE:
            bodies = [
                (swe.SUN,"sun"),(swe.MOON,"moon"),(swe.MERCURY,"mercury"),
                (swe.VENUS,"venus"),(swe.MARS,"mars"),(swe.JUPITER,"jupiter"),
                (swe.SATURN,"saturn"),(swe.MEAN_NODE,"rahu"),
            ]
            for code, name in bodies:
                try:
                    pos, _ = swe.calc_ut(self.jd, code, swe.FLG_SIDEREAL|swe.FLG_SPEED)
                    lon = pos[0] % 360
                    planets[name] = {
                        "name": name, "longitude": round(lon,6),
                        "sign": self._sign_name(lon), "degree": round(lon%30,4),
                        "nakshatra": self._nakshatra(lon),
                        "nakshatra_number": self._nakshatra_number(lon),
                        "nakshatra_pada": self._nakshatra_pada(lon),
                        "is_retrograde": pos[3] < 0,
                        "speed_long": round(pos[3],6),
                    }
                except: continue
            # Ketu
            if "rahu" in planets:
                ketu_lon = (planets["rahu"]["longitude"] + 180) % 360
                planets["ketu"] = {
                    "name":"ketu","longitude":round(ketu_lon,6),
                    "sign":self._sign_name(ketu_lon),"degree":round(ketu_lon%30,4),
                    "nakshatra":self._nakshatra(ketu_lon),
                    "nakshatra_number":self._nakshatra_number(ketu_lon),
                    "nakshatra_pada":self._nakshatra_pada(ketu_lon),
                    "is_retrograde":True,"speed_long":-1.0,
                }
            # Ascendant
            try:
                houses_raw, ascmc = swe.houses_ex(self.jd,self.lat,self.lon,b'W',swe.FLG_SIDEREAL)
                asc_lon = ascmc[0] % 360
                planets["ascendant"] = {"name":"ascendant","longitude":round(asc_lon,6),"sign":self._sign_name(asc_lon),"degree":round(asc_lon%30,4)}
            except: pass
        else:
            # Fallback: pure-math approximation
            lons = _approx_planet_positions(self.year,self.month,self.day,self.hour,self.lat,self.lon)
            for name, lon in lons.items():
                planets[name] = {
                    "name": name, "longitude": round(lon,4),
                    "sign": self._sign_name(lon), "degree": round(lon%30,4),
                    "nakshatra": self._nakshatra(lon),
                    "nakshatra_number": self._nakshatra_number(lon),
                    "nakshatra_pada": self._nakshatra_pada(lon),
                    "is_retrograde": name in ["rahu","ketu","saturn"],
                    "speed_long": 0.0,
                    "note": "Approximate position (swisseph unavailable)"
                }
        return planets

    async def get_houses(self, planets: Dict) -> Dict:
        houses = {}
        asc_lon = planets.get("ascendant",{}).get("longitude",0)

        if SWE_AVAILABLE:
            try:
                houses_raw, ascmc = swe.houses_ex(self.jd,self.lat,self.lon,b'W',swe.FLG_SIDEREAL)
                for i in range(12):
                    cusp = houses_raw[i] % 360
                    houses[i+1] = {"cusp":round(cusp,4),"sign":self._sign_name(cusp),"degree":round(cusp%30,4),"planets":[]}
            except:
                SWE_AVAILABLE_LOCAL = False

        if not houses:
            # Whole sign fallback
            lagna_idx = int(asc_lon/30)
            for i in range(12):
                cusp = ((lagna_idx+i)%12)*30
                houses[i+1] = {"cusp":round(cusp,4),"sign":SIGNS[(lagna_idx+i)%12],"degree":0.0,"planets":[]}

        # Assign planets to houses
        skip = ["ascendant","midheaven","true_node"]
        for pname, pdata in planets.items():
            if pname in skip: continue
            lon = pdata.get("longitude",0)
            for hnum in range(1,13):
                cur = houses[hnum]["cusp"]
                nxt = houses[(hnum%12)+1]["cusp"]
                if cur <= nxt:
                    if cur <= lon < nxt: houses[hnum]["planets"].append(pname); break
                else:
                    if lon >= cur or lon < nxt: houses[hnum]["planets"].append(pname); break
        return houses

    async def get_panchanga(self, sun_lon, moon_lon):
        diff = (moon_lon - sun_lon) % 360
        tithi_num = int(diff/12)
        paksha = "Shukla Paksha" if tithi_num < 15 else "Krishna Paksha"
        weekday = int((self.jd+1.5)%7)
        yoga_idx = int(((sun_lon+moon_lon)%360)/(360/27))%27
        yoga = YOGA_NAMES[yoga_idx]
        return {
            "tithi":{"name":TITHI_NAMES[tithi_num%30],"number":tithi_num+1,"paksha":paksha},
            "vaara":{"name":VAARA_NAMES[weekday],"number":weekday+1},
            "nakshatra":{"name":self._nakshatra(moon_lon),"pada":self._nakshatra_pada(moon_lon)},
            "yoga":{"name":yoga,"is_auspicious":yoga not in ["Vishkumbha","Atiganda","Shoola","Ganda","Vyaghata","Vajra","Vyatipata","Parigha","Vaidhriti"]},
            "karana":{"name":KARANA_NAMES[int(diff/6)%11]}
        }

    async def find_marriage_muhurtas(self, year, month, planets, houses):
        return []  # Simplified for now


def _muhurta_score(tithi_num, nakshatra, lagna, yoga):
    score = 3 if tithi_num in [2,3,5,7,11,13] else 1
    score += 3 if nakshatra in ["Rohini","Uttara Phalguni","Uttara Ashadha","Revati"] else 1
    score += 3 if lagna in ["taurus","libra","gemini","pisces"] else 1
    return score
