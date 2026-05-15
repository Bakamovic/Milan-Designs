# Foil Inventory

## What It Does

The Foil Inventory tab manages the physical rolls of vinyl wrap and other foil materials in stock. You add a roll by weighing it on the shop scale and entering the result — the app calculates how many metres are left automatically. Low-stock rolls are flagged when they drop below 5 metres.

---

## Why It Exists

The shop uses many different foil types every day. Manually measuring the remaining length on each roll is slow and impractical — you'd have to unroll and re-roll the vinyl, which risks damaging it. Every shop already has a scale for other purposes. Weighing a roll takes seconds and gives a precise answer. The app does the conversion, so there's no mental arithmetic and no guessing.

---

## How It Works

### The Weight-to-Length Formula

Defined in `_calculate_length()` ([database.py:114–120](../../database.py)):

```
calculated_length (m) = (total_weight_g - core_weight_g) / unit_weight_g_per_m
```

- **`total_weight_g`** — what the scale reads when you weigh the roll right now
- **`core_weight_g`** — the weight of the empty cardboard tube (calibrated per foil type)
- **`unit_weight_g_per_m`** — how many grams one metre of this specific foil weighs (calibrated per foil type)

The formula raises a `ValueError` if `total_weight` is less than `core_weight` (scale reading below the empty tube — likely a mistake).

### Adding a Roll ([app.py:183–206](../../app.py))

Before adding a roll, you must have at least one foil type configured in the [Calibration](calibration.md) tab.

| Field | Required | Notes |
|-------|----------|-------|
| Foil Type | Yes | Dropdown of calibrated materials |
| Roll Label | No | Optional identifier, e.g. `Roll A-01` |
| Total Weight (g) | Yes | Current scale reading |
| Notes | No | Free text |

On save, the calculated length is shown in the success message. The roll's `last_checked` date is set to today.

### Viewing Rolls ([app.py:209–226](../../app.py))

All rolls display in a table sorted by remaining length ascending (shortest first, so critical stock is always at the top). Columns shown:

`Roll ID` · `Label` · `Material` · `Total Weight (g)` · `Core Weight (g)` · `Unit Weight (g/m)` · `Calculated Length (m)` · `Last Checked` · `Notes`

If any rolls are below 5 metres, a warning banner lists them by label at the top of the section.

### Deleting a Roll ([app.py:220–224](../../app.py))

Select a roll by ID and click Delete. Permanent — no undo.

---

## Key Code Locations

| What | File | Lines |
|------|------|-------|
| `FoilRoll` model | [database.py](../../database.py) | 89–103 |
| `_calculate_length()` | [database.py](../../database.py) | 114–120 |
| `create_foil_roll()` | [database.py](../../database.py) | 261–278 |
| `read_all_foil_rolls()` | [database.py](../../database.py) | 281–303 |
| `delete_foil_roll()` | [database.py](../../database.py) | 323–330 |
| UI — add roll form | [app.py](../../app.py) | 183–206 |
| UI — view / delete | [app.py](../../app.py) | 208–226 |

---

## Limitations & Known Issues

- **Not linked to jobs.** When a job uses foil, the material cost on the job is entered manually and the roll weight is not automatically deducted. This is the biggest current gap — see [roadmap.md](../roadmap.md).
- **Low stock threshold is hardcoded** at 5 metres. There is no per-roll or per-type threshold setting.
- **No reorder tracking.** There is no way to mark a roll as "on order" or record when a new delivery arrived.

---

## Related Features

- [Calibration](calibration.md) — must be set up first; provides `core_weight` and `unit_weight` values
- [Roll Check-in](roll-check-in.md) — the day-to-day workflow for updating roll weights after use
- [Power BI Export](power-bi-export.md) — rolls feed the `dim_foil_inventory` sheet
- [Roadmap](../roadmap.md) — foil usage linked to jobs (priority #2)
