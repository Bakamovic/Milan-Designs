import streamlit as st
import pandas as pd
import database as db
import reporting
from datetime import date

st.set_page_config(
    page_title="Milan Designs",
    layout="wide",
)

db.init_db()

st.title("Milan Designs")

TAB_JOBS, TAB_CUSTOMERS, TAB_INV, TAB_CALIB, TAB_CHECKIN, TAB_PBI = st.tabs(
    ["Jobs", "Customers", "Foil Inventory", "Calibration", "Roll Check-in", "Power BI Export"]
)

with TAB_JOBS:
    st.header("Jobs")

    customer_opts = db.get_customer_options()
    cust_map = {c["display"]: c["id"] for c in customer_opts}

    with st.form("new_job_form", clear_on_submit=True):
        st.subheader("New Job")

        col1, col2, col3 = st.columns(3)
        with col1:
            job_date = st.date_input("Date", value=date.today(), format="DD/MM/YYYY")
        with col2:
            if customer_opts:
                chosen_cust_name = st.selectbox("Customer", list(cust_map.keys()))
            else:
                st.warning("No customers yet — add one in the Customers tab first.")
                chosen_cust_name = None
        with col3:
            job_type = st.selectbox("Job Type", db.JOB_TYPES)

        col4, col5, col6, col7, col8 = st.columns(5)
        with col4:
            charge = st.number_input("Charge (€)", min_value=0.0, step=0.01, format="%.2f")
        with col5:
            labour_cost = st.number_input("Labour (€)", min_value=0.0, step=0.01, format="%.2f")
        with col6:
            material_cost = st.number_input("Material (€)", min_value=0.0, step=0.01, format="%.2f")
        with col7:
            subcontractor_cost = st.number_input("Subcontractor (€)", min_value=0.0, step=0.01, format="%.2f")
        with col8:
            status = st.selectbox("Status", db.STATUS_OPTIONS)

        notes = st.text_area("Notes", height=70)
        submitted = st.form_submit_button("Save Job")

    if submitted:
        if not customer_opts or chosen_cust_name is None:
            st.error("Select a customer. Add customers in the Customers tab first.")
        else:
            j = db.create_job(
                job_date=job_date,
                customer_name=None,
                job_type=job_type,
                charge=charge,
                labour_cost=labour_cost,
                material_cost=material_cost,
                subcontractor_cost=subcontractor_cost,
                status=status,
                notes=notes or None,
                customer_id=cust_map[chosen_cust_name],
            )
            st.success(f"Job saved — Profit: € {j.gross_profit:,.2f} | Margin: {j.margin_pct:.1f}%")
            st.rerun()

    st.divider()
    st.subheader("All Jobs")

    jobs = db.read_all_jobs()

    if jobs:
        st.dataframe(pd.DataFrame(jobs), height=400)

        st.divider()
        st.subheader("Edit or Delete a Job")

        job_ids = [j["Job_ID"] for j in jobs]
        sel_id = st.selectbox("Select Job ID", job_ids)
        sel = next(j for j in jobs if j["Job_ID"] == sel_id)

        with st.expander("Edit selected job"):
            with st.form("edit_job_form"):
                c1, c2, c3 = st.columns(3)
                with c1:
                    e_date = st.date_input("Date", value=sel["Date"], format="DD/MM/YYYY")
                with c2:
                    if customer_opts:
                        cust_names = list(cust_map.keys())
                        current_cust_id = sel.get("Customer_ID")
                        if current_cust_id is not None:
                            current_cust_name = next(
                                (c["display"] for c in customer_opts if c["id"] == current_cust_id),
                                cust_names[0],
                            )
                            e_cust_idx = cust_names.index(current_cust_name)
                        else:
                            e_cust_idx = 0
                        e_chosen_cust = st.selectbox("Customer", cust_names, index=e_cust_idx)
                    else:
                        e_chosen_cust = None
                        st.text_input("Customer (legacy)", value=sel["Customer"], disabled=True)
                with c3:
                    e_type = st.selectbox("Job Type", db.JOB_TYPES, index=db.JOB_TYPES.index(sel["Job_Type"]))

                c4, c5, c6, c7, c8 = st.columns(5)
                with c4:
                    e_charge = st.number_input("Charge (€)", value=float(sel["Charge"]), step=0.01, format="%.2f")
                with c5:
                    e_labour = st.number_input("Labour (€)", value=float(sel["Labour_Cost"]), step=0.01, format="%.2f")
                with c6:
                    e_mat = st.number_input("Material (€)", value=float(sel["Material_Cost"]), step=0.01, format="%.2f")
                with c7:
                    e_sub = st.number_input("Subcontractor (€)", value=float(sel["Subcontractor_Cost"]), step=0.01, format="%.2f")
                with c8:
                    e_status = st.selectbox("Status", db.STATUS_OPTIONS, index=db.STATUS_OPTIONS.index(sel["Status"]))

                e_notes = st.text_area("Notes", value=sel["Notes"] or "")
                save_edit = st.form_submit_button("Save Changes")

            if save_edit:
                db.update_job(
                    job_id=sel_id,
                    job_date=e_date,
                    customer_id=cust_map[e_chosen_cust] if e_chosen_cust else None,
                    job_type=e_type,
                    charge=e_charge,
                    labour_cost=e_labour,
                    material_cost=e_mat,
                    subcontractor_cost=e_sub,
                    status=e_status,
                    notes=e_notes or None,
                )
                st.success("Job updated.")
                st.rerun()

        if st.button("Delete Job"):
            db.delete_job(sel_id)
            st.success(f"Job {sel_id} deleted.")
            st.rerun()
    else:
        st.info("No jobs yet.")

