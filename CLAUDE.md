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

To wipe and re-populate test data (development only — never run against the live DB):

```bash
python seed_data.py
```

`seed_data.py` deletes `shop_app.db` and recreates it from scratch with 8 foil types, 16 rolls, 23 customers, and 23 jobs spread across March–May 2026.

---

## Architecture

| Layer | File | Responsibility |
|-------|------|----------------|
| UI | `app.py` | All Streamlit tabs, forms, and user interaction |
| Data | `database.py` | SQLAlchemy ORM models, CRUD operations, DB setup, migration |
| Reporting | `reporting.py` | Aggregations, KPI calculations, Excel export |
| Dev data | `seed_data.py` | Test data — do not run against production DB |

**Database:** SQLite (`shop_app.db`) with WAL journaling enabled for concurrent-safe access.

Schema migrations run automatically at startup via `run_migrations()` inside `init_db()`. No Alembic — migrations use raw SQL with idempotent guards.

---

## Key Files

- [app.py](app.py) — UI entry point; login gate, 6 tabs, role guards, undo system
- [database.py](database.py) — ORM models (`Customer`, `Job`, `FoilType`, `FoilRoll`), all CRUD functions, constants
- [reporting.py](reporting.py) — `build_fact_jobs()`, `build_summary_weekly/monthly()`, `export_to_excel()`
- [Milan_designs.pbix](Milan_designs.pbix) — Power BI dashboard file; opened separately in Power BI Desktop
- [.streamlit/config.toml](.streamlit/config.toml) — forces dark theme for all users
- [.streamlit/secrets.toml](.streamlit/secrets.toml) — user credentials; **gitignored, never committed**

---

## Database Schema

**customers** — one row per customer (name, phone, email)  
**jobs** — one row per job; `customer_id` FK links to `customers` (nullable for legacy rows)  
**foil_types** — one row per calibrated foil material  
**foil_rolls** — one row per physical roll, linked to a `foil_type`

Relationships:
- `Customer` → `Job`: one-to-many; deleting a customer is blocked in Python if jobs are linked
- `FoilType` → `FoilRoll`: one-to-many with cascade delete
- Deleting a `foil_type` is blocked (`RESTRICT`) if live rolls reference it

Legacy jobs (pre-customer-DB) have `customer_id = NULL` and display their original `customer_name` string.

---

## Key Constants (database.py)

| Constant | Values / Notes |
|----------|----------------|
| `JOB_TYPES` | Full Wrap, Partial Wrap, Decals, Signage, PPF, Tint, Other |
| `STATUS_OPTIONS` | Pending, In Progress, Completed, Invoiced, Paid |
| `FOIL_BRANDS` | Oracal, 3M, Avery, Hexis, Arlon — each with product lines |
| `FOIL_COLORS` | Nested `{brand: {product_line: [(code, name), ...]}}`. Covers Oracal 651 (52 colors), Oracal 970RA (29), Avery SW900 (26), 3M 2080 (30). Product lines without catalog data fall back to free-text input. |

---

## Core Formulas

**Profit** — Python properties on `Job` model:

```
total_cost   = labour_cost + material_cost + subcontractor_cost
gross_profit = charge - total_cost
margin_pct   = gross_profit / charge × 100   (returns 0 if charge is 0)
```

**Foil length** — `_calculate_length()`:

```
calculated_length (m) = (total_weight_g - core_weight_g) / unit_weight_g_per_m
```

Low stock threshold: `< 5 metres`

---

## User Roles & Access

Login is required on startup. Credentials live in `.streamlit/secrets.toml` (gitignored). Three roles:

| Role | Login name | What they can do |
|------|-----------|-----------------|
| **Admin** | Admin | Full access — view, add, edit, delete everything. Unlimited undo. |
| **Milan** | Milan | View + add in all tabs. No edit or delete of jobs/customers. Cannot delete foil types or rolls. One undo. |
| **Worker** | Worker | Same as Milan for add/view, but CAN delete foil types and rolls. No edit/delete of jobs/customers. One undo. |

The undo button appears in the sidebar after any mutating action. Admin has an unlimited stack; Milan and Worker are capped at 1 (new action replaces old).

Undoable actions: create job, create customer, create foil type, create roll, roll check-in (restores previous weight).

---

## Conventions

- All currency in EUR (€), stored as `Float`
- All weights in grams (g), all lengths in metres (m)
- Dates stored as `date` objects; displayed as `DD/MM/YYYY` in the UI
- DB sessions use context managers: `with SessionLocal() as session`
- Streamlit forms use `clear_on_submit=True`; mutations call `st.rerun()` after success
- Foil type names follow the pattern: `"Brand ProductLine - Color Name (Code)"` e.g. `"Oracal 651 - Red (031)"`
- Roll labels are required (UI validation); format: `"Oracal 651 - Red #1"`
- **Minimal in-app charts** — the Overview tab shows weekly/monthly revenue and profit bar charts (Streamlit built-in). Deep analysis lives in Power BI. Do not add further analytics beyond what is already in the Overview tab without explicit request.
- **Dark mode enforced** — `.streamlit/config.toml` sets `base = "dark"` so the app never renders in light mode regardless of OS setting.

---

## Tab Reference

| Tab | Purpose | Edit/Delete |
|-----|---------|-------------|
| **Jobs** | Log and view jobs. Customer selected from dropdown. | Admin only |
| **Customers** | Add customers. Profile shows job history and total spend. | Admin only |
| **Foil Inventory** | Add rolls (label required), view stock, low-stock warning at < 5 m. | Admin + Worker |
| **Foil Types** | Define foil materials with brand + product line + color from catalog. Core/unit weights for length calculation. | Admin + Worker |
| **Roll Check-in** | Weigh a roll on the scale → app updates remaining length in inventory. | All roles |
| **Overview** | KPI metrics, weekly/monthly bar charts, detail tables (collapsible), Excel export for Power BI. | All roles |

---

## Power BI Integration

The Overview tab generates a `.xlsx` workbook with 4 sheets (see [reporting.py](reporting.py)):

| Sheet | Contents |
|-------|----------|
| `fact_jobs` | All jobs with date dimension columns + customer phone/email via LEFT JOIN |
| `dim_foil_inventory` | Current roll inventory snapshot |
| `summary_weekly` | Jobs aggregated by ISO week |
| `summary_monthly` | Jobs aggregated by month |

Dashboard refinement and analysis happen in `Milan_designs.pbix`, not in the app.

---

## Feature Docs

Detailed documentation for each module lives in [docs/features/](docs/features/):

- [Jobs](docs/features/jobs.md)
- [Customers](docs/features/customers.md)
- [Foil Inventory](docs/features/foil-inventory.md)
- [Foil Types](docs/features/foil-types.md)
- [Roll Check-in](docs/features/roll-check-in.md)
- [Overview](docs/features/overview.md)

Planned features and priorities: [docs/roadmap.md](docs/roadmap.md)
