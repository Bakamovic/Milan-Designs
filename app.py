import streamlit as st
import pandas as pd
import database as db
from datetime import date

st.set_page_config(
    page_title="Milan Designs",
    layout="wide",
)

db.init_db()

st.title("Milan Designs")

TAB_JOBS, TAB_INV, TAB_CALIB, TAB_CHECKIN = st.tabs(["Jobs", "Foil Inventory", "Calibration", "Roll Check-in"])

with TAB_JOBS:
    st.header("Jobs")

    with st.form("new_job_form", clear_on_submit=True):
        st.subheader("New Job")

        col1, col2, col3 = st.columns(3)
        with col1:
            job_date = st.date_input("Date", value=date.today(), format="DD/MM/YYYY")
        with col2:
            customer_name = st.text_input("Customer Name")
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
        if not customer_name.strip():
            st.error("Customer name is required.")
        else:
            j = db.create_job(
                job_date=job_date,
                customer_name=customer_name,
                job_type=job_type,
                charge=charge,
                labour_cost=labour_cost,
                material_cost=material_cost,
                subcontractor_cost=subcontractor_cost,
                status=status,
                notes=notes or None,
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
                    e_customer = st.text_input("Customer", value=sel["Customer"])
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
                    customer_name=e_customer,
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