with TAB_CUSTOMERS:
    st.header("Customers")

    with st.form("new_customer_form", clear_on_submit=True):
        st.subheader("Add New Customer")
        nc1, nc2, nc3 = st.columns(3)
        with nc1:
            new_name  = st.text_input("Name *")
        with nc2:
            new_phone = st.text_input("Phone", placeholder="e.g. +43 664 1234567")
        with nc3:
            new_email = st.text_input("Email", placeholder="e.g. customer@example.com")
        add_cust = st.form_submit_button("Save Customer")

    if add_cust:
        if not new_name.strip():
            st.error("Customer name is required.")
        else:
            db.create_customer(
                name=new_name,
                phone=new_phone or None,
                email=new_email or None,
            )
            st.success(f"Customer '{new_name.strip()}' saved.")
            st.rerun()

    st.divider()
    st.subheader("All Customers")

    customers = db.read_all_customers()

    if customers:
        st.dataframe(pd.DataFrame(customers), height=300)

        st.divider()
        st.subheader("Edit or Delete a Customer")

        cust_id_map = {
            f"[{c['Customer_ID']}] {c['Name']}": c["Customer_ID"]
            for c in customers
        }
        sel_cust_label = st.selectbox("Select Customer", list(cust_id_map.keys()))
        sel_cust_id    = cust_id_map[sel_cust_label]
        sel_cust       = next(c for c in customers if c["Customer_ID"] == sel_cust_id)

        with st.expander("Edit selected customer"):
            with st.form("edit_customer_form"):
                ec1, ec2, ec3 = st.columns(3)
                with ec1:
                    e_name  = st.text_input("Name *", value=sel_cust["Name"])
                with ec2:
                    e_phone = st.text_input("Phone",  value=sel_cust["Phone"])
                with ec3:
                    e_email = st.text_input("Email",  value=sel_cust["Email"])
                save_cust_edit = st.form_submit_button("Save Changes")

            if save_cust_edit:
                if not e_name.strip():
                    st.error("Customer name is required.")
                else:
                    db.update_customer(
                        customer_id=sel_cust_id,
                        name=e_name,
                        phone=e_phone,
                        email=e_email,
                    )
                    st.success("Customer updated.")
                    st.rerun()

        if st.button("Delete Customer"):
            try:
                db.delete_customer(sel_cust_id)
                st.success("Customer deleted.")
                st.rerun()
            except RuntimeError as exc:
                st.error(str(exc))

        st.divider()
        st.subheader("Customer Profile")

        prof_label = st.selectbox(
            "Select customer to view profile",
            list(cust_id_map.keys()),
            key="profile_selectbox",
        )
        prof_id = cust_id_map[prof_label]
        profile = db.get_customer_profile(prof_id)

        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Total Jobs",  profile["job_count"])
        col_b.metric("Total Spend", f"€ {profile['total_spend']:,.2f}")
        with col_c:
            st.caption("Phone")
            st.write(profile["phone"] or "—")
            st.caption("Email")
            st.write(profile["email"] or "—")

        if profile["jobs"]:
            st.dataframe(pd.DataFrame(profile["jobs"]), height=350)
        else:
            st.info("No jobs linked to this customer yet.")
    else:
        st.info("No customers yet. Add one above.")

