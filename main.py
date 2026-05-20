"""
AETHERIS — Classical Vedic Astrology API
Every prediction cited to exact classical source.
No hallucinations. No invented citations.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
import os

from app.models import VedicChartRequest, BirthDetails
from app.engine import AetherisEngine
from app.vedic_yogas import ClassicalYogaDetector
from app.shadbala import calc_complete_shadbala
from app.dasha_engine import (
    calculate_vimshottari_dashas,
    get_current_dasha,
    get_dasha_balance_at_birth
)
from app.classical_knowledge import (
    SUN_IN_HOUSES, BHAVA_KARAKATVA, MARRIAGE_MUHURTA, NAKSHATRAS
)
from app.database import AsyncSessionLocal, init_db
from app.models import UserChart


@asynccontextmanager
async def lifespan(app):
    await init_db()
    yield


app = FastAPI(
    title="Aetheris — Classical Vedic Astrology Engine",
    description="Every prediction cited to exact Book | Author | Chapter | Shloka",
    version="4.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)
app.router.lifespan_context = lifespan


@app.post("/api/vedic-chart")
async def vedic_chart(req: VedicChartRequest):
    """
    Generate complete Vedic horoscope with classical citations.
    """
    try:
        # ── 1. Calculate Planetary Positions ──────────────────────
        engine = AetherisEngine(req.birth_details)
        planets = await engine.get_planet_positions()
        houses = await engine.get_houses(planets)

        lagna_sign = houses.get(1, {}).get("sign", "aries")
        sun_lon = planets.get("sun", {}).get("longitude", 0)
        moon_lon = planets.get("moon", {}).get("longitude", 0)

        # ── 2. Panchanga ──────────────────────────────────────────
        panchanga = {}
        if req.include_panchanga:
            panchanga = await engine.get_panchanga(sun_lon, moon_lon)

        # ── 3. Shadbala for all planets ───────────────────────────
        shadbala = {}
        for planet in ["sun","moon","mars","mercury","jupiter","venus","saturn"]:
            pdata = planets.get(planet, {})
            if not pdata:
                continue
            planet_house = 1
            for hnum, hdata in houses.items():
                if planet in hdata.get("planets", []):
                    planet_house = hnum
                    break
            shadbala[planet] = calc_complete_shadbala(
                planet, pdata, planet_house, sun_lon,
                req.birth_details.dict()
            )

        # ── 4. Classical Yoga Detection ───────────────────────────
        detector = ClassicalYogaDetector(planets, houses, lagna_sign)
        yogas, doshas = detector.detect_all()

        # ── 5. Vimshottari Dasha ──────────────────────────────────
        birth_dt = datetime(
            req.birth_details.year, req.birth_details.month, req.birth_details.day,
            req.birth_details.hour, req.birth_details.minute
        )

        dasha_balance = get_dasha_balance_at_birth(moon_lon, 0)
        all_dashas = calculate_vimshottari_dashas(moon_lon, birth_dt, 120)
        current_dasha = get_current_dasha(moon_lon, birth_dt)

        # ── 6. Planet-in-House Results (with citations) ───────────
        planet_house_results = _get_planet_house_results(planets, houses, lagna_sign)

        # ── 7. House Significations ───────────────────────────────
        house_details = _get_house_details(houses, lagna_sign)

        # ── 8. Marriage Muhurta ───────────────────────────────────
        marriage_dates = []
        if req.include_muhurta:
            now = datetime.now()
            target = now + timedelta(days=30 * req.target_month_offset)
            marriage_dates = await engine.find_marriage_muhurtas(
                target.year, target.month, planets, houses
            )

        # ── 9. Save to DB ──────────────────────────────────────────
        chart_id = f"{req.birth_details.name}_{int(datetime.now().timestamp())}"
        async with AsyncSessionLocal() as session:
            chart = UserChart(
                chart_id=chart_id,
                user_name=req.birth_details.name,
                birth_details_json=req.birth_details.dict(),
                chart_data_json={"planets": planets, "houses": houses},
                yogas_json=yogas,
                doshas_json=doshas,
                panchanga_json=panchanga
            )
            session.add(chart)
            await session.commit()

        # ── 10. Build Response ─────────────────────────────────────
        return {
            "status": "success",
            "chart_id": chart_id,
            "engine_version": "4.0 — Classical Citations Engine",
            "citation_standard": "Every prediction cited to exact Book | Author | Chapter | Shloka",

            "birth_details": req.birth_details.dict(),

            "lagna": {
                "sign": lagna_sign.capitalize(),
                "degree": houses.get(1, {}).get("degree", 0),
                "significance": "Most important factor in chart — represents self, body, personality",
                "citation": "BPHS Lagna Adhyaya | Parashara | Shloka 1"
            },

            "planets": _format_planets_with_dignity(planets, shadbala),

            "houses": house_details,

            "panchanga": panchanga,

            "shadbala": {
                "summary": {p: {
                    "strength": s["strength_label"],
                    "dignity": s["dignity_state"],
                    "is_combust": s["combustion"]["is_combust"],
                    "total_vimsopaka": s["total_vimsopaka"]
                } for p, s in shadbala.items()},
                "detail": shadbala,
                "citation": "BPHS Graha Bala Adhyaya | Parashara | Shloka 1-21"
            },

            "yogas": yogas,
            "doshas": doshas,

            "yoga_summary": {
                "total_yogas_found": len(yogas),
                "total_doshas_found": len(doshas),
                "active_yogas": [y["name"] for y in yogas if "Cancelled" not in y.get("name","")],
                "citation_standard": "All yogas cited to BPHS (Parashara), Phaldipika (Mantreswara), Brihat Jataka (Varahamihira)"
            },

            "dasha": {
                "system": "Vimshottari",
                "total_years": 120,
                "balance_at_birth": dasha_balance,
                "current_period": current_dasha,
                "all_dashas": all_dashas[:9],  # Next 9 periods
                "citation": "BPHS Vimshottari Dasha Adhyaya | Parashara | Shloka 3-12"
            },

            "planet_house_results": planet_house_results,

            "marriage_muhurtas": {
                "dates": marriage_dates,
                "rules_applied": {
                    "tithis": MARRIAGE_MUHURTA["good_tithis"]["names"],
                    "nakshatras": MARRIAGE_MUHURTA["good_nakshatras"]["list"],
                    "lagnas": MARRIAGE_MUHURTA["good_lagnas"]["list"],
                    "tithi_citation": MARRIAGE_MUHURTA["good_tithis"]["citation"],
                    "nakshatra_citation": MARRIAGE_MUHURTA["good_nakshatras"]["citation"],
                    "lagna_citation": MARRIAGE_MUHURTA["good_lagnas"]["citation"]
                }
            },

            "classical_sources_used": [
                "Brihat Parashar Hora Shastra — Maharishi Parashara",
                "Brihat Jataka — Varahamihira",
                "Phaldipika — Mantreswara",
                "Jataka Parijata — Vaidyanatha Dikshita",
                "Saravali — Kalyanavarma",
                "Prasna Marga — Harihara",
                "Muhurta Chintamani (for Muhurta rules only)"
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")


def _format_planets_with_dignity(planets: dict, shadbala: dict) -> dict:
    """Format planet data with dignity and strength info."""
    formatted = {}
    for name, pdata in planets.items():
        if name in ["ascendant", "midheaven"]:
            continue
        sb = shadbala.get(name, {})
        formatted[name] = {
            "sign": pdata.get("sign", "").capitalize(),
            "degree": round(pdata.get("degree", 0), 2),
            "nakshatra": pdata.get("nakshatra", ""),
            "nakshatra_pada": pdata.get("nakshatra_pada", 0),
            "is_retrograde": pdata.get("is_retrograde", False),
            "dignity_state": sb.get("dignity_state", ""),
            "strength": sb.get("strength_label", ""),
            "is_combust": sb.get("combustion", {}).get("is_combust", False),
            "longitude": round(pdata.get("longitude", 0), 4),
        }
    return formatted


def _get_planet_house_results(planets: dict, houses: dict, lagna_sign: str) -> list:
    """Get classical results for Sun in houses (expand to all planets later)."""
    results = []
    sun_house = 1
    for hnum, hdata in houses.items():
        if "sun" in hdata.get("planets", []):
            sun_house = hnum
            break

    if sun_house in SUN_IN_HOUSES:
        result = SUN_IN_HOUSES[sun_house]
        results.append({
            "planet": "Sun",
            "house": sun_house,
            "result": result["result"],
            "strong_result": result["strong"],
            "weak_result": result["weak"],
            "citation": result["citation"],
            "contradiction": result.get("contradiction", ""),
            "note": result.get("note", "")
        })

    return results


def _get_house_details(houses: dict, lagna_sign: str) -> dict:
    """Add classical significations to each house."""
    detailed = {}
    from app.classical_knowledge import SIGNS, HOUSE_LORDS
    lagna_idx = SIGNS.index(lagna_sign)

    for hnum, hdata in houses.items():
        bhava = BHAVA_KARAKATVA.get(hnum, {})
        house_sign = SIGNS[(lagna_idx + hnum - 1) % 12]
        lord = HOUSE_LORDS.get(house_sign, "")

        detailed[hnum] = {
            "name": bhava.get("name", f"House {hnum}"),
            "sign": house_sign.capitalize(),
            "lord": lord.capitalize(),
            "planets": hdata.get("planets", []),
            "primary_significations": bhava.get("primary", ""),
            "karaka_planet": bhava.get("karaka", ""),
            "classification": bhava.get("classification", ""),
            "citation": bhava.get("citation", "")
        }
    return detailed


@app.get("/api/chart/{chart_id}")
async def get_chart(chart_id: str):
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        result = await session.execute(
            select(UserChart).where(UserChart.chart_id == chart_id)
        )
        chart = result.scalar_one_or_none()
        if not chart:
            raise HTTPException(404, "Chart not found")
        return {
            "chart_id": chart.chart_id,
            "birth_details": chart.birth_details_json,
            "yogas": chart.yogas_json,
            "doshas": chart.doshas_json,
            "panchanga": chart.panchanga_json
        }


@app.get("/api/nakshatra/{longitude}")
async def get_nakshatra_detail(longitude: float):
    """Get detailed Nakshatra info for a given longitude."""
    nak_num = int((longitude * 27) / 360) % 27 + 1
    nak = NAKSHATRAS.get(nak_num, {})
    return {
        "nakshatra": nak.get("name"),
        "number": nak_num,
        "ruling_planet": nak.get("ruler", "").capitalize(),
        "deity": nak.get("deity", ""),
        "gana": nak.get("gana", "").capitalize(),
        "yoni": nak.get("yoni", "").capitalize(),
        "nadi": nak.get("nadi", "").capitalize(),
        "nature": nak.get("nature", "").capitalize(),
        "degree_range": f"{nak.get('start_deg', 0):.3f}° — {nak.get('end_deg', 0):.3f}°",
        "citation": nak.get("citation", "")
    }


@app.get("/api/classical-sources")
async def get_classical_sources():
    """List all classical sources used in this engine."""
    return {
        "primary_texts": [
            {
                "title": "Brihat Parashar Hora Shastra",
                "author": "Maharishi Parashara",
                "significance": "Root text of all Vedic Astrology — foundational authority",
                "chapters_used": "Rashi Bheda, Graha Swaroopa, Graha Bala, Yoga, Dasha, Bhava Phala Adhyayas"
            },
            {
                "title": "Brihat Jataka",
                "author": "Varahamihira",
                "significance": "Most quoted classical text — verification standard",
                "chapters_used": "Chapters 1, 2, 7, 12"
            },
            {
                "title": "Phaldipika",
                "author": "Mantreswara",
                "significance": "Comprehensive predictive text",
                "chapters_used": "Chapters 1, 2, 6, 7, 17"
            },
            {
                "title": "Jataka Parijata",
                "author": "Vaidyanatha Dikshita",
                "significance": "Detailed yoga and predictive rules",
                "chapters_used": "Chapters 9, 11"
            },
            {
                "title": "Saravali",
                "author": "Kalyanavarma",
                "significance": "Comprehensive expansion of Brihat Jataka",
                "chapters_used": "Chapters 3, 22-30, 36"
            },
            {
                "title": "Prasna Marga",
                "author": "Harihara (Narayanan Nambutiri)",
                "significance": "Horary and medical astrology",
                "chapters_used": "Chapters 12, 13, 14, 15, 20"
            }
        ],
        "citation_policy": "Every prediction in this API is cited to exact Book, Author, Chapter, and Shloka number. Where classical authors contradict each other, both views are shown.",
        "no_ai_hallucinations": "This engine does NOT use AI to generate citations. All citations are from verified classical texts."
    }


# Static frontend
try:
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    @app.get("/", response_class=HTMLResponse)
    async def root():
        with open("app/static/index.html", "r") as f:
            return f.read()
except Exception:
    @app.get("/")
    async def root():
        return {"message": "Aetheris Classical Vedic Astrology API v4.0 — See /docs for API documentation"}
