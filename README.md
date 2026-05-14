# Milan Designs — Shop Management App

## The Problem

A vehicle wrap and sign shop was tracking jobs, materials and costs manually —
spreadsheets, paper notes, no structure. The owner had no clear picture of which
jobs were profitable, how much foil stock was left, or how the business was
performing week to week.

## What I Built

A custom internal business app from scratch using Python, Streamlit and SQLite.

### Job Tracking
Every job is logged with the customer name, job type, what was charged, and a
full cost breakdown split into labour, materials and subcontractor costs.
Profit and margin are calculated automatically on every entry.

### Foil Inventory
Vinyl wrap rolls are tracked by brand and product line — Oracal, 3M, Avery,
Hexis and Arlon. Because a roll loses weight as it is used, the app uses a
weight-to-length formula to calculate exactly how many metres are remaining
from a simple scale reading. Any roll below 5 metres is flagged as low stock.

### Power BI Export
All data exports to a structured Excel workbook that feeds directly into
Power BI for weekly and monthly reporting on revenue, costs, gross profit
and margin.

## Why I Was the Right Person

I am a muscle car enthusiast — I understand the world of wraps, the materials
involved, the difference between a full wrap and a partial, what foil brands
matter. I knew someone at the company, identified the problem firsthand, spoke
to the owner, and built a solution tailored to how the shop actually works.

## Tech Stack

- Python 3.12
- Streamlit
- SQLAlchemy
- SQLite
- Pandas
- Power BI

## Roadmap

The following features are planned following an upcoming meeting with the owner:

- UI redesign based on shop branding and owner feedback
- Additional job tracking fields (vehicle details, registration, colour)
- Customer database — store returning customers and job history
- Invoice generation — export a PDF invoice per job
- Material cost automation — link foil usage directly to job cost
- Power BI dashboard refinement based on real usage data

## How to Run

```bash
python -m venv venv
venv\Scripts\activate
pip install streamlit sqlalchemy pandas openpyxl
streamlit run app.py
```