with TAB_CALIB:
    st.header("Calibration")
    st.write("Add foil types with their core and unit weights.")

    with st.form("add_ft_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            brand = st.selectbox("Brand", list(db.FOIL_BRANDS.keys()))
        with c2:
            product_line = st.selectbox("Product Line", db.FOIL_BRANDS[brand])

        mat_name = f"{brand} {product_line}"
        st.write(f"Material Name: **{mat_name}**")

        c3, c4 = st.columns(2)
        with c3:
            core_w = st.number_input("Core Weight (g)", min_value=0.0, step=0.5, format="%.1f")
        with c4:
            unit_w = st.number_input("Unit Weight (g/m)", min_value=0.01, step=0.1, format="%.2f")
        ft_notes = st.text_area("Notes", height=60)
        add_ft = st.form_submit_button("Save Foil Type")

    if add_ft:
        db.create_foil_type(mat_name, core_w, unit_w, ft_notes or None)
        st.success(f"{mat_name} saved.")
        st.rerun()

    st.divider()
    st.subheader("Configured Foil Types")

    foil_types = db.read_all_foil_types()
    if foil_types:
        st.dataframe(pd.DataFrame(foil_types), height=300)

        st.divider()
        ft_del_map = {f["Material Name"]: f["foil_type_id"] for f in foil_types}
        del_name = st.selectbox("Select foil type to delete", list(ft_del_map.keys()))
        if st.button("Delete Foil Type"):
            try:
                db.delete_foil_type(ft_del_map[del_name])
                st.success(f"{del_name} deleted.")
                st.rerun()
            except RuntimeError as exc:
                st.error(str(exc))
    else:
        st.info("No foil types yet.")

with TAB_INV:
    st.header("Foil Inventory")

    foil_opts = db.get_foil_type_options()

    if not foil_opts:
        st.warning("No foil types configured. Go to Calibration first.")
    else:
        with st.form("add_roll_form", clear_on_submit=True):
            st.subheader("Add New Roll")
            ft_map = {f["name"]: f["id"] for f in foil_opts}
            c1, c2 = st.columns(2)
            with c1:
                chosen_ft = st.selectbox("Foil Type", list(ft_map.keys()))
            with c2:
                roll_label = st.text_input("Roll Label", placeholder="e.g. Roll A-01")
            total_weight = st.number_input("Total Weight (g)", min_value=0.0, step=0.1, format="%.1f")
            roll_notes = st.text_area("Notes", height=60)
            add_roll = st.form_submit_button("Add Roll")

        if add_roll:
            try:
                nr = db.create_foil_roll(
                    foil_type_id=ft_map[chosen_ft],
                    current_total_weight=total_weight,
                    roll_label=roll_label or None,
                    notes=roll_notes or None,
                )
                st.success(f"Roll added — {nr.calculated_length:.2f} m remaining.")
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))

        st.divider()
        st.subheader("All Rolls")

        rolls = db.read_all_foil_rolls()
        if rolls:
            low = [r for r in rolls if r["Low Stock"]]
            if low:
                st.warning(f"{len(low)} roll(s) below 5 metres: " + ", ".join(r["Label"] for r in low))

            st.dataframe(pd.DataFrame(rolls).drop(columns=["Low Stock"]), height=400)

            st.divider()
            del_id = st.selectbox("Select Roll ID to delete", [r["Roll ID"] for r in rolls])
            if st.button("Delete Roll"):
                db.delete_foil_roll(del_id)
                st.success(f"Roll {del_id} deleted.")
                st.rerun()
        else:
            st.info("No rolls yet.")

