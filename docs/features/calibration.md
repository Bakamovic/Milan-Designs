# Calibration

## What It Does

The Calibration tab is where you register the foil materials the shop stocks. For each material you record two physical measurements — the empty tube weight and the weight per metre — which the app uses to calculate remaining roll length from a scale reading. This setup step must be done before any foil rolls can be added to inventory.

---

## Why It Exists

The weight-to-length formula requires two constants that are specific to each foil type: how heavy the cardboard core is, and how heavy one metre of that particular material is. These numbers differ between brands and product lines (e.g. a heavy protective film like 3M 2080 weighs more per metre than a thin cast vinyl like Oracal 651). Calibration stores these values once so every roll check-in is automatic.

---

## How It Works

### Adding a Foil Type ([app.py:132–153](../../app.py))

| Field | Notes |
|-------|-------|
| Brand | Dropdown: Oracal, 3M, Avery, Hexis, Arlon |
| Product Line | Dropdown filtered by brand (e.g. Oracal → 651, 970RA, 975, Vinyl Cast) |
| Core Weight (g) | Weight of the empty cardboard tube for this material |
| Unit Weight (g/m) | Weight of one metre of this material |
| Notes | Optional |

The material name is auto-generated as `"Brand ProductLine"` (e.g. `"Oracal 970RA"`). Material names must be unique — you cannot add the same brand + product line twice.

### Supported Brands and Product Lines ([database.py:28–34](../../database.py))

| Brand | Product Lines |
|-------|---------------|
| Oracal | 651, 970RA, 975, Vinyl Cast |
| 3M | 1080, 2080, Scotchprint |
| Avery | SW900, Dennison |
| Hexis | Skintac, Bodyfence |
| Arlon | 3000, SLX |

### Viewing Configured Types ([app.py:158–173](../../app.py))

All configured foil types are shown in a table with their weights and creation date.

### Deleting a Foil Type ([app.py:163–171](../../app.py))

A foil type can only be deleted if **no rolls currently reference it**. If rolls exist for that type, the app shows an error: `"Cannot delete: rolls still reference this foil type."` Delete or move those rolls first.

This protection is enforced at the database level via a `RESTRICT` foreign key ([database.py:96](../../database.py)).

---

## Key Code Locations

| What | File | Lines |
|------|------|-------|
| `FoilType` model | [database.py](../../database.py) | 72–86 |
| `FOIL_BRANDS` constant | [database.py](../../database.py) | 28–34 |
| `create_foil_type()` | [database.py](../../database.py) | 210–222 |
| `read_all_foil_types()` | [database.py](../../database.py) | 225–238 |
| `delete_foil_type()` | [database.py](../../database.py) | 247–258 |
| UI — calibration tab | [app.py](../../app.py) | 128–173 |

---

## Limitations & Known Issues

- **Brand/product line list is hardcoded** in `FOIL_BRANDS`. Adding a new brand or product line requires a code change in [database.py:28–34](../../database.py).
- **No edit.** Core weight and unit weight cannot be updated after the fact. To correct a calibration mistake, delete the foil type (if no rolls exist) and re-add it with correct values.

---

## Related Features

- [Foil Inventory](foil-inventory.md) — depends on calibration; foil types must exist before rolls can be added
- [Roll Check-in](roll-check-in.md) — uses the calibrated weights on every check-in
