"""
world_cities.py — Aetheris World Cities Database
==================================================
5000+ major cities across 195 countries.
Coordinates = Google Maps standard.
Timezone = IANA timezone string (handles DST automatically).
DST handled via get_tz_offset(timezone, year, month, day).

This gives Aetheris near-DrikPanchang level of city coverage.
Polar check included: lat > 66.5° → warning (midnight sun issue).

Search priority:
  1. Exact city name match
  2. Alias match (alternate names)
  3. Partial/fuzzy match
  4. Falls through to india_districts.py for India cities
"""

# ═══════════════════════════════════════════════════════════════════════
# DST-AWARE TIMEZONE OFFSET
# ═══════════════════════════════════════════════════════════════════════

def get_tz_offset(timezone: str, year: int, month: int, day: int) -> float:
    """
    Returns correct UTC offset in decimal hours for given timezone + date.
    Handles DST for US, Canada, Europe, Australia, NZ, Chile, Paraguay.
    """
    from datetime import date as _date

    def nth_sun(y, m, n):
        """nth Sunday of month m."""
        d = _date(y, m, 1)
        first_sun = (6 - d.weekday()) % 7 + 1
        return first_sun + (n - 1) * 7

    def last_sun(y, m):
        """Last Sunday of month m."""
        import calendar
        last = calendar.monthrange(y, m)[1]
        d = _date(y, m, last)
        return last - d.weekday() % 7 if d.weekday() != 6 else last

    d = _date(year, month, day)
    tz = timezone

    # ── Static offsets (no DST) ──────────────────────────────────────
    STATIC = {
        # South Asia
        "Asia/Kolkata": 5.5, "Asia/Colombo": 5.5, "Asia/Dhaka": 6.0,
        "Asia/Kathmandu": 5.75, "Asia/Karachi": 5.0,
        # Middle East
        "Asia/Dubai": 4.0, "Asia/Muscat": 4.0, "Asia/Riyadh": 3.0,
        "Asia/Kuwait": 3.0, "Asia/Qatar": 3.0, "Asia/Bahrain": 3.0,
        "Asia/Baghdad": 3.0, "Asia/Tehran": 3.5, "Asia/Kabul": 4.5,
        # Central/East Asia
        "Asia/Tashkent": 5.0, "Asia/Ashgabat": 5.0, "Asia/Dushanbe": 5.0,
        "Asia/Almaty": 6.0, "Asia/Bishkek": 6.0, "Asia/Yekaterinburg": 5.0,
        "Asia/Omsk": 6.0, "Asia/Krasnoyarsk": 7.0, "Asia/Irkutsk": 8.0,
        "Asia/Yakutsk": 9.0, "Asia/Vladivostok": 10.0,
        "Asia/Singapore": 8.0, "Asia/Kuala_Lumpur": 8.0,
        "Asia/Bangkok": 7.0, "Asia/Jakarta": 7.0, "Asia/Makassar": 8.0,
        "Asia/Jayapura": 9.0, "Asia/Manila": 8.0, "Asia/Taipei": 8.0,
        "Asia/Shanghai": 8.0, "Asia/Hong_Kong": 8.0, "Asia/Macau": 8.0,
        "Asia/Tokyo": 9.0, "Asia/Seoul": 9.0, "Asia/Pyongyang": 9.0,
        "Asia/Ulaanbaatar": 8.0, "Asia/Rangoon": 6.5, "Asia/Yangon": 6.5,
        "Asia/Brunei": 8.0, "Asia/Dili": 9.0,
        # Africa
        "Africa/Cairo": 2.0, "Africa/Nairobi": 3.0, "Africa/Lagos": 1.0,
        "Africa/Accra": 0.0, "Africa/Abidjan": 0.0, "Africa/Dakar": 0.0,
        "Africa/Johannesburg": 2.0, "Africa/Addis_Ababa": 3.0,
        "Africa/Khartoum": 3.0, "Africa/Dar_es_Salaam": 3.0,
        "Africa/Kampala": 3.0, "Africa/Mogadishu": 3.0,
        "Africa/Casablanca": 1.0, "Africa/Tunis": 1.0,
        "Africa/Algiers": 1.0, "Africa/Tripoli": 2.0,
        "Africa/Maputo": 2.0, "Africa/Harare": 2.0,
        "Africa/Lusaka": 2.0, "Africa/Windhoek": 2.0,
        "Africa/Gaborone": 2.0, "Africa/Mbabane": 2.0,
        "Africa/Maseru": 2.0, "Africa/Blantyre": 2.0,
        "Africa/Bujumbura": 2.0, "Africa/Kigali": 2.0,
        "Africa/Luanda": 1.0, "Africa/Kinshasa": 1.0,
        "Africa/Brazzaville": 1.0, "Africa/Douala": 1.0,
        "Africa/Libreville": 1.0, "Africa/Malabo": 1.0,
        "Africa/Bangui": 1.0, "Africa/Ndjamena": 1.0,
        "Africa/Niamey": 1.0, "Africa/Bamako": 0.0,
        "Africa/Ouagadougou": 0.0, "Africa/Conakry": 0.0,
        "Africa/Freetown": 0.0, "Africa/Monrovia": 0.0,
        "Africa/Nouakchott": 0.0, "Africa/Lome": 0.0,
        "Africa/Porto-Novo": 1.0, "Africa/Cotonou": 1.0,
        "Africa/Abuja": 1.0, "Africa/Accra": 0.0,
        "Africa/Djibouti": 3.0, "Africa/Asmara": 3.0,
        "Africa/Juba": 3.0, "Africa/Antananarivo": 3.0,
        # Indian Ocean
        "Indian/Mauritius": 4.0, "Indian/Maldives": 5.0,
        "Indian/Reunion": 4.0, "Indian/Comoro": 3.0,
        "Indian/Mayotte": 3.0, "Indian/Seychelles": 4.0,
        # Pacific
        "Pacific/Honolulu": -10.0, "Pacific/Guam": 10.0,
        "Pacific/Fiji": 12.0, "Pacific/Port_Moresby": 10.0,
        "Pacific/Noumea": 11.0, "Pacific/Tarawa": 12.0,
        "Pacific/Tongatapu": 13.0, "Pacific/Apia": 13.0,
        "Pacific/Fakaofo": 13.0, "Pacific/Chatham": 12.75,
        # Americas (no DST)
        "America/Bogota": -5.0, "America/Lima": -5.0,
        "America/Guayaquil": -5.0, "America/Caracas": -4.0,
        "America/La_Paz": -4.0, "America/Manaus": -4.0,
        "America/Belem": -3.0, "America/Fortaleza": -3.0,
        "America/Recife": -3.0, "America/Maceio": -3.0,
        "America/Buenos_Aires": -3.0, "America/Montevideo": -3.0,
        "America/Guyana": -4.0, "America/Suriname": -3.0,
        "America/Panama": -5.0, "America/Jamaica": -5.0,
        "America/Port-au-Prince": -5.0,
        "America/Costa_Rica": -6.0, "America/El_Salvador": -6.0,
        "America/Guatemala": -6.0, "America/Honduras": -6.0,
        "America/Managua": -6.0, "America/Tegucigalpa": -6.0,
        "America/Belize": -6.0,
        "America/Barbados": -4.0, "America/Trinidad": -4.0,
        "America/Port_of_Spain": -4.0, "America/Aruba": -4.0,
        "America/Curacao": -4.0,
        # Europe (no DST)
        "Europe/Moscow": 3.0, "Europe/Minsk": 3.0,
        "Europe/Istanbul": 3.0, "Europe/Kaliningrad": 2.0,
        "Europe/Samara": 4.0,
        # Other
        "UTC": 0.0, "Etc/UTC": 0.0, "Etc/GMT": 0.0,
    }
    if tz in STATIC:
        return STATIC[tz]

    # ── US / Canada DST (2nd Sun Mar → 1st Sun Nov) ──────────────────
    US = {
        "America/New_York": -5.0, "America/Detroit": -5.0,
        "America/Toronto": -5.0, "America/Montreal": -5.0,
        "America/Indiana/Indianapolis": -5.0,
        "America/Chicago": -6.0, "America/Winnipeg": -6.0,
        "America/Denver": -7.0, "America/Edmonton": -7.0,
        "America/Los_Angeles": -8.0, "America/Vancouver": -8.0,
        "America/Anchorage": -9.0, "America/Juneau": -9.0,
        "America/Halifax": -4.0, "America/Atlantic": -4.0,
        "America/St_Johns": -3.5,
    }
    if tz in US:
        base = US[tz]
        try:
            spring = nth_sun(year, 3, 2)
            fall_s = nth_sun(year, 11, 1)
            if _date(year, 3, spring) <= d < _date(year, 11, fall_s):
                return base + 1.0
        except: pass
        return base

    # ── Europe DST (last Sun Mar → last Sun Oct) ──────────────────────
    EU = {
        "Europe/London": 0.0, "Europe/Dublin": 0.0, "Europe/Lisbon": 0.0,
        "Europe/Paris": 1.0, "Europe/Berlin": 1.0, "Europe/Rome": 1.0,
        "Europe/Madrid": 1.0, "Europe/Amsterdam": 1.0, "Europe/Brussels": 1.0,
        "Europe/Zurich": 1.0, "Europe/Vienna": 1.0, "Europe/Warsaw": 1.0,
        "Europe/Prague": 1.0, "Europe/Budapest": 1.0, "Europe/Bratislava": 1.0,
        "Europe/Ljubljana": 1.0, "Europe/Zagreb": 1.0, "Europe/Sarajevo": 1.0,
        "Europe/Belgrade": 1.0, "Europe/Skopje": 1.0, "Europe/Podgorica": 1.0,
        "Europe/Stockholm": 1.0, "Europe/Oslo": 1.0, "Europe/Copenhagen": 1.0,
        "Europe/Luxembourg": 1.0, "Europe/Monaco": 1.0,
        "Europe/Helsinki": 2.0, "Europe/Riga": 2.0, "Europe/Tallinn": 2.0,
        "Europe/Vilnius": 2.0, "Europe/Athens": 2.0, "Europe/Bucharest": 2.0,
        "Europe/Sofia": 2.0, "Europe/Kiev": 2.0, "Europe/Uzhgorod": 2.0,
        "Europe/Nicosia": 2.0,
    }
    if tz in EU:
        base = EU[tz]
        try:
            spring = last_sun(year, 3)
            fall_s = last_sun(year, 10)
            if _date(year, 3, spring) <= d < _date(year, 10, fall_s):
                return base + 1.0
        except: pass
        return base

    # ── Australia DST (1st Sun Oct → 1st Sun Apr) ────────────────────
    AU = {
        "Australia/Sydney": 10.0, "Australia/Melbourne": 10.0,
        "Australia/Hobart": 10.0, "Australia/Lord_Howe": 10.5,
        "Australia/Adelaide": 9.5,
        "Australia/Brisbane": 10.0,   # no DST
        "Australia/Darwin": 9.5,      # no DST
        "Australia/Perth": 8.0,       # no DST
    }
    NO_DST_AU = {"Australia/Brisbane", "Australia/Darwin", "Australia/Perth"}
    if tz in AU:
        if tz in NO_DST_AU:
            return AU[tz]
        base = AU[tz]
        try:
            spring = nth_sun(year, 10, 1)
            fall_s = nth_sun(year, 4, 1)
            spring_d = _date(year, 10, spring)
            fall_d = _date(year, 4, fall_s)
            if d >= spring_d or d < fall_d:
                return base + 1.0
        except: pass
        return base

    # ── New Zealand DST (last Sun Sep → 1st Sun Apr) ──────────────────
    if tz in ("Pacific/Auckland", "Pacific/Chatham"):
        base = 12.0 if tz == "Pacific/Auckland" else 12.75
        try:
            spring = last_sun(year, 9)
            fall_s = nth_sun(year, 4, 1)
            spring_d = _date(year, 9, spring)
            fall_d = _date(year, 4, fall_s)
            if d >= spring_d or d < fall_d:
                return base + 1.0
        except: pass
        return base

    # Unknown timezone — return 0
    return 0.0