with TAB_CHECKIN:
    st.header("Roll Check-in")
    st.write("Place a roll on the scale, enter the weight and the app recalculates the remaining length.")

    roll_opts = db.get_roll_options()

    if not roll_opts:
        st.warning("No rolls in inventory. Add rolls in the Foil Inventory tab first.")
    else:
        disp_map = {r["display"]: r["id"] for r in roll_opts}

        with st.form("checkin_form", clear_on_submit=True):
            chosen = st.selectbox("Select Roll", list(disp_map.keys()))
            weight = st.number_input("Scale Reading (g)", min_value=0.0, step=0.1, format="%.1f")
            ci_notes = st.text_input("Notes (optional)")
            ci_btn = st.form_submit_button("Confirm Check-in")

        if ci_btn:
            try:
                updated = db.update_foil_roll_weight(disp_map[chosen], weight, ci_notes or None)
                nl = updated.calculated_length
                if nl < 5:
                    st.warning(f"Saved — but low stock: {nl:.2f} m remaining. Reorder soon.")
                else:
                    st.success(f"Updated — {nl:.2f} m remaining.")
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))

        st.divider()
        st.subheader("Current Stock")
        rolls = db.read_all_foil_rolls()
        if rolls:
            st.dataframe(
                pd.DataFrame(rolls)[["Roll ID", "Label", "Material", "Calculated Length (m)", "Last Checked"]],
                height=300,
            )
with TAB_PBI:
    st.header("Power BI Export")

    kpi = reporting.get_kpi_snapshot()

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Jobs",          kpi["job_count"])
    k2.metric("Revenue",       f"€ {kpi['total_revenue']:,.2f}")
    k3.metric("Total Costs",   f"€ {kpi['total_costs']:,.2f}")
    k4.metric("Gross Profit",  f"€ {kpi['gross_profit']:,.2f}")
    k5.metric("Margin %",      f"{kpi['margin_pct']:.1f} %")

    st.divider()
    st.subheader("Weekly Summary")
    weekly = reporting.build_summary_weekly()
    if not weekly.empty:
        st.dataframe(weekly, height=300)
    else:
        st.info("No data yet.")

    st.divider()
    st.subheader("Monthly Summary")
    monthly = reporting.build_summary_monthly()
    if not monthly.empty:
        st.dataframe(monthly, height=300)
    else:
        st.info("No data yet.")

    st.divider()
    st.subheader("Download for Power BI")
    if st.button("Generate Export File"):
        with st.spinner("Building workbook..."):
            try:
                st.session_state["pbi_bytes"] = reporting.export_to_excel()
                st.success("Ready to download.")
            except Exception as exc:
                st.error(f"Export failed: {exc}")

    if "pbi_bytes" in st.session_state:
        from datetime import datetime
        filename = f"milan_designs_{datetime.today().strftime('%Y%m%d')}.xlsx"
        st.download_button(
            label="Download .xlsx",
            data=st.session_state["pbi_bytes"],
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )            