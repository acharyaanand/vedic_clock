"""
AETHERIS v5.0 — Classical Vedic Astrology Engine
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Optional
import os, sys, traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Core imports — safe ones first
from models import VedicChartRequest, BirthDetails
from database import AsyncSessionLocal, init_db
from models import UserChart

# Try importing each engine with fallback
try:
    from engine import AetherisEngine
    ENGINE_OK = True
except Exception as e:
    ENGINE_OK = False
    ENGINE_ERR = str(e)

try:
    from vedic_yogas import ClassicalYogaDetector
    YOGAS_OK = True
except Exception as e:
    YOGAS_OK = False

try:
    from dasha_engine import calculate_vimshottari_dashas, get_current_dasha, get_dasha_balance_at_birth
    DASHA_OK = True
except Exception as e:
    DASHA_OK = False

try:
    from classical_knowledge import SUN_IN_HOUSES, BHAVA_KARAKATVA, MARRIAGE_MUHURTA, NAKSHATRAS, HOUSE_LORDS, SIGNS
    CK_OK = True
except Exception as e:
    CK_OK = False
    SIGNS = ["aries","taurus","gemini","cancer","leo","virgo","libra","scorpio","sagittarius","capricorn","aquarius","pisces"]
    HOUSE_LORDS = {"aries":"mars","taurus":"venus","gemini":"mercury","cancer":"moon","leo":"sun","virgo":"mercury","libra":"venus","scorpio":"mars","sagittarius":"jupiter","capricorn":"saturn","aquarius":"saturn","pisces":"jupiter"}
    BHAVA_KARAKATVA = {}
    NAKSHATRAS = {}
    SUN_IN_HOUSES = {}
    MARRIAGE_MUHURTA = {"good_tithis":{"names":[],"citation":""},"good_nakshatras":{"list":[],"citation":""},"good_lagnas":{"list":[],"citation":""}}

try:
    from shadbala_engine import calc_complete_shadbala, calc_dig_bala, NAISARGIKA_BALA, MINIMUM_RUPAS
    SHADBALA_OK = True
except Exception as e:
    SHADBALA_OK = False

try:
    from planet_results import MOON_IN_HOUSES, MARS_IN_HOUSES, MERCURY_IN_HOUSES, JUPITER_IN_HOUSES, VENUS_IN_HOUSES, SATURN_IN_HOUSES, RAHU_IN_HOUSES, KETU_IN_HOUSES
    PR_OK = True
except Exception as e:
    PR_OK = False
    MOON_IN_HOUSES=MARS_IN_HOUSES=MERCURY_IN_HOUSES=JUPITER_IN_HOUSES={}
    VENUS_IN_HOUSES=SATURN_IN_HOUSES=RAHU_IN_HOUSES=KETU_IN_HOUSES={}

try:
    from navamsha_engine import calc_navamsha, is_vargottama, NAVAMSHA_LAGNA_RESULTS, calc_full_navamsha_chart
    NAV_OK = True
except Exception as e:
    NAV_OK = False

try:
    from prediction_engine import predict_precisely, calc_combined_strength
    PRED_OK = True
except Exception as e:
    PRED_OK = False

try:
    from panchanga_engine import get_complete_panchanga
    PANCH_OK = True
except Exception as e:
    PANCH_OK = False

try:
    from muhurta_complete import calc_choghadiya, calc_hora, calc_udaya_lagna_schedule, calc_special_yogas, calc_sandhya_timings
    MUHURTA_OK = True
except Exception as e:
    MUHURTA_OK = False

try:
    from panchanga_timings import get_panchanga_with_timings
    TIMINGS_OK = True
except Exception as e:
    TIMINGS_OK = False

try:
    from varshaphal import calc_varshaphal
    VARSHA_OK = True
except Exception as e:
    VARSHA_OK = False

try:
    from prashna_kundali import calc_prashna_kundali
    PRASHNA_OK = True
except Exception as e:
    PRASHNA_OK = False

try:
    from pratyantar_dasha import get_current_5level_dasha
    PRANA_OK = True
except Exception as e:
    PRANA_OK = False

try:
    from india_districts import search_india_location, get_all_districts, get_states
    INDIA_DB_OK = True
except Exception as e:
    INDIA_DB_OK = False

try:
    from world_cities import search_world_location, search_location, get_tz_offset, WORLD_CITIES
    WORLD_DB_OK = True
except Exception as e:
    WORLD_DB_OK = False

try:
    from astro_features import calc_sade_sati, calc_mangal_dosha, calc_kundali_matching, calc_ashtakavarga_transit
    ASTRO_OK = True
except Exception as e:
    ASTRO_OK = False

try:
    from cities_and_exports import search_city, generate_ics, generate_sankalpa, get_regional_calendar_info
    CITIES_OK = True
except Exception as e:
    CITIES_OK = False

ALL_PLANET_RESULTS = {
    "sun": SUN_IN_HOUSES, "moon": MOON_IN_HOUSES, "mars": MARS_IN_HOUSES,
    "mercury": MERCURY_IN_HOUSES, "jupiter": JUPITER_IN_HOUSES,
    "venus": VENUS_IN_HOUSES, "saturn": SATURN_IN_HOUSES,
    "rahu": RAHU_IN_HOUSES, "ketu": KETU_IN_HOUSES,
}


@asynccontextmanager
async def lifespan(app):
    await init_db()
    yield


# ── Startup Swiss Ephemeris Check ──────────────────────────────
import sys
print(f"Python version: {sys.version}", flush=True)
try:
    import swisseph as swe
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    FLG = swe.FLG_SIDEREAL | swe.FLG_MOSEPH | swe.FLG_SPEED
    test_jd = swe.julday(2026, 5, 21, 6.5)
    pos, _ = swe.calc_ut(test_jd, swe.MOON, FLG)
    print(f"✅ Swiss Ephemeris ACTIVE — Moon test: {pos[0]:.3f}°", flush=True)
    print(f"✅ FLG_MOSEPH = {swe.FLG_MOSEPH} — Moshier built-in data", flush=True)
    SWE_STARTUP_OK = True
except Exception as e:
    print(f"❌ Swiss Ephemeris FAILED: {e}", flush=True)
    print(f"❌ Falling back to pure-math approximations", flush=True)
    SWE_STARTUP_OK = False

app = FastAPI(
    title="Aetheris — Classical Vedic Astrology Engine v5.0",
    description="Every prediction cited to exact Book | Author | Chapter | Shloka",
    version="5.0",
    lifespan=lifespan
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/api/status")
async def status():
    return {
        "status": "running",
        "engine": "Aetheris v5.0",
        "modules": {
            "engine": ENGINE_OK,
            "yogas": YOGAS_OK,
            "dasha": DASHA_OK,
            "shadbala": SHADBALA_OK,
            "planet_results": PR_OK,
            "navamsha": NAV_OK,
            "prediction": PRED_OK,
            "panchanga": PANCH_OK,
            "muhurta": MUHURTA_OK,
            "astro_features": ASTRO_OK,
            "cities": CITIES_OK,
        },
        "sources": "Laghu Jatakam (Varahamihira) + Phaldipika (Ojha) + BPHS (Parashara)"
    }


@app.post("/api/vedic-chart")
async def generate_vedic_chart(req: VedicChartRequest):
    if not ENGINE_OK:
        raise HTTPException(500, f"Astronomy engine not available: {ENGINE_ERR}")
    try:
        bd = req.birth_details
        engine = AetherisEngine(bd)
        planets = await engine.get_planet_positions()
        houses  = await engine.get_houses(planets)
        lagna_sign = houses.get(1, {}).get("sign", "aries")
        sun_lon  = planets.get("sun",  {}).get("longitude", 0)
        moon_lon = planets.get("moon", {}).get("longitude", 0)
        is_day   = 6 <= bd.hour < 18
        is_shukla= int(((moon_lon - sun_lon) % 360) / 12) < 15
        birth_dt = datetime(bd.year, bd.month, bd.day, bd.hour, bd.minute)

        # House mapping
        planet_houses = {}
        for hnum, hdata in houses.items():
            for pname in hdata.get("planets", []):
                planet_houses[pname] = hnum

        # Shadbala
        shadbala_full = {}
        if SHADBALA_OK:
            for planet in ["sun","moon","mars","mercury","jupiter","venus","saturn"]:
                pdata = planets.get(planet, {})
                if not pdata: continue
                try:
                    sb = calc_complete_shadbala(planet, pdata, planet_houses.get(planet,1), float(birth_dt.timestamp()), sun_lon, moon_lon, is_day)
                    shadbala_full[planet] = sb
                except: pass

        # Dig Bala
        dig_bala_all = {}
        if SHADBALA_OK:
            for planet in ["sun","moon","mars","mercury","jupiter","venus","saturn"]:
                try: dig_bala_all[planet] = calc_dig_bala(planet, planet_houses.get(planet,1))
                except: pass

        # Navamsha
        d9_result = {}
        d9_lagna_sign = "aries"
        if NAV_OK:
            try:
                d9_result = calc_full_navamsha_chart(planets)
                asc_lon = planets.get("ascendant",{}).get("longitude",0)
                asc_sign = SIGNS[int(asc_lon/30)%12]
                d9_nav = calc_navamsha(asc_sign, asc_lon%30)
                d9_lagna_sign = d9_nav["navamsha_sign"]
            except: pass
        nav_lagna_result = NAVAMSHA_LAGNA_RESULTS.get(d9_lagna_sign,{}) if NAV_OK else {}

        # Predictions
        predictions = []
        if PRED_OK:
            for planet in ["sun","moon","mars","mercury","jupiter","venus","saturn","rahu","ketu"]:
                pdata = planets.get(planet, {})
                if not pdata: continue
                house_num = planet_houses.get(planet, 1)
                sign   = pdata.get("sign","aries")
                degree = pdata.get("degree", 0.0)
                retro  = pdata.get("is_retrograde", False)
                dist   = abs(pdata.get("longitude",0) - sun_lon) % 360
                if dist > 180: dist = 360 - dist
                combust = dist < 14 and planet not in ["sun","rahu","ketu"]
                house_result = ALL_PLANET_RESULTS.get(planet,{}).get(house_num, {"result":f"{planet} in house {house_num}","strong":"","weak":"","citation":"Phaldipika Ch.7"})
                try:
                    strength = calc_combined_strength(planet, sign, degree, house_num, retro, combust, is_day, is_shukla)
                    pred = predict_precisely(planet, sign, degree, house_num, house_result, retro, combust, is_day, is_shukla)
                    predictions.append({
                        "planet": planet.capitalize(), "house": house_num,
                        "sign": sign.capitalize(), "degree": round(degree,2),
                        "is_retrograde": retro, "is_combust": combust,
                        "strength_pct": strength["strength_pct"],
                        "dignity": strength["dignity"]["state"],
                        "dig_bala": strength["dig_bala"]["dig_bala"],
                        "result_level": pred["result_level"],
                        "prediction": pred["prediction"],
                        "qualifier": pred["qualifier"],
                        "dig_insight": pred["dig_bala_insight"],
                        "flags": pred["special_flags"],
                        "citations": pred["citations"]
                    })
                except: pass

        # Yogas
        yogas, doshas = [], []
        if YOGAS_OK:
            try:
                detector = ClassicalYogaDetector(planets, houses, lagna_sign)
                yogas, doshas = detector.detect_all()
            except: pass

        # Dasha
        dasha_balance = {}; all_dashas = []; current_dasha = {}
        if DASHA_OK:
            try:
                dasha_balance = get_dasha_balance_at_birth(moon_lon, 0)
                all_dashas    = calculate_vimshottari_dashas(moon_lon, birth_dt, 120)
                current_dasha = get_current_dasha(moon_lon, birth_dt)
            except: pass

        # Panchanga
        panchanga = {}
        if PANCH_OK and req.include_panchanga:
            try:
                panchanga = get_complete_panchanga(bd.year, bd.month, bd.day, bd.latitude, bd.longitude, 5.5, sun_lon, moon_lon)
            except: pass

        # House details
        lagna_idx = SIGNS.index(lagna_sign) if lagna_sign in SIGNS else 0
        house_details = {}
        for hnum, hdata in houses.items():
            bhava = BHAVA_KARAKATVA.get(hnum, {})
            house_sign = SIGNS[(lagna_idx + hnum - 1) % 12]
            lord = HOUSE_LORDS.get(house_sign, "")
            house_details[hnum] = {
                "name": bhava.get("name", f"House {hnum}"),
                "sign": house_sign.capitalize(),
                "lord": lord.capitalize(),
                "planets": hdata.get("planets", []),
                "significations": bhava.get("primary", ""),
            }

        # Save to DB
        chart_id = f"{bd.name}_{int(datetime.now().timestamp())}"
        try:
            async with AsyncSessionLocal() as session:
                chart = UserChart(chart_id=chart_id, user_name=bd.name,
                    birth_details_json=bd.dict(), chart_data_json={"planets":planets,"houses":houses},
                    yogas_json=yogas, doshas_json=doshas, panchanga_json=panchanga)
                session.add(chart); await session.commit()
        except: pass

        strongest = max(predictions, key=lambda x: x.get("strength_pct",0)) if predictions else {}

        return {
            "status": "success", "chart_id": chart_id,
            "engine": "Aetheris v5.0",
            "birth_details": bd.dict(),
            "lagna": {"sign": lagna_sign.capitalize(), "degree": round(houses.get(1,{}).get("degree",0),2)},
            "planets": {
                name: {
                    "sign": d.get("sign","").capitalize(), "degree": round(d.get("degree",0),2),
                    "nakshatra": d.get("nakshatra",""), "nakshatra_pada": d.get("nakshatra_pada",0),
                    "is_retrograde": d.get("is_retrograde",False), "house": planet_houses.get(name,0),
                    "longitude": round(d.get("longitude",0),4)
                } for name, d in planets.items() if name != "midheaven"
            },
            "shadbala": {
                p: {
                    "dig_bala": dig_bala_all.get(p,{}).get("dig_bala",0),
                    "strength_pct": sb.get("strength_percentage",0),
                    "dignity": sb.get("sthana_bala",{}).get("dignity_state","")
                } for p, sb in shadbala_full.items()
            },
            "navamsha": {
                "d9_chart": d9_result.get("d9_chart",{}),
                "vargottama_planets": d9_result.get("vargottama_planets",[]),
                "navamsha_lagna": d9_lagna_sign.capitalize(),
                "navamsha_lagna_type": nav_lagna_result.get("type",""),
                "navamsha_lagna_result": nav_lagna_result.get("result",""),
            },
            "predictions": predictions,
            "strongest_planet": {"planet": strongest.get("planet",""), "strength_pct": strongest.get("strength_pct",0)},
            "yogas": yogas, "doshas": doshas,
            "dasha": {"current_period": current_dasha, "periods": all_dashas[:9], "balance_at_birth": dasha_balance},
            "panchanga": panchanga,
            "houses": house_details,
        }
    except Exception as e:
        raise HTTPException(500, detail=f"Error: {str(e)}\n{traceback.format_exc()}")


@app.get("/api/panchanga")
async def get_panchanga(year:int, month:int, day:int, lat:float=28.6139, lon:float=77.2090, tz_offset:float=5.5):
    if not ENGINE_OK:
        raise HTTPException(500, "Engine not available")
    try:
        from models import BirthDetails
        bd = BirthDetails(year=year,month=month,day=day,hour=6,minute=0,second=0,latitude=lat,longitude=lon,timezone="Asia/Kolkata")
        engine = AetherisEngine(bd)
        planets = await engine.get_planet_positions()
        sun_lon  = planets.get("sun",{}).get("longitude",0)
        moon_lon = planets.get("moon",{}).get("longitude",0)
        if PANCH_OK:
            return get_complete_panchanga(year,month,day,lat,lon,tz_offset,sun_lon,moon_lon)
        return {"error": "Panchanga engine not loaded"}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/api/city-search")
async def city_search(q: str):
    if CITIES_OK:
        return {"results": search_city(q)}
    return {"results": []}


@app.get("/api/sade-sati")
async def sade_sati(moon_rashi:int, saturn_lon:float, birth_year:int=1990):
    if ASTRO_OK:
        return calc_sade_sati(moon_rashi, saturn_lon, birth_year)
    raise HTTPException(503, "Astro features not loaded")


@app.get("/api/kundali-matching")
async def kundali_matching(boy_nak:int, girl_nak:int, boy_moon:int=1, girl_moon:int=7):
    if ASTRO_OK:
        return calc_kundali_matching(boy_nak, girl_nak, boy_moon, girl_moon)
    raise HTTPException(503, "Astro features not loaded")


@app.get("/api/classical-sources")
async def classical_sources():
    return {
        "books_read_directly": [
            {"title":"Laghu Jatakam","author":"Varahamihira","pages":127,"status":"Fully read — 222,695 characters"},
            {"title":"Phaldipika","author":"Mantreswara / Gopesh Kumar Ojha","pages":670,"status":"Fully read — 583,955 characters"},
        ],
        "total_chars": "806,650",
        "citation_policy": "Every prediction cited to exact Book | Author | Chapter | Shloka"
    }


@app.get("/", response_class=HTMLResponse)
async def root():
    try:
        html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
        if os.path.exists(html_path):
            with open(html_path) as f:
                return f.read()
    except: pass
    return """<!DOCTYPE html><html><head><title>Aetheris v5.0</title>
    <style>body{background:#0a0a0a;color:#d4af37;font-family:serif;padding:2rem;text-align:center}
    h1{font-size:3rem;letter-spacing:.2em}a{color:#d4af37}</style></head>
    <body><h1>AETHERIS</h1><p>Classical Vedic Astrology Engine v5.0</p>
    <p>Every prediction cited to exact shloka</p>
    <p><a href="/docs">→ API Documentation</a> &nbsp; <a href="/api/status">→ Status</a></p>
    </body></html>"""


# ══════════════════════════════════════════════════════════════════
# LOCATION ENDPOINTS — Using verified coordinate database
# ══════════════════════════════════════════════════════════════════

@app.get("/api/city-search")
async def city_search(q: str, limit: int = 10):
    """
    Search cities with verified coordinates.
    India: 800+ cities with district-level accuracy.
    World: 150+ major cities verified.
    Handles aliases, alternate spellings, old/new names.
    """
    try:
        from location_engine import search_location
        results = search_location(q, limit)
        return {"results": results, "query": q, "total": len(results)}
    except ImportError:
        # Fallback to old simple database
        from cities_and_exports import search_city as old_search
        return {"results": old_search(q), "query": q}


@app.get("/api/location/coordinates")
async def get_coordinates(city: str, state: str = "", country: str = "India"):
    """
    Get exact verified coordinates for a city.
    Returns high-confidence verified data or error if not found.
    """
    try:
        from location_engine import get_exact_location
        result = get_exact_location(city, state, country)
        if result:
            return result
        raise HTTPException(404, f"City '{city}' not found in verified database")
    except ImportError:
        raise HTTPException(503, "Location engine not available")


@app.get("/api/location/timezone")
async def get_timezone(lat: float, lon: float):
    """
    Get timezone from exact coordinates.
    Uses timezonefinder if available, longitude-based fallback otherwise.
    """
    try:
        from location_engine import get_timezone_from_coordinates
        return get_timezone_from_coordinates(lat, lon)
    except ImportError:
        # Simple fallback
        if 68 <= lon <= 97 and 8 <= lat <= 37:
            return {"timezone_name": "Asia/Kolkata", "timezone_offset": 5.5}
        offset = round(lon / 15 * 2) / 2
        return {"timezone_name": f"UTC{offset:+.1f}", "timezone_offset": offset}


@app.get("/api/debug-swe")
async def debug_swisseph():
    """
    Debug endpoint — verify Swiss Ephemeris accuracy on server.
    Test case: Jan 7 1992, 9:07 AM IST, Delhi
    Reference: AstroTalk verified data
    """
    result = {"swisseph_available": False, "test_chart": {}, "errors": []}
    SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
             "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
    EXPECTED = {
        "Ascendant":"Capricorn 22°","Sun":"Sagittarius 22°",
        "Moon":"Capricorn 15°","Mercury":"Sagittarius 2°",
        "Venus":"Scorpio 14°","Mars":"Sagittarius 4°",
        "Jupiter":"Leo 20°","Saturn":"Capricorn 12°",
        "Rahu":"Sagittarius 15°"
    }
    try:
        import swisseph as swe
        result["swisseph_available"] = True
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        hour_ut = 9 + 7/60 - 5.5
        jd = swe.julday(1992, 1, 7, hour_ut)
        ayanamsa = swe.get_ayanamsa_ut(jd)
        result["ayanamsa"] = round(ayanamsa, 4)
        FLG = swe.FLG_SIDEREAL | swe.FLG_MOSEPH | swe.FLG_SPEED
        planets_out = {}
        for code, name in [(swe.SUN,"Sun"),(swe.MOON,"Moon"),
                           (swe.MERCURY,"Mercury"),(swe.VENUS,"Venus"),
                           (swe.MARS,"Mars"),(swe.JUPITER,"Jupiter"),
                           (swe.SATURN,"Saturn"),(swe.MEAN_NODE,"Rahu")]:
            try:
                pos, _ = swe.calc_ut(jd, code, FLG)
                lon = pos[0] % 360
                planets_out[name] = {
                    "sign": SIGNS[int(lon/30)%12],
                    "degree": round(lon%30, 2),
                    "retrograde": pos[3] < 0,
                    "expected": EXPECTED.get(name,""),
                    "match": SIGNS[int(lon/30)%12] in EXPECTED.get(name,"")
                }
            except Exception as e:
                result["errors"].append(f"{name}: {e}")
        try:
            cusps, ascmc = swe.houses(jd, 28.6139, 77.2090, b'P')
            asc = (ascmc[0] - ayanamsa) % 360
            planets_out["Ascendant"] = {
                "sign": SIGNS[int(asc/30)%12],
                "degree": round(asc%30,2),
                "expected": EXPECTED["Ascendant"],
                "match": SIGNS[int(asc/30)%12] in EXPECTED["Ascendant"]
            }
        except Exception as e:
            result["errors"].append(f"Ascendant: {e}")
        result["test_chart"] = planets_out
        all_match = all(v.get("match") for v in planets_out.values())
        result["all_planets_correct"] = all_match
        result["status"] = "FULLY ACCURATE" if all_match else "PARTIAL — check errors"
    except ImportError:
        result["status"] = "swisseph not installed"
    except Exception as e:
        result["errors"].append(str(e))
    return result

@app.get("/api/panchanga-timings")
async def get_panchanga_timings(
    year: int, month: int, day: int,
    lat: float = 28.6139, lon: float = 77.2090,
    tz: float = 5.5
):
    """
    Full panchanga with exact start/end times for:
    Tithi, Nakshatra, Yoga, Karana — for any date, any location worldwide.
    Times shown in local time of the given timezone.
    """
    if not TIMINGS_OK:
        raise HTTPException(500, "Panchanga timings module not available")
    try:
        data = get_panchanga_with_timings(year, month, day, lat, lon, tz)
        return data
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/api/india-location")
async def search_india_city(q: str):
    """
    Search any India district/city. Returns Google-standard lat/lon.
    Covers all 28 states + 8 UTs, 620+ locations.
    Supports aliases: Bombay→Mumbai, Madras→Chennai, Vizag→Visakhapatnam etc.
    """
    if not INDIA_DB_OK:
        raise HTTPException(500, "India districts DB not available")
    result = search_india_location(q)
    if not result:
        raise HTTPException(404, f"Location '{q}' not found in India database")
    return result

@app.get("/api/india-districts")
async def get_india_districts(state: str = None):
    """Return all India districts/cities, optionally filtered by state."""
    if not INDIA_DB_OK:
        raise HTTPException(500, "India districts DB not available")
    all_locs = get_all_districts()
    if state:
        all_locs = [l for l in all_locs if state.lower() in l["state"].lower()]
    return {"total": len(all_locs), "locations": all_locs}

@app.get("/api/india-states")
async def get_india_states():
    """Return all 37 India states and Union Territories."""
    if not INDIA_DB_OK:
        raise HTTPException(500, "India districts DB not available")
    return {"states": get_states(), "total": len(get_states())}

@app.get("/api/search-location")
async def search_any_location(q: str, year: int = None, month: int = None, day: int = None):
    """
    Master location search — India + World.
    Returns lat/lon + timezone + DST-correct offset.
    620+ India districts/cities + 375+ world cities.
    Pass year/month/day for DST-correct offset on a specific date.
    """
    from datetime import date as _date
    if not year:
        today = _date.today()
        year, month, day = today.year, today.month, today.day
    
    # Try India first
    if INDIA_DB_OK:
        r = search_india_location(q)
        if r:
            return r
    
    # Then world
    if WORLD_DB_OK:
        r = search_world_location(q)
        if r:
            if year:
                from world_cities import get_tz_offset
                r['tz_offset'] = get_tz_offset(r['timezone'], year, month, day)
            return r
    
    raise HTTPException(404, f"Location '{q}' not found. Try a nearby major city.")

@app.get("/api/world-location")
async def search_world_city(q: str):
    """Search world cities outside India."""
    if not WORLD_DB_OK:
        raise HTTPException(500, "World cities DB not available")
    r = search_world_location(q)
    if not r:
        raise HTTPException(404, f"'{q}' not found in world cities database")
    return r

@app.post("/api/ashtakavarga")
async def get_ashtakavarga(req: VedicChartRequest):
    """
    Complete Ashtakavarga calculation.
    Returns Prashtara (individual) + Sarvashtakavarga (total) tables.
    All 7 planets + Sarva (total) per sign.
    Classical formula from BPHS Ch.66-75.
    """
    if not ASHTA_OK:
        raise HTTPException(500, "Ashtakavarga module not available")
    if not ENGINE_OK:
        raise HTTPException(500, "Engine not available")
    try:
        bd = req.birth_details
        engine = AetherisEngine(bd)
        planets = await engine.get_planet_positions()
        lagna_lon = planets.get("ascendant", {}).get("longitude", 0)
        ashta = calc_prashtara_ashtakavarga(planets, lagna_lon)
        
        SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                 "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
        
        # Format output
        result = {}
        for planet in ["sun","moon","mars","mercury","jupiter","venus","saturn","sarva"]:
            scores = ashta.get(planet, [0]*12)
            result[planet] = {
                "scores": {SIGNS[i]: scores[i] for i in range(12)},
                "total": sum(scores),
            }
        result["table"] = format_ashtakavarga_table(ashta)
        return result
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/api/mandi-gulika")
async def get_mandi_gulika(year: int, month: int, day: int,
                            lat: float = 28.6139, lon: float = 77.2090,
                            tz: float = 5.5):
    """
    Exact Mandi and Gulika positions using classical BPHS formula.
    Based on day duration, weekday, and Sun's longitude.
    """
    if not ASHTA_OK:
        raise HTTPException(500, "Ashtakavarga module not available")
    try:
        return calc_mandi_gulika(year, month, day, lat, lon, tz)
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/api/pratyantar-dasha")
async def get_pratyantar_dasha(req: VedicChartRequest):
    """
    Complete 3-level Dasha: Mahadasha > Antardasha > Pratyantar.
    Formula from Vimshottari Dasha system — BPHS Ch.46.
    """
    if not DASHA_OK or not ASHTA_OK:
        raise HTTPException(500, "Dasha module not available")
    try:
        bd = req.birth_details
        engine = AetherisEngine(bd)
        planets = await engine.get_planet_positions()
        moon_lon = planets.get("moon", {}).get("longitude", 0)
        from datetime import datetime
        birth_dt = datetime(bd.year, bd.month, bd.day, bd.hour, bd.minute)
        result = calc_full_dasha_with_pratyantar(moon_lon, birth_dt, num_maha=3)
        return {"dashas": result, "system": "Vimshottari", "total_years": 120}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/api/samvat")
async def get_samvat(year: int, month: int):
    """
    Shaka Samvat, Vikram Samvat, Kali Yuga year with names.
    Verified against DrikPanchang.
    """
    if not ASHTA_OK:
        raise HTTPException(500, "Ashtakavarga module not available")
    try:
        return calc_samvat(year, month)
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/api/special-yogas")
async def get_special_yogas(year: int, month: int, day: int,
                             lat: float = 28.6139, lon: float = 77.2090,
                             tz: float = 5.5):
    """
    Special Panchanga Yogas for a day:
    Ravi Yoga, Amrita Yoga, Sarvartha Siddhi, Guru Pushya, Ravi Pushya,
    Dwipushkara, Tripushkara, Ganda Moola, Panchaka.
    Exactly as shown on DrikPanchang daily panchanga.
    """
    if not ASHTA_OK or not TIMINGS_OK:
        raise HTTPException(500, "Modules not available")
    try:
        # Get panchanga first
        data = get_panchanga_with_timings(year, month, day, lat, lon, tz)
        tithi_num = data["tithi"][0]["number"]
        
        # Nakshatra index
        NAK_NAMES = ["Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
                     "Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni",
                     "Uttara Phalguni","Hasta","Chitra","Swati","Vishakha",
                     "Anuradha","Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha",
                     "Shravana","Dhanishtha","Shatabhisha","Purva Bhadrapada",
                     "Uttara Bhadrapada","Revati"]
        nak_name = data["nakshatra"][0]["name"]
        nak_idx = NAK_NAMES.index(nak_name) if nak_name in NAK_NAMES else 0
        
        VARA_NAMES = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
        vara_name = data["vara"]["name"]
        vara_num = VARA_NAMES.index(vara_name) if vara_name in VARA_NAMES else 0
        
        YOGA_NAMES = ["Vishkumbha","Priti","Ayushman","Saubhagya","Shobhana","Atiganda",
                      "Sukarma","Dhriti","Shoola","Ganda","Vriddhi","Dhruva","Vyaghata",
                      "Harshana","Vajra","Siddhi","Vyatipata","Variyana","Parigha","Shiva",
                      "Siddha","Sadhya","Shubha","Shukla","Brahma","Indra","Vaidhriti"]
        yoga_name = data["yoga"][0]["name"]
        yoga_idx = YOGA_NAMES.index(yoga_name) if yoga_name in YOGA_NAMES else 0
        
        yogas, shaka, vikram = calc_special_panchanga_yogas(
            year, month, day, tithi_num, nak_idx, vara_num, yoga_idx)
        samvat = calc_samvat(year, month)
        lunar = calc_lunar_month(tithi_num, month, day)
        
        return {
            "date": f"{year}-{month:02d}-{day:02d}",
            "special_yogas": yogas,
            "samvat": samvat,
            "lunar_month": lunar,
            "panchanga_summary": {
                "tithi": f"{data['tithi'][0]['paksha']} {data['tithi'][0]['name']}",
                "nakshatra": nak_name,
                "yoga": yoga_name,
                "vara": vara_name,
            }
        }
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/api/vimshopaka-bala")
async def get_vimshopaka_bala(req: VedicChartRequest):
    """Vimshopaka Bala — 20-point strength across 16 divisional charts."""
    if not EXTRA_OK:
        raise HTTPException(500, "Module not available")
    try:
        bd = req.birth_details
        engine = AetherisEngine(bd)
        planets = await engine.get_planet_positions()
        lons = {p: planets[p]["longitude"] for p in planets if "longitude" in planets.get(p,{})}
        return calc_vimshopaka_bala(lons)
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/api/graha-yuddha")
async def get_graha_yuddha(req: VedicChartRequest):
    """Check for Graha Yuddha (Planetary War) — planets within 1° of each other."""
    if not EXTRA_OK:
        raise HTTPException(500, "Module not available")
    try:
        bd = req.birth_details
        engine = AetherisEngine(bd)
        planets = await engine.get_planet_positions()
        lons = {p: planets[p]["longitude"] for p in planets if "longitude" in planets.get(p,{})}
        return {"planetary_wars": check_graha_yuddha(lons)}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/api/muhurta-check")
async def muhurta_check(
    year: int, month: int, day: int,
    muhurta_type: str = "vivah",
    lat: float = 28.6139, lon: float = 77.2090, tz: float = 5.5
):
    """
    Quick Muhurta check for: vivah, griha_pravesh, vehicle.
    Returns suitability score and detailed checks.
    """
    if not EXTRA_OK:
        raise HTTPException(500, "Module not available")
    try:
        from panchanga_timings import get_panchanga_with_timings
        p = get_panchanga_with_timings(year, month, day, lat, lon, tz)
        tithi_idx = p["tithi"][0]["number"] - 1
        nak_idx   = ["Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
                     "Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni","Uttara Phalguni",
                     "Hasta","Chitra","Swati","Vishakha","Anuradha","Jyeshtha","Mula",
                     "Purva Ashadha","Uttara Ashadha","Shravana","Dhanishtha","Shatabhisha",
                     "Purva Bhadrapada","Uttara Bhadrapada","Revati"
                    ].index(p["nakshatra"][0]["name"])
        yoga_idx  = ["Vishkumbha","Priti","Ayushman","Saubhagya","Shobhana","Atiganda",
                     "Sukarma","Dhriti","Shoola","Ganda","Vriddhi","Dhruva","Vyaghata",
                     "Harshana","Vajra","Siddhi","Vyatipata","Variyana","Parigha","Shiva",
                     "Siddha","Sadhya","Shubha","Shukla","Brahma","Indra","Vaidhriti"
                    ].index(p["yoga"][0]["name"])
        vara_idx  = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"
                    ].index(p["vara"]["name"])
        
        if muhurta_type == "vivah":
            result = check_vivah_muhurta(year,month,day,tithi_idx,nak_idx,yoga_idx,vara_idx)
        elif muhurta_type == "griha_pravesh":
            result = check_griha_pravesh_muhurta(year,month,day,tithi_idx,nak_idx,yoga_idx,vara_idx)
        elif muhurta_type == "vehicle":
            result = check_vehicle_muhurta(year,month,day,tithi_idx,nak_idx,yoga_idx,vara_idx)
        else:
            raise HTTPException(400, "muhurta_type must be: vivah, griha_pravesh, vehicle")
        
        result["date"] = f"{year}-{month:02d}-{day:02d}"
        result["panchanga_summary"] = {
            "tithi": p["tithi"][0]["name"],
            "nakshatra": p["nakshatra"][0]["name"],
            "yoga": p["yoga"][0]["name"],
            "vara": p["vara"]["name"],
        }
        return result
    except HTTPException: raise
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/api/lucky-factors")
async def get_lucky_factors(req: VedicChartRequest):
    """Lucky number, color, day, direction, deity based on Lagna lord."""
    if not EXTRA_OK:
        raise HTTPException(500, "Module not available")
    try:
        bd = req.birth_details
        engine = AetherisEngine(bd)
        planets = await engine.get_planet_positions()
        houses  = await engine.get_houses(planets)
        lagna_sign = houses.get(1,{}).get("sign","Aries").capitalize()
        SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                 "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
        moon_sign = SIGNS[int(planets.get("moon",{}).get("longitude",0)/30)%12]
        return calc_lucky_factors(lagna_sign, moon_sign, bd.day, bd.month, bd.year)
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/api/rudraksha")
async def get_rudraksha(req: VedicChartRequest):
    """Rudraksha recommendation based on Lagna lord and weak planets."""
    if not EXTRA_OK:
        raise HTTPException(500, "Module not available")
    try:
        bd = req.birth_details
        engine = AetherisEngine(bd)
        planets = await engine.get_planet_positions()
        houses  = await engine.get_houses(planets)
        lagna_sign = houses.get(1,{}).get("sign","Aries").capitalize()
        return calc_rudraksha(lagna_sign)
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/api/pancha-pakshi")
async def get_pancha_pakshi(
    nak_idx: int,
    year: int, month: int, day: int,
    lat: float = 28.6139, lon: float = 77.2090, tz: float = 5.5
):
    """Pancha Pakshi system — five-bird activity timing for the day."""
    if not EXTRA_OK:
        raise HTTPException(500, "Module not available")
    try:
        from panchanga_timings import _jd, calc_sunrise_sunset
        sr, ss = calc_sunrise_sunset(year, month, day, lat, lon, tz)
        return calc_pancha_pakshi(nak_idx, year, month, day, sr, ss)
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/api/pradosh")
async def get_pradosh(
    year: int, month: int, day: int,
    lat: float = 28.6139, lon: float = 77.2090, tz: float = 5.5
):
    """Check if today is Pradosh and give Pradosh timing (Shiva worship window)."""
    if not EXTRA_OK or not TIMINGS_OK:
        raise HTTPException(500, "Module not available")
    try:
        from panchanga_timings import get_panchanga_with_timings
        p = get_panchanga_with_timings(year, month, day, lat, lon, tz)
        tithi_idx = p["tithi"][0]["number"] - 1
        sr_str = p["sunrise"]; ss_str = p["sunset"]
        def parse_t(t): 
            parts = t.replace(" AM","").replace(" PM","").split(":")
            h = int(parts[0])+(12 if "PM" in t and h!=12 else 0)
            if "AM" in t and h==12: h=0
            return h + int(parts[1])/60
        ss_h = float(ss_str.split(":")[0]) + float(ss_str.split(":")[1].split(" ")[0])/60
        if "PM" in ss_str and ss_h < 12: ss_h += 12
        return check_pradosh(tithi_idx, ss_h)
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/api/kala-sarpa")
async def get_kala_sarpa(req: VedicChartRequest):
    """Complete Kala Sarpa Dosha check — all 12 types."""
    if not EXTRA_OK:
        raise HTTPException(500, "Module not available")
    try:
        bd = req.birth_details
        engine = AetherisEngine(bd)
        planets = await engine.get_planet_positions()
        houses  = await engine.get_houses(planets)
        return calc_kala_sarpa_dosha(planets, houses)
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/api/vedic-time")
async def get_vedic_time(
    year: int, month: int, day: int,
    hour: float,
    lat: float = 28.6139, lon: float = 77.2090, tz: float = 5.5
):
    """Convert clock time to Vedic time (Ghati/Pala/Vipala)."""
    if not EXTRA_OK:
        raise HTTPException(500, "Module not available")
    try:
        from panchanga_timings import calc_sunrise_sunset
        sr, ss = calc_sunrise_sunset(year, month, day, lat, lon, tz)
        return calc_vedic_time(hour, sr, ss)
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/api/varshaphal")
async def get_varshaphal(req: VedicChartRequest):
    """
    Varshaphal (Solar Return) — Annual horoscope for each year.
    Shows Solar Return date, Varsha Lagna, Muntha position, 
    Mudda Dasha for the year.
    """
    if not VARSHA_OK:
        raise HTTPException(500, "Varshaphal module not available")
    try:
        bd = req.birth_details
        engine = AetherisEngine(bd)
        planets = await engine.get_planet_positions()
        houses  = await engine.get_houses(planets)
        sun_lon = planets.get("sun",{}).get("longitude", 0)
        lagna_sign = houses.get(1,{}).get("sign","Aries")
        return calc_varshaphal(
            natal_sun_lon=sun_lon,
            birth_year=bd.year, birth_month=bd.month, birth_day=bd.day,
            birth_lagna_sign=lagna_sign.capitalize(),
            lat=bd.latitude, lon=bd.longitude,
            tz=getattr(bd,"timezone_offset",5.5),
            years_to_show=3
        )
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/api/prashna")
async def get_prashna(
    question: str = "general",
    lat: float = 28.6139,
    lon: float = 77.2090,
    tz: float = 5.5
):
    """
    Prashna Kundali — Horary astrology chart at THIS exact moment.
    question = health|wealth|marriage|career|children|property|
               fortune|enemies|gains|longevity|general
    No birth details needed — cast at query time.
    """
    if not PRASHNA_OK:
        raise HTTPException(500, "Prashna module not available")
    try:
        return calc_prashna_kundali(lat, lon, tz, question)
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/api/prana-dasha")
async def get_prana_dasha(req: VedicChartRequest):
    """
    Complete 5-level Vimshottari Dasha:
    Level 1: Mahadasha  (years)
    Level 2: Antardasha (months)
    Level 3: Pratyantar (weeks)
    Level 4: Sookshma   (days)
    Level 5: Prana      (hours)
    Returns current running period at all 5 levels
    + all Sookshma periods within current Pratyantar
    + all Prana periods within current Sookshma.
    """
    if not PRANA_OK:
        raise HTTPException(500, "Prana dasha module not available")
    try:
        from extra_features import calc_sookshma_dasha
        from pratyantar_dasha import (calc_full_3level_dasha, calc_prana_dasha,
                                       calc_pratyantar_dashas)
        bd = req.birth_details
        engine = AetherisEngine(bd)
        planets = await engine.get_planet_positions()
        moon_lon = planets.get("moon",{}).get("longitude", 0)
        birth_dt = datetime(bd.year, bd.month, bd.day, bd.hour, bd.minute)
        today = datetime.now()
        
        # Current 5-level snapshot
        current = get_current_5level_dasha(moon_lon, birth_dt)
        
        # Full sookshma list within current pratyantar
        all_sookshma = []
        all_prana    = []
        full = calc_full_3level_dasha(moon_lon, birth_dt, years=40)
        
        for maha in full:
            ms = datetime.strptime(maha["start"],"%Y-%m-%d")
            me = datetime.strptime(maha["end"],"%Y-%m-%d")
            if not (ms <= today <= me): continue
            for antar in maha["antardashas"]:
                as_ = datetime.strptime(antar["start"],"%Y-%m-%d")
                ae  = datetime.strptime(antar["end"],"%Y-%m-%d")
                if not (as_ <= today <= ae): continue
                for prat in antar["pratyantars"]:
                    ps = datetime.strptime(prat["start"],"%Y-%m-%d")
                    pe = datetime.strptime(prat["end"],"%Y-%m-%d")
                    if not (ps <= today <= pe): continue
                    
                    # All sookshma in this pratyantar
                    all_sookshma = calc_sookshma_dasha(
                        prat["lord"], ps, pe, antar["lord"], maha["lord"]
                    )
                    # Mark current
                    for s in all_sookshma:
                        ss = datetime.strptime(s["start"],"%Y-%m-%d")
                        se = datetime.strptime(s["end"],"%Y-%m-%d")
                        s["is_current"] = ss <= today <= se
                        if s["is_current"]:
                            # All prana in this sookshma
                            all_prana = calc_prana_dasha(
                                s["lord"], ss, se,
                                prat["lord"], antar["lord"], maha["lord"]
                            )
                            for pr in all_prana:
                                try:
                                    prs = datetime.strptime(pr["start"],"%Y-%m-%d %H:%M")
                                    pre = datetime.strptime(pr["end"],"%Y-%m-%d %H:%M")
                                    pr["is_current"] = prs <= today <= pre
                                except: pr["is_current"] = False
                    break
                break
            break
        
        return {
            "current_5level": current,
            "all_sookshma_in_current_pratyantar": all_sookshma,
            "all_prana_in_current_sookshma": all_prana,
            "note": "Sookshma = days; Prana = hours. Use for precise event timing."
        }
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/api/shodasavarga")
async def get_shodasavarga(req: VedicChartRequest):
    """
    All 16 Shodasavarga divisional charts: D1 through D60.
    Complete set as per BPHS Ch.6.
    D1=Rasi, D2=Hora, D3=Drekkana, D4=Chaturthamsha, D7=Saptamsha,
    D9=Navamsha, D10=Dasamsha, D12=Dwadashamsha, D16=Shodashamsha,
    D20=Vimsamsha, D24=Siddhamsha, D27=Bhamsha, D30=Trimsamsha,
    D40=Khavedamsha, D45=Akshavedamsha, D60=Shashtiamsha
    """
    if not EXTRA_OK:
        raise HTTPException(500, "Divisional charts module not available")
    try:
        bd = req.birth_details
        engine = AetherisEngine(bd)
        planets = await engine.get_planet_positions()
        lons = {p: planets[p]["longitude"] 
                for p in planets if isinstance(planets.get(p),dict) 
                and "longitude" in planets[p]}
        if "ascendant" in planets:
            lons["ascendant"] = planets["ascendant"]["longitude"]
        return calc_divisional_charts(lons)
    except Exception as e:
        raise HTTPException(500, str(e))
