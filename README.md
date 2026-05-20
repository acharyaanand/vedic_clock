# Vedic Clock — Classical Jyotish Engine

**Every prediction cited to exact Book | Author | Chapter | Shloka**

No AI hallucinations. No invented citations. Only verified classical sources.

---

## Classical Sources Used

| Text | Author | Used For |
|------|--------|----------|
| Brihat Parashar Hora Shastra | Maharishi Parashara | Planetary dignity, Shadbala, Yogas, Dasha, Bhavas |
| Brihat Jataka | Varahamihira | Verification standard, Yogas |
| Phaldipika | Mantreswara | Yogas, Combustion, Muhurta |
| Jataka Parijata | Vaidyanatha Dikshita | Yoga definitions |
| Saravali | Kalyanavarma | Planet-in-house results |
| Prasna Marga | Harihara | Medical astrology, Muhurta |
| Muhurta Chintamani | Classical | Marriage Muhurta rules |

---

## File Structure

```
vedic_clock/
├── classical_knowledge.py   # All rules with classical citations
├── main.py                  # FastAPI app — all endpoints
├── engine.py                # Swiss Ephemeris calculations
├── vedic_yogas.py           # Yoga/Dosha detection with citations
├── shadbala.py              # Six-fold planetary strength
├── dasha_engine.py          # Vimshottari Dasha engine
├── models.py                # Pydantic + SQLAlchemy models
├── database.py              # Async DB setup
├── requirements.txt         # Dependencies
├── run.py                   # Entry point
└── .env                     # Environment variables (create this)
```

---

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Download Swiss Ephemeris files
Download from https://www.astro.com/ftp/swisseph/ephe/
Minimum required: `seas_18.se1`, `semo_18.se1`
Place in `./ephe/` folder.

### 3. Create .env file
```
DATABASE_URL=sqlite+aiosqlite:///./aetheris.db
REDIS_URL=redis://localhost:6379/0
SWISSEPH_PATH=./ephe/
```

### 4. Run
```bash
python run.py
```

### 5. Open API docs
```
http://localhost:8000/docs
```

---

## What Makes This Different

### Every prediction shows its source:
```json
{
  "planet": "Sun",
  "dignity_state": "Exalted (Uccha) — Very strong",
  "citation": {
    "book": "Brihat Jataka",
    "author": "Varahamihira",
    "chapter": "1",
    "shloka": "13",
    "corroborated_by": "BPHS Rashi Bheda Adhyaya Sl.38-39"
  }
}
```

### Classical contradictions are shown:
```json
{
  "name": "Mangal Dosha",
  "contradiction": "Parashara counts 2nd house also (6 houses). 
                    Mantreswara counts 5 houses only. 
                    Both views have classical support."
}
```

### Yoga cancellations are properly checked:
```json
{
  "name": "Budha-Aditya Yoga (CANCELLED — Mercury Combust)",
  "important_note": "Mercury within combustion orb — 
                     Mantreswara explicitly requires Mercury 
                     to be free from combustion"
}
```

---

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /api/vedic-chart` | Full horoscope with citations |
| `GET /api/chart/{id}` | Retrieve saved chart |
| `GET /api/nakshatra/{longitude}` | Nakshatra details |
| `GET /api/classical-sources` | List all classical sources used |
| `GET /docs` | Interactive API documentation |

---

## Built By

Classical Jyotish knowledge + modern Python engineering.
Every rule traceable to its original Sanskrit shloka.