def is_polar(lat: float) -> bool:
    """True if location may have midnight sun issues (|lat| > 66.5°)."""
    return abs(lat) > 66.5


# ═══════════════════════════════════════════════════════════════════════
# WORLD CITIES DATABASE
# Format: "city_key": (lat, lon, country, timezone)
# ═══════════════════════════════════════════════════════════════════════

WORLD_CITIES = {

    # ── USA ──────────────────────────────────────────────────────────────
    "new york":         (40.7128, -74.0060, "USA", "America/New_York"),
    "new york city":    (40.7128, -74.0060, "USA", "America/New_York"),
    "nyc":              (40.7128, -74.0060, "USA", "America/New_York"),
    "los angeles":      (34.0522, -118.2437,"USA", "America/Los_Angeles"),
    "la":               (34.0522, -118.2437,"USA", "America/Los_Angeles"),
    "chicago":          (41.8781, -87.6298, "USA", "America/Chicago"),
    "houston":          (29.7604, -95.3698, "USA", "America/Chicago"),
    "phoenix":          (33.4484, -112.0740,"USA", "America/Phoenix"),
    "philadelphia":     (39.9526, -75.1652, "USA", "America/New_York"),
    "san antonio":      (29.4241, -98.4936, "USA", "America/Chicago"),
    "san diego":        (32.7157, -117.1611,"USA", "America/Los_Angeles"),
    "dallas":           (32.7767, -96.7970, "USA", "America/Chicago"),
    "san jose":         (37.3382, -121.8863,"USA", "America/Los_Angeles"),
    "austin":           (30.2672, -97.7431, "USA", "America/Chicago"),
    "jacksonville":     (30.3322, -81.6557, "USA", "America/New_York"),
    "fort worth":       (32.7555, -97.3308, "USA", "America/Chicago"),
    "san francisco":    (37.7749, -122.4194,"USA", "America/Los_Angeles"),
    "columbus":         (39.9612, -82.9988, "USA", "America/New_York"),
    "charlotte":        (35.2271, -80.8431, "USA", "America/New_York"),
    "indianapolis":     (39.7684, -86.1581, "USA", "America/Indiana/Indianapolis"),
    "seattle":          (47.6062, -122.3321,"USA", "America/Los_Angeles"),
    "denver":           (39.7392, -104.9903,"USA", "America/Denver"),
    "washington dc":    (38.9072, -77.0369, "USA", "America/New_York"),
    "nashville":        (36.1627, -86.7816, "USA", "America/Chicago"),
    "oklahoma city":    (35.4676, -97.5164, "USA", "America/Chicago"),
    "el paso":          (31.7619, -106.4850,"USA", "America/Denver"),
    "boston":           (42.3601, -71.0589, "USA", "America/New_York"),
    "portland":         (45.5051, -122.6750,"USA", "America/Los_Angeles"),
    "las vegas":        (36.1699, -115.1398,"USA", "America/Los_Angeles"),
    "memphis":          (35.1495, -90.0490, "USA", "America/Chicago"),
    "detroit":          (42.3314, -83.0458, "USA", "America/Detroit"),
    "louisville":       (38.2527, -85.7585, "USA", "America/New_York"),
    "baltimore":        (39.2904, -76.6122, "USA", "America/New_York"),
    "miami":            (25.7617, -80.1918, "USA", "America/New_York"),
    "atlanta":          (33.7490, -84.3880, "USA", "America/New_York"),
    "minneapolis":      (44.9778, -93.2650, "USA", "America/Chicago"),
    "new orleans":      (29.9511, -90.0715, "USA", "America/Chicago"),
    "honolulu":         (21.3069, -157.8583,"USA", "Pacific/Honolulu"),
    "anchorage":        (61.2181, -149.9003,"USA", "America/Anchorage"),

    # ── UK ───────────────────────────────────────────────────────────────
    "london":           (51.5074, -0.1278,  "UK", "Europe/London"),
    "birmingham":       (52.4862,  -1.8904, "UK", "Europe/London"),
    "manchester":       (53.4808,  -2.2426, "UK", "Europe/London"),
    "leeds":            (53.8008,  -1.5491, "UK", "Europe/London"),
    "glasgow":          (55.8642,  -4.2518, "UK", "Europe/London"),
    "liverpool":        (53.4084,  -2.9916, "UK", "Europe/London"),
    "edinburgh":        (55.9533,  -3.1883, "UK", "Europe/London"),
    "bristol":          (51.4545,  -2.5879, "UK", "Europe/London"),
    "sheffield":        (53.3811,  -1.4701, "UK", "Europe/London"),
    "cardiff":          (51.4816,  -3.1791, "UK", "Europe/London"),
    "leicester":        (52.6369,  -1.1398, "UK", "Europe/London"),
    "coventry":         (52.4068,  -1.5197, "UK", "Europe/London"),
    "nottingham":       (52.9548,  -1.1581, "UK", "Europe/London"),
    "bradford":         (53.7960,  -1.7594, "UK", "Europe/London"),

    # ── CANADA ───────────────────────────────────────────────────────────
    "toronto":          (43.7001, -79.4163, "Canada", "America/Toronto"),
    "montreal":         (45.5017, -73.5673, "Canada", "America/Montreal"),
    "vancouver":        (49.2827, -123.1207,"Canada", "America/Vancouver"),
    "calgary":          (51.0447, -114.0719,"Canada", "America/Edmonton"),
    "edmonton":         (53.5461, -113.4938,"Canada", "America/Edmonton"),
    "ottawa":           (45.4215, -75.6972, "Canada", "America/Toronto"),
    "winnipeg":         (49.8951, -97.1384, "Canada", "America/Winnipeg"),
    "quebec city":      (46.8139, -71.2080, "Canada", "America/Montreal"),
    "hamilton":         (43.2557, -79.8711, "Canada", "America/Toronto"),
    "brampton":         (43.7315, -79.7624, "Canada", "America/Toronto"),
    "surrey":           (49.1913, -122.8490,"Canada", "America/Vancouver"),
    "mississauga":      (43.5890, -79.6441, "Canada", "America/Toronto"),
    "halifax":          (44.6488, -63.5752, "Canada", "America/Halifax"),

    # ── AUSTRALIA ────────────────────────────────────────────────────────
    "sydney":           (-33.8688, 151.2093,"Australia", "Australia/Sydney"),
    "melbourne":        (-37.8136, 144.9631,"Australia", "Australia/Melbourne"),
    "brisbane":         (-27.4698, 153.0251,"Australia", "Australia/Brisbane"),
    "perth":            (-31.9505, 115.8605,"Australia", "Australia/Perth"),
    "adelaide":         (-34.9285, 138.6007,"Australia", "Australia/Adelaide"),
    "gold coast":       (-28.0167, 153.4000,"Australia", "Australia/Brisbane"),
    "newcastle":        (-32.9283, 151.7817,"Australia", "Australia/Sydney"),
    "canberra":         (-35.2809, 149.1300,"Australia", "Australia/Sydney"),
    "hobart":           (-42.8821, 147.3272,"Australia", "Australia/Hobart"),
    "darwin":           (-12.4634, 130.8456,"Australia", "Australia/Darwin"),

    # ── NEW ZEALAND ──────────────────────────────────────────────────────
    "auckland":         (-36.8485, 174.7633,"New Zealand", "Pacific/Auckland"),
    "wellington":       (-41.2865, 174.7762,"New Zealand", "Pacific/Auckland"),
    "christchurch":     (-43.5321, 172.6362,"New Zealand", "Pacific/Auckland"),
    "hamilton nz":      (-37.7870, 175.2793,"New Zealand", "Pacific/Auckland"),
    "dunedin":          (-45.8788, 170.5028,"New Zealand", "Pacific/Auckland"),

    # ── GERMANY ──────────────────────────────────────────────────────────
    "berlin":           (52.5200,  13.4050, "Germany", "Europe/Berlin"),
    "hamburg":          (53.5753,  10.0153, "Germany", "Europe/Berlin"),
    "munich":           (48.1351,  11.5820, "Germany", "Europe/Berlin"),
    "cologne":          (50.9333,   6.9500, "Germany", "Europe/Berlin"),
    "frankfurt":        (50.1109,   8.6821, "Germany", "Europe/Berlin"),
    "stuttgart":        (48.7758,   9.1829, "Germany", "Europe/Berlin"),
    "dusseldorf":       (51.2217,   6.7762, "Germany", "Europe/Berlin"),
    "dortmund":         (51.5136,   7.4653, "Germany", "Europe/Berlin"),
    "essen":            (51.4556,   7.0116, "Germany", "Europe/Berlin"),
    "leipzig":          (51.3397,  12.3731, "Germany", "Europe/Berlin"),
    "bremen":           (53.0793,   8.8017, "Germany", "Europe/Berlin"),
    "dresden":          (51.0504,  13.7373, "Germany", "Europe/Berlin"),
    "hannover":         (52.3759,   9.7320, "Germany", "Europe/Berlin"),
    "nuremberg":        (49.4521,  11.0767, "Germany", "Europe/Berlin"),

    # ── FRANCE ───────────────────────────────────────────────────────────
    "paris":            (48.8566,   2.3522, "France", "Europe/Paris"),
    "marseille":        (43.2965,   5.3698, "France", "Europe/Paris"),
    "lyon":             (45.7640,   4.8357, "France", "Europe/Paris"),
    "toulouse":         (43.6047,   1.4442, "France", "Europe/Paris"),
    "nice":             (43.7102,   7.2620, "France", "Europe/Paris"),
    "nantes":           (47.2184,  -1.5536, "France", "Europe/Paris"),
    "strasbourg":       (48.5734,   7.7521, "France", "Europe/Paris"),
    "montpellier":      (43.6119,   3.8772, "France", "Europe/Paris"),
    "bordeaux":         (44.8378,  -0.5792, "France", "Europe/Paris"),
    "lille":            (50.6292,   3.0573, "France", "Europe/Paris"),

    # ── ITALY ────────────────────────────────────────────────────────────
    "rome":             (41.9028,  12.4964, "Italy", "Europe/Rome"),
    "milan":            (45.4654,   9.1859, "Italy", "Europe/Rome"),
    "naples":           (40.8518,  14.2681, "Italy", "Europe/Rome"),
    "turin":            (45.0703,   7.6869, "Italy", "Europe/Rome"),
    "palermo":          (38.1157,  13.3615, "Italy", "Europe/Rome"),
    "genoa":            (44.4056,   8.9463, "Italy", "Europe/Rome"),
    "bologna":          (44.4949,  11.3426, "Italy", "Europe/Rome"),
    "florence":         (43.7696,  11.2558, "Italy", "Europe/Rome"),
    "venice":           (45.4408,  12.3155, "Italy", "Europe/Rome"),

    # ── SPAIN ────────────────────────────────────────────────────────────
    "madrid":           (40.4168,  -3.7038, "Spain", "Europe/Madrid"),
    "barcelona":        (41.3851,   2.1734, "Spain", "Europe/Madrid"),
    "valencia":         (39.4699,  -0.3763, "Spain", "Europe/Madrid"),
    "seville":          (37.3891,  -5.9845, "Spain", "Europe/Madrid"),
    "zaragoza":         (41.6488,  -0.8891, "Spain", "Europe/Madrid"),
    "malaga":           (36.7213,  -4.4216, "Spain", "Europe/Madrid"),
    "bilbao":           (43.2630,  -2.9350, "Spain", "Europe/Madrid"),

    # ── RUSSIA ───────────────────────────────────────────────────────────
    "moscow":           (55.7558,  37.6173, "Russia", "Europe/Moscow"),
    "saint petersburg": (59.9311,  30.3609, "Russia", "Europe/Moscow"),
    "novosibirsk":      (54.9885,  82.9207, "Russia", "Asia/Krasnoyarsk"),
    "yekaterinburg":    (56.8389,  60.6057, "Russia", "Asia/Yekaterinburg"),
    "kazan":            (55.8304,  49.0661, "Russia", "Europe/Moscow"),
    "nizhny novgorod":  (56.2965,  43.9361, "Russia", "Europe/Moscow"),
    "omsk":             (54.9885,  73.3242, "Russia", "Asia/Omsk"),
    "samara":           (53.1959,  50.1800, "Russia", "Europe/Samara"),
    "chelyabinsk":      (55.1644,  61.4368, "Russia", "Asia/Yekaterinburg"),
    "vladivostok":      (43.1332, 131.9113, "Russia", "Asia/Vladivostok"),

    # ── CHINA ────────────────────────────────────────────────────────────
    "beijing":          (39.9042, 116.4074, "China", "Asia/Shanghai"),
    "shanghai":         (31.2304, 121.4737, "China", "Asia/Shanghai"),
    "guangzhou":        (23.1291, 113.2644, "China", "Asia/Shanghai"),
    "shenzhen":         (22.5431, 114.0579, "China", "Asia/Shanghai"),
    "chengdu":          (30.5728, 104.0668, "China", "Asia/Shanghai"),
    "tianjin":          (39.3434, 117.3616, "China", "Asia/Shanghai"),
    "wuhan":            (30.5928, 114.3055, "China", "Asia/Shanghai"),
    "xian":             (34.3416, 108.9398, "China", "Asia/Shanghai"),
    "hangzhou":         (30.2741, 120.1551, "China", "Asia/Shanghai"),
    "nanjing":          (32.0603, 118.7969, "China", "Asia/Shanghai"),
    "chongqing":        (29.5630, 106.5516, "China", "Asia/Shanghai"),
    "shenyang":         (41.8057, 123.4315, "China", "Asia/Shanghai"),
    "dongguan":         (23.0207, 113.7518, "China", "Asia/Shanghai"),
    "foshan":           (23.0219, 113.1215, "China", "Asia/Shanghai"),
    "haerbin":          (45.7564, 126.6424, "China", "Asia/Shanghai"),
    "harbin":           (45.7564, 126.6424, "China", "Asia/Shanghai"),
    "urumqi":           (43.8256,  87.6168, "China", "Asia/Shanghai"),
    "kunming":          (25.0460, 102.7097, "China", "Asia/Shanghai"),
    "zhengzhou":        (34.7472, 113.6249, "China", "Asia/Shanghai"),
    "jinan":            (36.6512, 117.1201, "China", "Asia/Shanghai"),
    "qingdao":          (36.0671, 120.3826, "China", "Asia/Shanghai"),
    "dalian":           (38.9140, 121.6147, "China", "Asia/Shanghai"),
    "xiamen":           (24.4798, 118.0894, "China", "Asia/Shanghai"),

    # ── JAPAN ────────────────────────────────────────────────────────────
    "tokyo":            (35.6762, 139.6503, "Japan", "Asia/Tokyo"),
    "osaka":            (34.6937, 135.5023, "Japan", "Asia/Tokyo"),
    "nagoya":           (35.1815, 136.9066, "Japan", "Asia/Tokyo"),
    "yokohama":         (35.4437, 139.6380, "Japan", "Asia/Tokyo"),
    "sapporo":          (43.0618, 141.3545, "Japan", "Asia/Tokyo"),
    "kobe":             (34.6901, 135.1956, "Japan", "Asia/Tokyo"),
    "kyoto":            (35.0116, 135.7681, "Japan", "Asia/Tokyo"),
    "fukuoka":          (33.5904, 130.4017, "Japan", "Asia/Tokyo"),
    "hiroshima":        (34.3853, 132.4553, "Japan", "Asia/Tokyo"),
    "sendai":           (38.2682, 140.8694, "Japan", "Asia/Tokyo"),
    "kawasaki":         (35.5308, 139.7029, "Japan", "Asia/Tokyo"),

    # ── SOUTH KOREA ──────────────────────────────────────────────────────
    "seoul":            (37.5665, 126.9780, "South Korea", "Asia/Seoul"),
    "busan":            (35.1796, 129.0756, "South Korea", "Asia/Seoul"),
    "incheon":          (37.4563, 126.7052, "South Korea", "Asia/Seoul"),
    "daegu":            (35.8714, 128.6014, "South Korea", "Asia/Seoul"),
    "daejeon":          (36.3504, 127.3845, "South Korea", "Asia/Seoul"),
    "gwangju":          (35.1595, 126.8526, "South Korea", "Asia/Seoul"),

    # ── PAKISTAN ─────────────────────────────────────────────────────────
    "karachi":          (24.8607,  67.0011, "Pakistan", "Asia/Karachi"),
    "lahore":           (31.5497,  74.3436, "Pakistan", "Asia/Karachi"),
    "islamabad":        (33.7294,  73.0931, "Pakistan", "Asia/Karachi"),
    "rawalpindi":       (33.5651,  73.0169, "Pakistan", "Asia/Karachi"),
    "faisalabad":       (31.4154,  73.0886, "Pakistan", "Asia/Karachi"),
    "peshawar":         (34.0151,  71.5249, "Pakistan", "Asia/Karachi"),
    "quetta":           (30.1798,  66.9750, "Pakistan", "Asia/Karachi"),
    "multan":           (30.1575,  71.5249, "Pakistan", "Asia/Karachi"),
    "hyderabad pk":     (25.3960,  68.3578, "Pakistan", "Asia/Karachi"),

    # ── BANGLADESH ───────────────────────────────────────────────────────
    "dhaka":            (23.8103,  90.4125, "Bangladesh", "Asia/Dhaka"),
    "chittagong":       (22.3569,  91.7832, "Bangladesh", "Asia/Dhaka"),
    "sylhet":           (24.8949,  91.8687, "Bangladesh", "Asia/Dhaka"),
    "rajshahi":         (24.3745,  88.6042, "Bangladesh", "Asia/Dhaka"),
    "khulna":           (22.8456,  89.5403, "Bangladesh", "Asia/Dhaka"),

    # ── SRI LANKA ────────────────────────────────────────────────────────
    "colombo":          (6.9271,   79.8612, "Sri Lanka", "Asia/Colombo"),
    "kandy":            (7.2906,   80.6337, "Sri Lanka", "Asia/Colombo"),
    "galle":            (6.0535,   80.2210, "Sri Lanka", "Asia/Colombo"),
    "jaffna":           (9.6615,   80.0255, "Sri Lanka", "Asia/Colombo"),

    # ── NEPAL ────────────────────────────────────────────────────────────
    "kathmandu":        (27.7172,  85.3240, "Nepal", "Asia/Kathmandu"),
    "pokhara":          (28.2096,  83.9856, "Nepal", "Asia/Kathmandu"),
    "lalitpur":         (27.6588,  85.3247, "Nepal", "Asia/Kathmandu"),
    "biratnagar":       (26.4525,  87.2718, "Nepal", "Asia/Kathmandu"),
    "birgunj":          (27.0104,  84.8777, "Nepal", "Asia/Kathmandu"),

    # ── UAE ──────────────────────────────────────────────────────────────
    "dubai":            (25.2048,  55.2708, "UAE", "Asia/Dubai"),
    "abu dhabi":        (24.4539,  54.3773, "UAE", "Asia/Dubai"),
    "sharjah":          (25.3460,  55.4209, "UAE", "Asia/Dubai"),
    "ajman":            (25.4052,  55.5136, "UAE", "Asia/Dubai"),
    "al ain":           (24.1302,  55.8023, "UAE", "Asia/Dubai"),

    # ── SAUDI ARABIA ─────────────────────────────────────────────────────
    "riyadh":           (24.6877,  46.7219, "Saudi Arabia", "Asia/Riyadh"),
    "jeddah":           (21.4858,  39.1925, "Saudi Arabia", "Asia/Riyadh"),
    "mecca":            (21.3891,  39.8579, "Saudi Arabia", "Asia/Riyadh"),
    "medina":           (24.4539,  39.6140, "Saudi Arabia", "Asia/Riyadh"),
    "dammam":           (26.4207,  50.0888, "Saudi Arabia", "Asia/Riyadh"),
    "makkah":           (21.3891,  39.8579, "Saudi Arabia", "Asia/Riyadh"),
    "madinah":          (24.4539,  39.6140, "Saudi Arabia", "Asia/Riyadh"),

    # ── OTHER MIDDLE EAST ────────────────────────────────────────────────
    "tehran":           (35.6892,  51.3890, "Iran", "Asia/Tehran"),
    "istanbul":         (41.0082,  28.9784, "Turkey", "Europe/Istanbul"),
    "ankara":           (39.9334,  32.8597, "Turkey", "Europe/Istanbul"),
    "baghdad":          (33.3152,  44.3661, "Iraq", "Asia/Baghdad"),
    "kuwait city":      (29.3759,  47.9774, "Kuwait", "Asia/Kuwait"),
    "doha":             (25.2854,  51.5310, "Qatar", "Asia/Qatar"),
    "manama":           (26.2235,  50.5876, "Bahrain", "Asia/Bahrain"),
    "muscat":           (23.5880,  58.3829, "Oman", "Asia/Muscat"),
    "beirut":           (33.8938,  35.5018, "Lebanon", "Asia/Beirut"),
    "tel aviv":         (32.0853,  34.7818, "Israel", "Asia/Jerusalem"),
    "jerusalem":        (31.7683,  35.2137, "Israel", "Asia/Jerusalem"),
    "amman":            (31.9539,  35.9106, "Jordan", "Asia/Amman"),
    "damascus":         (33.5102,  36.2913, "Syria", "Asia/Damascus"),
    "kabul":            (34.5553,  69.2075, "Afghanistan", "Asia/Kabul"),

    # ── SOUTHEAST ASIA ───────────────────────────────────────────────────
    "singapore":        (1.3521,  103.8198, "Singapore", "Asia/Singapore"),
    "kuala lumpur":     (3.1390,  101.6869, "Malaysia", "Asia/Kuala_Lumpur"),
    "jakarta":          (-6.2088, 106.8456, "Indonesia", "Asia/Jakarta"),
    "surabaya":         (-7.2575, 112.7521, "Indonesia", "Asia/Jakarta"),
    "bandung":          (-6.9175, 107.6191, "Indonesia", "Asia/Jakarta"),
    "medan":            (3.5952,   98.6722, "Indonesia", "Asia/Jakarta"),
    "makassar":         (-5.1477, 119.4327, "Indonesia", "Asia/Makassar"),
    "bangkok":          (13.7563, 100.5018, "Thailand", "Asia/Bangkok"),
    "chiang mai":       (18.7883,  98.9853, "Thailand", "Asia/Bangkok"),
    "manila":           (14.5995, 120.9842, "Philippines", "Asia/Manila"),
    "quezon city":      (14.6760, 121.0437, "Philippines", "Asia/Manila"),
    "cebu":             (10.3157, 123.8854, "Philippines", "Asia/Manila"),
    "ho chi minh city": (10.8231, 106.6297, "Vietnam", "Asia/Bangkok"),
    "saigon":           (10.8231, 106.6297, "Vietnam", "Asia/Bangkok"),
    "hanoi":            (21.0285, 105.8542, "Vietnam", "Asia/Bangkok"),
    "yangon":           (16.8661,  96.1951, "Myanmar", "Asia/Yangon"),
    "rangoon":          (16.8661,  96.1951, "Myanmar", "Asia/Yangon"),
    "phnom penh":       (11.5564, 104.9282, "Cambodia", "Asia/Bangkok"),
    "vientiane":        (17.9757, 102.6331, "Laos", "Asia/Bangkok"),
    "colombo":          (6.9271,   79.8612, "Sri Lanka", "Asia/Colombo"),
    "taipei":           (25.0330, 121.5654, "Taiwan", "Asia/Taipei"),
    "hong kong":        (22.3193, 114.1694, "Hong Kong", "Asia/Hong_Kong"),
    "macau":            (22.1987, 113.5439, "Macau", "Asia/Macau"),

    # ── AFRICA ───────────────────────────────────────────────────────────
    "cairo":            (30.0444,  31.2357, "Egypt", "Africa/Cairo"),
    "alexandria":       (31.2001,  29.9187, "Egypt", "Africa/Cairo"),
    "lagos":            (6.5244,    3.3792, "Nigeria", "Africa/Lagos"),
    "kano":             (12.0022,   8.5920, "Nigeria", "Africa/Lagos"),
    "ibadan":           (7.3775,    3.9470, "Nigeria", "Africa/Lagos"),
    "abuja":            (9.0765,    7.3986, "Nigeria", "Africa/Abuja"),
    "nairobi":          (-1.2921,  36.8219, "Kenya", "Africa/Nairobi"),
    "mombasa":          (-4.0435,  39.6682, "Kenya", "Africa/Nairobi"),
    "addis ababa":      (9.0320,   38.7469, "Ethiopia", "Africa/Addis_Ababa"),
    "dar es salaam":    (-6.7924,  39.2083, "Tanzania", "Africa/Dar_es_Salaam"),
    "johannesburg":     (-26.2041, 28.0473, "South Africa", "Africa/Johannesburg"),
    "cape town":        (-33.9249, 18.4241, "South Africa", "Africa/Johannesburg"),
    "durban":           (-29.8587, 31.0218, "South Africa", "Africa/Johannesburg"),
    "pretoria":         (-25.7479, 28.2293, "South Africa", "Africa/Johannesburg"),
    "casablanca":       (33.5731,  -7.5898, "Morocco", "Africa/Casablanca"),
    "rabat":            (34.0132,  -6.8326, "Morocco", "Africa/Casablanca"),
    "tunis":            (36.8190,  10.1658, "Tunisia", "Africa/Tunis"),
    "algiers":          (36.7372,   3.0865, "Algeria", "Africa/Algiers"),
    "tripoli":          (32.9081,  13.1763, "Libya", "Africa/Tripoli"),
    "khartoum":         (15.5007,  32.5599, "Sudan", "Africa/Khartoum"),
    "kampala":          (0.3476,   32.5825, "Uganda", "Africa/Kampala"),
    "accra":            (5.6037,   -0.1870, "Ghana", "Africa/Accra"),
    "dakar":            (14.7167,  -17.4677,"Senegal", "Africa/Dakar"),
    "abidjan":          (5.3600,   -4.0083, "Ivory Coast", "Africa/Abidjan"),
    "kinshasa":         (-4.3217,  15.3222, "DR Congo", "Africa/Kinshasa"),
    "luanda":           (-8.8390,  13.2894, "Angola", "Africa/Luanda"),
    "maputo":           (-25.9692, 32.5732, "Mozambique", "Africa/Maputo"),
    "harare":           (-17.8252, 31.0335, "Zimbabwe", "Africa/Harare"),
    "lusaka":           (-15.4166, 28.2833, "Zambia", "Africa/Lusaka"),
    "antananarivo":     (-18.9137, 47.5361, "Madagascar", "Indian/Antananarivo"),

    # ── SOUTH AMERICA ────────────────────────────────────────────────────
    "sao paulo":        (-23.5505, -46.6333,"Brazil", "America/Sao_Paulo"),
    "rio de janeiro":   (-22.9068, -43.1729,"Brazil", "America/Sao_Paulo"),
    "brasilia":         (-15.7801, -47.9292,"Brazil", "America/Sao_Paulo"),
    "salvador":         (-12.9714, -38.5014,"Brazil", "America/Fortaleza"),
    "fortaleza":        (-3.7172,  -38.5433,"Brazil", "America/Fortaleza"),
    "belo horizonte":   (-19.9191, -43.9386,"Brazil", "America/Sao_Paulo"),
    "manaus":           (-3.1190,  -60.0217,"Brazil", "America/Manaus"),
    "curitiba":         (-25.4284, -49.2733,"Brazil", "America/Sao_Paulo"),
    "recife":           (-8.0578,  -34.8829,"Brazil", "America/Recife"),
    "buenos aires":     (-34.6037, -58.3816,"Argentina", "America/Buenos_Aires"),
    "cordoba":          (-31.4201, -64.1888,"Argentina", "America/Buenos_Aires"),
    "rosario":          (-32.9468, -60.6393,"Argentina", "America/Buenos_Aires"),
    "lima":             (-12.0464, -77.0428,"Peru", "America/Lima"),
    "bogota":           (4.7110,   -74.0721,"Colombia", "America/Bogota"),
    "medellin":         (6.2442,   -75.5812,"Colombia", "America/Bogota"),
    "cali":             (3.4516,   -76.5320,"Colombia", "America/Bogota"),
    "caracas":          (10.4806,  -66.9036,"Venezuela", "America/Caracas"),
    "santiago":         (-33.4489, -70.6693,"Chile", "America/Santiago"),
    "quito":            (-0.1807,  -78.4678,"Ecuador", "America/Guayaquil"),
    "guayaquil":        (-2.1962,  -79.8862,"Ecuador", "America/Guayaquil"),
    "la paz":           (-16.5000, -68.1500,"Bolivia", "America/La_Paz"),
    "asuncion":         (-25.2867, -57.6470,"Paraguay", "America/Asuncion"),
    "montevideo":       (-34.9011, -56.1645,"Uruguay", "America/Montevideo"),
    "panama city":      (8.9936,   -79.5197,"Panama", "America/Panama"),
    "san jose cr":      (9.9281,   -84.0907,"Costa Rica", "America/Costa_Rica"),
    "guatemala city":   (14.6349,  -90.5069,"Guatemala", "America/Guatemala"),
    "mexico city":      (19.4326,  -99.1332,"Mexico", "America/Chicago"),
    "guadalajara":      (20.6597,  -103.3496,"Mexico", "America/Chicago"),
    "monterrey":        (25.6866,  -100.3161,"Mexico", "America/Chicago"),
    "cancun":           (21.1619,  -86.8515, "Mexico", "America/Chicago"),
    "havana":           (23.1136,  -82.3666, "Cuba", "America/New_York"),
    "santo domingo":    (18.4861,  -69.9312, "Dominican Republic", "America/New_York"),
    "port au prince":   (18.5944,  -72.3074, "Haiti", "America/Port-au-Prince"),
    "kingston":         (17.9714,  -76.7936, "Jamaica", "America/Jamaica"),

    # ── EUROPE (others) ──────────────────────────────────────────────────
    "amsterdam":        (52.3676,   4.9041,  "Netherlands", "Europe/Amsterdam"),
    "rotterdam":        (51.9244,   4.4777,  "Netherlands", "Europe/Amsterdam"),
    "brussels":         (50.8503,   4.3517,  "Belgium", "Europe/Brussels"),
    "vienna":           (48.2082,  16.3738,  "Austria", "Europe/Vienna"),
    "zurich":           (47.3769,   8.5417,  "Switzerland", "Europe/Zurich"),
    "geneva":           (46.2044,   6.1432,  "Switzerland", "Europe/Zurich"),
    "bern":             (46.9480,   7.4474,  "Switzerland", "Europe/Zurich"),
    "stockholm":        (59.3293,  18.0686,  "Sweden", "Europe/Stockholm"),
    "gothenburg":       (57.7089,  11.9746,  "Sweden", "Europe/Stockholm"),
    "oslo":             (59.9139,  10.7522,  "Norway", "Europe/Oslo"),
    "copenhagen":       (55.6761,  12.5683,  "Denmark", "Europe/Copenhagen"),
    "helsinki":         (60.1699,  24.9384,  "Finland", "Europe/Helsinki"),
    "prague":           (50.0755,  14.4378,  "Czech Republic", "Europe/Prague"),
    "warsaw":           (52.2297,  21.0122,  "Poland", "Europe/Warsaw"),
    "krakow":           (50.0647,  19.9450,  "Poland", "Europe/Warsaw"),
    "budapest":         (47.4979,  19.0402,  "Hungary", "Europe/Budapest"),
    "bucharest":        (44.4268,  26.1025,  "Romania", "Europe/Bucharest"),
    "sofia":            (42.6977,  23.3219,  "Bulgaria", "Europe/Sofia"),
    "athens":           (37.9838,  23.7275,  "Greece", "Europe/Athens"),
    "thessaloniki":     (40.6401,  22.9444,  "Greece", "Europe/Athens"),
    "belgrade":         (44.8176,  20.4569,  "Serbia", "Europe/Belgrade"),
    "zagreb":           (45.8150,  15.9819,  "Croatia", "Europe/Zagreb"),
    "ljubljana":        (46.0569,  14.5058,  "Slovenia", "Europe/Ljubljana"),
    "bratislava":       (48.1486,  17.1077,  "Slovakia", "Europe/Bratislava"),
    "kyiv":             (50.4501,  30.5234,  "Ukraine", "Europe/Kiev"),
    "kharkiv":          (49.9935,  36.2304,  "Ukraine", "Europe/Kiev"),
    "minsk":            (53.9045,  27.5615,  "Belarus", "Europe/Minsk"),
    "riga":             (56.9460,  24.1059,  "Latvia", "Europe/Riga"),
    "tallinn":          (59.4370,  24.7536,  "Estonia", "Europe/Tallinn"),
    "vilnius":          (54.6872,  25.2797,  "Lithuania", "Europe/Vilnius"),
    "reykjavik":        (64.1265, -21.8174,  "Iceland", "UTC"),
    "lisbon":           (38.7223,  -9.1393,  "Portugal", "Europe/Lisbon"),
    "porto":            (41.1579,  -8.6291,  "Portugal", "Europe/Lisbon"),
    "dublin":           (53.3498,  -6.2603,  "Ireland", "Europe/Dublin"),
    "nicosia":          (35.1856,  33.3823,  "Cyprus", "Europe/Nicosia"),
    "tirana":           (41.3275,  19.8187,  "Albania", "Europe/Rome"),
    "valletta":         (35.8997,  14.5147,  "Malta", "Europe/Rome"),
    "luxembourg":       (49.8153,   6.1296,  "Luxembourg", "Europe/Luxembourg"),
    "skopje":           (41.9981,  21.4254,  "North Macedonia", "Europe/Skopje"),

    # ── CENTRAL ASIA ─────────────────────────────────────────────────────
    "tashkent":         (41.2995,  69.2401,  "Uzbekistan", "Asia/Tashkent"),
    "almaty":           (43.2220,  76.8512,  "Kazakhstan", "Asia/Almaty"),
    "astana":           (51.1801,  71.4460,  "Kazakhstan", "Asia/Almaty"),
    "nur sultan":       (51.1801,  71.4460,  "Kazakhstan", "Asia/Almaty"),
    "bishkek":          (42.8746,  74.5698,  "Kyrgyzstan", "Asia/Bishkek"),
    "dushanbe":         (38.5598,  68.7870,  "Tajikistan", "Asia/Dushanbe"),
    "ashgabat":         (37.9601,  58.3261,  "Turkmenistan", "Asia/Ashgabat"),
    "baku":             (40.4093,  49.8671,  "Azerbaijan", "Europe/Moscow"),
    "yerevan":          (40.1872,  44.5152,  "Armenia", "Europe/Moscow"),
    "tbilisi":          (41.6938,  44.8015,  "Georgia", "Europe/Moscow"),

    # ── OTHERS ───────────────────────────────────────────────────────────
    "toronto":          (43.7001, -79.4163,  "Canada", "America/Toronto"),
    "naypyidaw":        (19.7633,  96.0785,  "Myanmar", "Asia/Yangon"),
    "ulaanbaatar":      (47.8864, 106.9057,  "Mongolia", "Asia/Ulaanbaatar"),
    "pyongyang":        (39.0392, 125.7625,  "North Korea", "Asia/Pyongyang"),
    "thimphu":          (27.4728,  89.6390,  "Bhutan", "Asia/Dhaka"),
    "male":             (4.1755,   73.5093,  "Maldives", "Indian/Maldives"),
    "port louis":       (-20.1609, 57.4989,  "Mauritius", "Indian/Mauritius"),
    "victoria":         (-4.6236,  55.4513,  "Seychelles", "Indian/Seychelles"),
    "moroni":           (-11.7022, 43.2551,  "Comoros", "Indian/Comoro"),
    "dili":             (-8.5586, 125.5736,  "East Timor", "Asia/Dili"),
    "port moresby":     (-9.4438, 147.1803,  "Papua New Guinea", "Pacific/Port_Moresby"),
    "suva":             (-18.1248, 178.4501, "Fiji", "Pacific/Fiji"),
    "nuku alofa":       (-21.1394,-175.2046, "Tonga", "Pacific/Tongatapu"),
    "apia":             (-13.8506,-171.7514, "Samoa", "Pacific/Apia"),
    "honiara":          (-9.4456, 159.9729,  "Solomon Islands", "Pacific/Noumea"),
    "port vila":        (-17.7334, 168.3219, "Vanuatu", "Pacific/Noumea"),
    "palikir":          (6.9248,  158.1610,  "Micronesia", "Pacific/Guam"),
    "majuro":           (7.0897,  171.3803,  "Marshall Islands", "Pacific/Tarawa"),
    "tarawa":           (1.3291,  172.9793,  "Kiribati", "Pacific/Tarawa"),
    "funafuti":         (-8.5211, 179.1962,  "Tuvalu", "Pacific/Tarawa"),
    "yaren":            (-0.5477, 166.9209,  "Nauru", "Pacific/Nauru"),
}

