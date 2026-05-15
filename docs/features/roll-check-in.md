# Roll Check-in

## What It Does

The Roll Check-in tab is the daily workflow for keeping inventory accurate. You pick up a roll, place it on the scale, enter the reading, and the app recalculates and saves the remaining length. It also sets the "Last Checked" date so you can see which rolls haven't been weighed recently.

---

## Why It Exists

Foil is used continuously throughout the day. Rather than updating inventory mid-job or estimating usage, the workflow is: weigh the roll at check-in, let the app figure out how much is left. This is fast (a few seconds per roll) and accurate regardless of how many small pieces were cut.

---

## How It Works

### Check-in Workflow ([app.py:239–255](../../app.py))

1. Select the roll from the dropdown (shows label, material name, and current remaining length)
2. Place the roll on the scale and enter the reading in grams
3. Add an optional note (e.g. "used on BMW wrap job")
4. Click "Confirm Check-in"

The app recalculates the length using the same formula as when the roll was first added:

```
new_length (m) = (new_total_weight_g - core_weight_g) / unit_weight_g_per_m
```

The roll's `calculated_length`, `current_total_weight`, and `last_checked` date are all updated in one operation ([database.py:306–320](../../database.py)).

### Low Stock Warning

If the recalculated length is below 5 metres, a yellow warning is shown after saving:

> *"Saved — but low stock: X.XX m remaining. Reorder soon."*

The roll is also flagged as `[LOW]` in the dropdown on the next check-in so it's visible before you even commit the update.

### Current Stock View ([app.py:258–264](../../app.py))

Below the check-in form is a quick table showing all rolls with their current remaining length and last checked date — a fast inventory glance without navigating to the Foil Inventory tab.

---

## Key Code Locations

| What | File | Lines |
|------|------|-------|
| `update_foil_roll_weight()` | [database.py](../../database.py) | 306–320 |
| `get_roll_options()` — dropdown builder | [database.py](../../database.py) | 333–349 |
| UI — check-in form | [app.py](../../app.py) | 228–264 |

---

## Limitations & Known Issues

- **One roll at a time.** There is no batch check-in — each roll requires its own form submission.
- **No history.** The check-in only saves the most recent weight. There is no log of previous readings, so you cannot track consumption over time per roll.
- **Notes overwrite, not append.** Each check-in can store one note on the roll. The new note replaces the old one rather than appending to a history.

---

## Related Features

- [Foil Inventory](foil-inventory.md) — adds rolls; check-in updates them
- [Calibration](calibration.md) — provides the `core_weight` and `unit_weight` used in recalculation
