"""
AETHERIS — AetherisEngine
Swiss Ephemeris based planetary calculation engine.
Handles planet positions, houses, panchanga, muhurta.
"""
import math
import swisseph as swe
from typing import Dict, List
from datetime import datetime, timedelta
import redis.asyncio as redis
import json
import os

redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
CACHE_TTL = 3600

SIGNS = ["aries","taurus","gemini","cancer","leo","virgo",
         "libra","scorpio","sagittarius","capricorn","aquarius","pisces"]

NAKSHATRAS_LIST = [
    "Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
    "Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni",
    "Uttara Phalguni","Hasta","Chitra","Swati","Vishakha","Anuradha",
    "Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha","Shravana",
    "Dhanishtha","Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati"
]

# Good nakshatras for marriage muhurta
# Source: BPHS Vivaha Adhyaya | Parashara | Shloka 7
GOOD_MARRIAGE_NAKSHATRAS = [
    "Rohini","Mrigashira","Magha","Uttara Phalguni","Hasta","Swati",
    "Anuradha","Uttara Ashadha","Shravana","Revati","Uttara Bhadrapada"
]

GOOD_MARRIAGE_LAGNAS = ["taurus","gemini","cancer","libra","sagittarius","pisces"]

# Good tithis for marriage (tithi numbers 1-based)
# Source: Muhurta Chintamani | Marriage Chapter | Shloka 3
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