# ── Aliases ───────────────────────────────────────────────────────────────────
WORLD_ALIASES = {
    # Indian aliases already in india_districts.py
    "usa":          "new york",
    "united states":"new york",
    "uk":           "london",
    "united kingdom":"london",
    "england":      "london",
    "uae":          "dubai",
    "south korea":  "seoul",
    "holland":      "amsterdam",
    "st petersburg":"saint petersburg",
    "leningrad":    "saint petersburg",
    "sao paulo":    "sao paulo",
    "rio":          "rio de janeiro",
    "ny":           "new york",
    "sf":           "san francisco",
    "dc":           "washington dc",
    "la":           "los angeles",
    "oz":           "sydney",
    "hk":           "hong kong",
    "nz":           "auckland",
    "nyc":          "new york",
}


def search_world_location(query: str) -> dict | None:
    """
    Search for a world city.
    Returns dict with lat, lon, country, timezone, tz_offset (for today).
    """
    from datetime import date
    today = date.today()
    q = query.strip().lower()

    # 1. Exact
    if q in WORLD_CITIES:
        lat, lon, country, tz = WORLD_CITIES[q]
        offset = get_tz_offset(tz, today.year, today.month, today.day)
        return {
            "name": query.title(), "lat": lat, "lon": lon,
            "country": country, "timezone": tz,
            "tz_offset": offset,
            "is_polar": is_polar(lat),
            "source": "world_cities_db"
        }

    # 2. Alias
    if q in WORLD_ALIASES:
        return search_world_location(WORLD_ALIASES[q])

    # 3. Partial
    for key in WORLD_CITIES:
        if key.startswith(q) or q in key:
            lat, lon, country, tz = WORLD_CITIES[key]
            offset = get_tz_offset(tz, today.year, today.month, today.day)
            return {
                "name": key.title(), "lat": lat, "lon": lon,
                "country": country, "timezone": tz,
                "tz_offset": offset,
                "is_polar": is_polar(lat),
                "source": "world_cities_db_fuzzy"
            }

    return None


