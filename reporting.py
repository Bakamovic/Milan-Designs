import io
import pandas as pd
from sqlalchemy import text
from database import engine


def _add_date_cols(df, date_col="Date"):
    dt = pd.to_datetime(df[date_col], errors="coerce")
    df["Year"]       = dt.dt.year.astype("Int64")
    df["Quarter"]    = dt.dt.quarter.astype("Int64")
    df["Month_Num"]  = dt.dt.month.astype("Int64")
    df["Month_Name"] = dt.dt.strftime("%B")
    df["ISO_Week"]   = dt.dt.isocalendar().week.astype("Int64")
    df["Week_Label"] = df["Year"].astype(str) + "-W" + df["ISO_Week"].astype(str).str.zfill(2)
    return df


def build_fact_jobs():
    sql = """
        SELECT j.job_id, j.date AS Date, j.customer_name AS Customer,
               j.customer_id AS Customer_ID,
               c.phone AS Customer_Phone, c.email AS Customer_Email,
               j.job_type AS Job_Type, j.status AS Status,
               j.charge AS Charge, j.labour_cost AS Labour_Cost,
               j.material_cost AS Material_Cost,
               j.subcontractor_cost AS Subcontractor_Cost,
               j.notes AS Notes
        FROM jobs j
        LEFT JOIN customers c ON j.customer_id = c.customer_id
        ORDER BY j.date ASC
    """
    with engine.connect() as conn:
        df = pd.read_sql(text(sql), conn)
    df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")

    if df.empty:
        return df

    df["Total_Cost"]   = (df["Labour_Cost"] + df["Material_Cost"] + df["Subcontractor_Cost"]).round(2)
    df["Gross_Profit"] = (df["Charge"] - df["Total_Cost"]).round(2)
    df["Margin_Pct"]   = (df["Gross_Profit"] / df["Charge"].replace(0, float("nan")) * 100).round(2)
    df = _add_date_cols(df, "Date")
    return df


def build_summary_weekly():
    fact = build_fact_jobs()
    if fact.empty:
        return pd.DataFrame()

    grp = (
        fact.groupby(["Year", "ISO_Week", "Week_Label"], dropna=False)
        .agg(
            Job_Count           =("job_id",            "count"),
            Revenue             =("Charge",             "sum"),
            Total_Costs         =("Total_Cost",          "sum"),
            Labour_Costs        =("Labour_Cost",         "sum"),
            Material_Costs      =("Material_Cost",       "sum"),
            Subcontractor_Costs =("Subcontractor_Cost",  "sum"),
        )
        .reset_index()
    )
    grp["Gross_Profit"] = (grp["Revenue"] - grp["Total_Costs"]).round(2)
    grp["Margin_Pct"]   = (grp["Gross_Profit"] / grp["Revenue"].replace(0, float("nan")) * 100).round(2)
    return grp.sort_values(["Year", "ISO_Week"]).reset_index(drop=True)


def build_summary_monthly():
    fact = build_fact_jobs()
    if fact.empty:
        return pd.DataFrame()

    grp = (
        fact.groupby(["Year", "Month_Num", "Month_Name"], dropna=False)
        .agg(
            Job_Count           =("job_id",            "count"),
            Revenue             =("Charge",             "sum"),
            Total_Costs         =("Total_Cost",          "sum"),
            Labour_Costs        =("Labour_Cost",         "sum"),
            Material_Costs      =("Material_Cost",       "sum"),
            Subcontractor_Costs =("Subcontractor_Cost",  "sum"),
        )
        .reset_index()
    )
    grp["Gross_Profit"] = (grp["Revenue"] - grp["Total_Costs"]).round(2)
    grp["Margin_Pct"]   = (grp["Gross_Profit"] / grp["Revenue"].replace(0, float("nan")) * 100).round(2)
    return grp.sort_values(["Year", "Month_Num"]).reset_index(drop=True)


def build_dim_foil_inventory():
    sql = """
        SELECT fr.roll_id AS Roll_ID, fr.roll_label AS Roll_Label,
               ft.material_name AS Material, ft.core_weight AS Core_Weight_g,
               ft.unit_weight AS Unit_Weight_g_per_m,
               fr.current_total_weight AS Total_Weight_g,
               fr.calculated_length AS Calculated_Length_m,
               fr.last_checked AS Last_Checked,
               CASE WHEN fr.calculated_length < 5.0 THEN 1 ELSE 0 END AS Low_Stock_Flag
        FROM foil_rolls fr
        JOIN foil_types ft ON fr.foil_type_id = ft.foil_type_id
        ORDER BY fr.roll_id ASC
    """
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn, parse_dates=["Last_Checked"])


def get_kpi_snapshot():
    fact = build_fact_jobs()
    if fact.empty:
        return {
            "job_count": 0, "total_revenue": 0.0, "total_costs": 0.0,
            "gross_profit": 0.0, "margin_pct": 0.0, "avg_job_value": 0.0,
        }

    total_revenue = float(fact["Charge"].sum())
    total_costs   = float(fact["Total_Cost"].sum())
    gross_profit  = round(total_revenue - total_costs, 2)
    job_count     = len(fact)

    return {
        "job_count":     job_count,
        "total_revenue": round(total_revenue, 2),
        "total_costs":   round(total_costs, 2),
        "gross_profit":  gross_profit,
        "margin_pct":    round(gross_profit / total_revenue * 100, 2) if total_revenue else 0.0,
        "avg_job_value": round(total_revenue / job_count, 2) if job_count else 0.0,
    }


def export_to_excel():
    sheets = {
        "fact_jobs":          build_fact_jobs(),
        "dim_foil_inventory": build_dim_foil_inventory(),
        "summary_weekly":     build_summary_weekly(),
        "summary_monthly":    build_summary_monthly(),
    }

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl", date_format="YYYY-MM-DD") as writer:
        for sheet_name, df in sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    return buffer.getvalue()