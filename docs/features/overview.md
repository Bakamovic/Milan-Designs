# Overview

## What It Does

The Overview tab is a data pipeline and quick summary. It shows current KPI cards, weekly and monthly bar charts, and collapsible detail tables — and lets you export everything to a structured Excel workbook for Power BI Desktop.

---

## Why It Exists

The app's job is clean data entry and management — it is not an analytics tool. Power BI handles all charting, trend analysis, and business reporting. The Overview tab is the bridge between the two: it normalises the raw data into analysis-ready sheets with date dimension columns added, so Power BI can connect without transformation work.

---

## How It Works

### KPI Snapshot

Five metric cards at the top of the tab show a current snapshot of all-time data:

| Metric | Formula |
|--------|---------|
| Jobs | Count of all job records |
| Revenue | Sum of all `charge` values |
| Total Costs | Sum of all `total_cost` values |
| Gross Profit | Revenue − Total Costs |
| Margin % | Gross Profit / Revenue × 100 |

These are calculated fresh from the database on every page load via `get_kpi_snapshot()` in `reporting.py`. They are a quick check — not meant to replace Power BI analysis.

### Weekly and Monthly Charts

Below the KPI cards, two bar charts show revenue over time:

- **Revenue by Week** — one bar per ISO week
- **Revenue by Month** — one bar per calendar month

Below each chart is a collapsible detail table with job count, revenue, cost breakdown, profit, and margin for that period. Both datasets are calculated by `build_summary_weekly()` and `build_summary_monthly()` in `reporting.py`.

### Generating the Export

Click "Generate Export File" to build the workbook in memory. When it's ready, a Download button appears. The filename includes today's date: `milan_designs_YYYYMMDD.xlsx`.

The workbook is cached in `st.session_state["pbi_bytes"]` so clicking Download multiple times doesn't re-run the query.

### Workbook Structure

The `.xlsx` file contains four sheets:

| Sheet | Source function | Contents |
|-------|----------------|---------|
| `fact_jobs` | `build_fact_jobs()` | All jobs with added date columns: Year, Quarter, Month_Num, Month_Name, ISO_Week, Week_Label |
| `dim_foil_inventory` | `build_dim_foil_inventory()` | Current roll snapshot with a `Low_Stock_Flag` column (1 = below 5m) |
| `summary_weekly` | `build_summary_weekly()` | Job count, revenue, cost breakdown, profit, margin — grouped by ISO week |
| `summary_monthly` | `build_summary_monthly()` | Same groupings by calendar month |

All date columns are formatted `YYYY-MM-DD` for Power BI compatibility.

---

## Key Code Locations

| What | File |
|------|------|
| `get_kpi_snapshot()` | `reporting.py` |
| `build_fact_jobs()` | `reporting.py` |
| `build_summary_weekly()` | `reporting.py` |
| `build_summary_monthly()` | `reporting.py` |
| `build_dim_foil_inventory()` | `reporting.py` |
| `export_to_excel()` | `reporting.py` |
| UI — Overview tab | `app.py` |

---

## Limitations & Known Issues

- **Snapshot only.** The export reflects the database at the moment you click "Generate Export File." Changes made after that point require re-generating.
- **No scheduled export.** Export is manual — there is no automated push to a shared folder or OneDrive.
- **KPI cards are all-time only.** There is no date filter on the KPI snapshot in the app.

---

## Related Features

- [Jobs](jobs.md) — primary data source for `fact_jobs` and summary sheets
- [Foil Inventory](foil-inventory.md) — source for `dim_foil_inventory`
- [Milan_designs.pbix](../../Milan_designs.pbix) — load the exported `.xlsx` here for analysis
