# Customers

## What It Does

The Customers tab manages the shop's customer records. Each customer has a name, phone number, and email. Once added, customers can be selected when logging a job. The tab also shows a profile for each customer with their full job history and total spend.

---

## Why It Exists

Before the customer database, job records stored customer names as plain text — the same person could appear as "Milan Petrović", "Milan P.", or "Milan" across different jobs, making it impossible to reliably group their history or calculate total spend. The Customers tab links jobs to real records, which feeds accurate customer data into reporting and the eventual invoice feature.

---

## How It Works

### Adding a Customer

Fill in the form at the top of the Customers tab:

| Field | Required | Notes |
|-------|----------|-------|
| Name | Yes | Whitespace stripped |
| Phone | No | Free text |
| Email | No | Free text |

On save the customer is immediately available in the Jobs dropdown.

### Viewing Customers

All customers display in a scrollable table showing name, phone, and email.

### Editing a Customer

Select a customer by name from the dropdown. An expander reveals the pre-filled edit form. Name, phone, and email can all be changed. **Admin only.**

### Deleting a Customer

Select a customer and click Delete. **Admin only.** Deletion is blocked if any jobs are currently linked to that customer — you must reassign or delete those jobs first. This prevents orphaned job records.

### Customer Profile

Select a customer from the profile dropdown at the bottom of the tab to see:

- **Total Jobs** — count of all linked jobs
- **Total Spend** — sum of all `charge` values across their jobs
- **Phone and Email** — contact details
- **Job History** — a table of all jobs, with date, type, status, charge, and profit

All roles can view customer profiles.

---

## Key Code Locations

| What | File |
|------|------|
| `Customer` model | `database.py` |
| `create_customer()` | `database.py` |
| `update_customer()` | `database.py` |
| `delete_customer()` | `database.py` |
| `get_customer_profile()` | `database.py` |
| UI — Customers tab | `app.py` |

---

## Limitations & Known Issues

- **No merge.** If the same customer was entered twice under slightly different names, there is no way to merge their records — jobs must be manually reassigned.
- **Legacy jobs.** Jobs created before the customer database existed have `customer_id = NULL` and retain their original freehand name. They do not appear in any customer's profile.
- **No contact validation.** Phone and email are free text — the app does not validate format.

---

## Related Features

- [Jobs](jobs.md) — customers must be added here before they can be selected on a job
- [Power BI Export](overview.md) — customer phone and email are joined into `fact_jobs` for reporting
- [Roadmap](../roadmap.md) — invoice generation will use customer contact details
