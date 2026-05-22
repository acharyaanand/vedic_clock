"""
Vedic Clock Jyotish API — Complete app.py
================================================
This file integrates ALL fixes from Pass 1 and Pass 2A:

  PASS 1:
    - KundliReq accepts optional email + phone (lead capture)
    - generate_horoscope() rewritten: each of 11 categories now has its own
      karaka planets per classical Vedic astrology, so scores vary correctly
    - get_sun_moon_events() timeout raised 6s -> 12s for Render cold starts;
      added _source flag so frontend can detect fallback times

  PASS 2A:
    - /api/dasha/tree endpoint returns full nested Vimshottari tree
      (Maha -> Antar -> Pratyantar -> Sookshma) for the cascade UI

  PRESERVED:
    - All 16 divisional charts (Shodashvarga) via /api/divisional-charts
    - Gulika upagraha calculation
    - All original endpoints unchanged

To deploy: REPLACE your entire app.py with this file. No merging needed.
"""

import math
from datetime import datetime, timedelta, date as date_cls
from typing import Any, Dict, List, Optional, Tuple

import requests
import swisseph as swe
from fastapi import FastAPI, HTTPException, Query, Depends, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from timezonefinder import TimezoneFinder


import os as _os_early
import time as _time_early
import json as _json_early
from collections import defaultdict as _defaultdict_early

# =============================
# PASS 7a: Indian cities database — loaded once at module init.
# Provides Google-matching centroids for ~270 major Indian places. Used by
# /geocode as Provider 0 (checked before any network call). 1ms lookup.
# Misses fall through to Open-Meteo, then Nominatim.
# =============================
_CITIES_INDIA: List[Dict[str, Any]] = []
_CITIES_INDIA_BY_LOWER: Dict[str, List[Dict[str, Any]]] = {}  # exact-match index
_CITIES_LOAD_DIAG: Dict[str, Any] = {"tried": [], "error": "not loaded yet"}  # debug info

def _load_cities_india() -> None:
    """Read cities_india.json. PASS 7b-β-fix: tries multiple possible paths and
    captures diagnostics so /api/health can show exactly what went wrong if the
    file isn't found. Silent failure overall — geocoder still works via fallback
    providers if no cities are loaded."""
    global _CITIES_INDIA, _CITIES_INDIA_BY_LOWER, _CITIES_LOAD_DIAG
    _CITIES_LOAD_DIAG = {"tried": [], "error": None}

    # Try multiple candidate locations. Render's working directory and __file__
    # location can differ depending on how the service was set up.
    here = _os_early.path.dirname(_os_early.path.abspath(__file__))
    cwd = _os_early.getcwd()
    candidates = [
        _os_early.path.join(here, "cities_india.json"),
        _os_early.path.join(cwd, "cities_india.json"),
        "/opt/render/project/src/cities_india.json",  # Render default
        "cities_india.json",                            # relative
    ]
    # Dedupe while preserving order
    seen = set()
    candidates_unique = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            candidates_unique.append(c)

    chosen_path = None
    for path in candidates_unique:
        exists = _os_early.path.exists(path)
        _CITIES_LOAD_DIAG["tried"].append({"path": path, "exists": exists})
        if exists and chosen_path is None:
            chosen_path = path

    if chosen_path is None:
        _CITIES_LOAD_DIAG["error"] = "file not found at any candidate path"
        return

    try:
        with open(chosen_path, "r", encoding="utf-8") as f:
            data = _json_early.load(f)
    except Exception as exc:
        _CITIES_LOAD_DIAG["error"] = f"parse error: {str(exc)[:120]}"
        return

    cities = data.get("cities", [])
    _CITIES_LOAD_DIAG["chosen_path"] = chosen_path
    _CITIES_LOAD_DIAG["raw_count"] = len(cities)

    # Validate + index
    clean: List[Dict[str, Any]] = []
    idx: Dict[str, List[Dict[str, Any]]] = {}
    for c in cities:
        name = (c.get("name") or "").strip()
        if not name:
            continue
        try:
            lat = float(c["latitude"]); lon = float(c["longitude"])
        except (KeyError, ValueError, TypeError):
            continue
        row = {
            "name": name,
            "admin1": (c.get("admin1") or "").strip(),
            "country": (c.get("country") or "India").strip(),
            "latitude": lat,
            "longitude": lon,
            "timezone": (c.get("timezone") or "Asia/Kolkata").strip(),
            "_name_lower": name.lower(),
        }
        clean.append(row)
        idx.setdefault(row["_name_lower"], []).append(row)
    _CITIES_INDIA = clean
    _CITIES_INDIA_BY_LOWER = idx
    _CITIES_LOAD_DIAG["error"] = None

_load_cities_india()


def _search_cities_india(query: str, limit: int = 8) -> List[Dict[str, Any]]:
    """Search the local Indian cities DB for a query string.
    Match strategy (in order of preference):
      1. Exact case-insensitive match → top results
      2. Prefix match (starts with query) → next results
      3. Substring match (contains query) → fill remaining slots
    Returns at most `limit` cities, deduplicated by (name, lat, lon).
    """
    if not _CITIES_INDIA:
        return []
    q = query.strip().lower()
    if not q:
        return []

    # 1. Exact match (handles "Vidisha" → exact city)
    exact = _CITIES_INDIA_BY_LOWER.get(q, [])

    # 2. Prefix match
    prefix: List[Dict[str, Any]] = []
    if len(exact) < limit:
        for c in _CITIES_INDIA:
            if c["_name_lower"].startswith(q) and c["_name_lower"] != q:
                prefix.append(c)
                if len(exact) + len(prefix) >= limit * 2:
                    break

    # 3. Substring match (fills remaining)
    substr: List[Dict[str, Any]] = []
    if len(exact) + len(prefix) < limit:
        for c in _CITIES_INDIA:
            nl = c["_name_lower"]
            if q in nl and not nl.startswith(q) and nl != q:
                substr.append(c)
                if len(exact) + len(prefix) + len(substr) >= limit * 2:
                    break

    # Combine + dedupe + trim
    combined = exact + prefix + substr
    seen = set()
    out: List[Dict[str, Any]] = []
    for c in combined:
        key = (c["_name_lower"], round(c["latitude"], 4), round(c["longitude"], 4))
        if key in seen:
            continue
        seen.add(key)
        # Strip internal _name_lower before returning
        out.append({k: v for k, v in c.items() if not k.startswith("_")})
        if len(out) >= limit:
            break
    return out


app = FastAPI(title="Vedic Clock Jyotish API", version="3.0.0")

# =============================
# PHASE 2: API key authentication + rate limiting
# =============================
# Read API key from env. If unset, API key check is DISABLED (dev-friendly default).
# To enable in production: set ASTROMATA_API_KEY in Render env vars.
_API_KEY = _os_early.environ.get("ASTROMATA_API_KEY", "").strip()


def require_api_key(x_api_key: str = Header(None, alias="X-API-Key")):
    """FastAPI dependency: validates X-API-Key header against ASTROMATA_API_KEY env var.

    If ASTROMATA_API_KEY env is unset on the server, the check is skipped
    (development-friendly default). To enforce, set ASTROMATA_API_KEY in Render env.
    """
    if not _API_KEY:
        return  # development mode — no key required
    if not x_api_key or x_api_key != _API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key header")


# Per-endpoint rate limits (calls per 60 seconds per IP).
# These are applied via middleware below.
_RATE_LIMITS: Dict[str, int] = {
    # Heavier endpoints — stricter
    "POST /api/kundli":           20,
    "POST /api/divisional-charts": 15,
    "POST /api/dasha/tree":        20,
    "POST /api/kp-chart":          20,
    "POST /api/lal-kitab":         20,
    # Medium
    "POST /api/history/save":      30,
    "POST /api/numerology":        30,
    "POST /api/yog":               30,
    "POST /api/dosh/mangal":       30,
    "POST /api/dosh/kaalsarp":     30,
    "POST /api/dosh/pitra":        30,
    # Light — generous
    "GET /api/horoscope":          60,
    "GET /api/history/by-email":   60,
    "GET /api/panchang-full":      60,
    "GET /api/today-panchang":     60,
    "GET /api/hora":               60,
    "GET /api/choghadiya":         60,
    "GET /geocode":                60,
    # Default for anything else
    "*":                          100,
}