class AetherisEngine:
    """
    Core calculation engine using Swiss Ephemeris.
    All calculations use Lahiri Ayanamsa (default) as per Parashara tradition.
    """

    def __init__(self, birth_details):
        self.details = birth_details
        self.jd = swe.julday(
            birth_details.year,
            birth_details.month,
            birth_details.day,
            birth_details.hour + birth_details.minute / 60.0 + birth_details.second / 3600.0
        )
        self.lat = birth_details.latitude
        self.lon = birth_details.longitude
        self.ayanamsa = self._ayanamsa_code(birth_details.ayanamsa)
        self.house_sys = self._house_code(birth_details.house_system)
        swe.set_sid_mode(self.ayanamsa)

        # Set ephemeris path if provided
        ephe_path = os.getenv("SWISSEPH_PATH", "./ephe/")
        if os.path.exists(ephe_path):
            swe.set_ephe_path(ephe_path)

    def _ayanamsa_code(self, name: str) -> int:
        mapping = {
            "lahiri": swe.SIDM_LAHIRI,
            "raman":  swe.SIDM_RAMAN,
            "kp":     swe.SIDM_KP
        }
        return mapping.get(name.lower(), swe.SIDM_LAHIRI)

    def _house_code(self, name: str) -> bytes:
        mapping = {
            "placidus":      b'P',
            "koch":          b'K',
            "regiomontanus": b'R',
            "equal":         b'E',
            "whole_sign":    b'W'
        }
        return mapping.get(name.lower(), b'P')

    async def get_planet_positions(self) -> Dict:
        """
        Calculate sidereal planetary positions using Swiss Ephemeris.
        Returns longitude, latitude, speed, nakshatra, pada for all planets.
        """
        cache_key = f"planets:{self.jd}:{self.ayanamsa}"
        try:
            cached = await redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception:
            pass  # Redis unavailable — continue without cache

        planets = {}
        bodies = [
            (swe.SUN,       "sun"),
            (swe.MOON,      "moon"),
            (swe.MERCURY,   "mercury"),
            (swe.VENUS,     "venus"),
            (swe.MARS,      "mars"),
            (swe.JUPITER,   "jupiter"),
            (swe.SATURN,    "saturn"),
            (swe.URANUS,    "uranus"),
            (swe.NEPTUNE,   "neptune"),
            (swe.PLUTO,     "pluto"),
            (swe.MEAN_NODE, "mean_node"),   # Rahu
            (swe.TRUE_NODE, "true_node"),   # True Rahu
        ]

        for code, name in bodies:
            try:
                pos, _ = swe.calc_ut(self.jd, code, swe.FLG_SIDEREAL | swe.FLG_SPEED)
                lon = pos[0] % 360
                planets[name] = {
                    "name": name,
                    "longitude": round(lon, 6),
                    "latitude": round(pos[1], 6),
                    "distance": round(pos[2], 6),
                    "speed_long": round(pos[3], 6),
                    "sign": self._sign_name(lon),
                    "degree": round(lon % 30, 4),
                    "nakshatra": self._nakshatra(lon),
                    "nakshatra_number": self._nakshatra_number(lon),
                    "nakshatra_pada": self._nakshatra_pada(lon),
                    "is_retrograde": pos[3] < 0,
                }
            except Exception as e:
                continue

        # Add Ketu (always 180° from Rahu)
        if "mean_node" in planets:
            rahu_lon = planets["mean_node"]["longitude"]
            ketu_lon = (rahu_lon + 180) % 360
            planets["ketu"] = {
                "name": "ketu",
                "longitude": round(ketu_lon, 6),
                "sign": self._sign_name(ketu_lon),
                "degree": round(ketu_lon % 30, 4),
                "nakshatra": self._nakshatra(ketu_lon),
                "nakshatra_number": self._nakshatra_number(ketu_lon),
                "nakshatra_pada": self._nakshatra_pada(ketu_lon),
                "is_retrograde": True,  # Ketu always retrograde
                "speed_long": -1.0,
            }

        # Ascendant and MC
        try:
            houses_raw, ascmc = swe.houses_ex(
                self.jd, self.lat, self.lon, self.house_sys,
                swe.FLG_SIDEREAL
            )
            asc_lon = ascmc[0] % 360
            mc_lon = ascmc[1] % 360
            planets["ascendant"] = {
                "name": "ascendant",
                "longitude": round(asc_lon, 6),
                "sign": self._sign_name(asc_lon),
                "degree": round(asc_lon % 30, 4),
            }
            planets["midheaven"] = {
                "name": "midheaven",
                "longitude": round(mc_lon, 6),
                "sign": self._sign_name(mc_lon),
                "degree": round(mc_lon % 30, 4),
            }
        except Exception:
            pass

        try:
            await redis_client.setex(cache_key, CACHE_TTL, json.dumps(planets))
        except Exception:
            pass

        return planets

    async def get_houses(self, planets: Dict) -> Dict:
        """
        Calculate 12 house cusps and assign planets to houses.
        """
        try:
            houses_raw, ascmc = swe.houses_ex(
                self.jd, self.lat, self.lon, self.house_sys,
                swe.FLG_SIDEREAL
            )
        except Exception:
            # Fallback to whole sign if calculation fails
            asc_lon = planets.get("ascendant", {}).get("longitude", 0)
            lagna_sign_idx = int(asc_lon / 30)
            houses_raw = [((lagna_sign_idx + i) * 30) % 360 for i in range(12)]
            houses_raw.append(houses_raw[0])  # close the circle

        houses = {}
        for i in range(12):
            cusp = houses_raw[i] % 360
            houses[i + 1] = {
                "cusp": round(cusp, 4),
                "sign": self._sign_name(cusp),
                "degree": round(cusp % 30, 4),
                "planets": []
            }

        # Assign planets to houses
        skip = ["ascendant", "midheaven", "true_node"]
        for pname, pdata in planets.items():
            if pname in skip:
                continue
            lon = pdata.get("longitude", 0)
            house_num = self._longitude_to_house(lon, houses)
            if house_num:
                houses[house_num]["planets"].append(pname)

        return houses

    def _longitude_to_house(self, lon: float, houses: Dict) -> int:
        """Find which house a longitude falls in."""
        for hnum in range(1, 13):
            cur_cusp = houses[hnum]["cusp"]
            next_cusp = houses[(hnum % 12) + 1]["cusp"]

            if cur_cusp <= next_cusp:
                if cur_cusp <= lon < next_cusp:
                    return hnum
            else:  # Crosses 0°
                if lon >= cur_cusp or lon < next_cusp:
                    return hnum
        return 1

    async def get_panchanga(self, sun_lon: float, moon_lon: float) -> Dict:
        """
        Calculate Panchanga — five limbs of the day.
        Source: BPHS Panchanga Adhyaya (Parashara)
        """
        # 1. Tithi — Moon's distance from Sun in multiples of 12°
        diff = (moon_lon - sun_lon) % 360
        tithi_num = int(diff / 12)  # 0-29
        tithi_name = TITHI_NAMES[tithi_num % 30]
        paksha = "Shukla Paksha" if tithi_num < 15 else "Krishna Paksha"

        # 2. Vara (Weekday)
        weekday = int((self.jd + 1.5) % 7)
        vaara = VAARA_NAMES[weekday]

        # 3. Nakshatra (Moon's Nakshatra)
        nakshatra = self._nakshatra(moon_lon)
        nak_pada = self._nakshatra_pada(moon_lon)

        # 4. Yoga — Sun + Moon longitude / (360/27)
        yoga_sum = (sun_lon + moon_lon) % 360
        yoga_idx = int(yoga_sum / (360 / 27)) % 27
        yoga = YOGA_NAMES[yoga_idx]
        is_good_yoga = yoga not in ["Vishkumbha","Atiganda","Shoola","Ganda",
                                     "Vyaghata","Vajra","Vyatipata","Parigha","Vaidhriti"]

        # 5. Karana — half-tithi
        karana_idx = int(diff / 6) % 11
        karana = KARANA_NAMES[karana_idx]

        return {
            "tithi": {
                "name": tithi_name,
                "number": tithi_num + 1,
                "paksha": paksha,
                "citation": "BPHS Panchanga Adhyaya | Parashara"
            },
            "vaara": {
                "name": vaara,
                "number": weekday + 1,
            },
            "nakshatra": {
                "name": nakshatra,
                "pada": nak_pada,
                "moon_longitude": round(moon_lon, 4),
            },
            "yoga": {
                "name": yoga,
                "is_auspicious": is_good_yoga,
                "citation": "BPHS Panchanga Adhyaya | Parashara"
            },
            "karana": {
                "name": karana,
            }
        }

    async def find_marriage_muhurtas(self, year: int, month: int,
                                      planets: Dict, houses: Dict) -> List[Dict]:
        """
        Find auspicious marriage dates using classical Muhurta rules.
        Source: BPHS Vivaha Adhyaya | Parashara | Shloka 7-12
                Muhurta Chintamani | Marriage Chapter | Shloka 3-11
        """
        good_dates = []
        try:
            start = datetime(year, month, 1)
            if month == 12:
                end = datetime(year + 1, 1, 1) - timedelta(days=1)
            else:
                end = datetime(year, month + 1, 1) - timedelta(days=1)
        except ValueError:
            return []

        for day in range(start.day, end.day + 1):
            try:
                jd_noon = swe.julday(year, month, day, 12.0)
                swe.set_sid_mode(self.ayanamsa)

                sun_pos, _ = swe.calc_ut(jd_noon, swe.SUN, swe.FLG_SIDEREAL)
                moon_pos, _ = swe.calc_ut(jd_noon, swe.MOON, swe.FLG_SIDEREAL)
                sun_lon = sun_pos[0] % 360
                moon_lon = moon_pos[0] % 360

                # Tithi check
                diff = (moon_lon - sun_lon) % 360
                tithi_num = int(diff / 12) + 1  # 1-30
                tithi_name = TITHI_NAMES[(tithi_num - 1) % 30]
                if tithi_num not in GOOD_MARRIAGE_TITHIS:
                    continue

                # Nakshatra check
                nakshatra = self._nakshatra(moon_lon)
                if nakshatra not in GOOD_MARRIAGE_NAKSHATRAS:
                    continue

                # Lagna check (using noon ascendant as approximation)
                try:
                    h_raw, _ = swe.houses_ex(
                        jd_noon, self.lat, self.lon, self.house_sys, swe.FLG_SIDEREAL
                    )
                    lagna_lon = h_raw[0] % 360
                    lagna_sign = self._sign_name(lagna_lon)
                except Exception:
                    lagna_sign = "unknown"

                if lagna_sign not in GOOD_MARRIAGE_LAGNAS:
                    continue

                # Yoga check
                yoga_sum = (sun_lon + moon_lon) % 360
                yoga_idx = int(yoga_sum / (360 / 27)) % 27
                yoga = YOGA_NAMES[yoga_idx]
                bad_yogas = ["Vishkumbha","Atiganda","Shoola","Ganda",
                             "Vyaghata","Vajra","Vyatipata","Parigha","Vaidhriti"]
                if yoga in bad_yogas:
                    continue

                weekday = int((jd_noon + 1.5) % 7)
                vaara = VAARA_NAMES[weekday]

                good_dates.append({
                    "date": f"{year}-{month:02d}-{day:02d}",
                    "day": vaara,
                    "tithi": tithi_name,
                    "nakshatra": nakshatra,
                    "yoga": yoga,
                    "lagna": lagna_sign.capitalize(),
                    "score": _muhurta_score(tithi_num, nakshatra, lagna_sign, yoga),
                    "rules_satisfied": [
                        f"Tithi: {tithi_name} — BPHS Vivaha Adhyaya Sl.7",
                        f"Nakshatra: {nakshatra} — BPHS Vivaha Adhyaya Sl.7",
                        f"Lagna: {lagna_sign.capitalize()} — Muhurta Chintamani Sl.10",
                        f"Yoga: {yoga} (auspicious) — classical Muhurta rule"
                    ]
                })

            except Exception:
                continue

        # Sort by score — best dates first
        good_dates.sort(key=lambda x: x["score"], reverse=True)
        return good_dates[:10]  # Return top 10

    # ── Helper Methods ──────────────────────────────────
    def _sign_name(self, lon: float) -> str:
        return SIGNS[int(lon / 30) % 12]

    def _nakshatra(self, lon: float) -> str:
        return NAKSHATRAS_LIST[int((lon * 27) / 360) % 27]

    def _nakshatra_number(self, lon: float) -> int:
        return int((lon * 27) / 360) % 27 + 1

    def _nakshatra_pada(self, lon: float) -> int:
        star_len = 360 / 27
        star_idx = int((lon * 27) / 360) % 27
        star_start = star_idx * star_len
        return int((lon - star_start) / (star_len / 4)) + 1


def _muhurta_score(tithi_num: int, nakshatra: str, lagna: str, yoga: str) -> int:
    """Score a muhurta date — higher is better."""
    score = 0

    # Best tithis get higher score
    best_tithis = [2, 3, 5, 7, 11, 13]
    if tithi_num in best_tithis:
        score += 3
    else:
        score += 1

    # Best nakshatras
    best_nakshatras = ["Rohini","Uttara Phalguni","Uttara Ashadha",
                        "Uttara Bhadrapada","Shravana","Revati"]
    if nakshatra in best_nakshatras:
        score += 3
    else:
        score += 1

    # Best lagnas
    best_lagnas = ["taurus","libra","gemini","pisces"]
    if lagna in best_lagnas:
        score += 3
    else:
        score += 1

    # Best yogas
    best_yogas = ["Siddhi","Shubha","Siddha","Sadhya","Priti","Ayushman","Vriddhi"]
    if yoga in best_yogas:
        score += 2

    return score
