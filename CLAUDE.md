# Milan Designs — Shop Management System

## Overview

Custom internal web app for Milan Designs, a vehicle wrap and signage shop. Tracks jobs with full cost breakdowns, manages vinyl foil inventory by weight, and exports structured data to Power BI for business analysis.

**Primary users:** Djanan (developer) and Milan (shop owner), both using it in daily shop operations.

---

## How to Run

```bash
# Activate virtual environment (Windows)
venv\Scripts\activate

# Start the app
streamlit run app.py
```

App runs at http://localhost:8501 by default.

To populate test data (development only — never run against the live DB):

```bash
python seed_data.py
```

---

## Architecture

| Layer | File | Responsibility |
|-------|------|----------------|
| UI | `app.py` | All Streamlit tabs, forms, and user interaction |
| Data | `database.py` | SQLAlchemy ORM models, CRUD operations, DB setup |
| Reporting | `reporting.py` | Aggregations, KPI calculations, Excel export |
| Dev data | `seed_data.py` | Test data — do not run against production DB |

**Database:** SQLite (`shop_app.db`) with WAL journaling enabled for concurrent-safe access.

---

## Key Files

- [app.py](app.py) — UI entry point; 5 tabs: Jobs, Foil Inventory, Calibration, Roll Check-in, Power BI Export
- [database.py](database.py) — ORM models (`Job`, `FoilType`, `FoilRoll`), all CRUD functions, constants
- [reporting.py](reporting.py) — `build_fact_jobs()`, `build_summary_weekly/monthly()`, `export_to_excel()`
- [Milan_designs.pbix](Milan_designs.pbix) — Power BI dashboard file; opened separately in Power BI Desktop

---

## Database Schema

**jobs** — one row per job  
**foil_types** — one row per calibrated foil material (brand + product line)  
**foil_rolls** — one row per physical roll, linked to a `foil_type`

Relationships:
- `FoilType` → `FoilRoll`: one-to-many with cascade delete
- Deleting a `foil_type` is blocked (`RESTRICT`) if live rolls reference it

---

## Key Constants (database.py)

| Constant | Line | Values |
|----------|------|--------|
| `JOB_TYPES` | 25 | Full Wrap, Partial Wrap, Decals, Signage, PPF, Tint, Other |
| `STATUS_OPTIONS` | 26 | Pending, In Progress, Completed, Invoiced, Paid |
| `FOIL_BRANDS` | 28 | Oracal, 3M, Avery, Hexis, Arlon (each with product lines) |

---

## Core Formulas

**Profit** — Python properties on `Job` model ([database.py:57–69](database.py)):

```
total_cost   = labour_cost + material_cost + subcontractor_cost
gross_profit = charge - total_cost
margin_pct   = gross_profit / charge × 100   (returns 0 if charge is 0)
```

**Foil length** — `_calculate_length()` ([database.py:114–120](database.py)):

```
calculated_length (m) = (total_weight_g - core_weight_g) / unit_weight_g_per_m
```

Low stock threshold: `< 5 metres`

---

## Conventions

- All currency in EUR (€), stored as `Float`
- All weights in grams (g), all lengths in metres (m)
- Dates stored as `date` objects; displayed as `DD/MM/YYYY` in the UI
- DB sessions use context managers: `with SessionLocal() as session`
- Streamlit forms use `clear_on_submit=True`; mutations call `st.rerun()` after success
- **No in-app analytics** — the app is a data entry and management tool only; charts and analysis live in Power BI

---

## Power BI Integration

The export tab generates a `.xlsx` workbook with 4 sheets (see [reporting.py](reporting.py)):

| Sheet | Contents |
|-------|----------|
| `fact_jobs` | All jobs with date dimension columns added |
| `dim_foil_inventory` | Current roll inventory snapshot |
| `summary_weekly` | Jobs aggregated by ISO week |
| `summary_monthly` | Jobs aggregated by month |

Dashboard refinement and analysis happen in `Milan_designs.pbix`, not in the app. Do not add in-app charts or analytics.

---

## Feature Docs

Detailed documentation for each module lives in [docs/features/](docs/features/):

- [Jobs](docs/features/jobs.md)
- [Foil Inventory](docs/features/foil-inventory.md)
- [Calibration](docs/features/calibration.md)
- [Roll Check-in](docs/features/roll-check-in.md)
- [Power BI Export](docs/features/power-bi-export.md)

Planned features and priorities: [docs/roadmap.md](docs/roadmap.md)
