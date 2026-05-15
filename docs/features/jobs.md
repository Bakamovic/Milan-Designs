# Jobs

## What It Does

The Jobs tab is the core of the app — it lets you log, view, edit, and delete jobs for the shop. Every job records who the customer is, what type of work was done, how much was charged, and how costs were split across labour, materials, and subcontractors. Profit and margin are calculated automatically on save.

---

## Why It Exists

Before this app, jobs were tracked on paper or spreadsheets with no consistent structure and no automatic profit calculation. Milan had no quick way to know whether a job was profitable or what his margin looked like across the week. The Jobs module replaces that manual process with a single source of truth.

---

## How It Works

### Creating a Job ([app.py:21–63](../../app.py))

Fill in the form at the top of the Jobs tab:

| Field | Required | Notes |
|-------|----------|-------|
| Date | Yes | Defaults to today, DD/MM/YYYY format |
| Customer Name | Yes | Free text; whitespace stripped |
| Job Type | Yes | Dropdown: Full Wrap, Partial Wrap, Decals, Signage, PPF, Tint, Other |
| Charge (€) | No | What the customer is billed |
| Labour (€) | No | Internal labour cost |
| Material (€) | No | Material cost (entered manually — not yet linked to foil rolls) |
| Subcontractor (€) | No | Any work outsourced |
| Status | Yes | Pending / In Progress / Completed / Invoiced / Paid |
| Notes | No | Free text, optional |

On save, the app immediately shows the gross profit and margin for the new job. The form clears automatically.

### Profit Calculations

Calculated as Python properties on the `Job` model ([database.py:57–69](../../database.py)) — not stored in the database, always derived fresh:

```
total_cost   = labour_cost + material_cost + subcontractor_cost
gross_profit = charge - total_cost
margin_pct   = gross_profit / charge × 100
```

If `charge` is zero, `margin_pct` returns `0.0` to avoid division by zero.

### Viewing Jobs ([app.py:66–71](../../app.py))

All jobs display in a scrollable table sorted newest-first, showing:

`Job_ID` · `Date` · `Customer` · `Job_Type` · `Status` · `Charge` · `Labour_Cost` · `Material_Cost` · `Subcontractor_Cost` · `Total_Cost` · `Gross_Profit` · `Margin_Pct` · `Notes`

### Editing a Job ([app.py:80–119](../../app.py))

Select a job by ID from the dropdown below the table. An expander reveals the pre-filled edit form. All fields can be changed. Save updates the record immediately.

### Deleting a Job ([app.py:121–124](../../app.py))

The "Delete Job" button permanently removes the selected job. No soft delete — the record is gone.

---

## Key Code Locations

| What | File | Lines |
|------|------|-------|
| Job model + profit properties | [database.py](../../database.py) | 37–69 |
| `create_job()` | [database.py](../../database.py) | 123–141 |
| `read_all_jobs()` | [database.py](../../database.py) | 144–164 |
| `update_job()` | [database.py](../../database.py) | 167–185 |
| `delete_job()` | [database.py](../../database.py) | 188–195 |
| UI — new job form | [app.py](../../app.py) | 21–63 |
| UI — view / edit / delete | [app.py](../../app.py) | 66–126 |

---

## Limitations & Known Issues

- **Material cost is manual.** There is no connection between the Material (€) field and the actual foil rolls used. This is a known gap — see [roadmap.md](../roadmap.md).
- **No customer lookup.** Customer name is a free-text field; the same customer can be entered differently across jobs. A customer database is planned.
- **No vehicle details.** Make, model, registration, and colour are not captured yet — planned for a future release.
- **No invoice generation.** Invoices must be created manually outside the app — also on the roadmap.

---

## Related Features

- [Foil Inventory](foil-inventory.md) — will eventually link to material costs on jobs
- [Power BI Export](power-bi-export.md) — jobs feed the `fact_jobs` sheet for analysis
- [Roadmap](../roadmap.md) — customer database, vehicle details, invoice generation
