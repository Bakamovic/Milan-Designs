# Roadmap

Features planned for future development, ordered by priority.

> The app is a data entry and management tool. New analytics or charting features should not be added here — analysis lives in Power BI.

---

## 1. Customer Database *(highest priority)*

**Problem:** Customer name is a free-text field. The same customer can be spelled differently across jobs, and there is no way to see all jobs for a given customer in one place.

**What to build:**
- A `customers` table with name, phone, and email
- A `customer_id` foreign key on the `jobs` table
- A Customers tab (or section within Jobs) to create and manage customers
- On job creation, select a customer from the list instead of typing a name
- A customer profile view showing all their jobs and total spend

**Notes:**
- Existing jobs will need to be migrated — either linked to new customer records or left with a null `customer_id` (both approaches are valid)
- This is a prerequisite for vehicle details (feature #3) and invoice generation (feature #4)

---

## 2. Foil Usage Linked to Jobs

**Problem:** The Material (€) field on a job is entered manually with no connection to which rolls were actually used. Roll inventory is not automatically deducted when a job is completed.

**What to build:**
- A way to select one or more rolls when logging a job
- Record how much weight (or length) was consumed from each roll
- Auto-calculate the material cost from actual roll usage (using the calibrated unit weight and a cost-per-metre rate)
- Deduct the consumed weight from the roll on job save

**Notes:**
- Requires either a junction table (`job_foil_usage`) or a direct link from rolls to jobs
- Cost-per-metre rate would need to be added to `FoilType` or derived from a purchase price field
- This is the biggest operational gap currently — material costs are the least accurate field in the data

---

## 3. Vehicle Details on Jobs

**Problem:** The shop wraps specific vehicles but the app doesn't capture any vehicle information.

**What to build:**
- Add `vehicle_make`, `vehicle_model`, `vehicle_year`, `registration`, and `colour` fields to the `jobs` table
- Display these in the jobs table and export
- If a customer database exists (feature #1), optionally store the vehicle on the customer record so it pre-fills on new jobs

---

## 4. Invoice PDF Generation

**Problem:** Invoices are created manually outside the app after a job is logged.

**What to build:**
- A "Generate Invoice" button on any completed job
- PDF output with Milan Designs branding, job details, cost breakdown, and total
- Option to download or save the PDF

**Dependencies:** A customer database (feature #1) is needed for customer contact details on the invoice.

---

## 5. Mobile-Friendly UI

**Problem:** Streamlit's default layout is desktop-first. Logging a job or checking inventory from a phone at the shop is awkward.

**What to build:**
- Responsive column layouts that stack on small screens
- Larger tap targets on form inputs
- Possibly a simplified "quick log" view for mobile job entry

**Notes:** This can be approached incrementally — fixing the most-used forms (new job, roll check-in) first without a full redesign.

---

## Completed

| Feature | Notes |
|---------|-------|
| Job tracking with profit/margin | Live |
| Foil inventory (weight-based) | Live |
| Foil type calibration | Live |
| Roll check-in workflow | Live |
| Power BI Excel export | Live |