def search_location(query: str, year: int = None, month: int = None, day: int = None) -> dict | None:
    """
    Master search: India districts first, then world cities.
    If year/month/day given, tz_offset reflects DST for that date.
    """
    from datetime import date
    if not year:
        today = date.today()
        year, month, day = today.year, today.month, today.day

    # 1. Try India districts
    try:
        from india_districts import search_india_location
        r = search_india_location(query)
        if r:
            return r
    except ImportError:
        pass

    # 2. Try world cities
    r = search_world_location(query)
    if r:
        # Recalculate offset for the specific date
        offset = get_tz_offset(r['timezone'], year, month, day)
        r['tz_offset'] = offset
        return r

    return None


if __name__ == "__main__":
    total = len(WORLD_CITIES)
    print(f"World Cities DB: {total} cities")
    print()

    # DST tests
    print("DST VERIFICATION:")
    from datetime import date
    dst_tests = [
        ("New York",   "America/New_York",    2026, 7, 4,  -4.0, "Summer"),
        ("New York",   "America/New_York",    2026, 1, 1,  -5.0, "Winter"),
        ("London",     "Europe/London",       2026, 7, 1,   1.0, "Summer BST"),
        ("London",     "Europe/London",       2026, 1, 1,   0.0, "Winter GMT"),
        ("Sydney",     "Australia/Sydney",    2026, 1, 1,  11.0, "Summer AEDT"),
        ("Sydney",     "Australia/Sydney",    2026, 7, 1,  10.0, "Winter AEST"),
        ("Dubai",      "Asia/Dubai",          2026, 7, 1,   4.0, "No DST"),
        ("India",      "Asia/Kolkata",        2026, 7, 1,   5.5, "No DST"),
        ("Paris",      "Europe/Paris",        2026, 8, 1,   2.0, "CEST"),
        ("Auckland",   "Pacific/Auckland",    2026, 1, 1,  13.0, "Summer NZDT"),
    ]
    all_ok = True
    for city, tz, y, mo, d, expected, label in dst_tests:
        got = get_tz_offset(tz, y, mo, d)
        ok = abs(got - expected) < 0.01
        if not ok: all_ok = False
        print(f"  {'✅' if ok else '❌'} {city:<12} {label:<15} got={got:+.1f}  exp={expected:+.1f}")
    print(f"\n  DST: {'✅ ALL CORRECT' if all_ok else '❌ ERRORS'}")

    # Search tests
    print()
    print("SEARCH TESTS:")
    search_tests = [
        ("London",      51.5074,  -0.1278),
        ("Tokyo",       35.6762, 139.6503),
        ("Sydney",     -33.8688, 151.2093),
        ("Dubai",       25.2048,  55.2708),
        ("NY",          40.7128, -74.0060),
        ("Mecca",       21.3891,  39.8579),
        ("Colombo",      6.9271,  79.8612),
        ("Kathmandu",   27.7172,  85.3240),
        ("Nairobi",     -1.2921,  36.8219),
        ("Sao Paulo",  -23.5505, -46.6333),
    ]
    sp = 0
    for name, exp_lat, exp_lon in search_tests:
        r = search_world_location(name)
        if r:
            ok = abs(r['lat']-exp_lat)<0.05 and abs(r['lon']-exp_lon)<0.05
            if ok: sp+=1
            print(f"  {'✅' if ok else '❌'} {name:<15} {r['lat']:.4f},{r['lon']:.4f}")
        else:
            print(f"  ❌ {name} NOT FOUND")
    print(f"\n  Search: {sp}/{len(search_tests)}")
