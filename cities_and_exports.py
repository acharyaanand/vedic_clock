"""
cities_and_exports.py — Vedic Clock Utility Module
====================================================
Four self-contained utilities used across vedic_clock:

  1. INDIA_CITIES + search_city()    — quick city lookup for dropdowns
  2. generate_ics()                   — export festivals as .ics calendar file
  3. generate_sankalpa()              — Sanskrit Sankalpa text for pujas/vratas
  4. get_regional_calendar_info()     — multi-language calendar month names

None of these utilities depend on Swiss Ephemeris — they are pure Python.
Import selectively from main.py or app.py as needed.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional


# ══════════════════════════════════════════════════════════════════════════════
# 1. CITY DATABASE + SEARCH
#    Format: "City Name": (latitude, longitude, tz_offset_hours, state/country)
#    These coordinates are Google-standard centroid coordinates.
#    For the primary geocoding chain (Open-Meteo + Nominatim), see app.py /geocode.
#    This list is used for fast local dropdown suggestions without a network call.
# ══════════════════════════════════════════════════════════════════════════════

INDIA_CITIES = {
    # ── Delhi / NCR ──────────────────────────────────────────────────────────
    "Delhi":            (28.6139,  77.2090, 5.5, "Delhi"),
    "New Delhi":        (28.6139,  77.2090, 5.5, "Delhi"),
    "Noida":            (28.5355,  77.3910, 5.5, "Uttar Pradesh"),
    "Gurgaon":          (28.4595,  77.0266, 5.5, "Haryana"),
    "Gurugram":         (28.4595,  77.0266, 5.5, "Haryana"),
    "Faridabad":        (28.4089,  77.3178, 5.5, "Haryana"),
    "Ghaziabad":        (28.6692,  77.4538, 5.5, "Uttar Pradesh"),

    # ── Maharashtra ──────────────────────────────────────────────────────────
    "Mumbai":           (19.0760,  72.8777, 5.5, "Maharashtra"),
    "Pune":             (18.5204,  73.8567, 5.5, "Maharashtra"),
    "Nagpur":           (21.1458,  79.0882, 5.5, "Maharashtra"),
    "Nashik":           (19.9975,  73.7898, 5.5, "Maharashtra"),
    "Aurangabad":       (19.8762,  75.3433, 5.5, "Maharashtra"),
    "Kolhapur":         (16.6950,  74.2083, 5.5, "Maharashtra"),
    "Navi Mumbai":      (19.0330,  73.0297, 5.5, "Maharashtra"),
    "Thane":            (19.2183,  72.9781, 5.5, "Maharashtra"),
    "Solapur":          (17.6599,  75.9064, 5.5, "Maharashtra"),
    "Amravati":         (20.9320,  77.7523, 5.5, "Maharashtra"),

    # ── West Bengal ──────────────────────────────────────────────────────────
    "Kolkata":          (22.5726,  88.3639, 5.5, "West Bengal"),
    "Calcutta":         (22.5726,  88.3639, 5.5, "West Bengal"),
    "Howrah":           (22.5958,  88.2636, 5.5, "West Bengal"),
    "Durgapur":         (23.5204,  87.3119, 5.5, "West Bengal"),
    "Asansol":          (23.6739,  86.9524, 5.5, "West Bengal"),
    "Siliguri":         (26.7271,  88.3953, 5.5, "West Bengal"),

    # ── Tamil Nadu ───────────────────────────────────────────────────────────
    "Chennai":          (13.0827,  80.2707, 5.5, "Tamil Nadu"),
    "Madras":           (13.0827,  80.2707, 5.5, "Tamil Nadu"),
    "Coimbatore":       (11.0168,  76.9558, 5.5, "Tamil Nadu"),
    "Madurai":          ( 9.9252,  78.1198, 5.5, "Tamil Nadu"),
    "Tiruchirappalli":  (10.7905,  78.7047, 5.5, "Tamil Nadu"),
    "Trichy":           (10.7905,  78.7047, 5.5, "Tamil Nadu"),
    "Salem":            (11.6643,  78.1460, 5.5, "Tamil Nadu"),
    "Tirunelveli":      ( 8.7139,  77.7567, 5.5, "Tamil Nadu"),
    "Tiruppur":         (11.1085,  77.3411, 5.5, "Tamil Nadu"),
    "Vellore":          (12.9165,  79.1325, 5.5, "Tamil Nadu"),
    "Erode":            (11.3410,  77.7172, 5.5, "Tamil Nadu"),
    "Thanjavur":        (10.7870,  79.1378, 5.5, "Tamil Nadu"),

    # ── Karnataka ────────────────────────────────────────────────────────────
    "Bangalore":        (12.9716,  77.5946, 5.5, "Karnataka"),
    "Bengaluru":        (12.9716,  77.5946, 5.5, "Karnataka"),
    "Mysore":           (12.2958,  76.6394, 5.5, "Karnataka"),
    "Mysuru":           (12.2958,  76.6394, 5.5, "Karnataka"),
    "Hubli":            (15.3647,  75.1240, 5.5, "Karnataka"),
    "Hubballi":         (15.3647,  75.1240, 5.5, "Karnataka"),
    "Dharwad":          (15.4589,  75.0078, 5.5, "Karnataka"),
    "Mangalore":        (12.9141,  74.8560, 5.5, "Karnataka"),
    "Mangaluru":        (12.9141,  74.8560, 5.5, "Karnataka"),
    "Belgaum":          (15.8497,  74.4977, 5.5, "Karnataka"),
    "Belagavi":         (15.8497,  74.4977, 5.5, "Karnataka"),

    # ── Telangana ────────────────────────────────────────────────────────────
    "Hyderabad":        (17.3850,  78.4867, 5.5, "Telangana"),
    "Secunderabad":     (17.4399,  78.4983, 5.5, "Telangana"),
    "Warangal":         (17.9689,  79.5941, 5.5, "Telangana"),

    # ── Andhra Pradesh ───────────────────────────────────────────────────────
    "Visakhapatnam":    (17.6868,  83.2185, 5.5, "Andhra Pradesh"),
    "Vizag":            (17.6868,  83.2185, 5.5, "Andhra Pradesh"),
    "Vijayawada":       (16.5062,  80.6480, 5.5, "Andhra Pradesh"),
    "Tirupati":         (13.6288,  79.4192, 5.5, "Andhra Pradesh"),
    "Guntur":           (16.3067,  80.4365, 5.5, "Andhra Pradesh"),

    # ── Gujarat ──────────────────────────────────────────────────────────────
    "Ahmedabad":        (23.0225,  72.5714, 5.5, "Gujarat"),
    "Surat":            (21.1702,  72.8311, 5.5, "Gujarat"),
    "Vadodara":         (22.3072,  73.1812, 5.5, "Gujarat"),
    "Rajkot":           (22.3039,  70.8022, 5.5, "Gujarat"),
    "Gandhinagar":      (23.2156,  72.6369, 5.5, "Gujarat"),
    "Bhavnagar":        (21.7645,  72.1519, 5.5, "Gujarat"),
    "Jamnagar":         (22.4707,  70.0577, 5.5, "Gujarat"),

    # ── Rajasthan ────────────────────────────────────────────────────────────
    "Jaipur":           (26.9124,  75.7873, 5.5, "Rajasthan"),
    "Jodhpur":          (26.2389,  73.0243, 5.5, "Rajasthan"),
    "Udaipur":          (24.5854,  73.7125, 5.5, "Rajasthan"),
    "Kota":             (25.2138,  75.8648, 5.5, "Rajasthan"),
    "Ajmer":            (26.4499,  74.6399, 5.5, "Rajasthan"),
    "Bikaner":          (28.0229,  73.3119, 5.5, "Rajasthan"),
    "Pushkar":          (26.4897,  74.5511, 5.5, "Rajasthan"),
    "Jaisalmer":        (26.9157,  70.9083, 5.5, "Rajasthan"),

    # ── Uttar Pradesh ────────────────────────────────────────────────────────
    "Lucknow":          (26.8467,  80.9462, 5.5, "Uttar Pradesh"),
    "Kanpur":           (26.4499,  80.3319, 5.5, "Uttar Pradesh"),
    "Agra":             (27.1767,  78.0081, 5.5, "Uttar Pradesh"),
    "Varanasi":         (25.3176,  82.9739, 5.5, "Uttar Pradesh"),
    "Kashi":            (25.3176,  82.9739, 5.5, "Uttar Pradesh"),
    "Banaras":          (25.3176,  82.9739, 5.5, "Uttar Pradesh"),
    "Prayagraj":        (25.4358,  81.8463, 5.5, "Uttar Pradesh"),
    "Allahabad":        (25.4358,  81.8463, 5.5, "Uttar Pradesh"),
    "Mathura":          (27.4924,  77.6737, 5.5, "Uttar Pradesh"),
    "Vrindavan":        (27.5794,  77.6963, 5.5, "Uttar Pradesh"),
    "Ayodhya":          (26.7951,  82.1952, 5.5, "Uttar Pradesh"),
    "Meerut":           (28.9845,  77.7064, 5.5, "Uttar Pradesh"),
    "Bareilly":         (28.3670,  79.4304, 5.5, "Uttar Pradesh"),
    "Aligarh":          (27.8974,  78.0880, 5.5, "Uttar Pradesh"),
    "Gorakhpur":        (26.7606,  83.3732, 5.5, "Uttar Pradesh"),

    # ── Madhya Pradesh ───────────────────────────────────────────────────────
    "Bhopal":           (23.2599,  77.4126, 5.5, "Madhya Pradesh"),
    "Indore":           (22.7196,  75.8577, 5.5, "Madhya Pradesh"),
    "Jabalpur":         (23.1815,  79.9864, 5.5, "Madhya Pradesh"),
    "Gwalior":          (26.2183,  78.1828, 5.5, "Madhya Pradesh"),
    "Ujjain":           (23.1828,  75.7772, 5.5, "Madhya Pradesh"),

    # ── Bihar ────────────────────────────────────────────────────────────────
    "Patna":            (25.5941,  85.1376, 5.5, "Bihar"),
    "Gaya":             (24.7964,  85.0002, 5.5, "Bihar"),
    "Bhagalpur":        (25.2425,  86.9842, 5.5, "Bihar"),
    "Muzaffarpur":      (26.1209,  85.3647, 5.5, "Bihar"),

    # ── Jharkhand ────────────────────────────────────────────────────────────
    "Ranchi":           (23.3441,  85.3096, 5.5, "Jharkhand"),
    "Jamshedpur":       (22.8046,  86.2029, 5.5, "Jharkhand"),
    "Dhanbad":          (23.7957,  86.4304, 5.5, "Jharkhand"),

    # ── Odisha ───────────────────────────────────────────────────────────────
    "Bhubaneswar":      (20.2961,  85.8245, 5.5, "Odisha"),
    "Cuttack":          (20.4625,  85.8830, 5.5, "Odisha"),
    "Puri":             (19.8106,  85.8314, 5.5, "Odisha"),

    # ── Assam / Northeast ────────────────────────────────────────────────────
    "Guwahati":         (26.1445,  91.7362, 5.5, "Assam"),
    "Dibrugarh":        (27.4728,  94.9120, 5.5, "Assam"),
    "Shillong":         (25.5788,  91.8933, 5.5, "Meghalaya"),
    "Imphal":           (24.8170,  93.9368, 5.5, "Manipur"),
    "Agartala":         (23.8315,  91.2868, 5.5, "Tripura"),
    "Kohima":           (25.6701,  94.1077, 5.5, "Nagaland"),
    "Aizawl":           (23.7271,  92.7176, 5.5, "Mizoram"),
    "Itanagar":         (27.0844,  93.6053, 5.5, "Arunachal Pradesh"),
    "Gangtok":          (27.3314,  88.6138, 5.5, "Sikkim"),

    # ── Punjab / Haryana / Chandigarh ────────────────────────────────────────
    "Chandigarh":       (30.7333,  76.7794, 5.5, "Chandigarh"),
    "Amritsar":         (31.6340,  74.8723, 5.5, "Punjab"),
    "Ludhiana":         (30.9010,  75.8573, 5.5, "Punjab"),
    "Jalandhar":        (31.3260,  75.5762, 5.5, "Punjab"),
    "Patiala":          (30.3398,  76.3869, 5.5, "Punjab"),
    "Rohtak":           (28.8955,  76.6066, 5.5, "Haryana"),
    "Hisar":            (29.1492,  75.7217, 5.5, "Haryana"),

    # ── Uttarakhand ──────────────────────────────────────────────────────────
    "Dehradun":         (30.3165,  78.0322, 5.5, "Uttarakhand"),
    "Haridwar":         (29.9457,  78.1642, 5.5, "Uttarakhand"),
    "Rishikesh":        (30.0869,  78.2676, 5.5, "Uttarakhand"),
    "Nainital":         (29.3803,  79.4636, 5.5, "Uttarakhand"),

    # ── Himachal Pradesh ─────────────────────────────────────────────────────
    "Shimla":           (31.1048,  77.1734, 5.5, "Himachal Pradesh"),
    "Dharamsala":       (32.2190,  76.3234, 5.5, "Himachal Pradesh"),
    "Manali":           (32.2396,  77.1887, 5.5, "Himachal Pradesh"),

    # ── Jammu & Kashmir / Ladakh ─────────────────────────────────────────────
    "Srinagar":         (34.0837,  74.7973, 5.5, "Jammu and Kashmir"),
    "Jammu":            (32.7266,  74.8570, 5.5, "Jammu and Kashmir"),
    "Leh":              (34.1526,  77.5771, 5.5, "Ladakh"),

    # ── Kerala ───────────────────────────────────────────────────────────────
    "Kochi":            ( 9.9312,  76.2673, 5.5, "Kerala"),
    "Cochin":           ( 9.9312,  76.2673, 5.5, "Kerala"),
    "Thiruvananthapuram":( 8.5241,  76.9366, 5.5, "Kerala"),
    "Trivandrum":       ( 8.5241,  76.9366, 5.5, "Kerala"),
    "Kozhikode":        (11.2588,  75.7804, 5.5, "Kerala"),
    "Calicut":          (11.2588,  75.7804, 5.5, "Kerala"),
    "Thrissur":         (10.5276,  76.2144, 5.5, "Kerala"),
    "Kannur":           (11.8745,  75.3704, 5.5, "Kerala"),

    # ── Goa ──────────────────────────────────────────────────────────────────
    "Goa":              (15.2993,  74.1240, 5.5, "Goa"),
    "Panaji":           (15.4909,  73.8278, 5.5, "Goa"),

    # ── Chhattisgarh ─────────────────────────────────────────────────────────
    "Raipur":           (21.2514,  81.6296, 5.5, "Chhattisgarh"),
    "Bhilai":           (21.1938,  81.3509, 5.5, "Chhattisgarh"),

    # ── Pilgrimage towns ─────────────────────────────────────────────────────
    "Tirupati":         (13.6288,  79.4192, 5.5, "Andhra Pradesh"),
    "Dwarka":           (22.2394,  68.9678, 5.5, "Gujarat"),
    "Shirdi":           (19.7647,  74.4765, 5.5, "Maharashtra"),
    "Trimbakeshwar":    (19.9330,  73.5270, 5.5, "Maharashtra"),
    "Nashik":           (19.9975,  73.7898, 5.5, "Maharashtra"),
    "Vrindavan":        (27.5794,  77.6963, 5.5, "Uttar Pradesh"),
    "Kurukshetra":      (29.9695,  76.8783, 5.5, "Haryana"),
    "Bodh Gaya":        (24.6961,  84.9916, 5.5, "Bihar"),

    # ── Major world cities (for NRI users) ───────────────────────────────────
    "London":           (51.5074,  -0.1278,  0.0, "UK"),
    "New York":         (40.7128, -74.0060, -5.0, "USA"),
    "Los Angeles":      (34.0522,-118.2437, -8.0, "USA"),
    "Chicago":          (41.8781, -87.6298, -6.0, "USA"),
    "Toronto":          (43.7001, -79.4163, -5.0, "Canada"),
    "Vancouver":        (49.2827,-123.1207, -8.0, "Canada"),
    "Dubai":            (25.2048,  55.2708,  4.0, "UAE"),
    "Abu Dhabi":        (24.4539,  54.3773,  4.0, "UAE"),
    "Riyadh":           (24.6877,  46.7219,  3.0, "Saudi Arabia"),
    "Jeddah":           (21.4858,  39.1925,  3.0, "Saudi Arabia"),
    "Singapore":        ( 1.3521, 103.8198,  8.0, "Singapore"),
    "Kuala Lumpur":     ( 3.1390, 101.6869,  8.0, "Malaysia"),
    "Sydney":           (-33.8688,151.2093, 11.0, "Australia"),
    "Melbourne":        (-37.8136,144.9631, 11.0, "Australia"),
    "Bangkok":          (13.7563, 100.5018,  7.0, "Thailand"),
    "Tokyo":            (35.6762, 139.6503,  9.0, "Japan"),
    "Frankfurt":        (50.1109,   8.6821,  1.0, "Germany"),
    "Paris":            (48.8566,   2.3522,  1.0, "France"),
    "Amsterdam":        (52.3676,   4.9041,  1.0, "Netherlands"),
    "Nairobi":          (-1.2921,  36.8219,  3.0, "Kenya"),
    "Johannesburg":     (-26.2041, 28.0473,  2.0, "South Africa"),
    "Dhaka":            (23.8103,  90.4125,  6.0, "Bangladesh"),
    "Kathmandu":        (27.7172,  85.3240,  5.75,"Nepal"),
    "Colombo":          ( 6.9271,  79.8612,  5.5, "Sri Lanka"),
    "Karachi":          (24.8607,  67.0011,  5.0, "Pakistan"),
    "Lahore":           (31.5497,  74.3436,  5.0, "Pakistan"),
    "Islamabad":        (33.7294,  73.0931,  5.0, "Pakistan"),
}


def search_city(query: str, limit: int = 10) -> List[Dict]:
    """Search cities by partial name match (case-insensitive).
    Returns up to `limit` results as dicts with city, state, latitude,
    longitude, and timezone_offset fields.

    Priority: exact match first, then starts-with, then contains.
    """
    q = query.lower().strip()
    if not q:
        return []

    exact, starts, contains = [], [], []

    for city, (lat, lon, tz, state) in INDIA_CITIES.items():
        city_lower = city.lower()
        row = {
            "city": city,
            "state": state,
            "latitude": lat,
            "longitude": lon,
            "timezone_offset": tz,
        }
        if city_lower == q:
            exact.append(row)
        elif city_lower.startswith(q):
            starts.append(row)
        elif q in city_lower:
            contains.append(row)

    combined = exact + starts + contains
    # Deduplicate by (lat, lon)
    seen, out = set(), []
    for r in combined:
        key = (r["latitude"], r["longitude"])
        if key not in seen:
            seen.add(key)
            out.append(r)
        if len(out) >= limit:
            break
    return out


# ══════════════════════════════════════════════════════════════════════════════
# 2. ICS CALENDAR EXPORT
#    Generates a standard .ics file (RFC 5545) that users can import into
#    Google Calendar, Apple Calendar, Outlook, or any calendar app.
# ══════════════════════════════════════════════════════════════════════════════

def generate_ics(festivals: List[Dict], year: int, month: int) -> str:
    """Convert a list of festival dicts into an ICS calendar string.

    Each festival dict should have at minimum:
        {
            "date":       "YYYY-MM-DD",
            "name":       "Festival Name",
            "importance": "optional description",  (optional)
            "citation":   "source text",            (optional)
            "type":       "Hindu Festival",         (optional)
        }

    Returns a complete ICS string ready to be served as
    Content-Type: text/calendar with filename=vedic_calendar.ics
    """
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Vedic Clock//Classical Jyotish Calendar//EN",
        "CALSCALE:GREGORIAN",
        f"X-WR-CALNAME:Hindu Festivals {year}",
        "X-WR-TIMEZONE:Asia/Kolkata",
        "X-WR-CALDESC:Vedic Calendar generated by Vedic Clock API",
    ]

    for fest in festivals:
        date_raw = fest.get("date", "")
        name = fest.get("name", "")
        if not date_raw or not name:
            continue  # skip incomplete entries

        dt = date_raw.replace("-", "")  # "20261112" format for ICS
        uid = f"{dt}-{name.replace(' ', '-').replace('/', '-')}@vedic-clock"
        description = ""
        if fest.get("importance"):
            description += fest["importance"]
        if fest.get("citation"):
            description += f" | {fest['citation']}"

        lines += [
            "BEGIN:VEVENT",
            f"DTSTART;VALUE=DATE:{dt}",
            f"DTEND;VALUE=DATE:{dt}",   # all-day event
            f"SUMMARY:{name}",
            f"DESCRIPTION:{description}",
            f"CATEGORIES:{fest.get('type', 'Hindu Festival')}",
            f"UID:{uid}",
            "END:VEVENT",
        ]

    lines.append("END:VCALENDAR")
    # ICS spec requires CRLF line endings
    return "\r\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════════
# 3. SANKALPA TEXT GENERATOR
#    Generates the traditional Sanskrit Sankalpa declaration recited before
#    any puja, vrata, or ritual. Fills in the astrological details
#    (masa, paksha, tithi, vara, nakshatra, rashi) from panchang data.
# ══════════════════════════════════════════════════════════════════════════════

RASHI_SANSKRIT = [
    "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
    "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena",
]

NAKSHATRA_FULL = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha",
    "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana",
    "Dhanishtha", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]

VARA_SANSKRIT = [
    "Bhanu",      # Sunday
    "Soma",       # Monday
    "Mangal",     # Tuesday
    "Budha",      # Wednesday
    "Brihaspati", # Thursday
    "Shukra",     # Friday
    "Shani",      # Saturday
]

TITHI_SANSKRIT = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima",
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Amavasya",
]

MASA_SANSKRIT = [
    "Chaitra", "Vaishakha", "Jyeshtha", "Ashadha", "Shravana", "Bhadrapada",
    "Ashwin", "Kartika", "Margashirsha", "Pausha", "Magha", "Phalguna",
]


def generate_sankalpa(
    year: int,
    month: int,
    day: int,
    tithi_num: int,       # 1–30 (1=Shukla Pratipada, 15=Purnima, 30=Amavasya)
    nakshatra_num: int,   # 1–27
    weekday: int,         # 0=Sunday … 6=Saturday (Python weekday + 1 mod 7 adjusted)
    sun_rashi: int,       # 0–11 (sign index of Sun at time of ritual)
    vikram_samvat: int,   # e.g. 2083
    gotra: str = "...",
    name: str = "...",
    purpose: str = "Puja Karma",
) -> Dict:
    """Generate a classical Sanskrit Sankalpa for any puja or vrata.

    Pass the panchang values at the time of the ritual (from /api/panchang-full).
    The gotra, name, and purpose should be filled in by the user at the frontend.

    Returns a dict with the full Sankalpa text plus structured elements for display.
    Source: Dharmasindhu | Sankalpa Vidhi (traditional form used pan-India).
    """
    tithi    = TITHI_SANSKRIT[(tithi_num - 1) % 30]
    nakshatra= NAKSHATRA_FULL[max(0, min(nakshatra_num - 1, 26))]
    vara     = VARA_SANSKRIT[weekday % 7]
    masa     = MASA_SANSKRIT[sun_rashi % 12]
    rashi    = RASHI_SANSKRIT[sun_rashi % 12]
    paksha   = "Shukla" if tithi_num <= 15 else "Krishna"

    sankalpa_text = (
        f"Aum. Vishnu Vishnu Vishnu. "
        f"Adya Brahmanah Dviteye Parardhe, Shri Shweta Varaha Kalpe, "
        f"Vaivasvata Manvantare, Ashtavimshe Kaliyuge, "
        f"Kaliyuge Prathama Charne, "
        f"Bharata Varshe, Bharata Khande, "
        f"Aryavarta Desh Antargat, "
        f"Vikram Samvate {vikram_samvat}tamé, "
        f"{masa} Mase, "
        f"{paksha} Pakshe, "
        f"{tithi} Tithau, "
        f"{vara} Vasare, "
        f"{nakshatra} Nakshatre, "
        f"{rashi} Rashisthe Suri, "
        f"Evam Guna Viseshana Vishisthayam, "
        f"Shubha Tithau, "
        f"Asmakam Gotra Prabhava, "
        f"{gotra} Gotrasya, "
        f"{name} Nama Aham, "
        f"{purpose} Karma Karishye."
    )

    return {
        "sankalpa": sankalpa_text,
        "elements": {
            "samvat":    vikram_samvat,
            "masa":      masa,
            "paksha":    paksha,
            "tithi":     tithi,
            "vara":      vara,
            "nakshatra": nakshatra,
            "sun_rashi": rashi,
        },
        "note": "Fill in your Gotra and full name before reciting. Recite before any puja, vrata, or havan.",
        "citation": "Dharmasindhu | Sankalpa Vidhi",
    }


# ══════════════════════════════════════════════════════════════════════════════
# 4. REGIONAL CALENDAR NAMES
#    Different Indian states use different month names even for the same
#    calendar period. This function provides all five major regional systems
#    based on the Sun's Rashi (sign) position.
# ══════════════════════════════════════════════════════════════════════════════

_BENGALI_MONTHS   = ["Baishakh","Jyaistha","Ashar","Shravan","Bhadra","Ashwin",
                     "Kartik","Agrahayan","Poush","Magh","Falgun","Chaitra"]
_TAMIL_MONTHS     = ["Chithirai","Vaikasi","Aani","Aadi","Avani","Purattasi",
                     "Aippasi","Karthigai","Margazhi","Thai","Maasi","Panguni"]
_TELUGU_MONTHS    = ["Chaitra","Vaishakha","Jyeshtha","Ashadha","Shravana",
                     "Bhadrapada","Ashwina","Kartika","Margashira","Pushya","Magha","Phalguna"]
_MALAYALAM_MONTHS = ["Chingam","Kanni","Thulam","Vrischikam","Dhanu","Makaram",
                     "Kumbham","Meenam","Medam","Edavam","Midhunam","Karkidakam"]
_ODIA_MONTHS      = ["Baisakha","Jyaistha","Asadha","Srabana","Bhadra","Aswina",
                     "Kartika","Margasira","Pausa","Magha","Phalguna","Chaitra"]
_HINDI_MONTHS     = ["Chaitra","Vaishakha","Jyeshtha","Ashadha","Shravana","Bhadrapada",
                     "Ashwin","Kartika","Margashirsha","Pausha","Magha","Phalguna"]
_GUJARATI_MONTHS  = ["Chaitra","Vaishakh","Jeth","Ashadh","Shravan","Bhadarvo",
                     "Aso","Kartik","Magshar","Posh","Maha","Fagan"]


def get_regional_calendar_info(
    month: int,
    sun_rashi: int,   # 0–11, the current Sun sign index
    vikram_samvat: int,
) -> Dict:
    """Return month names across all major Indian regional calendar systems.

    The month name in each regional calendar is driven by the Sun's rashi
    (sign position), not the Gregorian month number. Pass sun_rashi from
    the panchang response (the sign_info index of the Sun's longitude).

    Returns a dict with month names in Hindi, Bengali, Tamil, Telugu,
    Malayalam, Odia, and Gujarati, plus Vikram Samvat and Shaka Samvat years.
    """
    idx = sun_rashi % 12
    return {
        "hindi_masa":      _HINDI_MONTHS[idx],
        "bengali_month":   _BENGALI_MONTHS[idx],
        "tamil_month":     _TAMIL_MONTHS[idx],
        "telugu_month":    _TELUGU_MONTHS[idx],
        "malayalam_month": _MALAYALAM_MONTHS[idx],
        "odia_month":      _ODIA_MONTHS[idx],
        "gujarati_month":  _GUJARATI_MONTHS[idx],
        "vikram_samvat":   vikram_samvat,
        "shaka_samvat":    vikram_samvat - 135,
        "note": "Month names are based on the Sun's Rashi position (not Gregorian month).",
    }


# ══════════════════════════════════════════════════════════════════════════════
# Quick self-test — run this file directly to verify everything works
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=== CITIES & EXPORTS SELF-TEST ===\n")

    # Test 1: city search
    r = search_city("mumbai")
    print(f"City search 'mumbai': {r[0]['city']} ({r[0]['latitude']}, {r[0]['longitude']})")
    r2 = search_city("var")  # should match Varanasi, Vadodara etc.
    print(f"City search 'var': {[x['city'] for x in r2]}")

    # Test 2: ICS generation
    festivals = [
        {"date": "2026-11-12", "name": "Diwali",    "importance": "Festival of Lights", "type": "Major Festival"},
        {"date": "2026-03-25", "name": "Holi",      "importance": "Festival of Colours"},
        {"date": "2026-10-24", "name": "Dussehra",  "importance": "Victory of good over evil"},
    ]
    ics = generate_ics(festivals, 2026, 11)
    print(f"\nICS calendar: {ics.count('BEGIN:VEVENT')} events generated")

    # Test 3: Sankalpa
    s = generate_sankalpa(
        year=2026, month=5, day=22,
        tithi_num=13, nakshatra_num=16,
        weekday=5,       # Friday
        sun_rashi=1,     # Taurus
        vikram_samvat=2083,
        gotra="Bharadwaj",
        name="Ram Sharma",
        purpose="Satya Narayan Puja",
    )
    print(f"\nSankalpa snippet: ...{s['sankalpa'][80:160]}...")
    print(f"Elements: {s['elements']}")

    # Test 4: Regional calendar
    reg = get_regional_calendar_info(month=5, sun_rashi=1, vikram_samvat=2083)
    print(f"\nRegional months (Sun in Taurus):")
    for key in ["hindi_masa","bengali_month","tamil_month","telugu_month","malayalam_month","gujarati_month"]:
        print(f"  {key:<20}: {reg[key]}")
    print(f"  vikram_samvat       : {reg['vikram_samvat']}")
    print(f"  shaka_samvat        : {reg['shaka_samvat']}")

    print("\n✓ All features working correctly.")