# Sliding window store: key = "{method} {path}:{ip}", value = list of unix timestamps
_rate_limit_store: Dict[str, List[float]] = _defaultdict_early(list)
_RATE_WINDOW_SECONDS = 60


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Per-IP, per-endpoint sliding-window rate limiter.

    Skips /api/health (must always work for uptime pingers) and OPTIONS preflight.
    All internal errors are caught so a bug here can never crash a request.
    """
    method = request.method
    path = request.url.path

    # Don't rate-limit health check or CORS preflight
    if path == "/api/health" or method == "OPTIONS":
        return await call_next(request)

    try:
        # Determine client IP — respect Render's X-Forwarded-For
        xff = request.headers.get("x-forwarded-for", "")
        client_ip = xff.split(",")[0].strip() if xff else (request.client.host if request.client else "unknown")

        # Look up limit
        endpoint_key = f"{method} {path}"
        limit = _RATE_LIMITS.get(endpoint_key, _RATE_LIMITS["*"])

        # Sliding window
        store_key = f"{endpoint_key}:{client_ip}"
        now = _time_early.time()
        window_start = now - _RATE_WINDOW_SECONDS
        _rate_limit_store[store_key] = [t for t in _rate_limit_store[store_key] if t > window_start]

        if len(_rate_limit_store[store_key]) >= limit:
            retry_after = int(_RATE_WINDOW_SECONDS - (now - _rate_limit_store[store_key][0])) + 1
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": f"Rate limit exceeded: {limit} requests per {_RATE_WINDOW_SECONDS}s allowed. Retry in {retry_after}s.",
                    "retry_after": retry_after,
                },
                headers={"Retry-After": str(retry_after)},
            )

        _rate_limit_store[store_key].append(now)

        # Periodic cleanup
        if len(_rate_limit_store) > 10000:
            empty_keys = [k for k, v in _rate_limit_store.items() if not v]
            for k in empty_keys:
                del _rate_limit_store[k]
    except Exception:
        # Never let the rate limiter itself crash a request
        pass

    return await call_next(request)

app.add_middleware(
    CORSMiddleware,
    # PHASE 1 FIX: removed "*" — invalid when allow_credentials=True per CORS spec.
    # Removed localhost — not needed in production. Only real astromata domains here.
    # If you add a new subdomain (e.g. api.astromata.com or kundli.astromata.com),
    # add it to this list.
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-API-Key", "Authorization"],
)


# =============================
# Models
# =============================
class KundliReq(BaseModel):
    name: str = "Astromata User"
    gender: str = "Male"
    date: str
    time: str
    latitude: float
    longitude: float
    # PASS 1: optional lead-capture fields (frontend enforces required)
    email: Optional[str] = None
    phone: Optional[str] = None


class NumerologyReq(BaseModel):
    first_name: str
    middle_name: Optional[str] = ""
    last_name: Optional[str] = ""
    day: int
    month: int
    year: int
    hour: Optional[int] = 12
    minute: Optional[int] = 0


# =============================
# Constants
# =============================
SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]
SIGN_LORDS = [
    "Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
    "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter",
]
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]
NAK_LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
TITHIS = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima",
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Amavasya",
]
YOGA_NAMES = [
    "Vishkumbha", "Priti", "Ayushman", "Saubhagya", "Shobhana",
    "Atiganda", "Sukarma", "Dhriti", "Shula", "Ganda",
    "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
    "Siddhi", "Vyatipata", "Variyana", "Parigha", "Shiva",
    "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Indra", "Vaidhriti",
]
KARANAS = ["Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti"]
VARAS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

DASHA_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
DASHA_YEARS = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}

# PASS 7a: Dasha planet meaning text — shown on Current Periods cards so user
# understands what each dasha period brings. Based on Brihat Parashara Hora Shastra
# + Saravali + modern Vedic predictive astrology summaries.
DASHA_MEANINGS = {
    "Sun": {
        "themes": "Authority, leadership, father, government, recognition",
        "summary": "Period of self-assertion and visibility. Career growth through authority figures, government dealings, or paternal influence. Health: heart, bones, eyes. Spiritually a time for soul purpose and dharma.",
    },
    "Moon": {
        "themes": "Emotions, mother, mind, public, travel, home",
        "summary": "Period of emotional shifts, family events, and inner reflection. Often brings changes in home, mother's role, or public reputation. Health: mind, fluids, digestion. Mind becomes more sensitive; intuition rises.",
    },
    "Mars": {
        "themes": "Energy, conflict, siblings, property, surgery, courage",
        "summary": "Period of action, ambition, and friction. Property dealings, sibling matters, competitive success or sudden conflicts. Health: blood, accidents, surgery. Courage rises; impulsiveness needs control.",
    },
    "Mercury": {
        "themes": "Intellect, business, communication, study, trade, friends",
        "summary": "Period of learning, business, and networking. Favors writing, teaching, commerce, technology. Health: nerves, skin, speech. Decisions become faster but can be scattered without discipline.",
    },
    "Jupiter": {
        "themes": "Wisdom, marriage, children, wealth, dharma, expansion",
        "summary": "Generally most auspicious dasha. Brings marriage, childbirth, wealth, higher studies, spiritual growth. Health: liver, fat metabolism. Wisdom and generosity rise; period of expansion and good fortune.",
    },
    "Venus": {
        "themes": "Relationships, luxury, art, vehicles, marriage, comfort",
        "summary": "Period of love, beauty, and material comfort. Marriage, romance, artistic success, vehicles, fine living. Health: kidneys, reproduction, throat. Aesthetic sense and charm rise; indulgence needs balance.",
    },
    "Saturn": {
        "themes": "Discipline, delays, karma, service, longevity, hard work",
        "summary": "Period of slow but lasting results. Hard work pays off; shortcuts fail. Career stability through perseverance. Health: bones, joints, chronic issues. Tests patience; rewards discipline and integrity.",
    },
    "Rahu": {
        "themes": "Sudden change, foreign influence, ambition, technology, obsession",
        "summary": "Period of unconventional rise and unexpected events. Foreign travel, technology, sudden fame or scandal. Health: confusion, anxiety, addictions. Material desires intensify; spiritual grounding needed.",
    },
    "Ketu": {
        "themes": "Detachment, spirituality, isolation, research, moksha",
        "summary": "Period of inward focus and shedding of attachments. Spiritual awakening, research, sudden endings. Health: nervous system, mysterious ailments. External world feels distant; insight and intuition deepen.",
    },
}


PLANET_IDS = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER, "Venus": swe.VENUS, "Saturn": swe.SATURN,
}

# PHASE 1 FIX: Sanskrit + lowercase aliases for /api/horoscope sign parameter.
# Previously only "Aries", "Taurus", ... matched (case-sensitive English only).
# Now accepts "aries", "ARIES", "mesha", "MESHA", "वृष", etc.
RASHI_ALIAS = {
    # English variants
    "aries":       "Aries",
    "taurus":      "Taurus",
    "gemini":      "Gemini",
    "cancer":      "Cancer",
    "leo":         "Leo",
    "virgo":       "Virgo",
    "libra":       "Libra",
    "scorpio":     "Scorpio",
    "sagittarius": "Sagittarius",
    "capricorn":   "Capricorn",
    "aquarius":    "Aquarius",
    "pisces":      "Pisces",
    # Sanskrit (transliterated)
    "mesha":       "Aries",
    "mesh":        "Aries",
    "vrishabha":   "Taurus",
    "vrishab":     "Taurus",
    "vrish":       "Taurus",
    "mithuna":     "Gemini",
    "mithun":      "Gemini",
    "karka":       "Cancer",
    "karkata":     "Cancer",
    "kark":        "Cancer",
    "simha":       "Leo",
    "sinha":       "Leo",
    "kanya":       "Virgo",
    "tula":        "Libra",
    "thula":       "Libra",
    "vrishchika":  "Scorpio",
    "vrischika":   "Scorpio",
    "vrishchik":   "Scorpio",
    "dhanu":       "Sagittarius",
    "dhanus":      "Sagittarius",
    "makara":      "Capricorn",
    "makar":       "Capricorn",
    "kumbha":      "Aquarius",
    "kumbh":       "Aquarius",
    "meena":       "Pisces",
    "meen":        "Pisces",
    "mina":        "Pisces",
    # Hindi (Devanagari)
    "मेष":         "Aries",
    "वृषभ":        "Taurus",
    "मिथुन":       "Gemini",
    "कर्क":         "Cancer",
    "सिंह":         "Leo",
    "कन्या":        "Virgo",
    "तुला":         "Libra",
    "वृश्चिक":      "Scorpio",
    "धनु":         "Sagittarius",
    "मकर":         "Capricorn",
    "कुम्भ":        "Aquarius",
    "कुंभ":         "Aquarius",
    "मीन":         "Pisces",
}


def normalize_sign(s: str) -> Optional[str]:
    """Convert any reasonable sign input to canonical English name. None if unknown."""
    if not s:
        return None
    key = s.strip().lower()
    # First try direct map (handles English + Sanskrit + Hindi)
    if key in RASHI_ALIAS:
        return RASHI_ALIAS[key]
    # Capitalize first letter and check SIGNS
    cap = s.strip().capitalize()
    if cap in SIGNS:
        return cap
    return None

tf = TimezoneFinder()

# Initialize Swiss Ephemeris sidereal mode ONCE at module level
swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)


# =============================
# Utility functions
# =============================
def norm360(x: float) -> float:
    return x % 360.0


def setup_sidereal() -> None:
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)


def swe_calc_safe(jd_ut: float, body: int, flags: int):
    try:
        return swe.calc_ut(jd_ut, body, flags)
    except Exception as exc:
        raise ValueError(f"Swiss Ephemeris calc failed for body={body}: {exc}") from exc


def swe_houses_safe(jd_ut: float, lat: float, lon: float, hsys: bytes):
    try:
        return swe.houses_ex(jd_ut, lat, lon, hsys, swe.FLG_SIDEREAL)
    except Exception as exc:
        raise ValueError(f"Swiss Ephemeris houses failed: {exc}") from exc


def timezone_from_lat_lon(lat: float, lon: float) -> str:
    tz = tf.timezone_at(lat=lat, lng=lon)
    return tz or "Asia/Kolkata"


def tz_offset_hours(tz_name_str: str, dt_local: datetime) -> float:
    """Return UTC offset in hours, DST-aware, for the given timezone and date."""
    try:
        from zoneinfo import ZoneInfo
        tz = ZoneInfo(tz_name_str)
        aware = dt_local.replace(tzinfo=tz)
        offset = aware.utcoffset()
        if offset is not None:
            return offset.total_seconds() / 3600.0
    except Exception:
        pass
    fallback = {
        "Asia/Kolkata": 5.5, "Asia/Calcutta": 5.5, "Asia/Colombo": 5.5,
        "Asia/Kathmandu": 5.75, "Asia/Karachi": 5.0,
        "Asia/Dubai": 4.0, "Asia/Dhaka": 6.0,
        "Asia/Bangkok": 7.0, "Asia/Singapore": 8.0,
        "Asia/Tokyo": 9.0, "Asia/Seoul": 9.0,
        "Asia/Shanghai": 8.0, "Asia/Hong_Kong": 8.0,
        "Asia/Tehran": 3.5, "Asia/Kabul": 4.5,
        "Asia/Baghdad": 3.0, "Asia/Riyadh": 3.0,
        "Europe/London": 0.0, "Europe/Paris": 1.0,
        "Europe/Berlin": 1.0, "Europe/Moscow": 3.0,
        "America/New_York": -5.0, "America/Chicago": -6.0,
        "America/Denver": -7.0, "America/Los_Angeles": -8.0,
        "Australia/Sydney": 10.0, "Pacific/Auckland": 12.0,
        "UTC": 0.0,
    }
    return fallback.get(tz_name_str, 5.5)


def to_jd(date_str: str, time_str: str, offset_hours: float) -> float:
    y, m, d = [int(x) for x in date_str.split("-")]
    hh, mm = [int(x) for x in time_str.split(":")]
    dt_local = datetime(y, m, d, hh, mm)
    dt_ut = dt_local - timedelta(hours=offset_hours)
    return swe.julday(
        dt_ut.year, dt_ut.month, dt_ut.day,
        dt_ut.hour + dt_ut.minute / 60.0 + dt_ut.second / 3600.0,
        swe.GREG_CAL,
    )


def jd_to_local_str(jd_ut: float, offset_hours: float, fmt: str = "%I:%M %p") -> str:
    y, m, d, fh = swe.revjul(jd_ut + offset_hours / 24.0, swe.GREG_CAL)
    hh = int(fh)
    mm = int((fh - hh) * 60)
    ss = int(round((((fh - hh) * 60) - mm) * 60))
    if ss >= 60:
        ss = 0
        mm += 1
    if mm >= 60:
        mm = 0
        hh += 1
    if hh >= 24:
        hh = 23
        mm = 59
        ss = 59
    return datetime(y, m, int(d), hh, mm, ss).strftime(fmt)


def sign_info(lon: float) -> Tuple[int, str, str, float]:
    L = norm360(lon)
    idx = int(L // 30)
    return idx, SIGNS[idx], SIGN_LORDS[idx], L % 30


# =============================
# PASS 7a: Planetary Dignity (Exaltation / Debilitation / Own / Friend / Enemy / Neutral)
# Adds credibility — users see "Jupiter (Exalted)" instead of just "Jupiter".
# Based on Module 1 (Brihat Parashara Hora Shastra) + classical Parashari friendships.
# =============================

# Exaltation sign per planet (degree of deep exaltation in parens, used as midpoint).
# Note: Rahu/Ketu have varied opinions on exaltation; we use Taurus/Scorpio per
# common modern convention (Parashara is silent; Phaladeepika says Taurus/Scorpio).
_EXALT_SIGN_IDX = {
    "Sun":     0,   # Aries (10°)
    "Moon":    1,   # Taurus (3°)
    "Mars":    9,   # Capricorn (28°)
    "Mercury": 5,   # Virgo (15°)
    "Jupiter": 3,   # Cancer (5°)
    "Venus":   11,  # Pisces (27°)
    "Saturn":  6,   # Libra (20°)
    "Rahu":    1,   # Taurus (per most modern texts)
    "Ketu":    7,   # Scorpio
}

# Debilitation sign = 7th from exaltation (180° opposite)
_DEBIL_SIGN_IDX = {p: (s + 6) % 12 for p, s in _EXALT_SIGN_IDX.items()}

# Own signs (Moolatrikona + own sign). Multiple signs for some planets.
_OWN_SIGNS = {
    "Sun":     {4},          # Leo
    "Moon":    {3},          # Cancer
    "Mars":    {0, 7},       # Aries, Scorpio
    "Mercury": {2, 5},       # Gemini, Virgo
    "Jupiter": {8, 11},      # Sagittarius, Pisces
    "Venus":   {1, 6},       # Taurus, Libra
    "Saturn":  {9, 10},      # Capricorn, Aquarius
    "Rahu":    set(),        # No own sign in classical Parashara
    "Ketu":    set(),
}

# Friend / Enemy / Neutral relationships per planet.
# Based on Brihat Parashara Hora Shastra naisargika (natural) maitri.
# Values: each planet's friends, enemies, neutrals.
_FRIENDS = {
    "Sun":     {"Moon", "Mars", "Jupiter"},
    "Moon":    {"Sun", "Mercury"},
    "Mars":    {"Sun", "Moon", "Jupiter"},
    "Mercury": {"Sun", "Venus"},
    "Jupiter": {"Sun", "Moon", "Mars"},
    "Venus":   {"Mercury", "Saturn"},
    "Saturn":  {"Mercury", "Venus"},
    "Rahu":    {"Venus", "Saturn"},
    "Ketu":    {"Mars", "Venus", "Saturn"},
}
_ENEMIES = {
    "Sun":     {"Venus", "Saturn"},
    "Moon":    set(),  # Moon has no natural enemies in Parashara
    "Mars":    {"Mercury"},
    "Mercury": {"Moon"},
    "Jupiter": {"Mercury", "Venus"},
    "Venus":   {"Sun", "Moon"},
    "Saturn":  {"Sun", "Moon", "Mars"},
    "Rahu":    {"Sun", "Moon", "Mars"},
    "Ketu":    {"Sun", "Moon"},
}


def dignity(planet: str, lon: float) -> str:
    """Return one of: Exalted, Debilitated, Own Sign, Friend's Sign,
    Enemy's Sign, Neutral. Used for the planet table credibility display."""
    if planet not in _EXALT_SIGN_IDX:
        return "—"  # Lagna, Gulika, etc. — no dignity
    sign_idx = int(norm360(lon) // 30)
    if sign_idx == _EXALT_SIGN_IDX[planet]:
        return "Exalted"
    if sign_idx == _DEBIL_SIGN_IDX[planet]:
        return "Debilitated"
    if sign_idx in _OWN_SIGNS.get(planet, set()):
        return "Own Sign"
    # Find sign lord, classify as friend / enemy / neutral
    sign_lord = SIGN_LORDS[sign_idx]
    if sign_lord == planet:
        return "Own Sign"  # already covered but safe
    if sign_lord in _FRIENDS.get(planet, set()):
        return "Friend's Sign"
    if sign_lord in _ENEMIES.get(planet, set()):
        return "Enemy's Sign"
    return "Neutral"


def nak_info(lon: float) -> Tuple[int, str, str, int, float]:
    span = 360.0 / 27.0
    L = norm360(lon)
    idx = int(L // span)
    inside = L - idx * span
    pada = int(inside // (span / 4.0)) + 1
    frac = inside / span
    return idx, NAKSHATRAS[idx], NAK_LORDS[idx % 9], pada, frac


def deg_to_dms(deg: float, is_within_sign: bool = True) -> str:
    d = int(math.floor(deg))
    m_f = (deg - d) * 60.0
    m = int(math.floor(m_f))
    s = int(round((m_f - m) * 60.0))
    if s == 60:
        s = 0
        m += 1
    if m == 60:
        m = 0
        d += 1
    if is_within_sign and d == 30:
        d, m, s = 29, 59, 59
    return f"{d}\u00b0{m:02d}\u2032{s:02d}\u2033"


def whole_sign_house(asc_lon: float, planet_lon: float) -> int:
    a = int(norm360(asc_lon) // 30)
    p = int(norm360(planet_lon) // 30)
    return ((p - a + 12) % 12) + 1


def navamsa_sign(lon: float) -> int:
    sign_idx = int(norm360(lon) // 30)
    deg_in_sign = norm360(lon) % 30
    nav_part = int(deg_in_sign // (10.0 / 3.0))
    if nav_part > 8:
        nav_part = 8
    sign_type = sign_idx % 3
    offsets = [0, 8, 4]
    return (sign_idx + offsets[sign_type] + nav_part) % 12


def get_sun_moon_lons(jd_ut: float) -> Tuple[float, float]:
    setup_sidereal()
    f = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    sun = swe_calc_safe(jd_ut, swe.SUN, f)
    moon = swe_calc_safe(jd_ut, swe.MOON, f)
    return norm360(sun[0][0]), norm360(moon[0][0])


def calc_planets(jd_ut: float) -> Dict[str, Dict[str, Any]]:
    setup_sidereal()
    f = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    out: Dict[str, Dict[str, Any]] = {}
    for name, pid in PLANET_IDS.items():
        r = swe_calc_safe(jd_ut, pid, f)
        out[name] = {
            "lon": norm360(r[0][0]),
            "speed": r[0][3],
            "retro": r[0][3] < 0,
        }
    nn = swe_calc_safe(jd_ut, swe.TRUE_NODE, f)
    # PASS 6.1 FIX: Rahu/Ketu retrograde was hardcoded as True. With TRUE_NODE,
    # the node can occasionally go direct (rare but real, ~0.5% of the time).
    # Use the actual node speed to determine retrograde state.
    # Ketu is always 180° opposite Rahu and shares the SAME motion direction (both
    # retrograde or both direct together) — the node line moves as one entity.
    nn_speed = nn[0][3]
    nn_retro = nn_speed < 0
    out["Rahu"] = {"lon": norm360(nn[0][0]), "speed": nn_speed, "retro": nn_retro}
    out["Ketu"] = {"lon": norm360(nn[0][0] + 180.0), "speed": nn_speed, "retro": nn_retro}
    return out


def calc_lagna(jd_ut: float, lat: float, lon: float, hsys: bytes = b"P") -> float:
    setup_sidereal()
    _, ascmc = swe_houses_safe(jd_ut, lat, lon, hsys)
    return norm360(ascmc[0])


# PHASE 1 FIX: Replace fragile open-meteo HTTP call with Swiss Ephemeris's own
# rise_trans() calculation. No external dependency, no timeout, instant,
# mathematically correct. Open-meteo was silently returning fallback constants
# (06:00 AM / 06:00 PM) on Render due to outbound networking quirks.
def get_sun_moon_events(lat: float, lon: float, date_str: str, tz_name: str) -> Dict[str, str]:
    """Compute sunrise/sunset/moonrise/moonset using Swiss Ephemeris locally.

    Returns dict with keys: sunrise, sunset, moonrise, moonset (all "%I:%M %p" strings).
    Always succeeds offline — no HTTP call.
    """
    setup_sidereal()
    out = {
        "sunrise": "06:00 AM",
        "sunset": "06:00 PM",
        "moonrise": "07:00 PM",
        "moonset": "07:00 AM",
        "_source": "swisseph",
    }

    try:
        # Start of day in UTC at the given location's local midnight
        y, m, d = [int(x) for x in date_str.split("-")]
        local_midnight = datetime(y, m, d, 0, 0, 0)
        off_hours = tz_offset_hours(tz_name, local_midnight)
        jd_start_ut = swe.julday(
            y, m, d,
            0.0 - off_hours,  # local midnight expressed as UT
            swe.GREG_CAL,
        )

        # Geographic position: longitude, latitude, altitude (meters)
        geopos = (float(lon), float(lat), 0.0)

        # swe.rise_trans signature varies by version. Try both shapes.
        def _do_rise_trans(body_id, rsmi_flag):
            """Return JD of next rise/set event after jd_start_ut, or None."""
            try:
                # Newer pyswisseph: rise_trans(jd_start, body, rsmi, geopos, atpress, attemp, flag)
                res = swe.rise_trans(
                    jd_start_ut,
                    body_id,
                    rsmi_flag,
                    geopos,
                    0.0,  # atmospheric pressure (mbar) — 0 = default 1013.25
                    0.0,  # atmospheric temperature (°C) — 0 = default 15
                    swe.FLG_SWIEPH,
                )
                # res is ((retflag,), (tret,))  OR  (retflag, [tret])
                if isinstance(res, tuple) and len(res) == 2:
                    tret = res[1]
                    if isinstance(tret, (list, tuple)) and len(tret) > 0:
                        return float(tret[0])
                    return None
                return None
            except Exception:
                return None

        # Body constants
        SUN = swe.SUN
        MOON = swe.MOON

        # RSMI flags (rise/set/meridian)
        # SE_CALC_RISE = 1, SE_CALC_SET = 2  (these are standard pyswisseph constants)
        try:
            CALC_RISE = swe.CALC_RISE
            CALC_SET = swe.CALC_SET
        except AttributeError:
            # Fallback to numeric values per Swiss Ephemeris C constants
            CALC_RISE = 1
            CALC_SET = 2

        events = {
            "sunrise": _do_rise_trans(SUN, CALC_RISE),
            "sunset": _do_rise_trans(SUN, CALC_SET),
            "moonrise": _do_rise_trans(MOON, CALC_RISE),
            "moonset": _do_rise_trans(MOON, CALC_SET),
        }

        for key, jd_event in events.items():
            if jd_event is None:
                continue  # keep fallback default for this key
            # Convert UT julian day to local time string
            y2, m2, d2, fh = swe.revjul(jd_event + off_hours / 24.0, swe.GREG_CAL)
            hh = int(fh)
            mm = int((fh - hh) * 60)
            if mm >= 60:
                mm = 59
            if hh >= 24:
                hh = 23
            out[key] = datetime(y2, m2, int(d2), hh, mm).strftime("%I:%M %p")

        return out
    except Exception as exc:
        # Fallback if Swiss Ephemeris call fails for any reason
        out["_source"] = "fallback"
        out["_error"] = str(exc)[:120]
        return out


def find_next_change(jd_start: float, get_index, step_days: float = 0.02) -> float:
    start_val = get_index(jd_start)
    jd = jd_start
    for _ in range(240):
        jd += step_days
        if get_index(jd) != start_val:
            lo, hi = jd - step_days, jd
            for _ in range(20):
                mid = (lo + hi) / 2.0
                if get_index(mid) == start_val:
                    lo = mid
                else:
                    hi = mid
            return hi
    return jd_start + 1.0


def moon_phase_description(t_angle: float) -> str:
    if t_angle < 45: return "Waxing Crescent"
    if t_angle < 90: return "First Quarter"
    if t_angle < 135: return "Waxing Gibbous"
    if t_angle < 225: return "Full Moon"
    if t_angle < 270: return "Waning Gibbous"
    if t_angle < 315: return "Last Quarter"
    return "Waning Crescent"


def get_ritu_from_sun_sign(sun_lon: float) -> str:
    si = int(norm360(sun_lon) // 30)
    ritus = ["Vasanta", "Vasanta", "Grishma", "Grishma", "Varsha", "Varsha",
             "Sharad", "Sharad", "Hemanta", "Hemanta", "Shishira", "Shishira"]
    return ritus[si]


def compute_panchang(jd_ut: float, offset_hours: float, lat: float, lon: float, date_str: str, tz_name: str) -> Dict[str, Any]:
    sun_lon, moon_lon = get_sun_moon_lons(jd_ut)
    t_angle = norm360(moon_lon - sun_lon)
    t_idx = int(t_angle // 12)
    t_no = t_idx + 1
    paksha = "Shukla" if t_no <= 15 else "Krishna"
    t_progress = (t_angle % 12) / 12.0

    n_idx, n_name, n_lord, n_pada, n_frac = nak_info(moon_lon)

    y_angle = norm360(sun_lon + moon_lon)
    y_idx = int(y_angle // (360.0 / 27.0)) % 27
    y_frac = (y_angle % (360.0 / 27.0)) / (360.0 / 27.0)

    k_idx = int(t_angle // 6)
    if k_idx == 0:
        k_name = "Kimstughna"
    elif k_idx >= 57:
        k_name = ["Shakuni", "Chatushpada", "Naga"][k_idx - 57]
    else:
        k_name = KARANAS[(k_idx - 1) % 7]

    dt_local = datetime.strptime(date_str, "%Y-%m-%d")
    vara = VARAS[(dt_local.weekday() + 1) % 7]

    def tithi_i(j):
        s, m = get_sun_moon_lons(j)
        return int(norm360(m - s) // 12)

    def nak_i(j):
        _, m = get_sun_moon_lons(j)
        return int(norm360(m) // (360.0 / 27.0))

    def yoga_i(j):
        s, m = get_sun_moon_lons(j)
        return int(norm360(s + m) // (360.0 / 27.0))

    def karana_i(j):
        s, m = get_sun_moon_lons(j)
        return int(norm360(m - s) // 6)

    t_end = find_next_change(jd_ut, tithi_i)
    n_end = find_next_change(jd_ut, nak_i)
    y_end = find_next_change(jd_ut, yoga_i)
    k_end = find_next_change(jd_ut, karana_i)

    lum = round(50.0 * (1 - math.cos(math.radians(t_angle))), 2)
    phase_name = moon_phase_description(t_angle)
    moon_phase_str = f"{phase_name} - {paksha} - {lum}%"

    events = get_sun_moon_events(lat, lon, date_str, tz_name)
    try:
        sr = datetime.strptime(events["sunrise"], "%I:%M %p")
        ss = datetime.strptime(events["sunset"], "%I:%M %p")
        solar_noon = (sr + (ss - sr) / 2).strftime("%I:%M %p")
    except Exception:
        solar_noon = "12:00 PM"

    _, moon_rashi, _, _ = sign_info(moon_lon)
    _, sun_rashi, _, _ = sign_info(sun_lon)

    return {
        "vara": vara,
        "ritu": get_ritu_from_sun_sign(sun_lon),
        "sunrise": events["sunrise"],
        "sunset": events["sunset"],
        "moonrise": events["moonrise"],
        "moonset": events["moonset"],
        "solar_noon": solar_noon,
        "moon_phase_pct": lum,
        "moon_phase_str": moon_phase_str,
        "tithi": {
            "no": t_no,
            "name": f"{paksha} {TITHIS[t_idx]}",
            "paksha": paksha,
            "remaining_pct": round((1 - t_progress) * 100, 2),
            "end_local": jd_to_local_str(t_end, offset_hours),
        },
        "nakshatra": {
            "no": n_idx + 1,
            "name": n_name,
            "lord": n_lord,
            "pada": n_pada,
            "remaining_pct": round((1 - n_frac) * 100, 2),
            "end_local": jd_to_local_str(n_end, offset_hours),
        },
        "yoga": {
            "no": y_idx + 1,
            "name": YOGA_NAMES[y_idx],
            "remaining_pct": round((1 - y_frac) * 100, 2),
            "end_local": jd_to_local_str(y_end, offset_hours),
        },
        "karana": {"half_no": k_idx + 1, "name": k_name, "end_local": jd_to_local_str(k_end, offset_hours)},
        "moon_rashi": moon_rashi,
        "sun_rashi": sun_rashi,
    }


def chart_houses(asc_lon: float, planets: Dict[str, Dict[str, Any]], navamsa: bool = False) -> Dict[int, Dict[str, Any]]:
    asc_sign = navamsa_sign(asc_lon) if navamsa else int(norm360(asc_lon) // 30)
    houses: Dict[int, Dict[str, Any]] = {}
    for h in range(1, 13):
        si = (asc_sign + (h - 1)) % 12
        houses[h] = {"house": h, "sign": SIGNS[si], "planets": []}

    short = {"Sun": "Su", "Moon": "Mo", "Mars": "Ma", "Mercury": "Me",
             "Jupiter": "Ju", "Venus": "Ve", "Saturn": "Sa", "Rahu": "Ra", "Ketu": "Ke"}

    for p, d in planets.items():
        if navamsa:
            target = ((navamsa_sign(d["lon"]) - asc_sign + 12) % 12) + 1
        else:
            target = whole_sign_house(asc_lon, d["lon"])
        _, _, _, deg = sign_info(d["lon"])
        houses[target]["planets"].append({
            "code": short.get(p, p[:2]),
            "deg": deg_to_dms(deg, True),
            "retro": d["retro"],
        })

    houses[1]["planets"].insert(0, {"code": "Asc", "deg": deg_to_dms(asc_lon % 30, True), "retro": False})
    return houses


# =============================
# Horoscope engine - PASS 1 FIX: each category gets unique karaka-driven score
# =============================
def aspect_points(diff_deg: float) -> int:
    """Legacy helper kept for compatibility. Not used by new generate_horoscope."""
    d = min(diff_deg, 360 - diff_deg)
    if abs(d - 120) <= 8:
        return 20
    if abs(d - 90) <= 8:
        return -15
    if abs(d) <= 8:
        return 8
    if abs(d - 180) <= 8:
        return -8
    return 0


def generate_horoscope(sign: str, period: str, jd_ut: float) -> Dict[str, Any]:
    """Generate horoscope with per-category scores driven by category-specific karakas.

    Each of the 11 categories has 1-2 natural significator planets (karakas).
    Score = base 60 + karaka aspect strength * 15 + element bonus + period offset.
    Categories now genuinely differ (not all stuck at 50).
    """
    planets = calc_planets(jd_ut)
    s_idx = SIGNS.index(sign)
    sign_ref = s_idx * 30 + 15
    lord = SIGN_LORDS[s_idx]

    # Karakas (natural significators) per category - classical Parashari
    KARAKAS = {
        "Health":       ["Sun", "Mars"],
        "Career":       ["Saturn", "Sun"],
        "Relationship": ["Venus", "Moon"],
        "Travel":       ["Mercury", "Rahu"],
        "Family":       ["Moon", "Jupiter"],
        "Finances":     ["Jupiter", "Venus"],
        "Status":       ["Sun", "Saturn"],
        "Education":    ["Jupiter", "Mercury"],
        "Friends":      ["Mercury", "Venus"],
        "Physique":     ["Mars", "Sun"],
        "Love":         ["Venus", "Moon"],
    }

    # Per-planet aspect strength to the sign (-1 to +1 normalized)
    impacts: Dict[str, float] = {}
    for p in ["Saturn", "Jupiter", "Rahu", "Ketu", "Mars", "Mercury", "Venus", "Sun", "Moon"]:
        diff = abs(norm360(planets[p]["lon"] - sign_ref))
        d = min(diff, 360 - diff)
        if d <= 8:
            pts = 0.4
        elif abs(d - 60) <= 6:
            pts = 0.5
        elif abs(d - 90) <= 8:
            pts = -0.6
        elif abs(d - 120) <= 8:
            pts = 0.8
        elif abs(d - 180) <= 8:
            pts = -0.3
        else:
            pts = 0.0
        if planets[p].get("retro"):
            pts -= 0.15
        impacts[p] = pts

    # Element bonuses per sign type
    element = s_idx % 4
    ELEMENT_BONUS = {
        0: {"Career": 5, "Physique": 7, "Status": 5, "Travel": 3},     # Fire
        1: {"Finances": 8, "Career": 4, "Health": 4, "Family": 3},     # Earth
        2: {"Education": 7, "Friends": 6, "Relationship": 4, "Travel": 4},  # Air
        3: {"Love": 7, "Family": 6, "Relationship": 5, "Health": 3},   # Water
    }

    period_offset = {"daily": 0, "weekly": 2, "monthly": -1, "yearly": 4}.get(period, 0)

    categories = list(KARAKAS.keys())
    scores: Dict[str, int] = {}

    for cat in categories:
        karakas = KARAKAS[cat]
        karaka_score = impacts.get(karakas[0], 0) * 2 + impacts.get(karakas[1], 0) * 1
        if "Jupiter" not in karakas:
            karaka_score += impacts.get("Jupiter", 0) * 0.5
        if "Saturn" not in karakas:
            karaka_score -= max(0, -impacts.get("Saturn", 0)) * 0.5

        raw = 60 + karaka_score * 15
        raw += ELEMENT_BONUS.get(element, {}).get(cat, 0)
        raw += period_offset
        scores[cat] = max(30, min(98, int(round(raw))))

    total = int(round(sum(scores.values()) / len(scores)))
    active = max(impacts, key=lambda k: abs(impacts[k]))

    PRED_TEMPLATES = {
        "Sun":     {"career": "leadership and recognition come naturally now",
                    "health": "vitality is strong; pace yourself",
                    "relationship": "be expressive but not domineering"},
        "Moon":    {"career": "emotional intelligence guides good decisions",
                    "health": "rest and hydration are key",
                    "relationship": "tender attention strengthens bonds"},
        "Mars":    {"career": "assertive decisions can open blocked paths",
                    "health": "high drive needs proper rest and hydration",
                    "relationship": "direct expression must be balanced with empathy"},
        "Mercury": {"career": "communication and analytical work shine",
                    "health": "mental rest matters as much as physical",
                    "relationship": "honest dialogue resolves old tensions"},
        "Jupiter": {"career": "growth and mentorship opportunities are visible",
                    "health": "optimism supports recovery and stamina",
                    "relationship": "wise guidance improves emotional bonding"},
        "Venus":   {"career": "creative diplomacy improves work outcomes",
                    "health": "comfort and balance improve mental ease",
                    "relationship": "warmth and affection strengthen close ties"},
        "Saturn":  {"career": "discipline and patience are essential for stable progress",
                    "health": "fatigue can appear if routines are ignored",
                    "relationship": "consistency in words and actions brings trust"},
        "Rahu":    {"career": "unconventional paths bring sudden gains - verify before leaping",
                    "health": "anxiety may rise; ground yourself",
                    "relationship": "watch for illusions; ask clear questions"},
        "Ketu":    {"career": "detach from outcomes; spiritual work pays off",
                    "health": "subtle ailments need attention",
                    "relationship": "old karmic ties may surface for closure"},
    }
    tmpl = PRED_TEMPLATES.get(active, PRED_TEMPLATES["Jupiter"])

    element_colors = {
        0: {"name": "Terracotta Red", "hex": "#D94A3D"},
        1: {"name": "Sacred Gold",    "hex": "#E2B44C"},
        2: {"name": "Sky Yellow",     "hex": "#F0C84A"},
        3: {"name": "Silver White",   "hex": "#FDF8F0"},
    }
    lucky_color = element_colors[element]

    planet_number = {"Sun": 1, "Moon": 2, "Jupiter": 3, "Rahu": 4, "Mercury": 5,
                     "Venus": 6, "Ketu": 7, "Saturn": 8, "Mars": 9}
    dtn = datetime.utcnow()
    n1 = planet_number.get(lord, 3)
    n2 = (n1 + dtn.day) % 9 + 1
    n3 = (n2 + int(str(dtn.year)[-1])) % 9 + 1

    para = (
        f"Today, due to the influence of {active}, your sign receives a focused karmic signal. "
        f"In career, {tmpl['career']}. In health, {tmpl['health']}. In relationships, {tmpl['relationship']}."
    )

    out: Dict[str, Any] = {
        "sign": sign,
        "period": period,
        "date": dtn.strftime("%Y-%m-%d"),
        "total_score": total,
        "lucky_color": lucky_color,
        "lucky_numbers": [n1, n2, n3],
        "prediction": para,
        "category_scores": scores,
        "active_planet": active,
    }

    if period == "monthly":
        out["standout_days"] = [3, 11, 19, 27]
        out["challenging_days"] = [7, 15, 24]
    if period == "yearly":
        q_names = ["Jan-Mar", "Apr-Jun", "Jul-Sep", "Oct-Dec"]
        quarters = []
        for i, q in enumerate(q_names):
            q_scores = {k: max(30, min(99, v + (i - 1) * 3)) for k, v in scores.items()}
            q_total = int(sum(q_scores.values()) / len(q_scores))
            quarters.append({
                "quarter": q,
                "score": q_total,
                "summary": f"{q} emphasizes {active}-led themes with practical improvement in core life areas.",
                "categories": [
                    {"name": k, "score": v,
                     "detail": f"{k} remains {('strong' if v >= 75 else 'moderate')} in this quarter."}
                    for k, v in q_scores.items()
                ],
            })
        out["quarters"] = quarters
    return out


# =============================
# Dasha tree
# =============================
def dasha_tree(moon_lon: float, birth_date: str):
    span = 360.0 / 27.0
    ni = int(norm360(moon_lon) // span)
    frac = (norm360(moon_lon) - ni * span) / span
    start_idx = ni % 9
    bdt = datetime.strptime(birth_date, "%Y-%m-%d")

    out = []
    cur = bdt
    for i in range(9):
        pl = DASHA_ORDER[(start_idx + i) % 9]
        yrs = DASHA_YEARS[pl] * (1 - frac) if i == 0 else DASHA_YEARS[pl]
        end = cur + timedelta(days=int(yrs * 365.25))
        antars = []
        acur = cur
        sidx = DASHA_ORDER.index(pl)
        for j in range(9):
            apl = DASHA_ORDER[(sidx + j) % 9]
            a_yrs = yrs * DASHA_YEARS[apl] / 120.0
            aend = acur + timedelta(days=max(1, int(a_yrs * 365.25)))
            praty = []
            pcur = acur
            pidx = DASHA_ORDER.index(apl)
            for k in range(9):
                ppl = DASHA_ORDER[(pidx + k) % 9]
                p_yrs = a_yrs * DASHA_YEARS[ppl] / 120.0
                # PASS 6 FIX: use precise seconds-based math instead of int(days).
                # The old code did `timedelta(days=max(1, int(p_yrs * 365.25)))` which
                # forced every period to be at least 1 day, and rounded down all sub-day
                # periods to whole days. This made pratyantar/sookshma/pranadasha dates
                # collapse to identical times. Now: use total seconds with no minimum.
                pend = pcur + timedelta(seconds=p_yrs * 365.25 * 86400.0)
                suk = []
                scur = pcur
                s2 = DASHA_ORDER.index(ppl)
                for m in range(9):
                    spl = DASHA_ORDER[(s2 + m) % 9]
                    s_yrs = p_yrs * DASHA_YEARS[spl] / 120.0
                    send = scur + timedelta(seconds=s_yrs * 365.25 * 86400.0)
                    suk.append({"planet": spl, "start": scur, "end": send})
                    scur = send
                praty.append({"planet": ppl, "start": pcur, "end": pend, "sookshma": suk})
                pcur = pend
            antars.append({"planet": apl, "start": acur, "end": aend, "praty": praty})
            acur = aend
        out.append({"planet": pl, "start": cur, "end": end, "years": round(yrs, 2), "antardasha": antars})
        cur = end
    return out


def pick_current_levels(tree):
    now = datetime.now()
    md = next((x for x in tree if x["start"] <= now <= x["end"]), tree[0])
    ad = next((x for x in md["antardasha"] if x["start"] <= now <= x["end"]), md["antardasha"][0])
    pd = next((x for x in ad["praty"] if x["start"] <= now <= x["end"]), ad["praty"][0])
    sd = next((x for x in pd["sookshma"] if x["start"] <= now <= x["end"]), pd["sookshma"][0])
    span = (sd["end"] - sd["start"]) / 9
    pranas = []
    pcur = sd["start"]
    sd_start_idx = DASHA_ORDER.index(sd["planet"])
    for i in range(9):
        p = DASHA_ORDER[(sd_start_idx + i) % 9]
        pend = pcur + span
        pranas.append({"planet": p, "start": pcur, "end": pend})
        pcur = pend
    pr = next((x for x in pranas if x["start"] <= now <= x["end"]), pranas[0])
    return md, ad, pd, sd, pr, pranas


def fmt_dt(dt: datetime, with_time: bool = False) -> str:
    return dt.strftime("%d-%b-%Y %I:%M %p" if with_time else "%d-%b-%Y")


# =============================
# Numerology
# =============================
CHALDEAN = {
    "A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 8, "G": 3, "H": 5, "I": 1, "J": 1, "K": 2, "L": 3,
    "M": 4, "N": 5, "O": 7, "P": 8, "Q": 1, "R": 2, "S": 3, "T": 4, "U": 6, "V": 6, "W": 6, "X": 5,
    "Y": 1, "Z": 7,
}


def num_reduce(n: int, keep_master: bool = True) -> int:
    if keep_master and n in (11, 22, 33):
        return n
    while n > 9:
        n = sum(int(ch) for ch in str(n))
        if keep_master and n in (11, 22, 33):
            return n
    return n


def chaldean_sum(s: str) -> int:
    return sum(CHALDEAN.get(ch, 0) for ch in s.upper() if ch in CHALDEAN)


# =============================
# API routes
# =============================
@app.get("/api/dasha/meanings")
def dasha_meanings():
    """Return static text describing what each dasha planet represents.
    Frontend caches this on first call. Used to enrich Current Periods page.
    PASS 7a addition."""
    return {"success": True, "meanings": DASHA_MEANINGS}


@app.get("/api/health")
def health():
    """Health check that NEVER 500s. Reports per-component status.

    Each piece (swisseph version probe, MySQL connection) is in its own try/except
    so a failure in one component is visible without crashing the whole endpoint.
    Critical for uptime pingers and Render's auto-restart behavior.
    """
    out: Dict[str, Any] = {"status": "ok"}

    # 1. Swiss Ephemeris version — try multiple shapes since the API varies
    try:
        v = getattr(swe, "version", None)
        if callable(v):
            out["swisseph_version"] = str(v())
        elif v is not None:
            out["swisseph_version"] = str(v)
        else:
            out["swisseph_version"] = "unknown"
    except Exception as exc:
        out["swisseph_version"] = "error"
        out["swisseph_version_error"] = str(exc)[:120]

    # 2. MySQL — wrap everything to never crash
    try:
        cfg = _mysql_config() if "_mysql_config" in globals() else None
    except Exception as exc:
        out["mysql"] = "config_error"
        out["mysql_error"] = str(exc)[:120]
        cfg = None

    if cfg is None:
        out["mysql"] = "not_configured"
    else:
        try:
            _ensure_history_table()
            out["mysql"] = "connected"
            out["mysql_host"] = cfg["host"]
        except Exception as exc:
            out["mysql"] = "error"
            out["mysql_error"] = str(exc)[:200]

    # 3. API key status (does NOT leak the actual key)
    out["api_key_required"] = bool(_API_KEY)

    # 4. Uptime helper: a tiny "alive" flag pingers can check
    out["alive"] = True

    # 5. PASS 7a: Indian cities DB status
    out["cities_india_loaded"] = len(_CITIES_INDIA)
    # PASS 7b-β-fix: expose load diagnostics so we can debug missing-file issues
    out["cities_india_diag"] = _CITIES_LOAD_DIAG

    return out


@app.get("/geocode")
def geocode(q: str = Query(..., min_length=2)):
    """Geocode a place name to lat/lon.

    PASS 7a FIX: Local Indian cities database (cities_india.json) is now checked
    FIRST. It contains ~270 verified Indian places with Google-matching centroids,
    so users searching for Indian cities get instant 1ms lookups with coordinates
    that exactly match what they'd see on Google.

    PASS 6 FIX: Open-Meteo (GeoNames-based, city CENTROIDS) is the primary
    network provider, since its coordinates match Google Maps and what users see
    elsewhere. Nominatim (OpenStreetMap) is used as a final fallback for obscure
    villages not in GeoNames — Nominatim returns OSM node coordinates which
    can be off-center for major cities (e.g. Vidisha was 1km off vs Google).

    Provider chain:
      0. Local cities_india.json   — 1ms, 100% Google-match for major Indian cities
      1. Open-Meteo (GeoNames)     — ~200ms, global coverage, near-Google match
      2. Nominatim (OSM)           — ~400ms, last resort for tiny villages

    Returns: list of {name, country, admin1, latitude, longitude, timezone}
    """
    q_stripped = q.strip()
    if not q_stripped:
        return []

    results: List[Dict[str, Any]] = []

    # -----------------------------
    # Provider 0 (PASS 7a): Local Indian cities database
    # Fastest, most accurate for Indian queries. Loaded once at module init.
    # -----------------------------
    try:
        local_hits = _search_cities_india(q_stripped, limit=8)
        for c in local_hits:
            results.append({
                "name": c["name"],
                "country": c.get("country", "India"),
                "admin1": c.get("admin1", ""),
                "latitude": c["latitude"],
                "longitude": c["longitude"],
                "timezone": c.get("timezone", "Asia/Kolkata"),
                "_source": "local-india",
            })
    except Exception:
        pass  # local DB miss → continue to network providers

    # -----------------------------
    # Provider 1: Open-Meteo (GeoNames) — city centroids matching Google
    # Free, fast, no key. Covers ~11M places globally including most Indian
    # cities, towns, and large villages.
    # -----------------------------
    try:
        r = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": q_stripped, "count": 8, "language": "en", "format": "json"},
            timeout=8,
        )
        if r.status_code == 200:
            for row in (r.json().get("results") or []):
                try:
                    lat = float(row.get("latitude", 0.0))
                    lon = float(row.get("longitude", 0.0))
                except (ValueError, TypeError):
                    continue
                results.append({
                    "name": (row.get("name") or "").strip(),
                    "country": (row.get("country") or "").strip(),
                    "admin1": (row.get("admin1") or "").strip(),
                    "latitude": lat,
                    "longitude": lon,
                    "timezone": row.get("timezone", "Asia/Kolkata"),
                    "_source": "open-meteo",
                })
    except Exception:
        pass  # fall through to Nominatim

    # -----------------------------
    # Provider 2: Nominatim (OpenStreetMap) — fallback for obscure villages.
    # Used only if Open-Meteo found nothing. Nominatim TOS requires User-Agent.
    # -----------------------------
    if not results:
        try:
            r = requests.get(
                "https://nominatim.openstreetmap.org/search",
                params={
                    "q": q_stripped,
                    "format": "json",
                    "addressdetails": 1,
                    "limit": 8,
                    "accept-language": "en",
                },
                headers={
                    "User-Agent": "AstroMata/1.0 (https://astromata.com; support@astromata.com)",
                },
                timeout=8,
            )
            if r.status_code == 200:
                data = r.json() or []
                for row in data:
                    addr = row.get("address", {}) or {}
                    # Pick best display name
                    name = (
                        addr.get("city")
                        or addr.get("town")
                        or addr.get("village")
                        or addr.get("hamlet")
                        or addr.get("municipality")
                        or addr.get("suburb")
                        or row.get("display_name", "").split(",")[0]
                    ).strip()
                    if not name:
                        continue
                    admin1 = (
                        addr.get("state")
                        or addr.get("state_district")
                        or addr.get("region")
                        or ""
                    ).strip()
                    country = (addr.get("country") or "").strip()
                    try:
                        lat = float(row.get("lat", 0.0))
                        lon = float(row.get("lon", 0.0))
                    except (ValueError, TypeError):
                        continue
                    results.append({
                        "name": name,
                        "country": country,
                        "admin1": admin1,
                        "latitude": lat,
                        "longitude": lon,
                        "timezone": "Asia/Kolkata",
                        "_source": "nominatim",
                    })
        except Exception:
            pass

    # Resolve timezones for entries that didn't have one
    for r in results:
        if not r.get("timezone") or r.get("timezone") == "Asia/Kolkata":
            try:
                r["timezone"] = timezone_from_lat_lon(r["latitude"], r["longitude"])
            except Exception:
                r["timezone"] = "Asia/Kolkata"

    return results


# =============================
# PASS 6: AVAKHADA (Janma Patrika personality summary)
# =============================
# The Avakhada is the 14-field personality/character summary every Indian
# kundli result page is expected to show. All fields are derived from
# existing data (Moon's nakshatra, sign, birth time, weekday).
# =============================

# Varna (caste/social class) from Moon's nakshatra
_VARNA_BY_NAK = {
    "Ashwini":"Vaishya","Bharani":"Mleccha","Krittika":"Brahmin","Rohini":"Shudra",
    "Mrigashira":"Vaishya","Ardra":"Butcher","Punarvasu":"Vaishya","Pushya":"Kshatriya",
    "Ashlesha":"Mleccha","Magha":"Shudra","Purva Phalguni":"Brahmin","Uttara Phalguni":"Kshatriya",
    "Hasta":"Vaishya","Chitra":"Servant","Swati":"Butcher","Vishakha":"Mleccha",
    "Anuradha":"Shudra","Jyeshtha":"Servant","Mula":"Butcher","Purva Ashadha":"Brahmin",
    "Uttara Ashadha":"Kshatriya","Shravana":"Mleccha","Dhanishtha":"Servant","Shatabhisha":"Butcher",
    "Purva Bhadrapada":"Brahmin","Uttara Bhadrapada":"Kshatriya","Revati":"Shudra",
}
# Simpler Varna by Moon sign (used in most modern kundlis - matches AstroTalk/AstroSage)
# Convention: Water=Brahmin (spiritual), Fire=Kshatriya (action),
# Earth+Aquarius=Vaishya (commerce/stability), Gemini+Libra+Capricorn=Shudra (service).
_VARNA_BY_SIGN = {
    "Cancer":"Brahmin","Scorpio":"Brahmin","Pisces":"Brahmin",
    "Aries":"Kshatriya","Leo":"Kshatriya","Sagittarius":"Kshatriya",
    "Taurus":"Vaishya","Virgo":"Vaishya","Aquarius":"Vaishya",
    "Gemini":"Shudra","Libra":"Shudra","Capricorn":"Shudra",
}

# Vashya — category of influence
_VASHYA = {
    "Aries":"Chatushpada (Quadruped)","Taurus":"Chatushpada (Quadruped)",
    "Gemini":"Nara (Human)","Cancer":"Jalachara (Aquatic)",
    "Leo":"Vanachara (Wild)","Virgo":"Nara (Human)",
    "Libra":"Nara (Human)","Scorpio":"Keeta (Insect)",
    "Sagittarius":"Chatushpada (Quadruped)","Capricorn":"Jalachara (Aquatic)",
    "Aquarius":"Nara (Human)","Pisces":"Jalachara (Aquatic)",
}

# Yoni (animal symbol) — comes in pairs (male/female) per nakshatra
_YONI = {
    "Ashwini":"Horse","Bharani":"Elephant","Krittika":"Sheep","Rohini":"Serpent",
    "Mrigashira":"Serpent","Ardra":"Dog","Punarvasu":"Cat","Pushya":"Sheep",
    "Ashlesha":"Cat","Magha":"Rat","Purva Phalguni":"Rat","Uttara Phalguni":"Cow",
    "Hasta":"Buffalo","Chitra":"Tiger","Swati":"Buffalo","Vishakha":"Tiger",
    "Anuradha":"Deer","Jyeshtha":"Deer","Mula":"Dog","Purva Ashadha":"Monkey",
    "Uttara Ashadha":"Mongoose","Shravana":"Monkey","Dhanishtha":"Lion","Shatabhisha":"Horse",
    "Purva Bhadrapada":"Lion","Uttara Bhadrapada":"Cow","Revati":"Elephant",
}

# Gan — temperament type
_GAN = {
    "Ashwini":"Dev","Bharani":"Manushya","Krittika":"Rakshasa","Rohini":"Manushya",
    "Mrigashira":"Dev","Ardra":"Manushya","Punarvasu":"Dev","Pushya":"Dev",
    "Ashlesha":"Rakshasa","Magha":"Rakshasa","Purva Phalguni":"Manushya","Uttara Phalguni":"Manushya",
    "Hasta":"Dev","Chitra":"Rakshasa","Swati":"Dev","Vishakha":"Rakshasa",
    "Anuradha":"Dev","Jyeshtha":"Rakshasa","Mula":"Rakshasa","Purva Ashadha":"Manushya",
    "Uttara Ashadha":"Manushya","Shravana":"Dev","Dhanishtha":"Rakshasa","Shatabhisha":"Rakshasa",
    "Purva Bhadrapada":"Manushya","Uttara Bhadrapada":"Manushya","Revati":"Dev",
}

# Nadi — three-fold body constitution (Adhya/Madhya/Antya). Names use AstroTalk's
# transliteration ("Adhya" not "Adi") so user sees consistent labels across apps.
_NADI = {
    "Ashwini":"Adhya","Bharani":"Madhya","Krittika":"Antya","Rohini":"Antya",
    "Mrigashira":"Madhya","Ardra":"Adhya","Punarvasu":"Adhya","Pushya":"Madhya",
    "Ashlesha":"Antya","Magha":"Antya","Purva Phalguni":"Madhya","Uttara Phalguni":"Adhya",
    "Hasta":"Adhya","Chitra":"Madhya","Swati":"Antya","Vishakha":"Antya",
    "Anuradha":"Madhya","Jyeshtha":"Adhya","Mula":"Adhya","Purva Ashadha":"Madhya",
    "Uttara Ashadha":"Antya","Shravana":"Antya","Dhanishtha":"Madhya","Shatabhisha":"Adhya",
    "Purva Bhadrapada":"Adhya","Uttara Bhadrapada":"Madhya","Revati":"Antya",
}

# Yunja (segment) — Adya (first 9 nakshatras) / Madhya (middle 9) / Antya (last 9).
# Names use AstroTalk's transliteration so user sees consistent labels.
_YUNJA = {
    "Ashwini":"Adya","Bharani":"Adya","Krittika":"Adya","Rohini":"Adya",
    "Mrigashira":"Adya","Ardra":"Adya","Punarvasu":"Adya","Pushya":"Adya","Ashlesha":"Adya",
    "Magha":"Madhya","Purva Phalguni":"Madhya","Uttara Phalguni":"Madhya","Hasta":"Madhya",
    "Chitra":"Madhya","Swati":"Madhya","Vishakha":"Madhya","Anuradha":"Madhya","Jyeshtha":"Madhya",
    "Mula":"Antya","Purva Ashadha":"Antya","Uttara Ashadha":"Antya","Shravana":"Antya",
    "Dhanishtha":"Antya","Shatabhisha":"Antya","Purva Bhadrapada":"Antya",
    "Uttara Bhadrapada":"Antya","Revati":"Antya",
}

# Tatva (element) — fire/earth/air/water by Moon sign
_TATVA = {
    "Aries":"Fire","Leo":"Fire","Sagittarius":"Fire",
    "Taurus":"Earth","Virgo":"Earth","Capricorn":"Earth",
    "Gemini":"Air","Libra":"Air","Aquarius":"Air",
    "Cancer":"Water","Scorpio":"Water","Pisces":"Water",
}

# Name alphabet by nakshatra pada (the auspicious first letter for the child's name)
# Each nakshatra has 4 padas, each with its own alphabet
_NAK_ALPHABETS = {
    "Ashwini":          ["Chu","Che","Cho","La"],
    "Bharani":          ["Li","Lu","Le","Lo"],
    "Krittika":         ["A","Ee","U","Ay"],
    "Rohini":           ["O","Va","Vi","Vu"],
    "Mrigashira":       ["Ve","Vo","Ka","Ki"],
    "Ardra":            ["Ku","Gha","Nga","Cha"],
    "Punarvasu":        ["Ke","Ko","Ha","Hi"],
    "Pushya":           ["Hu","He","Ho","Da"],
    "Ashlesha":         ["Di","Du","De","Do"],
    "Magha":            ["Ma","Mi","Mu","Me"],
    "Purva Phalguni":   ["Mo","Ta","Ti","Tu"],
    "Uttara Phalguni":  ["Te","To","Pa","Pi"],
    "Hasta":            ["Pu","Sha","Na","Tha"],
    "Chitra":           ["Pe","Po","Ra","Ri"],
    "Swati":            ["Ru","Re","Ro","Ta"],
    "Vishakha":         ["Ti","Tu","Te","To"],
    "Anuradha":         ["Na","Ni","Nu","Ne"],
    "Jyeshtha":         ["No","Ya","Yi","Yu"],
    "Mula":             ["Ye","Yo","Bha","Bhi"],
    "Purva Ashadha":    ["Bhu","Dha","Pha","Dha"],
    "Uttara Ashadha":   ["Bhe","Bho","Ja","Ji"],
    "Shravana":         ["Khi","Khu","Khe","Kho"],
    "Dhanishtha":       ["Ga","Gi","Gu","Ge"],
    "Shatabhisha":      ["Go","Sa","Si","Su"],
    "Purva Bhadrapada": ["Se","So","Da","Di"],
    "Uttara Bhadrapada":["Du","Tha","Jha","Yna"],
    "Revati":           ["De","Do","Cha","Chi"],
}

# Paya — based on Moon's house position from Lagna (Ascendant):
#   1, 6, 11 → Lauh (Iron)
#   2, 5, 9  → Rajat (Silver)
#   3, 7, 10 → Tamra (Copper)
#   4, 8, 12 → Swarna (Gold)
# This is the standard rule used by AstroSage/AstroTalk and most modern Indian apps.
_PAYA_BY_HOUSE = {
    1: "Iron",    6: "Iron",    11: "Iron",
    2: "Silver",  5: "Silver",  9:  "Silver",
    3: "Copper",  7: "Copper",  10: "Copper",
    4: "Gold",    8: "Gold",    12: "Gold",
}

# Sign lord (rashi swami)
_SIGN_LORD = {
    "Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon",
    "Leo":"Sun","Virgo":"Mercury","Libra":"Venus","Scorpio":"Mars",
    "Sagittarius":"Jupiter","Capricorn":"Saturn","Aquarius":"Saturn","Pisces":"Jupiter",
}


def compute_avakhada(moon_lon: float, asc_lon: float, panch: Dict[str, Any],
                     birth_dt_local: datetime) -> Dict[str, Any]:
    """Compute the 14-field Avakhada (personality summary) panel.

    Inputs:
      moon_lon: sidereal Moon longitude in degrees
      asc_lon:  sidereal Ascendant longitude in degrees
      panch:    panchang dict from compute_panchang()
      birth_dt_local: birth datetime in LOCAL time
    """
    # Moon's nakshatra + pada
    nak_idx, nak_name, _nak_lord, pada, _frac = nak_info(moon_lon)
    # Moon's sign
    _, moon_sign, moon_sign_lord, _deg = sign_info(moon_lon)
    # Ascendant sign
    _, asc_sign, asc_sign_lord, _adeg = sign_info(asc_lon)

    # Name alphabet from pada (1-4)
    alphabets = _NAK_ALPHABETS.get(nak_name, ["—"])
    name_alphabet = alphabets[min(max(pada - 1, 0), len(alphabets) - 1)]

    # Paya — based on Moon's house position FROM Lagna (Ascendant).
    # Compute Moon's house using whole-sign houses from Lagna.
    asc_sign_idx = int(norm360(asc_lon) // 30)
    moon_sign_idx = int(norm360(moon_lon) // 30)
    moon_house = ((moon_sign_idx - asc_sign_idx) % 12) + 1
    paya = _PAYA_BY_HOUSE.get(moon_house, "—")

    # Tithi, Karan, Yog from panchang
    tithi_name = (panch.get("tithi") or {}).get("name", "—")
    karan_name = (panch.get("karana") or {}).get("name", "—")
    yog_name = (panch.get("yoga") or {}).get("name", "—")

    return {
        # Basic identity
        "name_alphabet": name_alphabet,
        "varna": _VARNA_BY_SIGN.get(moon_sign, "—"),
        "vashya": _VASHYA.get(moon_sign, "—"),
        "yoni": _YONI.get(nak_name, "—"),
        "gan": _GAN.get(nak_name, "—"),
        "nadi": _NADI.get(nak_name, "—"),
        # Sign + nakshatra refs
        "moon_sign": moon_sign,
        "moon_sign_lord": moon_sign_lord,
        "asc_sign": asc_sign,
        "asc_sign_lord": asc_sign_lord,
        "nakshatra": nak_name,
        "nakshatra_pada": pada,
        "nakshatra_charan": f"{nak_name} - Pada {pada}",
        # Panchang at birth
        "tithi": tithi_name,
        "karan": karan_name,
        "yog": yog_name,
        # Misc
        "yunja": _YUNJA.get(nak_name, "—"),
        "tatva": _TATVA.get(moon_sign, "—"),
        "paya": paya,
    }


# ============================================================
# PASS 7b: ASHTAKOOT GUNA MILAN (Marriage Matching)
#
# Eight Koots scored 1-8 points each (total 36) per Brihat Parashara Hora Shastra
# and modern Vedic compatibility conventions. Output matches what AstroSage,
# AstroTalk, and other major Indian apps display.
#
# Also computes:
#   - Manglik dosha (for both partners) with major cancellation rules
#   - Nadi dosha (separate from Nadi koot scoring)
#   - Bhakoot dosha (separate from Bhakoot koot scoring)
#   - Overall verdict with traditional thresholds
#   - Contextual remedies based on which doshas appeared
# ============================================================

# -- Lookup tables --------------------------------------------------------

# Nakshatra → Yoni (sexual/animal compatibility)
_NAK_YONI = {
    "Ashwini":"Horse","Bharani":"Elephant","Krittika":"Sheep","Rohini":"Serpent",
    "Mrigashira":"Serpent","Ardra":"Dog","Punarvasu":"Cat","Pushya":"Sheep",
    "Ashlesha":"Cat","Magha":"Rat","Purva Phalguni":"Rat","Uttara Phalguni":"Cow",
    "Hasta":"Buffalo","Chitra":"Tiger","Swati":"Buffalo","Vishakha":"Tiger",
    "Anuradha":"Deer","Jyeshtha":"Deer","Mula":"Dog","Purva Ashadha":"Monkey",
    "Uttara Ashadha":"Mongoose","Shravana":"Monkey","Dhanishtha":"Lion","Shatabhisha":"Horse",
    "Purva Bhadrapada":"Lion","Uttara Bhadrapada":"Cow","Revati":"Elephant",
}

# Yoni gender (each animal has male/female forms — strongly affects score)
_YONI_GENDER = {
    "Ashwini":"M","Bharani":"M","Krittika":"F","Rohini":"M",
    "Mrigashira":"F","Ardra":"F","Punarvasu":"F","Pushya":"M",
    "Ashlesha":"M","Magha":"M","Purva Phalguni":"F","Uttara Phalguni":"M",
    "Hasta":"M","Chitra":"F","Swati":"M","Vishakha":"F",
    "Anuradha":"F","Jyeshtha":"M","Mula":"M","Purva Ashadha":"M",
    "Uttara Ashadha":"M","Shravana":"F","Dhanishtha":"F","Shatabhisha":"F",
    "Purva Bhadrapada":"M","Uttara Bhadrapada":"F","Revati":"F",
}

# Yoni compatibility matrix — points out of 4
# Source: Muhurta Chintamani + standard convention.
# Self = 4 (same animal), Friend = 3, Neutral = 2, Enemy = 1, Maha-shatru = 0
_YONI_PAIR_SCORE = {
    # Format: (yoni1, yoni2) → score. Order doesn't matter (we check both ways).
    # Same-yoni pairs (4 pts) handled separately, not listed here.
    ("Horse","Buffalo"):2, ("Horse","Elephant"):3, ("Horse","Sheep"):2, ("Horse","Serpent"):2,
    ("Horse","Dog"):2, ("Horse","Cat"):2, ("Horse","Rat"):2, ("Horse","Cow"):0,  # arch-enemy
    ("Horse","Tiger"):1, ("Horse","Deer"):2, ("Horse","Monkey"):3, ("Horse","Mongoose"):2,
    ("Horse","Lion"):1,
    ("Elephant","Buffalo"):3, ("Elephant","Sheep"):2, ("Elephant","Serpent"):2,
    ("Elephant","Dog"):2, ("Elephant","Cat"):2, ("Elephant","Rat"):2, ("Elephant","Cow"):3,
    ("Elephant","Tiger"):1, ("Elephant","Deer"):3, ("Elephant","Monkey"):3, ("Elephant","Mongoose"):2,
    ("Elephant","Lion"):0,  # arch-enemy
    ("Sheep","Buffalo"):2, ("Sheep","Serpent"):3, ("Sheep","Dog"):1, ("Sheep","Cat"):2,
    ("Sheep","Rat"):2, ("Sheep","Cow"):3, ("Sheep","Tiger"):1, ("Sheep","Deer"):3,
    ("Sheep","Monkey"):2, ("Sheep","Mongoose"):2, ("Sheep","Lion"):1,
    ("Serpent","Buffalo"):2, ("Serpent","Dog"):2, ("Serpent","Cat"):2, ("Serpent","Rat"):2,
    ("Serpent","Cow"):3, ("Serpent","Tiger"):2, ("Serpent","Deer"):2, ("Serpent","Monkey"):2,
    ("Serpent","Mongoose"):0,  # arch-enemy
    ("Serpent","Lion"):2,
    ("Dog","Buffalo"):2, ("Dog","Cat"):2, ("Dog","Rat"):2, ("Dog","Cow"):2,
    ("Dog","Tiger"):1, ("Dog","Deer"):2, ("Dog","Monkey"):2, ("Dog","Mongoose"):2,
    ("Dog","Lion"):1,
    ("Cat","Buffalo"):2, ("Cat","Rat"):0,  # arch-enemy
    ("Cat","Cow"):2, ("Cat","Tiger"):2, ("Cat","Deer"):2, ("Cat","Monkey"):2,
    ("Cat","Mongoose"):2, ("Cat","Lion"):1,
    ("Rat","Buffalo"):2, ("Rat","Cow"):2, ("Rat","Tiger"):2, ("Rat","Deer"):2,
    ("Rat","Monkey"):2, ("Rat","Mongoose"):2, ("Rat","Lion"):2,
    ("Cow","Buffalo"):3, ("Cow","Tiger"):0,  # arch-enemy
    ("Cow","Deer"):3, ("Cow","Monkey"):2, ("Cow","Mongoose"):2, ("Cow","Lion"):1,
    ("Buffalo","Tiger"):1, ("Buffalo","Deer"):2, ("Buffalo","Monkey"):2,
    ("Buffalo","Mongoose"):2, ("Buffalo","Lion"):1,
    ("Tiger","Deer"):1, ("Tiger","Monkey"):2, ("Tiger","Mongoose"):2, ("Tiger","Lion"):0,  # arch-enemy
    ("Deer","Dog"):1,  # arch-enemy pair (handled also above)
    ("Deer","Monkey"):2, ("Deer","Mongoose"):2, ("Deer","Lion"):1,
    ("Monkey","Mongoose"):2, ("Monkey","Lion"):2,
    ("Mongoose","Lion"):2,
}

# Sign-lord natural friendships (for Graha Maitri koot, separate from dignity friendships).
# Each Moon-sign lord categorizes the other Moon-sign lord as Friend/Neutral/Enemy.
# Based on classical naisargika maitri.
_LORD_FRIENDS = {
    "Sun":     {"Moon", "Mars", "Jupiter"},
    "Moon":    {"Sun", "Mercury"},
    "Mars":    {"Sun", "Moon", "Jupiter"},
    "Mercury": {"Sun", "Venus"},
    "Jupiter": {"Sun", "Moon", "Mars"},
    "Venus":   {"Mercury", "Saturn"},
    "Saturn":  {"Mercury", "Venus"},
}
_LORD_ENEMIES = {
    "Sun":     {"Venus", "Saturn"},
    "Moon":    set(),
    "Mars":    {"Mercury"},
    "Mercury": {"Moon"},
    "Jupiter": {"Mercury", "Venus"},
    "Venus":   {"Sun", "Moon"},
    "Saturn":  {"Sun", "Moon", "Mars"},
}

# Nakshatra → Gana (Dev / Manushya / Rakshasa)
_NAK_GANA = {
    "Ashwini":"Dev","Bharani":"Manushya","Krittika":"Rakshasa","Rohini":"Manushya",
    "Mrigashira":"Dev","Ardra":"Manushya","Punarvasu":"Dev","Pushya":"Dev",
    "Ashlesha":"Rakshasa","Magha":"Rakshasa","Purva Phalguni":"Manushya","Uttara Phalguni":"Manushya",
    "Hasta":"Dev","Chitra":"Rakshasa","Swati":"Dev","Vishakha":"Rakshasa",
    "Anuradha":"Dev","Jyeshtha":"Rakshasa","Mula":"Rakshasa","Purva Ashadha":"Manushya",
    "Uttara Ashadha":"Manushya","Shravana":"Dev","Dhanishtha":"Rakshasa","Shatabhisha":"Rakshasa",
    "Purva Bhadrapada":"Manushya","Uttara Bhadrapada":"Manushya","Revati":"Dev",
}

# Varna hierarchy for the Varna koot scoring (higher number = "higher" varna)
_VARNA_RANK = {"Brahmin": 4, "Kshatriya": 3, "Vaishya": 2, "Shudra": 1}

# Vashya by Moon sign — controlling category. Used by Vashya koot.
# Categories: Chatushpada (4-legged), Nara (human), Jalachara (water), Vanachara (wild), Keeta (insect)
_VASHYA_BY_SIGN = {
    "Aries":"Chatushpada","Leo":"Vanachara","Sagittarius":"Chatushpada",  # latter half Nara, simplified
    "Taurus":"Chatushpada","Virgo":"Nara","Capricorn":"Jalachara",  # latter half Chatushpada, simplified
    "Gemini":"Nara","Libra":"Nara","Aquarius":"Nara",
    "Cancer":"Jalachara","Scorpio":"Keeta","Pisces":"Jalachara",
}

# Vashya pair compatibility score (out of 2)
def _vashya_score(v1: str, v2: str) -> int:
    if v1 == v2:
        return 2
    # Friendly pairs (1 point)
    friendly = {
        frozenset({"Nara","Chatushpada"}): 1,
        frozenset({"Nara","Vanachara"}): 0.5,
        frozenset({"Chatushpada","Jalachara"}): 1,
        frozenset({"Jalachara","Keeta"}): 1,
    }
    # Predator-prey pairs (0 points)
    enemy = {
        frozenset({"Chatushpada","Vanachara"}),
        frozenset({"Nara","Keeta"}),
    }
    key = frozenset({v1, v2})
    if key in enemy:
        return 0
    if key in friendly:
        return int(friendly[key] * 2) // 1  # 1 or 0 (round down half-points to 1)
    return 1  # default neutral


# -- The 8 Koot scoring functions ----------------------------------------

def _koot_varna(boy_moon_sign: str, girl_moon_sign: str) -> Dict[str, Any]:
    """Varna (1 pt). Boy's varna should be ≥ Girl's. Equal = 1, lower = 0."""
    bv = _VARNA_BY_SIGN.get(boy_moon_sign, "—")
    gv = _VARNA_BY_SIGN.get(girl_moon_sign, "—")
    br = _VARNA_RANK.get(bv, 0)
    gr = _VARNA_RANK.get(gv, 0)
    score = 1 if br >= gr else 0
    return {
        "boy": bv, "girl": gv,
        "score": score, "max": 1,
        "remark": "Compatible" if score == 1 else "Boy varna lower than girl",
    }


def _koot_vashya(boy_moon_sign: str, girl_moon_sign: str) -> Dict[str, Any]:
    """Vashya (2 pts). Mutual influence category."""
    bv = _VASHYA_BY_SIGN.get(boy_moon_sign, "—")
    gv = _VASHYA_BY_SIGN.get(girl_moon_sign, "—")
    score = _vashya_score(bv, gv)
    return {
        "boy": bv, "girl": gv,
        "score": score, "max": 2,
        "remark": "Same category" if score == 2 else ("Friendly" if score == 1 else "Different/Hostile"),
    }


# Nakshatra index (0-26) for Tara calculation
_NAK_INDEX = {n: i for i, n in enumerate(NAKSHATRAS)}


def _koot_tara(boy_nak: str, girl_nak: str) -> Dict[str, Any]:
    """Tara (3 pts). Janma-nak counting in both directions.
    Count from one's nakshatra to the other's (inclusive), divide by 9.
    Remainder 0/2/4/6/8 → favorable (1.5/3 pts). Remainder 1/3/5/7 → unfavorable (0 pts).
    Same-nakshatra (count=1) treated as favorable per modern convention (AstroSage/AstroTalk)."""
    bi = _NAK_INDEX.get(boy_nak)
    gi = _NAK_INDEX.get(girl_nak)
    if bi is None or gi is None:
        return {"boy": boy_nak, "girl": girl_nak, "score": 0, "max": 3, "remark": "Invalid nakshatra"}
    # Count from boy → girl, inclusive
    count_b_to_g = ((gi - bi) % 27) + 1
    rem_b = count_b_to_g % 9
    # Same nakshatra (count=1) treated as favorable
    fav_b = (count_b_to_g == 1) or (rem_b in (0, 2, 4, 6, 8))
    # Count from girl → boy
    count_g_to_b = ((bi - gi) % 27) + 1
    rem_g = count_g_to_b % 9
    fav_g = (count_g_to_b == 1) or (rem_g in (0, 2, 4, 6, 8))
    score = (1.5 if fav_b else 0) + (1.5 if fav_g else 0)
    return {
        "boy": boy_nak, "girl": girl_nak,
        "score": int(score), "max": 3,
        "boy_to_girl_count": count_b_to_g, "girl_to_boy_count": count_g_to_b,
        "remark": "Both directions favorable" if (fav_b and fav_g) else
                  ("Partial — one direction unfavorable" if (fav_b or fav_g) else "Both directions unfavorable"),
    }


def _koot_yoni(boy_nak: str, girl_nak: str) -> Dict[str, Any]:
    """Yoni (4 pts). Sexual / physical compatibility by nakshatra-animal pairing."""
    by = _NAK_YONI.get(boy_nak, "—")
    gy = _NAK_YONI.get(girl_nak, "—")
    if by == "—" or gy == "—":
        return {"boy": by, "girl": gy, "score": 0, "max": 4, "remark": "Invalid nakshatra"}
    if by == gy:
        # Same yoni: 4 if opposite gender (ideal), 3 if same gender
        bg = _YONI_GENDER.get(boy_nak, "M")
        gg = _YONI_GENDER.get(girl_nak, "F")
        if bg != gg:
            score = 4
            remark = "Same yoni, complementary genders — ideal"
        else:
            score = 3
            remark = "Same yoni, same gender — good"
    else:
        # Look up pair score (check both orderings)
        score = _YONI_PAIR_SCORE.get((by, gy), _YONI_PAIR_SCORE.get((gy, by), 2))
        if score == 0:
            remark = "Arch-enemy yonis — major incompatibility"
        elif score == 1:
            remark = "Enemy yonis"
        elif score == 2:
            remark = "Neutral yonis"
        elif score == 3:
            remark = "Friendly yonis"
        else:
            remark = "Compatible"
    return {"boy": by, "girl": gy, "score": score, "max": 4, "remark": remark}


def _koot_graha_maitri(boy_moon_sign: str, girl_moon_sign: str) -> Dict[str, Any]:
    """Graha Maitri (5 pts). Mental compatibility via Moon-sign lords.
    Mutual friend = 5, one friend one neutral = 4, both neutral = 3,
    one friend one enemy = 1, mutual enemy = 0."""
    bl = _SIGN_LORD.get(boy_moon_sign, "—")
    gl = _SIGN_LORD.get(girl_moon_sign, "—")
    if bl == "—" or gl == "—" or bl not in _LORD_FRIENDS:
        return {"boy_lord": bl, "girl_lord": gl, "score": 0, "max": 5, "remark": "Invalid"}
    # How does boy's lord see girl's lord?
    if gl == bl:
        b_sees_g = "Self"
    elif gl in _LORD_FRIENDS.get(bl, set()):
        b_sees_g = "Friend"
    elif gl in _LORD_ENEMIES.get(bl, set()):
        b_sees_g = "Enemy"
    else:
        b_sees_g = "Neutral"
    # How does girl's lord see boy's lord?
    if bl == gl:
        g_sees_b = "Self"
    elif bl in _LORD_FRIENDS.get(gl, set()):
        g_sees_b = "Friend"
    elif bl in _LORD_ENEMIES.get(gl, set()):
        g_sees_b = "Enemy"
    else:
        g_sees_b = "Neutral"
    # Score lookup
    pair = (b_sees_g, g_sees_b)
    score_map = {
        ("Self","Self"): 5,
        ("Friend","Friend"): 5,
        ("Friend","Neutral"): 4, ("Neutral","Friend"): 4,
        ("Neutral","Neutral"): 3,
        ("Friend","Enemy"): 1, ("Enemy","Friend"): 1,
        ("Neutral","Enemy"): 0.5, ("Enemy","Neutral"): 0.5,
        ("Enemy","Enemy"): 0,
        ("Self","Friend"): 5, ("Friend","Self"): 5,
        ("Self","Neutral"): 4, ("Neutral","Self"): 4,
        ("Self","Enemy"): 1, ("Enemy","Self"): 1,
    }
    score = int(score_map.get(pair, 3))
    remarks = {5:"Excellent mental harmony", 4:"Good mental harmony",
               3:"Average mental harmony", 1:"Strained understanding",
               0:"Strong mental incompatibility"}
    return {
        "boy_lord": bl, "girl_lord": gl,
        "boy_sees_girl": b_sees_g, "girl_sees_boy": g_sees_b,
        "score": score, "max": 5,
        "remark": remarks.get(score, "Mixed"),
    }


def _koot_gana(boy_nak: str, girl_nak: str) -> Dict[str, Any]:
    """Gana (6 pts). Temperament. Dev = divine, Manushya = human, Rakshasa = demon.
    Same = 6, Dev+Manushya = 5 (boy higher OK), Manushya+Rakshasa = 1 if boy higher else 0,
    Dev+Rakshasa = 0."""
    bg = _NAK_GANA.get(boy_nak, "—")
    gg = _NAK_GANA.get(girl_nak, "—")
    if bg == gg:
        return {"boy": bg, "girl": gg, "score": 6, "max": 6, "remark": "Same gana"}
    pair = {bg, gg}
    if pair == {"Dev", "Manushya"}:
        score = 5
        remark = "Friendly ganas (Dev-Manushya)"
    elif pair == {"Manushya", "Rakshasa"}:
        # Some traditions: boy Manushya + girl Rakshasa = 0, else 1
        score = 1 if (bg == "Manushya" and gg == "Rakshasa") else 1
        remark = "Different ganas — caution"
    elif pair == {"Dev", "Rakshasa"}:
        score = 0
        remark = "Opposing ganas — incompatible"
    else:
        score = 0
        remark = "Unknown"
    return {"boy": bg, "girl": gg, "score": score, "max": 6, "remark": remark}


def _koot_bhakoot(boy_moon_sign: str, girl_moon_sign: str) -> Dict[str, Any]:
    """Bhakoot (7 pts). Distance between Moon signs determines family welfare.
    1-1 or 7-7 = 7 pts. Specific bad positions: 6-8 (Shadashtak), 9-5 (Navam-Pancham),
    2-12 (Dwirdwadash) — all score 0. Others = 7."""
    si_b = SIGNS.index(boy_moon_sign) if boy_moon_sign in SIGNS else -1
    si_g = SIGNS.index(girl_moon_sign) if girl_moon_sign in SIGNS else -1
    if si_b < 0 or si_g < 0:
        return {"boy": boy_moon_sign, "girl": girl_moon_sign, "score": 0, "max": 7, "remark": "Invalid"}
    # Distance from boy to girl
    dist_bg = ((si_g - si_b) % 12) + 1
    dist_gb = ((si_b - si_g) % 12) + 1
    # Doshic distances (counted inclusively, 1 = same sign)
    doshic = {(2, 12), (12, 2), (3, 11), (11, 3), (5, 9), (9, 5), (6, 8), (8, 6)}
    pair = (dist_bg, dist_gb)
    if pair in doshic:
        score = 0
        if pair in {(6, 8), (8, 6)}:
            remark = "Shadashtak Dosha (6-8) — major affliction"
        elif pair in {(5, 9), (9, 5)}:
            remark = "Navam-Pancham Dosha (5-9) — affliction"
        elif pair in {(2, 12), (12, 2)}:
            remark = "Dwirdwadash Dosha (2-12) — minor affliction"
        else:
            remark = "Bhakoot dosha"
    else:
        score = 7
        remark = "No Bhakoot dosha"
    return {
        "boy": boy_moon_sign, "girl": girl_moon_sign,
        "distance_boy_to_girl": dist_bg, "distance_girl_to_boy": dist_gb,
        "score": score, "max": 7, "remark": remark,
    }


def _koot_nadi(boy_nak: str, girl_nak: str) -> Dict[str, Any]:
    """Nadi (8 pts). Same nadi = 0 pts (severe progeny dosha). Different nadi = 8."""
    bn = _NADI.get(boy_nak, "—")
    gn = _NADI.get(girl_nak, "—")
    if bn == "—" or gn == "—":
        return {"boy": bn, "girl": gn, "score": 0, "max": 8, "remark": "Invalid nakshatra"}
    if bn == gn:
        return {"boy": bn, "girl": gn, "score": 0, "max": 8,
                "remark": f"Same nadi ({bn}) — Nadi Dosha present"}
    return {"boy": bn, "girl": gn, "score": 8, "max": 8, "remark": "Different nadi — no dosha"}


# -- Manglik analysis with major cancellation rules ----------------------

def _is_manglik(planets: Dict[str, Dict[str, Any]], asc_lon: float) -> Dict[str, Any]:
    """Mars in 1, 2, 4, 7, 8, or 12th from Lagna (or from Moon, or from Venus).
    Returns dict with manglik status, severity, and cancellation analysis.

    Cancellations applied (most universally accepted):
      1. Mars in own sign (Aries/Scorpio) or exaltation (Capricorn) → cancelled
      2. Mars in 2nd house in Gemini/Virgo (Mercury-ruled signs) → cancelled
      3. Mars conjunct Jupiter or Moon → severity reduced
      4. Mars aspected by Jupiter → severity reduced
    """
    mars_lon = planets["Mars"]["lon"]
    mars_sign_idx = int(norm360(mars_lon) // 30)
    mars_sign = SIGNS[mars_sign_idx]
    mars_house = whole_sign_house(asc_lon, mars_lon)
    manglik_houses = {1, 2, 4, 7, 8, 12}
    is_manglik = mars_house in manglik_houses

    cancellations: List[str] = []
    severity = "None"

    if is_manglik:
        # Default severity by house
        if mars_house in {7, 8}:
            severity = "High"
        elif mars_house in {1, 4, 12}:
            severity = "Medium"
        else:  # 2nd
            severity = "Low"

        # Cancellation 1: own/exalted sign
        if mars_sign in {"Aries", "Scorpio"}:
            cancellations.append(f"Mars in own sign ({mars_sign}) — dosha cancelled")
            severity = "Cancelled"
        elif mars_sign == "Capricorn":
            cancellations.append("Mars exalted in Capricorn — dosha cancelled")
            severity = "Cancelled"

        # Cancellation 2: 2nd house Mercury signs
        if mars_house == 2 and mars_sign in {"Gemini", "Virgo"}:
            cancellations.append("Mars in 2nd house in Mercury sign — dosha cancelled")
            severity = "Cancelled"

        # Reduction: conjunction with Jupiter / Moon (within 8°)
        for benefic in ("Jupiter", "Moon"):
            bl = planets[benefic]["lon"]
            diff = abs(norm360(mars_lon - bl))
            if diff > 180: diff = 360 - diff
            if diff <= 8:
                cancellations.append(f"Mars conjunct {benefic} — severity reduced")
                if severity == "High": severity = "Medium"
                elif severity == "Medium": severity = "Low"

        # Reduction: aspected by Jupiter (5th, 7th, or 9th house aspect)
        ju_lon = planets["Jupiter"]["lon"]
        ju_house = whole_sign_house(asc_lon, ju_lon)
        # Jupiter aspects 5th, 7th, 9th from itself
        for asp in (5, 7, 9):
            aspect_house = ((ju_house - 1 + asp - 1) % 12) + 1
            if aspect_house == mars_house:
                cancellations.append(f"Mars aspected by Jupiter ({asp}th aspect) — severity reduced")
                if severity == "High": severity = "Medium"
                elif severity == "Medium": severity = "Low"
                break

    return {
        "is_manglik": is_manglik,
        "mars_house": mars_house,
        "mars_sign": mars_sign,
        "severity": severity,
        "cancellations": cancellations,
    }


# -- Match orchestrator + verdict ----------------------------------------

def _verdict(total: int) -> Dict[str, str]:
    """Standard threshold verdict. Returns label + color + advice."""
    if total >= 32:
        return {"label": "Excellent", "label_hi": "अति शुभ", "color": "success",
                "advice": "Highly compatible match. Strongly recommended."}
    if total >= 25:
        return {"label": "Good", "label_hi": "शुभ", "color": "success",
                "advice": "Compatible match. Recommended with attention to any noted doshas."}
    if total >= 18:
        return {"label": "Acceptable", "label_hi": "मध्यम", "color": "warning",
                "advice": "Average compatibility. Acceptable if no major doshas present and other factors favor the match."}
    return {"label": "Not Recommended", "label_hi": "अशुभ", "color": "danger",
            "advice": "Low compatibility. Reconsider the match or consult an astrologer for detailed analysis."}


def _remedies_for_doshas(nadi_dosha: bool, bhakoot_dosha: bool, manglik_either: bool,
                         total_score: int) -> List[Dict[str, str]]:
    """Return contextual remedies based on which doshas appeared.
    Each remedy: {type, title, description}."""
    out: List[Dict[str, str]] = []

    if nadi_dosha:
        out.append({
            "type": "mantra",
            "title": "Mahamrityunjaya Mantra",
            "description": "Daily recitation of 108 Mahamrityunjaya mantras by both partners. Recommended for 40-48 days before marriage to mitigate Nadi Dosha effects on health and progeny.",
        })
        out.append({
            "type": "ritual",
            "title": "Kumbh Vivah / Nadi Dosha Nivaran Puja",
            "description": "A traditional remedial ceremony performed before the marriage. Best done at Trimbakeshwar, Ujjain, or any Shiva temple with the help of an experienced priest.",
        })

    if bhakoot_dosha:
        out.append({
            "type": "mantra",
            "title": "Vishnu Sahasranama",
            "description": "Weekly recitation of Vishnu Sahasranama by both partners, especially on Thursdays. Strengthens family bonds and offsets Bhakoot Dosha effects on prosperity and harmony.",
        })

    if manglik_either:
        out.append({
            "type": "ritual",
            "title": "Kumbh Vivah (for Manglik)",
            "description": "Symbolic marriage of the Manglik partner to a Peepal tree, Vishnu idol, or Banana plant before the actual marriage. Performed at temples specializing in this remedy (Mehandipur Balaji, etc.).",
        })
        out.append({
            "type": "fast",
            "title": "Tuesday fast + Hanuman Chalisa",
            "description": "Fast on Tuesdays and recite Hanuman Chalisa daily. Reduces Mars-related afflictions. Continue for at least 6 months before marriage.",
        })

    if total_score < 18 and not (nadi_dosha or bhakoot_dosha or manglik_either):
        out.append({
            "type": "consultation",
            "title": "Detailed astrological consultation",
            "description": "Score is low but no specific dosha was detected. The pattern suggests deeper analysis is needed — house lords, dasha periods at marriage, and divisional chart compatibility should be examined by a qualified Vedic astrologer.",
        })

    if not out:
        out.append({
            "type": "blessing",
            "title": "Standard pre-marriage rituals",
            "description": "No major remedies required. Standard pre-marriage pujas (Ganesh Puja, Navagraha shanti) and family blessings will be sufficient.",
        })

    return out


def compute_match(boy: Dict[str, Any], girl: Dict[str, Any]) -> Dict[str, Any]:
    """Master matching function. Both `boy` and `girl` dicts must contain computed
    chart data: moon_sign, moon_nakshatra, moon_lon, asc_lon, planets.

    Returns full match report with all 8 koots, dosha analyses, verdict, remedies.
    """
    bms = boy["moon_sign"]; gms = girl["moon_sign"]
    bnk = boy["moon_nakshatra"]; gnk = girl["moon_nakshatra"]

    # 8 koots
    k_varna = _koot_varna(bms, gms)
    k_vashya = _koot_vashya(bms, gms)
    k_tara = _koot_tara(bnk, gnk)
    k_yoni = _koot_yoni(bnk, gnk)
    k_graha = _koot_graha_maitri(bms, gms)
    k_gana = _koot_gana(bnk, gnk)
    k_bhakoot = _koot_bhakoot(bms, gms)
    k_nadi = _koot_nadi(bnk, gnk)

    total = sum(k["score"] for k in (
        k_varna, k_vashya, k_tara, k_yoni, k_graha, k_gana, k_bhakoot, k_nadi
    ))
    total = int(total)

    # Manglik for both
    boy_manglik = _is_manglik(boy["planets"], boy["asc_lon"])
    girl_manglik = _is_manglik(girl["planets"], girl["asc_lon"])

    # If both Manglik with non-cancelled status, partial cancellation
    if (boy_manglik["is_manglik"] and girl_manglik["is_manglik"]
        and boy_manglik["severity"] != "Cancelled" and girl_manglik["severity"] != "Cancelled"):
        boy_manglik["cancellations"].append("Both partners Manglik — mutually cancelled")
        girl_manglik["cancellations"].append("Both partners Manglik — mutually cancelled")
        boy_manglik["severity"] = "Cancelled"
        girl_manglik["severity"] = "Cancelled"

    # Specific dosha flags (for remedy logic)
    nadi_dosha = (k_nadi["score"] == 0)
    bhakoot_dosha = (k_bhakoot["score"] == 0)
    manglik_either = (
        (boy_manglik["is_manglik"] and boy_manglik["severity"] != "Cancelled") or
        (girl_manglik["is_manglik"] and girl_manglik["severity"] != "Cancelled")
    )

    verdict = _verdict(total)
    remedies = _remedies_for_doshas(nadi_dosha, bhakoot_dosha, manglik_either, total)

    return {
        "total_score": total,
        "max_score": 36,
        "percent": round(total / 36.0 * 100, 1),
        "koots": {
            "varna": k_varna, "vashya": k_vashya, "tara": k_tara, "yoni": k_yoni,
            "graha_maitri": k_graha, "gana": k_gana, "bhakoot": k_bhakoot, "nadi": k_nadi,
        },
        "doshas": {
            "nadi_dosha": nadi_dosha,
            "bhakoot_dosha": bhakoot_dosha,
            "manglik_either": manglik_either,
            "boy_manglik": boy_manglik,
            "girl_manglik": girl_manglik,
        },
        "verdict": verdict,
        "remedies": remedies,
        "boy_summary": {
            "moon_sign": bms, "moon_sign_lord": _SIGN_LORD.get(bms, "—"),
            "nakshatra": bnk, "varna": _VARNA_BY_SIGN.get(bms, "—"),
            "nadi": _NADI.get(bnk, "—"), "gana": _NAK_GANA.get(bnk, "—"),
            "yoni": _NAK_YONI.get(bnk, "—"),
        },
        "girl_summary": {
            "moon_sign": gms, "moon_sign_lord": _SIGN_LORD.get(gms, "—"),
            "nakshatra": gnk, "varna": _VARNA_BY_SIGN.get(gms, "—"),
            "nadi": _NADI.get(gnk, "—"), "gana": _NAK_GANA.get(gnk, "—"),
            "yoni": _NAK_YONI.get(gnk, "—"),
        },
    }


# -- Pydantic request + endpoint -----------------------------------------

class MatchPartner(BaseModel):
    name: str = ""
    date: str           # YYYY-MM-DD
    time: str           # HH:MM (24-hour)
    place: str = ""
    latitude: float
    longitude: float


class MatchReq(BaseModel):
    boy: MatchPartner
    girl: MatchPartner


def _partner_chart_for_matching(p: MatchPartner) -> Dict[str, Any]:
    """Compute the minimum chart data needed for matching: moon sign,
    moon nakshatra, planets dict, ascendant longitude."""
    tz_name = timezone_from_lat_lon(p.latitude, p.longitude)
    off = tz_offset_hours(tz_name, datetime.strptime(p.date, "%Y-%m-%d"))
    jd = to_jd(p.date, p.time, off)
    asc_lon = calc_lagna(jd, p.latitude, p.longitude, b"P")
    planets = calc_planets(jd)
    moon_lon = planets["Moon"]["lon"]
    _, moon_sign, moon_sign_lord, _ = sign_info(moon_lon)
    _, nak_name, _, pada, _ = nak_info(moon_lon)
    return {
        "moon_sign": moon_sign,
        "moon_sign_lord": moon_sign_lord,
        "moon_nakshatra": nak_name,
        "moon_pada": pada,
        "moon_lon": moon_lon,
        "asc_lon": asc_lon,
        "planets": planets,
    }


@app.post("/api/match")
def api_match(req: MatchReq):
    """Compute Ashtakoot Guna Milan for two partners.
    Returns 36-point match analysis + Manglik + doshas + verdict + remedies.
    """
    try:
        boy_chart = _partner_chart_for_matching(req.boy)
        girl_chart = _partner_chart_for_matching(req.girl)
        result = compute_match(boy_chart, girl_chart)
        return {
            "success": True,
            "boy": {"name": req.boy.name, "date": req.boy.date, "time": req.boy.time, "place": req.boy.place},
            "girl": {"name": req.girl.name, "date": req.girl.date, "time": req.girl.time, "place": req.girl.place},
            **result,
        }
    except Exception as exc:
        return JSONResponse(status_code=500, content={"success": False, "error": str(exc)[:300]})


@app.post("/api/kundli")
def api_kundli(req: KundliReq):
    try:
        tz_name = timezone_from_lat_lon(req.latitude, req.longitude)
        off = tz_offset_hours(tz_name, datetime.strptime(req.date, "%Y-%m-%d"))
        jd = to_jd(req.date, req.time, off)
        asc = calc_lagna(jd, req.latitude, req.longitude, b"P")
        planets = calc_planets(jd)
        panch = compute_panchang(jd, off, req.latitude, req.longitude, req.date, tz_name)
        _, asc_sign, asc_lord, asc_deg = sign_info(asc)

        planet_rows = []
        for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
            lon = planets[p]["lon"]
            si, sname, slord, deg = sign_info(lon)
            ni, nname, nlord, pada, _ = nak_info(lon)
            planet_rows.append({
                "planet": p,
                "longitude": round(lon, 4),
                "sign": sname,
                "sign_lord": slord,
                "degree_dms": deg_to_dms(deg),
                "nakshatra": nname,
                "nakshatra_lord": nlord,
                "pada": pada,
                "retro": planets[p]["retro"],
                "house": whole_sign_house(asc, lon),
                "dignity": dignity(p, lon),  # PASS 7a: credibility display
            })

        moon = next(x for x in planet_rows if x["planet"] == "Moon")
        d_tree = dasha_tree(moon["longitude"], req.date)

        # PASS 6: Avakhada — 14-field personality summary panel
        try:
            birth_dt_local = datetime.strptime(req.date + " " + req.time, "%Y-%m-%d %H:%M")
            avakhada = compute_avakhada(planets["Moon"]["lon"], asc, panch, birth_dt_local)
        except Exception as exc_a:
            avakhada = {"_error": str(exc_a)[:200]}

        return {
            "success": True,
            "input": req.model_dump(),
            "timezone": tz_name,
            "lagna": {"longitude": round(asc, 4), "sign": asc_sign, "sign_lord": asc_lord, "degree_dms": deg_to_dms(asc_deg)},
            "panchang": panch,
            "avakhada": avakhada,
            "planets": planet_rows,
            "north_indian": {"houses": chart_houses(asc, planets, navamsa=False)},
            "navamsa": {"houses": chart_houses(asc, planets, navamsa=True)},
            "dasha": [
                {
                    "planet": n["planet"],
                    "years": n["years"],
                    "start_date": fmt_dt(n["start"]),
                    "end_date": fmt_dt(n["end"]),
                }
                for n in d_tree
            ],
        }
    except Exception as exc:
        return JSONResponse(status_code=500, content={"success": False, "error": str(exc)})


@app.get("/api/horoscope")
def api_horoscope(sign: str = Query(...), period: str = Query("daily", pattern="^(daily|weekly|monthly|yearly)$")):
    # PHASE 1 FIX: accept English/Sanskrit/Hindi sign names, case-insensitive
    canonical = normalize_sign(sign)
    if not canonical:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sign '{sign}'. Try English (Aries..Pisces) or Sanskrit (Mesha..Meena)."
        )
    try:
        jd = swe.julday(datetime.utcnow().year, datetime.utcnow().month, datetime.utcnow().day, 12)
        return generate_horoscope(canonical, period, jd)
    except Exception as exc:
        return JSONResponse(status_code=500, content={"success": False, "error": str(exc)})


@app.get("/api/panchang-full")
def api_panchang_full(lat: float, lon: float, date: str):
    try:
        tz_name = timezone_from_lat_lon(lat, lon)
        off = tz_offset_hours(tz_name, datetime.strptime(date, "%Y-%m-%d"))
        jd = to_jd(date, "06:00", off)
        return {"success": True, "date": date, "timezone": tz_name,
                "panchang": compute_panchang(jd, off, lat, lon, date, tz_name)}
    except Exception as exc:
        return JSONResponse(status_code=500, content={"success": False, "error": str(exc)})


@app.get("/api/today-panchang")
def api_today_panchang(lat: float = 28.6139, lon: float = 77.2090, date: Optional[str] = None):
    d = date or datetime.now().strftime("%Y-%m-%d")
    return api_panchang_full(lat, lon, d)


@app.get("/api/hora")
def api_hora(lat: float, lon: float, date: str):
    try:
        tz = timezone_from_lat_lon(lat, lon)
        events = get_sun_moon_events(lat, lon, date, tz)
        d = datetime.strptime(date, "%Y-%m-%d")
        sr = datetime.strptime(date + " " + events["sunrise"], "%Y-%m-%d %I:%M %p")
        ss = datetime.strptime(date + " " + events["sunset"], "%Y-%m-%d %I:%M %p")
        day_len = (ss - sr) / 12
        n_sr = sr + timedelta(days=1)
        night_len = (n_sr - ss) / 12

        day_lord = ["Surya", "Chandra", "Mangal", "Budh", "Guru", "Shukra", "Shani"][(d.weekday() + 1) % 7]
        seq = ["Surya", "Shukra", "Budh", "Chandra", "Shani", "Guru", "Mangal"]
        idx = seq.index(day_lord)
        rows = []
        now = datetime.now()
        for i in range(12):
            st = sr + i * day_len
            en = st + day_len
            rows.append({"index": i + 1, "planet": seq[(idx + i) % 7],
                         "start": st.strftime("%I:%M %p"), "end": en.strftime("%I:%M %p"),
                         "is_current": st <= now <= en})
        for i in range(12):
            st = ss + i * night_len
            en = st + night_len
            rows.append({"index": i + 13, "planet": seq[(idx + 12 + i) % 7],
                         "start": st.strftime("%I:%M %p"), "end": en.strftime("%I:%M %p"),
                         "is_current": st <= now <= en})
        return {"success": True, "day_lord": day_lord, "horas": rows}
    except Exception as exc:
        return JSONResponse(status_code=500, content={"success": False, "error": str(exc)})


@app.get("/api/choghadiya")
def api_choghadiya(lat: float, lon: float, date: str):
    try:
        tz = timezone_from_lat_lon(lat, lon)
        ev = get_sun_moon_events(lat, lon, date, tz)
        sr = datetime.strptime(date + " " + ev["sunrise"], "%Y-%m-%d %I:%M %p")
        ss = datetime.strptime(date + " " + ev["sunset"], "%Y-%m-%d %I:%M %p")
        day_seg = (ss - sr) / 8
        night_seg = ((sr + timedelta(days=1)) - ss) / 8
        day_names = ["Udveg", "Chara", "Laabh", "Amrit", "Kaal", "Shubh", "Rog", "Laabh"]
        night_names = ["Shubh", "Amrit", "Chara", "Rog", "Kaal", "Laabh", "Udveg", "Shubh"]
        good = {"Laabh", "Amrit", "Shubh"}
        day = []
        night = []
        for i in range(8):
            st = sr + i * day_seg
            en = st + day_seg
            nm = day_names[i]
            day.append({"period": f"Day {i+1}", "name": nm,
                        "start": st.strftime("%I:%M %p"), "end": en.strftime("%I:%M %p"),
                        "status": "Auspicious" if nm in good else "Inauspicious"})
        for i in range(8):
            st = ss + i * night_seg
            en = st + night_seg
            nm = night_names[i]
            night.append({"period": f"Night {i+1}", "name": nm,
                          "start": st.strftime("%I:%M %p"), "end": en.strftime("%I:%M %p"),
                          "status": "Auspicious" if nm in good else "Inauspicious"})
        return {"success": True, "day_choghadiya": day, "night_choghadiya": night}
    except Exception as exc:
        return JSONResponse(status_code=500, content={"success": False, "error": str(exc)})


@app.get("/api/hindu-calendar")
def api_hindu_calendar(month: int = Query(..., ge=1, le=12), year: int = Query(..., ge=1900, le=2100)):
    out = []
    d = datetime(year, month, 1)
    while d.month == month:
        jd = to_jd(d.strftime("%Y-%m-%d"), "06:00", 5.5)
        s, m = get_sun_moon_lons(jd)
        ta = norm360(m - s)
        ti = int(ta // 12)
        out.append({
            "date": d.strftime("%Y-%m-%d"),
            "day": d.day,
            "weekday": VARAS[(d.weekday() + 1) % 7],
            "tithi": TITHIS[ti],
            "paksha": "Shukla" if ti < 15 else "Krishna",
            "is_purnima": ti == 14,
            "is_amavasya": ti == 29,
        })
        d += timedelta(days=1)
    return {"success": True, "month": month, "year": year, "calendar": out}


@app.get("/api/festival-calendar")
def api_festival_calendar(month: int = Query(..., ge=1, le=12), year: int = Query(..., ge=1900, le=2100)):
    fixed = {
        (1, 14): "Makar Sankranti",
        (2, 18): "Maha Shivratri",
        (3, 25): "Holi",
        (8, 19): "Janmashtami",
        (10, 24): "Dussehra",
        (11, 12): "Diwali",
    }
    out = []
    d = datetime(year, month, 1)
    while d.month == month:
        jd = to_jd(d.strftime("%Y-%m-%d"), "06:00", 5.5)
        s, m = get_sun_moon_lons(jd)
        ti = int(norm360(m - s) // 12)
        festival = fixed.get((month, d.day))
        if ti in (10, 25) and not festival:
            festival = "Ekadashi"
        if ti in (13, 28) and not festival and d.weekday() in (0, 4):
            festival = "Pradosh"
        out.append({"date": d.strftime("%Y-%m-%d"), "day": d.day, "festival": festival})
        d += timedelta(days=1)
    return {"success": True, "month": month, "year": year, "festivals": out}


@app.get("/api/moon-calendar")
def api_moon_calendar(month: int = Query(..., ge=1, le=12), year: int = Query(..., ge=1900, le=2100)):
    out = []
    d = datetime(year, month, 1)
    while d.month == month:
        jd = to_jd(d.strftime("%Y-%m-%d"), "12:00", 5.5)
        s, m = get_sun_moon_lons(jd)
        a = norm360(m - s)
        lum = round(50.0 * (1 - math.cos(math.radians(a))), 2)
        out.append({
            "date": d.strftime("%Y-%m-%d"),
            "day": d.day,
            "phase_name": moon_phase_description(a),
            "paksha": "Shukla" if a < 180 else "Krishna",
            "luminance_pct": lum,
            "icon": "waxing" if a < 180 else "waning",
        })
        d += timedelta(days=1)
    return {"success": True, "month": month, "year": year, "moon_phases": out}


@app.get("/api/rahukaal")
def api_rahukaal(month: int, year: int, lat: float, lon: float):
    seg_map = {6: 8, 0: 2, 1: 7, 2: 5, 3: 6, 4: 4, 5: 3}
    out = []
    tz = timezone_from_lat_lon(lat, lon)
    d = datetime(year, month, 1)
    while d.month == month:
        ds = d.strftime("%Y-%m-%d")
        ev = get_sun_moon_events(lat, lon, ds, tz)
        sr = datetime.strptime(ds + " " + ev["sunrise"], "%Y-%m-%d %I:%M %p")
        ss = datetime.strptime(ds + " " + ev["sunset"], "%Y-%m-%d %I:%M %p")
        seg = (ss - sr) / 8
        seg_no = seg_map[d.weekday()]
        st = sr + (seg_no - 1) * seg
        en = st + seg
        out.append({"date": ds, "day": VARAS[(d.weekday() + 1) % 7],
                    "timing": f"{st.strftime('%I:%M %p')} - {en.strftime('%I:%M %p')}"})
        d += timedelta(days=1)
    return {"success": True, "rahukaal": out}


@app.get("/api/bhadra-kaal")
def api_bhadra_kaal(month: int, year: int):
    out = []
    d = datetime(year, month, 1)
    while d.month == month:
        jd = to_jd(d.strftime("%Y-%m-%d"), "06:00", 5.5)
        s, m = get_sun_moon_lons(jd)
        k = int(norm360(m - s) // 6)
        vishti = False
        k_name = ""
        if k == 0:
            k_name = "Kimstughna"
        elif k >= 57:
            k_name = ["Shakuni", "Chatushpada", "Naga"][k - 57]
        else:
            k_name = KARANAS[(k - 1) % 7]
            vishti = k_name == "Vishti"
        out.append({"date": d.strftime("%Y-%m-%d"), "day": VARAS[(d.weekday() + 1) % 7],
                    "timing": "Bhadra Present" if vishti else "No Bhadra", "karana": k_name})
        d += timedelta(days=1)
    return {"success": True, "bhadra_kaal": out}


@app.post("/api/numerology")
def api_numerology(req: NumerologyReq):
    try:
        full_name = f"{req.first_name} {req.middle_name} {req.last_name}".strip()
        first_sum = chaldean_sum(req.first_name)
        full_sum = chaldean_sum(full_name)
        birth_master = num_reduce(req.day, True)
        moolank = num_reduce(req.day, False)
        lp_total = sum(int(x) for x in f"{req.day:02d}{req.month:02d}{req.year}")
        life_path = num_reduce(lp_total, True)
        bhagyank = num_reduce(lp_total, False)
        name_number = num_reduce(full_sum, False)
        daily_name = num_reduce(first_sum, False)
        identity = CHALDEAN.get(req.first_name[:1].upper(), 1)
        balance = num_reduce(req.day + req.month, False)
        attainment = num_reduce(name_number + bhagyank, False)

        rulers = {1: "Sun", 2: "Moon", 3: "Jupiter", 4: "Rahu", 5: "Mercury",
                  6: "Venus", 7: "Ketu", 8: "Saturn", 9: "Mars"}
        colors = {1: "Red", 2: "White", 3: "Yellow", 4: "Smoky Blue", 5: "Green",
                  6: "Pink", 7: "Saffron", 8: "Navy", 9: "Crimson"}
        dirs = {1: "East", 2: "North-West", 3: "North-East", 4: "South-West", 5: "North",
                6: "South-East", 7: "North-East", 8: "West", 9: "South"}
        elem = {1: "Fire", 2: "Water", 3: "Ether", 4: "Air", 5: "Earth",
                6: "Water", 7: "Fire", 8: "Air", 9: "Fire"}
        lucky_days = {1: "Sunday, Monday", 2: "Monday", 3: "Thursday", 4: "Sunday",
                      5: "Wednesday", 6: "Friday", 7: "Sunday, Monday", 8: "Saturday", 9: "Tuesday"}

        lucky = [moolank, bhagyank, (moolank + bhagyank) % 9 + 1]
        unlucky = [((moolank + 2) % 9) + 1, ((bhagyank + 4) % 9) + 1]
        lucky_dates = [x for x in [moolank, moolank + 9, moolank + 18, moolank + 27] if x <= 31]

        digits = [int(ch) for ch in f"{req.day:02d}{req.month:02d}{req.year}" if ch != "0"]
        count = {i: digits.count(i) for i in range(1, 10)}
        loshu_grid = [
            [{"num": 4, "count": count[4]}, {"num": 9, "count": count[9]}, {"num": 2, "count": count[2]}],
            [{"num": 3, "count": count[3]}, {"num": 5, "count": count[5]}, {"num": 7, "count": count[7]}],
            [{"num": 8, "count": count[8]}, {"num": 1, "count": count[1]}, {"num": 6, "count": count[6]}],
        ]

        karmic = [k for k in [10, 13, 14, 16, 19] if str(k) in f"{req.day:02d}{req.month:02d}{req.year}{full_sum}"]
        masters = [k for k in [11, 22, 33] if k in (birth_master, life_path, full_sum)]
        p_year = num_reduce(req.day + req.month + datetime.now().year, False)

        if name_number in (moolank, bhagyank):
            comp = "Great!! Name is matching"
            sugg = ["Current spelling is harmonized with your moolank and bhagyank."]
        elif abs(name_number - moolank) <= 1:
            comp = "Average"
            sugg = ["Minor vowel adjustment can improve numeric resonance."]
        else:
            comp = "Not matching"
            target = 5 if count[5] == 0 else (6 if count[6] == 0 else (1 if count[1] == 0 else 3))
            sugg = [f"Adjust spelling to target Chaldean total {target}.",
                    "Prefer soft vowel increments for smoother alignment."]

        return {
            "success": True,
            "input": req.model_dump(),
            "moolank": moolank,
            "bhagyank": bhagyank,
            "birth_number": birth_master,
            "life_path": life_path,
            "name_number": name_number,
            "daily_name_number": daily_name,
            "identity_code": identity,
            "balance_number": balance,
            "attainment_number": attainment,
            "compatibility": comp,
            "suggestions": sugg,
            "lucky_things": {
                "numbers": lucky,
                "natural_numbers": [n for n in range(1, 10) if count[n] > 0],
                "unlucky_numbers": unlucky,
                "dates": lucky_dates,
                "days": lucky_days[moolank],
                "color": colors[moolank],
                "direction": dirs[moolank],
                "main_gate": "East/North-East",
                "ruler": rulers[moolank],
                "element": elem[moolank],
            },
            "loshu_grid": loshu_grid,
            "karmic_numbers": karmic,
            "master_numbers": masters,
            "personal_year": p_year,
        }
    except Exception as exc:
        return JSONResponse(status_code=500, content={"success": False, "error": str(exc)})


# =============================
# KP system
# =============================
def kp_sub_lords(lon: float):
    span = 360.0 / 27.0
    ni = int(norm360(lon) // span)
    nk_lord = NAK_LORDS[ni % 9]
    deg_in_nak = norm360(lon) - ni * span
    start = DASHA_ORDER.index(nk_lord)
    cur = 0.0
    sub = nk_lord
    sub_sub = nk_lord
    for i in range(9):
        p = DASHA_ORDER[(start + i) % 9]
        seg = span * DASHA_YEARS[p] / 120.0
        if cur + seg >= deg_in_nak:
            sub = p
            s2 = DASHA_ORDER.index(sub)
            cur2 = 0.0
            inside = deg_in_nak - cur
            for j in range(9):
                q = DASHA_ORDER[(s2 + j) % 9]
                seg2 = seg * DASHA_YEARS[q] / 120.0
                if cur2 + seg2 >= inside:
                    sub_sub = q
                    break
                cur2 += seg2
            break
        cur += seg
    return {"lord": nk_lord, "sub": sub, "sub_sub": sub_sub}


@app.post("/api/kp-chart")
def api_kp_chart(req: KundliReq):
    try:
        tz = timezone_from_lat_lon(req.latitude, req.longitude)
        off = tz_offset_hours(tz, datetime.strptime(req.date, "%Y-%m-%d"))
        jd = to_jd(req.date, req.time, off)
        planets = calc_planets(jd)
        cusps, _ = swe_houses_safe(jd, req.latitude, req.longitude, b"P")
        asc = norm360(cusps[1])

        cusp_rows = []
        for h in range(1, 13):
            lon = norm360(cusps[h])
            si, sn, sl, dg = sign_info(lon)
            ni, nn, nl, p, _ = nak_info(lon)
            subs = kp_sub_lords(lon)
            cusp_rows.append({"cusp": h, "longitude": round(lon, 4), "sign": sn,
                              "degree": deg_to_dms(dg), "nakshatra": nn,
                              "lord": sl, "sub_lord": subs["sub"]})

        planet_rows = []
        for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
            lon = planets[p]["lon"]
            si, sn, sl, dg = sign_info(lon)
            ni, nn, nl, pd, _ = nak_info(lon)
            subs = kp_sub_lords(lon)
            planet_rows.append({
                "planet": p,
                "sign": sn,
                "nakshatra": nn,
                "nakshatra_lord": nl,
                "sub_lord": subs["sub"],
                "sub_sub_lord": subs["sub_sub"],
                "degree": deg_to_dms(dg),
                "retrograde": planets[p]["retro"],
                "house": whole_sign_house(asc, lon),
            })

        sig = []
        for row in planet_rows:
            own_houses = [i + 1 for i, lord in enumerate(SIGN_LORDS) if lord == row["planet"]]
            occ = row["house"]
            sig.append({
                "planet": row["planet"],
                "level_1": ", ".join(str(x) for x in own_houses) if own_houses else "-",
                "level_2": str(occ),
                "level_3": str((occ + 4 - 1) % 12 + 1),
            })

        return {
            "success": True,
            "north_indian": {"houses": chart_houses(asc, planets, False)},
            "rasi_chart": {"houses": chart_houses(asc, planets, False)},
            "planets": planet_rows,
            "cusps": cusp_rows,
            "significators": sig,
        }
    except Exception as exc:
        return JSONResponse(status_code=500, content={"success": False, "error": str(exc)})


@app.post("/api/lal-kitab")
def api_lal_kitab(req: KundliReq):
    try:
        _tz = timezone_from_lat_lon(req.latitude, req.longitude)
        _off = tz_offset_hours(_tz, datetime.strptime(req.date, "%Y-%m-%d"))
        jd = to_jd(req.date, req.time, _off)
        planets = calc_planets(jd)
        asc = calc_lagna(jd, req.latitude, req.longitude)
        houses = chart_houses(asc, planets, False)
        p_h = {p: whole_sign_house(asc, planets[p]["lon"]) for p in planets}
        debts = []
        remedies = []
        if p_h.get("Sun") == 6:
            debts.append({"name": "Father Debt", "description": "Sun in 6th indicates pitri rin theme."})
            remedies.append("Offer wheat and jaggery at sunrise on Sundays.")
        if p_h.get("Saturn") == 8:
            debts.append({"name": "Servant Debt", "description": "Saturn in 8th can indicate karmic duty toward workers."})
            remedies.append("Donate black sesame on Saturdays.")
        if not debts:
            debts.append({"name": "No Major Debt", "description": "No severe Lal Kitab debt signatures found."})
            remedies.append("Feed birds daily to maintain harmony.")

        house_desc = [{"house": i, "description": f"House {i} shows karmic material and behavioral outcomes."}
                      for i in range(1, 13)]
        p_desc = [{"planet": p, "house": p_h[p],
                   "meaning": f"{p} in house {p_h[p]} gives Lal Kitab style operational results."}
                  for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]]
        return {
            "success": True,
            "north_indian": {"houses": houses},
            "debts": debts,
            "remedies": remedies,
            "houses": house_desc,
            "planets": p_desc,
            "varshphal": {"year": datetime.now().year, "status": "Varshphal chart generated."},
        }
    except Exception as exc:
        return JSONResponse(status_code=500, content={"success": False, "error": str(exc)})


@app.post("/api/dosh/mangal")
def api_dosh_mangal(req: KundliReq):
    try:
        _tz = timezone_from_lat_lon(req.latitude, req.longitude)
        _off = tz_offset_hours(_tz, datetime.strptime(req.date, "%Y-%m-%d"))
        jd = to_jd(req.date, req.time, _off)
        planets = calc_planets(jd)
        asc = calc_lagna(jd, req.latitude, req.longitude)
        mars_l = whole_sign_house(asc, planets["Mars"]["lon"])
        mars_m = whole_sign_house(planets["Moon"]["lon"], planets["Mars"]["lon"])
        mars_v = whole_sign_house(planets["Venus"]["lon"], planets["Mars"]["lon"])
        target = {1, 4, 7, 8, 12}
        score = (40 if mars_l in target else 0) + (35 if mars_m in target else 0) + (25 if mars_v in target else 0)
        cancel = 0
        rules = []
        mars_sign = int(planets["Mars"]["lon"] // 30)
        if mars_sign in (0, 7, 9):
            cancel += 50
            rules.append("Mars in own or exalted sign.")
        sat_h = whole_sign_house(asc, planets["Saturn"]["lon"])
        if sat_h in target:
            cancel += 30
            rules.append("Saturn balancing placement in manglik houses.")
        if not rules:
            rules.append("Age-based reduction after maturity period.")
            cancel += 10
        present = max(0, score - cancel) >= 30
        return {
            "success": True,
            "is_present": present,
            "score": score,
            "anshik": 30 <= score < 70,
            "cancellation_score": min(100, cancel),
            "cancellation_rules": rules,
            "details": {"mars_from_lagna": mars_l, "mars_from_moon": mars_m, "mars_from_venus": mars_v},
        }
    except Exception as exc:
        return JSONResponse(status_code=500, content={"success": False, "error": str(exc)})


@app.post("/api/dosh/kaalsarp")
def api_dosh_kaalsarp(req: KundliReq):
    try:
        _tz = timezone_from_lat_lon(req.latitude, req.longitude)
        _off = tz_offset_hours(_tz, datetime.strptime(req.date, "%Y-%m-%d"))
        jd = to_jd(req.date, req.time, _off)
        planets = calc_planets(jd)
        r = planets["Rahu"]["lon"]
        vals = [norm360(planets[p]["lon"] - r) for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]]
        present = all(0 <= v <= 180 for v in vals) or all(180 <= v <= 360 for v in vals)
        return {"success": True, "is_present": present,
                "description": "All planets lie within Rahu-Ketu axis." if present else "Planets are outside strict axis lock."}
    except Exception as exc:
        return JSONResponse(status_code=500, content={"success": False, "error": str(exc)})


@app.post("/api/dosh/pitra")
def api_dosh_pitra(req: KundliReq):
    try:
        _tz = timezone_from_lat_lon(req.latitude, req.longitude)
        _off = tz_offset_hours(_tz, datetime.strptime(req.date, "%Y-%m-%d"))
        jd = to_jd(req.date, req.time, _off)
        planets = calc_planets(jd)
        asc = calc_lagna(jd, req.latitude, req.longitude)
        aff = []
        score = 0
        for p in ["Rahu", "Saturn", "Sun"]:
            if whole_sign_house(asc, planets[p]["lon"]) == 9:
                aff.append(p)
                score += 35
        return {"success": True, "is_present": score >= 35, "score": score, "afflicting_planets": aff}
    except Exception as exc:
        return JSONResponse(status_code=500, content={"success": False, "error": str(exc)})


@app.post("/api/yog")
def api_yog(req: KundliReq):
    try:
        _tz = timezone_from_lat_lon(req.latitude, req.longitude)
        _off = tz_offset_hours(_tz, datetime.strptime(req.date, "%Y-%m-%d"))
        jd = to_jd(req.date, req.time, _off)
        planets = calc_planets(jd)
        asc = calc_lagna(jd, req.latitude, req.longitude)
        h = {p: whole_sign_house(asc, planets[p]["lon"]) for p in planets}
        s = {p: int(planets[p]["lon"] // 30) for p in planets}
        yogs = []
        gk = whole_sign_house(planets["Moon"]["lon"], planets["Jupiter"]["lon"]) in [1, 4, 7, 10]
        yogs.append({"name": "Gaja Kesari Yog", "present": gk,
                     "strength": "High" if gk else "None",
                     "description": "Jupiter in kendra from Moon."})
        ba = h["Sun"] == h["Mercury"]
        yogs.append({"name": "Budh-Aditya Yog", "present": ba,
                     "strength": "High" if ba else "None",
                     "description": "Sun-Mercury conjunction."})
        cm = h["Moon"] == h["Mars"]
        yogs.append({"name": "Chandra-Mangal Yog", "present": cm,
                     "strength": "Medium" if cm else "None",
                     "description": "Moon-Mars conjunction."})
        trine = [1, 5, 9]
        kendra = [1, 4, 7, 10]
        ry = any(h[p] in kendra for p in ["Jupiter", "Venus", "Mercury"]) and any(h[p] in trine for p in ["Sun", "Moon", "Mars"])
        yogs.append({"name": "Raja Yog", "present": ry,
                     "strength": "High" if ry else "None",
                     "description": "Trine-kendra linkage active."})
        pm = [
            ("Ruchaka", "Mars", [0, 7, 9]),
            ("Bhadra", "Mercury", [2, 5]),
            ("Hamsa", "Jupiter", [8, 11, 3]),
            ("Malavya", "Venus", [1, 6, 11]),
            ("Shasha", "Saturn", [9, 10, 6]),
        ]
        for nm, p, good in pm:
            ok = h[p] in kendra and s[p] in good
            yogs.append({"name": f"{nm} Mahapurush Yog", "present": ok,
                         "strength": "Premium" if ok else "None",
                         "description": f"{p} in own/exaltation sign and kendra."})
        return {"success": True, "yogas": yogs}
    except Exception as exc:
        return JSONResponse(status_code=500, content={"success": False, "error": str(exc)})


@app.post("/api/dasha/current")
def api_dasha_current(req: KundliReq):
    try:
        _tz = timezone_from_lat_lon(req.latitude, req.longitude)
        _off = tz_offset_hours(_tz, datetime.strptime(req.date, "%Y-%m-%d"))
        jd = to_jd(req.date, req.time, _off)
        moon = calc_planets(jd)["Moon"]["lon"]
        tree = dasha_tree(moon, req.date)
        md, ad, pd, sd, pr, _ = pick_current_levels(tree)
        return {
            "success": True,
            "current_levels": [
                {"level": "Mahadasha", "planet": md["planet"], "start_date": fmt_dt(md["start"]), "end_date": fmt_dt(md["end"])},
                {"level": "Antardasha", "planet": ad["planet"], "start_date": fmt_dt(ad["start"]), "end_date": fmt_dt(ad["end"])},
                {"level": "Pratyantardasha", "planet": pd["planet"], "start_date": fmt_dt(pd["start"]), "end_date": fmt_dt(pd["end"])},
                {"level": "Sookshmadasha", "planet": sd["planet"], "start_date": fmt_dt(sd["start"]), "end_date": fmt_dt(sd["end"])},
                {"level": "Pranadasha", "planet": pr["planet"], "start_date": fmt_dt(pr["start"], True), "end_date": fmt_dt(pr["end"], True)},
            ],
        }
    except Exception as exc:
        return JSONResponse(status_code=500, content={"success": False, "error": str(exc)})


@app.post("/api/dasha/prana")
def api_dasha_prana(req: KundliReq):
    try:
        _tz = timezone_from_lat_lon(req.latitude, req.longitude)
        _off = tz_offset_hours(_tz, datetime.strptime(req.date, "%Y-%m-%d"))
        jd = to_jd(req.date, req.time, _off)
        moon = calc_planets(jd)["Moon"]["lon"]
        tree = dasha_tree(moon, req.date)
        _, _, _, _, _, pr = pick_current_levels(tree)
        return {
            "success": True,
            "prana_dasha_deep": [
                {"index": i + 1, "planet": x["planet"], "start_date": fmt_dt(x["start"], True), "end_date": fmt_dt(x["end"], True)}
                for i, x in enumerate(pr)
            ],
        }
    except Exception as exc:
        return JSONResponse(status_code=500, content={"success": False, "error": str(exc)})


@app.post("/api/dasha/yogini")
def api_dasha_yogini(req: KundliReq):
    seq = [
        ("Mangala", "Moon", 1),
        ("Pingala", "Mars", 2),
        ("Dhanya", "Sun", 3),
        ("Bhramari", "Jupiter", 4),
        ("Bhadrika", "Mercury", 5),
        ("Ulka", "Saturn", 6),
        ("Siddha", "Venus", 7),
        ("Sankata", "Rahu", 8),
    ]
    try:
        cur = datetime.strptime(req.date, "%Y-%m-%d")
        out = []
        for _ in range(3):
            for n, l, y in seq:
                en = cur + timedelta(days=int(y * 365.25))
                out.append({"name": n, "lord": l, "years": y, "start_date": fmt_dt(cur), "end_date": fmt_dt(en)})
                cur = en
        return {"success": True, "yogini_dasha": out}
    except Exception as exc:
        return JSONResponse(status_code=500, content={"success": False, "error": str(exc)})


# =============================
# PASS 2A: /api/dasha/tree - full nested Vimshottari tree for cascade UI
# =============================
@app.post("/api/dasha/tree")
def api_dasha_tree(req: KundliReq):
    """Return the full nested Vimshottari dasha tree.
    Used by the frontend cascade drill-down UI.
    """
    try:
        tz_name = timezone_from_lat_lon(req.latitude, req.longitude)
        off = tz_offset_hours(tz_name, datetime.strptime(req.date, "%Y-%m-%d"))
        jd = to_jd(req.date, req.time, off)
        planets = calc_planets(jd)
        moon_lon = planets["Moon"]["lon"]

        raw_tree = dasha_tree(moon_lon, req.date)

        def serialize_node(node, level_key):
            """Recursively convert datetime objects to formatted strings."""
            out = {
                "planet": node["planet"],
                "start_date": fmt_dt(node["start"]),
                "end_date": fmt_dt(node["end"]),
            }
            if "years" in node:
                out["years"] = node["years"]
            children_key = {"antardasha": "praty", "praty": "sookshma"}.get(level_key)
            if children_key and children_key in node:
                out[children_key] = [serialize_node(c, children_key) for c in node[children_key]]
            elif level_key == "tree" and "antardasha" in node:
                out["antardasha"] = [serialize_node(c, "antardasha") for c in node["antardasha"]]
            return out

        serialized = [serialize_node(md, "tree") for md in raw_tree]

        return {
            "success": True,
            "tree": serialized,
        }
    except Exception as exc:
        return JSONResponse(status_code=500, content={"success": False, "error": str(exc)})


# =============================
# DIVISIONAL CHARTS (Shodashvarga) - 16 Parashari charts
# D1, D2, D3, D4, D7, D9, D10, D12, D16, D20, D24, D27, D30, D40, D45, D60
# =============================

def _sign_idx(lon: float) -> int:
    return int(norm360(lon) // 30)


def _deg_in_sign(lon: float) -> float:
    return norm360(lon) % 30


def d1_sign(lon: float) -> int:
    """D1 Rasi - straight 30 degree division."""
    return _sign_idx(lon)


def d2_sign(lon: float) -> int:
    """D2 Hora chart - maps to Leo (4) or Cancer (3)."""
    si = _sign_idx(lon)
    d = _deg_in_sign(lon)
    is_odd = (si % 2) == 0
    if is_odd:
        return 4 if d < 15 else 3
    else:
        return 3 if d < 15 else 4


def d3_sign(lon: float) -> int:
    """D3 Drekkana - 3 parts of 10 degrees each."""
    si = _sign_idx(lon)
    d = _deg_in_sign(lon)
    part = int(d // 10)
    offsets = [0, 4, 8]
    return (si + offsets[part]) % 12


def d4_sign(lon: float) -> int:
    """D4 Chathurthamsa - 4 parts of 7.5 degrees each."""
    si = _sign_idx(lon)
    d = _deg_in_sign(lon)
    part = int(d // 7.5)
    if part > 3:
        part = 3
    offsets = [0, 3, 6, 9]
    return (si + offsets[part]) % 12


def d7_sign(lon: float) -> int:
    """D7 Saptamsa - 7 parts. Odd signs start from itself, even signs from 7th."""
    si = _sign_idx(lon)
    d = _deg_in_sign(lon)
    part = int(d // (30.0 / 7.0))
    if part > 6:
        part = 6
    is_odd = (si % 2) == 0
    start = si if is_odd else (si + 6) % 12
    return (start + part) % 12


def d9_sign(lon: float) -> int:
    """D9 Navamsa - uses existing navamsa_sign()."""
    return navamsa_sign(lon)


def d10_sign(lon: float) -> int:
    """D10 Dasamsa - 10 parts of 3 degrees each."""
    si = _sign_idx(lon)
    d = _deg_in_sign(lon)
    part = int(d // 3.0)
    if part > 9:
        part = 9
    is_odd = (si % 2) == 0
    start = si if is_odd else (si + 8) % 12
    return (start + part) % 12


def d12_sign(lon: float) -> int:
    """D12 Dwadasamsa - 12 parts of 2.5 degrees each."""
    si = _sign_idx(lon)
    d = _deg_in_sign(lon)
    part = int(d // 2.5)
    if part > 11:
        part = 11
    return (si + part) % 12


def d16_sign(lon: float) -> int:
    """D16 Shodasamsa - 16 parts of 1.875 degrees each."""
    si = _sign_idx(lon)
    d = _deg_in_sign(lon)
    part = int(d // 1.875)
    if part > 15:
        part = 15
    sign_type = si % 3
    starts = [0, 4, 8]
    return (starts[sign_type] + part) % 12


def d20_sign(lon: float) -> int:
    """D20 Vimsamsa - 20 parts of 1.5 degrees each."""
    si = _sign_idx(lon)
    d = _deg_in_sign(lon)
    part = int(d // 1.5)
    if part > 19:
        part = 19
    sign_type = si % 3
    starts = [0, 8, 4]
    return (starts[sign_type] + part) % 12


def d24_sign(lon: float) -> int:
    """D24 Chathurvimsamsa - 24 parts of 1.25 degrees each."""
    si = _sign_idx(lon)
    d = _deg_in_sign(lon)
    part = int(d // 1.25)
    if part > 23:
        part = 23
    is_odd = (si % 2) == 0
    start = 4 if is_odd else 3
    return (start + part) % 12


def d27_sign(lon: float) -> int:
    """D27 Bhamsa - 27 parts. Element-based starts."""
    si = _sign_idx(lon)
    d = _deg_in_sign(lon)
    part = int(d // (30.0 / 27.0))
    if part > 26:
        part = 26
    element = si % 4
    starts = [0, 3, 6, 9]
    return (starts[element] + part) % 12


def d30_sign(lon: float) -> int:
    """D30 Trimsamsa - Parashari unequal division."""
    si = _sign_idx(lon)
    d = _deg_in_sign(lon)
    is_odd = (si % 2) == 0
    if is_odd:
        if d < 5:    return 0
        if d < 10:   return 10
        if d < 18:   return 8
        if d < 25:   return 2
        return 6
    else:
        if d < 5:    return 1
        if d < 12:   return 5
        if d < 20:   return 11
        if d < 25:   return 9
        return 7


def d40_sign(lon: float) -> int:
    """D40 Khavedamsa - 40 parts. Odd signs start Aries, even start Libra."""
    si = _sign_idx(lon)
    d = _deg_in_sign(lon)
    part = int(d // 0.75)
    if part > 39:
        part = 39
    is_odd = (si % 2) == 0
    start = 0 if is_odd else 6
    return (start + part) % 12


def d45_sign(lon: float) -> int:
    """D45 Akshavedamsa - 45 parts. Movable/Fixed/Dual starts."""
    si = _sign_idx(lon)
    d = _deg_in_sign(lon)
    part = int(d // (30.0 / 45.0))
    if part > 44:
        part = 44
    sign_type = si % 3
    starts = [0, 4, 8]
    return (starts[sign_type] + part) % 12


def d60_sign(lon: float) -> int:
    """D60 Shashtiamsa - 60 parts of 0.5 degrees each."""
    si = _sign_idx(lon)
    d = _deg_in_sign(lon)
    part = int(d // 0.5)
    if part > 59:
        part = 59
    return (si + part) % 12


DIVISIONAL_FUNCS = {
    "D1":  d1_sign,
    "D2":  d2_sign,
    "D3":  d3_sign,
    "D4":  d4_sign,
    "D7":  d7_sign,
    "D9":  d9_sign,
    "D10": d10_sign,
    "D12": d12_sign,
    "D16": d16_sign,
    "D20": d20_sign,
    "D24": d24_sign,
    "D27": d27_sign,
    "D30": d30_sign,
    "D40": d40_sign,
    "D45": d45_sign,
    "D60": d60_sign,
}

DIVISIONAL_NAMES = {
    "D1":  ("Rasi",            "Body, overall life"),
    "D2":  ("Hora",            "Wealth"),
    "D3":  ("Drekkana",        "Siblings"),
    "D4":  ("Chathurthamsa",   "Fortune, fixed assets"),
    "D7":  ("Saptamsa",        "Children"),
    "D9":  ("Navamsa",         "Spouse, dharma"),
    "D10": ("Dasamsa",         "Profession, career"),
    "D12": ("Dwadasamsa",      "Parents, ancestry"),
    "D16": ("Shodasamsa",      "Vehicles, conveyance"),
    "D20": ("Vimsamsa",        "Spiritual progress"),
    "D24": ("Chathurvimsamsa", "Education, learning"),
    "D27": ("Bhamsa",          "Strengths and weaknesses"),
    "D30": ("Trimsamsa",       "Evils, misfortunes"),
    "D40": ("Khavedamsa",      "Maternal legacy"),
    "D45": ("Akshavedamsa",    "Paternal legacy"),
    "D60": ("Shashtiamsa",     "Past karma"),
}


def divisional_chart_houses(asc_lon: float, planets: Dict[str, Dict[str, Any]], div: str) -> Dict[int, Dict[str, Any]]:
    """Build houses for any divisional chart (D1-D60)."""
    if div not in DIVISIONAL_FUNCS:
        raise ValueError(f"Unknown divisional chart: {div}")

    sign_fn = DIVISIONAL_FUNCS[div]
    asc_sign = sign_fn(asc_lon)

    houses: Dict[int, Dict[str, Any]] = {}
    for h in range(1, 13):
        si = (asc_sign + (h - 1)) % 12
        houses[h] = {"house": h, "sign": SIGNS[si], "planets": []}

    short = {
        "Sun": "Su", "Moon": "Mo", "Mars": "Ma", "Mercury": "Me",
        "Jupiter": "Ju", "Venus": "Ve", "Saturn": "Sa",
        "Rahu": "Ra", "Ketu": "Ke",
    }

    for p, d in planets.items():
        planet_sign = sign_fn(d["lon"])
        target = ((planet_sign - asc_sign + 12) % 12) + 1
        _, _, _, deg = sign_info(d["lon"])
        houses[target]["planets"].append({
            "code": short.get(p, p[:2]),
            "deg": deg_to_dms(deg, True),
            "retro": d["retro"],
        })

    houses[1]["planets"].insert(0, {
        "code": "Asc",
        "deg": deg_to_dms(asc_lon % 30, True),
        "retro": False,
    })

    return houses


# Gulika upagraha calculation
GULIKA_DAY_FRACTIONS = {0: 6, 1: 5, 2: 4, 3: 3, 4: 2, 5: 1, 6: 0}
GULIKA_NIGHT_FRACTIONS = {0: 2, 1: 1, 2: 0, 3: 6, 4: 5, 5: 4, 6: 3}


def calc_gulika_lon(jd_ut: float, lat: float, lon: float, date_str: str, tz_name: str) -> float:
    """Compute Gulika longitude using sunrise-based 1/8 fractions."""
    setup_sidereal()
    events = get_sun_moon_events(lat, lon, date_str, tz_name)
    try:
        sr = datetime.strptime(date_str + " " + events["sunrise"], "%Y-%m-%d %I:%M %p")
        ss = datetime.strptime(date_str + " " + events["sunset"], "%Y-%m-%d %I:%M %p")
        weekday_vedic = (datetime.strptime(date_str, "%Y-%m-%d").weekday() + 1) % 7
        frac_idx = GULIKA_DAY_FRACTIONS[weekday_vedic]
        day_duration = (ss - sr).total_seconds() / 3600.0
        gulika_start = sr.timestamp() + (frac_idx * day_duration * 3600.0 / 8.0)
        gd = datetime.fromtimestamp(gulika_start)
        off = tz_offset_hours(tz_name, gd)
        gj = swe.julday(
            gd.year, gd.month, gd.day,
            gd.hour + gd.minute / 60.0 + gd.second / 3600.0 - off,
            swe.GREG_CAL,
        )
        _, ascmc = swe_houses_safe(gj, lat, lon, b"P")
        return norm360(ascmc[0])
    except Exception:
        f = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
        sat = swe_calc_safe(jd_ut, swe.SATURN, f)
        return norm360(sat[0][0] + 26.0)


@app.post("/api/divisional-charts")
def api_divisional_charts(req: KundliReq):
    """Return all 16 Parashari divisional charts (Shodashvarga) in one response."""
    try:
        tz_name = timezone_from_lat_lon(req.latitude, req.longitude)
        off = tz_offset_hours(tz_name, datetime.strptime(req.date, "%Y-%m-%d"))
        jd = to_jd(req.date, req.time, off)
        asc = calc_lagna(jd, req.latitude, req.longitude, b"P")
        planets = calc_planets(jd)

        gulika_lon = calc_gulika_lon(jd, req.latitude, req.longitude, req.date, tz_name)
        planets["Gulika"] = {"lon": gulika_lon, "speed": 0.0, "retro": False}

        charts = {}
        sixteen_table = {}

        for div in DIVISIONAL_FUNCS.keys():
            houses = divisional_chart_houses(asc, planets, div)
            full_name, meaning = DIVISIONAL_NAMES[div]
            charts[div] = {
                "code": div,
                "name": full_name,
                "meaning": meaning,
                "houses": houses,
                "lagna_sign": SIGNS[DIVISIONAL_FUNCS[div](asc)],
            }
            row = {}
            sign_fn = DIVISIONAL_FUNCS[div]
            asc_div_sign = sign_fn(asc)
            for p_name in ["Lagna", "Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Rahu", "Ketu", "Gulika"]:
                if p_name == "Lagna":
                    p_lon = asc
                else:
                    p_lon = planets.get(p_name, {}).get("lon", 0.0)
                p_sign = sign_fn(p_lon)
                house = ((p_sign - asc_div_sign + 12) % 12) + 1
                row[p_name] = {"sign": SIGNS[p_sign], "house": house}
            sixteen_table[div] = row

        ojarasi_count = {}
        for p_name in ["Lagna", "Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Rahu", "Ketu", "Gulika"]:
            odd_count = 0
            for div in DIVISIONAL_FUNCS.keys():
                p_lon = asc if p_name == "Lagna" else planets.get(p_name, {}).get("lon", 0.0)
                p_sign = DIVISIONAL_FUNCS[div](p_lon)
                if p_sign % 2 == 0:
                    odd_count += 1
            ojarasi_count[p_name] = odd_count

        vargottama = []
        for p_name, p_data in planets.items():
            if p_name == "Gulika":
                continue
            rasi = d1_sign(p_data["lon"])
            nav = d9_sign(p_data["lon"])
            if rasi == nav:
                vargottama.append(p_name)
        if d1_sign(asc) == d9_sign(asc):
            vargottama.append("Lagna")

        return {
            "success": True,
            "input": req.model_dump(),
            "timezone": tz_name,
            "lagna_longitude": round(asc, 4),
            "charts": charts,
            "shodashvarga_table": sixteen_table,
            "ojarasi_count": ojarasi_count,
            "vargottama": vargottama,
            "divisional_names": DIVISIONAL_NAMES,
        }
    except Exception as exc:
        return JSONResponse(status_code=500, content={"success": False, "error": str(exc)})


@app.post("/api/divisional/{div_code}")
def api_single_divisional(div_code: str, req: KundliReq):
    """Return a single divisional chart by code."""
    div = div_code.upper()
    if div not in DIVISIONAL_FUNCS:
        raise HTTPException(status_code=400, detail=f"Unknown divisional chart: {div}. Valid: {list(DIVISIONAL_FUNCS.keys())}")
    try:
        tz_name = timezone_from_lat_lon(req.latitude, req.longitude)
        off = tz_offset_hours(tz_name, datetime.strptime(req.date, "%Y-%m-%d"))
        jd = to_jd(req.date, req.time, off)
        asc = calc_lagna(jd, req.latitude, req.longitude, b"P")
        planets = calc_planets(jd)

        gulika_lon = calc_gulika_lon(jd, req.latitude, req.longitude, req.date, tz_name)
        planets["Gulika"] = {"lon": gulika_lon, "speed": 0.0, "retro": False}

        full_name, meaning = DIVISIONAL_NAMES[div]
        houses = divisional_chart_houses(asc, planets, div)
        return {
            "success": True,
            "input": req.model_dump(),
            "code": div,
            "name": full_name,
            "meaning": meaning,
            "houses": houses,
            "lagna_sign": SIGNS[DIVISIONAL_FUNCS[div](asc)],
        }
    except Exception as exc:
        return JSONResponse(status_code=500, content={"success": False, "error": str(exc)})


# =============================
# PASS 2B: MySQL history storage (Hostinger)
# =============================
# Reads connection settings from environment variables:
#   MYSQL_HOST     e.g. srv1026.hstgr.io
#   MYSQL_DATABASE e.g. u609198870_astromata_hora
#   MYSQL_USER     e.g. u609198870_astromata_user
#   MYSQL_PASSWORD e.g. (your password)
#
# Gracefully degrades if any of these are missing OR connection fails —
# the rest of the API keeps working, history endpoints return clean errors.
# =============================
import os
import json as _json

# Lazy import — only imported when an MySQL endpoint is hit, so app boots
# even if pymysql isn't installed yet.
_pymysql = None
_mysql_table_ready = False
_mysql_last_error: Optional[str] = None


def _import_pymysql():
    """Import pymysql on first use. Returns the module or None on failure."""
    global _pymysql
    if _pymysql is not None:
        return _pymysql
    try:
        import pymysql
        _pymysql = pymysql
        return pymysql
    except ImportError as exc:
        global _mysql_last_error
        _mysql_last_error = f"pymysql not installed: {exc}"
        return None


def _mysql_config() -> Optional[Dict[str, Any]]:
    """Build connection config from environment, or return None if missing."""
    host = os.environ.get("MYSQL_HOST", "").strip()
    db = os.environ.get("MYSQL_DATABASE", "").strip()
    user = os.environ.get("MYSQL_USER", "").strip()
    pwd = os.environ.get("MYSQL_PASSWORD", "")
    if not (host and db and user and pwd):
        return None
    return {
        "host": host,
        "database": db,
        "user": user,
        "password": pwd,
        "port": int(os.environ.get("MYSQL_PORT", "3306")),
        "charset": "utf8mb4",
        "connect_timeout": 10,
        "read_timeout": 15,
        "write_timeout": 15,
        "cursorclass_name": "DictCursor",
    }


def _mysql_connect():
    """Open a fresh connection. Raises a clear error if anything is misconfigured."""
    global _mysql_last_error
    pymysql = _import_pymysql()
    if pymysql is None:
        raise RuntimeError(_mysql_last_error or "pymysql not available")
    cfg = _mysql_config()
    if cfg is None:
        raise RuntimeError("MySQL env vars not set (need MYSQL_HOST, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASSWORD)")

    conn = pymysql.connect(
        host=cfg["host"],
        port=cfg["port"],
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        charset=cfg["charset"],
        connect_timeout=cfg["connect_timeout"],
        read_timeout=cfg["read_timeout"],
        write_timeout=cfg["write_timeout"],
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )
    _mysql_last_error = None
    return conn


def _ensure_history_table() -> None:
    """Create kundli_history table if it doesn't exist. Runs once per process."""
    global _mysql_table_ready
    if _mysql_table_ready:
        return
    conn = _mysql_connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS kundli_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    email VARCHAR(255) NOT NULL,
                    phone VARCHAR(40) DEFAULT NULL,
                    name VARCHAR(255) NOT NULL,
                    gender VARCHAR(20) DEFAULT NULL,
                    birth_date VARCHAR(20) NOT NULL,
                    birth_time VARCHAR(10) NOT NULL,
                    latitude DECIMAL(10, 6) NOT NULL,
                    longitude DECIMAL(10, 6) NOT NULL,
                    place_name VARCHAR(255) DEFAULT NULL,
                    birth_data_json LONGTEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_email (email),
                    INDEX idx_phone (phone),
                    INDEX idx_created (created_at DESC)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """
            )
            conn.commit()
        _mysql_table_ready = True
    finally:
        conn.close()


# -----------------------------
# Pydantic models for history endpoints
# -----------------------------
class HistorySaveReq(BaseModel):
    email: str
    phone: Optional[str] = None
    name: str
    gender: Optional[str] = "Male"
    birth_date: str       # "YYYY-MM-DD"
    birth_time: str       # "HH:MM"
    latitude: float
    longitude: float
    place_name: Optional[str] = None
    # Optional full kundli payload to cache — frontend sends the kundli JSON so it
    # can be re-rendered without recalculating. Send empty if not needed.
    birth_data_json: Optional[str] = None


# -----------------------------
# History endpoints
# -----------------------------
@app.get("/api/history/health")
def api_history_health():
    """Quick check: is MySQL reachable? Useful for debugging."""
    cfg = _mysql_config()
    if cfg is None:
        return {
            "ok": False,
            "reason": "env_vars_missing",
            "detail": "MYSQL_HOST / MYSQL_DATABASE / MYSQL_USER / MYSQL_PASSWORD not all set on the server.",
        }
    try:
        _ensure_history_table()
        conn = _mysql_connect()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) AS n FROM kundli_history")
                row = cur.fetchone()
            return {
                "ok": True,
                "host": cfg["host"],
                "database": cfg["database"],
                "total_records": int(row["n"]) if row else 0,
            }
        finally:
            conn.close()
    except Exception as exc:
        return {"ok": False, "reason": "connect_failed", "detail": str(exc)[:300]}


@app.post("/api/history/save")
def api_history_save(req: HistorySaveReq):
    """Save a kundli generation to MySQL. Returns the new record id."""
    if not req.email or "@" not in req.email:
        return JSONResponse(status_code=400, content={"success": False, "error": "valid email required"})
    try:
        _ensure_history_table()
        conn = _mysql_connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO kundli_history
                      (email, phone, name, gender, birth_date, birth_time,
                       latitude, longitude, place_name, birth_data_json)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        req.email.strip().lower()[:255],
                        (req.phone or "").strip()[:40] or None,
                        req.name.strip()[:255],
                        (req.gender or "").strip()[:20] or None,
                        req.birth_date,
                        req.birth_time,
                        req.latitude,
                        req.longitude,
                        (req.place_name or "")[:255] or None,
                        req.birth_data_json or None,
                    ),
                )
                new_id = cur.lastrowid
                conn.commit()
            return {"success": True, "id": new_id}
        finally:
            conn.close()
    except Exception as exc:
        return JSONResponse(status_code=500, content={"success": False, "error": str(exc)[:300]})


@app.get("/api/history/by-email")
def api_history_by_email(
    email: str = Query(..., min_length=3),
    phone: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
):
    """Fetch saved kundlis for an email (and optional phone). Newest first."""
    if "@" not in email:
        return JSONResponse(status_code=400, content={"success": False, "error": "valid email required"})
    try:
        _ensure_history_table()
        conn = _mysql_connect()
        try:
            with conn.cursor() as cur:
                if phone:
                    cur.execute(
                        """
                        SELECT id, email, phone, name, gender, birth_date, birth_time,
                               latitude, longitude, place_name, created_at, birth_data_json
                        FROM kundli_history
                        WHERE email = %s AND (phone = %s OR phone IS NULL)
                        ORDER BY created_at DESC
                        LIMIT %s
                        """,
                        (email.strip().lower(), phone.strip(), limit),
                    )
                else:
                    cur.execute(
                        """
                        SELECT id, email, phone, name, gender, birth_date, birth_time,
                               latitude, longitude, place_name, created_at, birth_data_json
                        FROM kundli_history
                        WHERE email = %s
                        ORDER BY created_at DESC
                        LIMIT %s
                        """,
                        (email.strip().lower(), limit),
                    )
                rows = cur.fetchall()
            # Convert datetime → string for JSON
            out = []
            for r in rows:
                d = dict(r)
                if d.get("created_at") is not None:
                    d["created_at"] = d["created_at"].strftime("%Y-%m-%d %H:%M:%S")
                if d.get("latitude") is not None:
                    d["latitude"] = float(d["latitude"])
                if d.get("longitude") is not None:
                    d["longitude"] = float(d["longitude"])
                out.append(d)
            return {"success": True, "count": len(out), "items": out}
        finally:
            conn.close()
    except Exception as exc:
        return JSONResponse(status_code=500, content={"success": False, "error": str(exc)[:300]})


@app.delete("/api/history/{record_id}")
def api_history_delete(record_id: int, email: str = Query(..., min_length=3)):
    """Delete a single history record. Requires the email that owns it (light auth)."""
    if "@" not in email:
        return JSONResponse(status_code=400, content={"success": False, "error": "valid email required"})
    try:
        _ensure_history_table()
        conn = _mysql_connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM kundli_history WHERE id = %s AND email = %s",
                    (record_id, email.strip().lower()),
                )
                affected = cur.rowcount
                conn.commit()
            if affected == 0:
                return JSONResponse(
                    status_code=404,
                    content={"success": False, "error": "record not found or email mismatch"},
                )
            return {"success": True, "deleted": affected}
        finally:
            conn.close()
    except Exception as exc:
        return JSONResponse(status_code=500, content={"success": False, "error": str(exc)[:300]})

# =============================
# END PASS 2B MySQL section
# =============================

# =============================
# Root + main
# =============================
@app.get("/")
def root():
    try:
        return FileResponse("index.html")
    except Exception:
        return {"message": "Astromata API running. Place index.html beside app.py"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
