# Power BI Export

## What It Does

The Power BI Export tab is a data pipeline. It packages all job and inventory data into a structured Excel workbook that gets loaded into Power BI Desktop for analysis and dashboarding. The tab also shows a quick KPI summary and weekly/monthly tables as a sanity check before you export.

---

## Why It Exists

The app's job is clean data entry and management — it is not an analytics tool. Power BI handles all charting, trend analysis, and business reporting. The export tab is the bridge between the two: it normalises the raw data into analysis-ready sheets with date dimension columns added, so Power BI can connect without transformation work.

---

## How It Works

### KPI Snapshot ([app.py:268–275](../../app.py))

Five metric cards at the top of the tab show a current snapshot of all-time data:

| Metric | Formula |
|--------|---------|
| Jobs | Count of all job records |
| Revenue | Sum of all `charge` values |
| Total Costs | Sum of all `total_cost` values |
| Gross Profit | Revenue − Total Costs |
| Margin % | Gross Profit / Revenue × 100 |

These are calculated fresh from the database on every page load via `get_kpi_snapshot()` ([reporting.py:103–123](../../reporting.py)). They are a quick check — not meant to replace Power BI analysis.

### Weekly and Monthly Previews ([app.py:278–291](../../app.py))

Two preview tables let you verify the data before exporting:

- **Weekly** — jobs grouped by ISO week (`YYYY-Www` label), with job count, revenue, cost breakdown, profit, and margin
- **Monthly** — same groupings by calendar month

Both are calculated by `build_summary_weekly()` and `build_summary_monthly()` in [reporting.py](../../reporting.py).

### Generating the Export ([app.py:294–309](../../app.py))

Click "Generate Export File" to build the workbook in memory. When it's ready, a Download button appears. The filename includes today's date: `milan_designs_YYYYMMDD.xlsx`.

The workbook is cached in `st.session_state["pbi_bytes"]` so clicking Download multiple times doesn't re-run the query.

### Workbook Structure ([reporting.py:126–138](../../reporting.py))

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

| What | File | Lines |
|------|------|-------|
| `get_kpi_snapshot()` | [reporting.py](../../reporting.py) | 103–123 |
| `build_fact_jobs()` | [reporting.py](../../reporting.py) | 18–39 |
| `build_summary_weekly()` | [reporting.py](../../reporting.py) | 42–61 |
| `build_summary_monthly()` | [reporting.py](../../reporting.py) | 64–83 |
| `build_dim_foil_inventory()` | [reporting.py](../../reporting.py) | 86–100 |
| `export_to_excel()` | [reporting.py](../../reporting.py) | 126–138 |
| UI — export tab | [app.py](../../app.py) | 265–310 |

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
