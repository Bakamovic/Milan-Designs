# Foil Types

## What It Does

The Foil Types tab is where you register the foil materials the shop stocks. For each material you select the brand, product line, and colour, then record two physical measurements — the empty tube weight and the weight per metre. These values let the app calculate remaining roll length from a scale reading.

---

## Why It Exists

The weight-to-length formula requires two constants specific to each foil type: how heavy the cardboard core is, and how heavy one metre of that particular material is. These differ between brands and product lines (e.g. a heavy protective film like 3M 2080 weighs more per metre than a thin cast vinyl like Oracal 651). Registering these values once means every roll check-in is automatic.

Tracking colour in the material name also distinguishes rolls of the same product line — two rolls of Oracal 651 in different colours get separate entries so inventory is unambiguous.

---

## How It Works

### Adding a Foil Type

| Field | Notes |
|-------|-------|
| Brand | Dropdown: Oracal, 3M, Avery, Hexis, Arlon |
| Product Line | Dropdown filtered by brand |
| Color / Finish | Dropdown from built-in catalog (where available), or free-text entry |
| Core Weight (g) | Weight of the empty cardboard tube |
| Unit Weight (g/m) | Weight of one metre of this material |
| Notes | Optional |

The material name is auto-generated. Format depends on how colour was entered:

| Scenario | Example name |
|----------|-------------|
| Catalog colour with code | `Oracal 651 - Red (031)` |
| Free-text colour | `Hexis Skintac - Gloss Black` |
| No colour entered | `Arlon SLX` |

Material names must be unique — the same brand / product line / colour combination cannot be added twice.

### Color Catalogs

Some product lines have a built-in colour catalog. Others use free-text entry:

| Brand | Product Line | Colour Entry |
|-------|-------------|--------------|
| Oracal | 651 | Catalog — 52 colours (e.g. "Red (031)") |
| Oracal | 970RA | Catalog — 29 colours |
| Oracal | 975 | Free text |
| Oracal | Vinyl Cast | Free text |
| 3M | 1080 | Free text |
| 3M | 2080 | Catalog — 30 colours |
| 3M | Scotchprint | Free text |
| Avery | SW900 | Catalog — 26 colours |
| Avery | Dennison | Free text |
| Hexis | Skintac | Free text |
| Hexis | Bodyfence | Free text |
| Arlon | 3000 | Free text |
| Arlon | SLX | Free text |

The catalog data lives in the `FOIL_COLORS` constant in `database.py`. Adding new colors or product lines requires a code change there.

### Viewing Configured Types

All configured foil types display in a table with material name, core weight, unit weight, creation date, and notes.

### Deleting a Foil Type

A foil type can only be deleted if **no rolls currently reference it**. If rolls exist for that type, the app blocks deletion with: `"Cannot delete: rolls still reference this foil type."` Delete or reassign those rolls first.

This protection is enforced at the database level via a `RESTRICT` foreign key on the `foil_rolls` table.

**Admin and Worker roles** can delete foil types.

---

## Key Code Locations

| What | File |
|------|------|
| `FoilType` model | `database.py` |
| `FOIL_BRANDS` constant | `database.py` |
| `FOIL_COLORS` constant (color catalogs) | `database.py` |
| `create_foil_type()` | `database.py` |
| `read_all_foil_types()` | `database.py` |
| `delete_foil_type()` | `database.py` |
| UI — Foil Types tab | `app.py` |

---

## Limitations & Known Issues

- **Brand/product line list is hardcoded.** Adding a new brand or product line requires a code change in `database.py` (`FOIL_BRANDS`).
- **Color catalogs are hardcoded.** Adding new colour options for a catalogued line requires a code change in `database.py` (`FOIL_COLORS`).
- **No edit.** Core weight and unit weight cannot be updated after the fact. To correct a calibration mistake, delete the foil type (if no rolls reference it) and re-add it with correct values.

---

## Related Features

- [Foil Inventory](foil-inventory.md) — foil types must exist before rolls can be added
- [Roll Check-in](roll-check-in.md) — uses the calibrated weights on every check-in
