from datetime import date
from database import init_db, create_job, create_foil_type, create_foil_roll

init_db()

# ── Foil Types ──────────────────────────────────────────────
from database import SessionLocal, FoilType

def get_or_create_foil_type(material_name, core_weight, unit_weight):
    with SessionLocal() as session:
        ft = session.query(FoilType).filter_by(material_name=material_name).first()
        if ft:
            return ft
        from database import create_foil_type
        return create_foil_type(material_name, core_weight=core_weight, unit_weight=unit_weight)

ft1 = get_or_create_foil_type("Oracal 970RA", core_weight=120.0, unit_weight=36.5)
ft2 = get_or_create_foil_type("3M 2080",      core_weight=115.0, unit_weight=42.0)
ft3 = get_or_create_foil_type("Avery SW900",  core_weight=110.0, unit_weight=38.0)

# ── Foil Rolls ──────────────────────────────────────────────
create_foil_roll(ft1.foil_type_id, current_total_weight=2000.0, roll_label="Roll A-01")
create_foil_roll(ft1.foil_type_id, current_total_weight=1500.0, roll_label="Roll A-02")
create_foil_roll(ft2.foil_type_id, current_total_weight=3000.0, roll_label="Roll B-01")
create_foil_roll(ft3.foil_type_id, current_total_weight=180.0,  roll_label="Roll C-01")

# ── Jobs — March ────────────────────────────────────────────
create_job(date(2026, 3, 3),  "Klaus Bauer",      "Full Wrap",     2800.0, 400.0, 320.0, 0.0,   "Completed")
create_job(date(2026, 3, 6),  "Stefan Müller",    "Partial Wrap",  1200.0, 200.0, 150.0, 0.0,   "Completed")
create_job(date(2026, 3, 10), "Audi Zentrum GmbH","Decals",         450.0,  80.0,  40.0, 0.0,   "Completed")
create_job(date(2026, 3, 14), "Marco Rossi",      "Full Wrap",     3200.0, 450.0, 380.0, 200.0, "Completed")
create_job(date(2026, 3, 18), "BMW Händler AG",   "PPF",           1800.0, 300.0, 200.0, 0.0,   "Completed")
create_job(date(2026, 3, 21), "Tobias Werner",    "Tint",           380.0,  60.0,  20.0, 0.0,   "Completed")
create_job(date(2026, 3, 25), "Julia Schneider",  "Partial Wrap",  1400.0, 220.0, 180.0, 0.0,   "Completed")
create_job(date(2026, 3, 28), "Fahrzeug Profi",   "Signage",        900.0, 150.0, 120.0, 80.0,  "Completed")

# ── Jobs — April ────────────────────────────────────────────
create_job(date(2026, 4, 2),  "Hans Zimmermann",  "Full Wrap",     3100.0, 420.0, 360.0, 0.0,   "Completed")
create_job(date(2026, 4, 5),  "Petra Hofmann",    "Decals",         320.0,  50.0,  30.0, 0.0,   "Completed")
create_job(date(2026, 4, 8),  "Autohaus König",   "Full Wrap",     2950.0, 430.0, 340.0, 220.0, "Completed")
create_job(date(2026, 4, 11), "Leon Fischer",     "Partial Wrap",  1350.0, 210.0, 160.0, 0.0,   "Completed")
create_job(date(2026, 4, 15), "Mercedes Fleet",   "PPF",           4200.0, 600.0, 480.0, 300.0, "Completed")
create_job(date(2026, 4, 18), "Nina Braun",       "Tint",           420.0,  70.0,  25.0, 0.0,   "Completed")
create_job(date(2026, 4, 22), "Rapid Logistics",  "Signage",       1100.0, 180.0, 140.0, 90.0,  "Completed")
create_job(date(2026, 4, 25), "David Krause",     "Full Wrap",     2750.0, 400.0, 320.0, 0.0,   "Completed")
create_job(date(2026, 4, 29), "Sabine Wolf",      "Partial Wrap",  1250.0, 200.0, 155.0, 0.0,   "Completed")

# ── Jobs — May ──────────────────────────────────────────────
create_job(date(2026, 5, 2),  "Thomas Engel",     "Full Wrap",     3050.0, 440.0, 370.0, 0.0,   "Completed")
create_job(date(2026, 5, 5),  "Autohaus Stern",   "PPF",           2200.0, 320.0, 260.0, 180.0, "Invoiced")
create_job(date(2026, 5, 7),  "Michael Hartmann", "Decals",         480.0,  90.0,  45.0, 0.0,   "Invoiced")
create_job(date(2026, 5, 9),  "VW Fleet GmbH",    "Full Wrap",     5800.0, 800.0, 720.0, 400.0, "In Progress")
create_job(date(2026, 5, 12), "Anna Richter",     "Partial Wrap",  1450.0, 230.0, 175.0, 0.0,   "In Progress")
create_job(date(2026, 5, 13), "Carsten Vogel",    "Tint",           350.0,  55.0,  20.0, 0.0,   "Pending")

print("Done — database seeded with 3 months of data.")