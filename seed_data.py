import os
from datetime import date
from database import (
    init_db, create_customer, create_job,
    create_foil_type, create_foil_roll,
)

# Wipe and recreate the database
if os.path.exists("shop_app.db"):
    os.remove("shop_app.db")
init_db()

# ── Foil Types ────────────────────────────────────────────────
ft_black_651   = create_foil_type("Oracal 651 - Black (070)",                180, 155)
ft_white_651   = create_foil_type("Oracal 651 - White (010)",                180, 155)
ft_red_651     = create_foil_type("Oracal 651 - Red (031)",                  180, 155)
ft_mblack_970  = create_foil_type("Oracal 970RA - Matte Black (070M)",       210, 168)
ft_wgloss_970  = create_foil_type("Oracal 970RA - White Gloss (010G)",       210, 168)
ft_gblack_3m   = create_foil_type("3M 2080 - Gloss Black (G12)",             240, 182)
ft_brush_3m    = create_foil_type("3M 2080 - Brushed Aluminum (BR120)",      240, 182)
ft_red_avery   = create_foil_type("Avery SW900 - Gloss Red (SW900-318-O)",   200, 162)

# ── Foil Rolls ────────────────────────────────────────────────
# Oracal 651 - Black: full roll + partial
create_foil_roll(ft_black_651.foil_type_id,  4055, "Oracal 651 - Black #1")   # 25 m
create_foil_roll(ft_black_651.foil_type_id,  1885, "Oracal 651 - Black #2")   # 11 m

# Oracal 651 - White: full roll + low stock
create_foil_roll(ft_white_651.foil_type_id,  4055, "Oracal 651 - White #1")   # 25 m
create_foil_roll(ft_white_651.foil_type_id,   800, "Oracal 651 - White #2")   # 4 m (low stock)

# Oracal 651 - Red: one roll
create_foil_roll(ft_red_651.foil_type_id,    3280, "Oracal 651 - Red #1")     # 20 m

# Oracal 970RA - Matte Black: full roll + partial
create_foil_roll(ft_mblack_970.foil_type_id, 4410, "Oracal 970RA - Matte Black #1")  # 25 m
create_foil_roll(ft_mblack_970.foil_type_id, 2562, "Oracal 970RA - Matte Black #2")  # 14 m

# Oracal 970RA - White Gloss: full roll + low stock
create_foil_roll(ft_wgloss_970.foil_type_id, 4410, "Oracal 970RA - White Gloss #1")  # 25 m
create_foil_roll(ft_wgloss_970.foil_type_id,  714, "Oracal 970RA - White Gloss #2")  # 3 m (low stock)

# 3M 2080 - Gloss Black: full roll + partial
create_foil_roll(ft_gblack_3m.foil_type_id,  4790, "3M 2080 - Gloss Black #1")       # 25 m
create_foil_roll(ft_gblack_3m.foil_type_id,  3516, "3M 2080 - Gloss Black #2")       # 18 m

# 3M 2080 - Brushed Aluminum: full roll + partial
create_foil_roll(ft_brush_3m.foil_type_id,   4790, "3M 2080 - Brushed Aluminum #1")  # 25 m
create_foil_roll(ft_brush_3m.foil_type_id,   1696, "3M 2080 - Brushed Aluminum #2")  # 8 m

# Avery SW900 - Gloss Red: three rolls, varied usage
create_foil_roll(ft_red_avery.foil_type_id,  4250, "Avery SW900 - Gloss Red #1")     # 25 m
create_foil_roll(ft_red_avery.foil_type_id,  2792, "Avery SW900 - Gloss Red #2")     # 16 m
create_foil_roll(ft_red_avery.foil_type_id,  1334, "Avery SW900 - Gloss Red #3")     # 7 m

# ── Customers ─────────────────────────────────────────────────
c_bauer      = create_customer("Klaus Bauer",       "+43 664 1234567",  "k.bauer@mail.at")
c_mueller    = create_customer("Stefan Müller",     "+43 676 2345678",  "s.mueller@web.de")
c_audi       = create_customer("Audi Zentrum GmbH", "+43 1 3456789",    "office@audizentrum.at")
c_rossi      = create_customer("Marco Rossi",       "+43 699 4567890",  "m.rossi@gmail.com")
c_bmw        = create_customer("BMW Händler AG",    "+43 1 5678901",    "fleet@bmwhaendler.at")
c_werner     = create_customer("Tobias Werner",     "+43 650 6789012",  "t.werner@outlook.com")
c_schneider  = create_customer("Julia Schneider",   "+43 660 7890123",  "julia.schneider@mail.at")
c_profi      = create_customer("Fahrzeug Profi",    "+43 1 8901234",    "info@fahrzeugprofi.at")
c_zimmermann = create_customer("Hans Zimmermann",   "+43 676 9012345",  "h.zimmermann@gmail.com")
c_hofmann    = create_customer("Petra Hofmann",     "+43 664 0123456",  "p.hofmann@web.at")
c_koenig     = create_customer("Autohaus König",    "+43 1 1234568",    "office@autohauekoenig.at")
c_fischer    = create_customer("Leon Fischer",      "+43 699 2345679",  "l.fischer@mail.com")
c_mercedes   = create_customer("Mercedes Fleet",    "+43 1 3456780",    "fleet@mercedesfleet.at")
c_braun      = create_customer("Nina Braun",        "+43 650 4567891",  "n.braun@gmail.com")
c_rapid      = create_customer("Rapid Logistics",   "+43 1 5678902",    "ops@rapidlogistics.at")
c_krause     = create_customer("David Krause",      "+43 660 6789013",  "d.krause@outlook.com")
c_wolf       = create_customer("Sabine Wolf",       "+43 664 7890124",  "s.wolf@mail.at")
c_engel      = create_customer("Thomas Engel",      "+43 676 8901235",  "t.engel@web.de")
c_stern      = create_customer("Autohaus Stern",    "+43 1 9012346",    "info@autohausstern.at")
c_hartmann   = create_customer("Michael Hartmann",  "+43 699 0123457",  "m.hartmann@gmail.com")
c_vw         = create_customer("VW Fleet GmbH",     "+43 1 1234569",    "fleet@vwfleet.at")
c_richter    = create_customer("Anna Richter",      "+43 650 2345680",  "a.richter@mail.at")
c_vogel      = create_customer("Carsten Vogel",     "+43 660 3456791",  "c.vogel@outlook.com")

# ── Jobs — March 2026 ─────────────────────────────────────────
create_job(date(2026, 3, 3),  None, "Full Wrap",    2800.0, 400.0, 320.0,   0.0, "Completed", customer_id=c_bauer.customer_id)
create_job(date(2026, 3, 6),  None, "Partial Wrap", 1200.0, 200.0, 150.0,   0.0, "Completed", customer_id=c_mueller.customer_id)
create_job(date(2026, 3, 10), None, "Decals",        450.0,  80.0,  40.0,   0.0, "Completed", customer_id=c_audi.customer_id)
create_job(date(2026, 3, 14), None, "Full Wrap",    3200.0, 450.0, 380.0, 200.0, "Completed", customer_id=c_rossi.customer_id)
create_job(date(2026, 3, 18), None, "PPF",          1800.0, 300.0, 200.0,   0.0, "Completed", customer_id=c_bmw.customer_id)
create_job(date(2026, 3, 21), None, "Tint",          380.0,  60.0,  20.0,   0.0, "Completed", customer_id=c_werner.customer_id)
create_job(date(2026, 3, 25), None, "Partial Wrap", 1400.0, 220.0, 180.0,   0.0, "Completed", customer_id=c_schneider.customer_id)
create_job(date(2026, 3, 28), None, "Signage",       900.0, 150.0, 120.0,  80.0, "Completed", customer_id=c_profi.customer_id)

# ── Jobs — April 2026 ────────────────────────────────────────
create_job(date(2026, 4, 2),  None, "Full Wrap",    3100.0, 420.0, 360.0,   0.0, "Completed", customer_id=c_zimmermann.customer_id)
create_job(date(2026, 4, 5),  None, "Decals",        320.0,  50.0,  30.0,   0.0, "Completed", customer_id=c_hofmann.customer_id)
create_job(date(2026, 4, 8),  None, "Full Wrap",    2950.0, 430.0, 340.0, 220.0, "Completed", customer_id=c_koenig.customer_id)
create_job(date(2026, 4, 11), None, "Partial Wrap", 1350.0, 210.0, 160.0,   0.0, "Completed", customer_id=c_fischer.customer_id)
create_job(date(2026, 4, 15), None, "PPF",          4200.0, 600.0, 480.0, 300.0, "Completed", customer_id=c_mercedes.customer_id)
create_job(date(2026, 4, 18), None, "Tint",          420.0,  70.0,  25.0,   0.0, "Completed", customer_id=c_braun.customer_id)
create_job(date(2026, 4, 22), None, "Signage",      1100.0, 180.0, 140.0,  90.0, "Completed", customer_id=c_rapid.customer_id)
create_job(date(2026, 4, 25), None, "Full Wrap",    2750.0, 400.0, 320.0,   0.0, "Completed", customer_id=c_krause.customer_id)
create_job(date(2026, 4, 29), None, "Partial Wrap", 1250.0, 200.0, 155.0,   0.0, "Completed", customer_id=c_wolf.customer_id)

# ── Jobs — May 2026 ──────────────────────────────────────────
create_job(date(2026, 5, 2),  None, "Full Wrap",    3050.0, 440.0, 370.0,   0.0, "Completed",   customer_id=c_engel.customer_id)
create_job(date(2026, 5, 5),  None, "PPF",          2200.0, 320.0, 260.0, 180.0, "Invoiced",    customer_id=c_stern.customer_id)
create_job(date(2026, 5, 7),  None, "Decals",        480.0,  90.0,  45.0,   0.0, "Invoiced",    customer_id=c_hartmann.customer_id)
create_job(date(2026, 5, 9),  None, "Full Wrap",    5800.0, 800.0, 720.0, 400.0, "In Progress", customer_id=c_vw.customer_id)
create_job(date(2026, 5, 12), None, "Partial Wrap", 1450.0, 230.0, 175.0,   0.0, "In Progress", customer_id=c_richter.customer_id)
create_job(date(2026, 5, 13), None, "Tint",          350.0,  55.0,  20.0,   0.0, "Pending",     customer_id=c_vogel.customer_id)

print("Done — seeded 8 foil types, 16 rolls, 23 customers, 23 jobs.")
