import streamlit as st
import pandas as pd
import database as db
import reporting
from datetime import date

st.set_page_config(
    page_title="Milan Designs",
    layout="wide",
)


# ── Auth & undo helpers ───────────────────────────────────────

def render_login():
    _, col, _ = st.columns([2, 1, 2])
    with col:
        st.title("Milan Designs")
        st.subheader("Sign in")
        with st.form("login_form"):
            username = st.selectbox("User", list(st.secrets["users"].keys()))
            password = st.text_input("Password", type="password")
            login_btn = st.form_submit_button("Sign in", use_container_width=True)
        if login_btn:
            cfg = st.secrets["users"].get(username, {})
            if cfg.get("password") == password:
                st.session_state["user"]       = username
                st.session_state["role"]       = cfg["role"]
                st.session_state["undo_stack"] = []
                st.rerun()
            else:
                st.error("Incorrect password.")


def render_sidebar():
    with st.sidebar:
        st.write(f"**{st.session_state['user']}**")
        if st.button("Sign out"):
            st.session_state.clear()
            st.rerun()
        stack = st.session_state.get("undo_stack", [])
        if stack:
            st.divider()
            if st.button(f"↩ Undo: {stack[-1]['label']}"):
                _execute_undo(stack.pop())
                st.rerun()


def push_undo(action: dict):
    stack = st.session_state.setdefault("undo_stack", [])
    stack.append(action)
    if st.session_state["role"] != "admin" and len(stack) > 1:
        stack.pop(0)


def _execute_undo(action):
    t = action["type"]
    if   t == "create_job":       db.delete_job(action["job_id"])
    elif t == "create_customer":  db.delete_customer(action["customer_id"])
    elif t == "create_foil_type": db.delete_foil_type(action["foil_type_id"])
    elif t == "create_foil_roll": db.delete_foil_roll(action["roll_id"])
    elif t == "checkin_roll":     db.update_foil_roll_weight(action["roll_id"], action["prev_weight"])


# ── Startup ───────────────────────────────────────────────────

db.init_db()

if "user" not in st.session_state:
    render_login()
    st.stop()

render_sidebar()
role = st.session_state["role"]
can_delete_foil = role in ("admin", "worker")

st.title("Milan Designs")

TAB_JOBS, TAB_CUSTOMERS, TAB_INV, TAB_CALIB, TAB_CHECKIN, TAB_PBI = st.tabs(
    ["Jobs", "Customers", "Foil Inventory", "Foil Types", "Roll Check-in", "Overview"]
)

# ── Jobs ──────────────────────────────────────────────────────

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
            push_undo({"type": "create_job", "label": f"New job — {j.customer_name}", "job_id": j.job_id})
            st.success(f"Job saved — Profit: € {j.gross_profit:,.2f} | Margin: {j.margin_pct:.1f}%")
            st.rerun()

    st.divider()
    st.subheader("All Jobs")

    jobs = db.read_all_jobs()

    if jobs:
        st.dataframe(pd.DataFrame(jobs), height=400)

        if role == "admin":
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

# ── Customers ─────────────────────────────────────────────────

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
            c = db.create_customer(
                name=new_name,
                phone=new_phone or None,
                email=new_email or None,
            )
            push_undo({"type": "create_customer", "label": f"New customer — {new_name.strip()}", "customer_id": c.customer_id})
            st.success(f"Customer '{new_name.strip()}' saved.")
            st.rerun()

    st.divider()
    st.subheader("All Customers")

    customers = db.read_all_customers()

    if customers:
        st.dataframe(pd.DataFrame(customers), height=300)

        st.divider()
        st.subheader("Edit or Delete a Customer" if role == "admin" else "Customers")

        cust_id_map = {
            f"[{c['Customer_ID']}] {c['Name']}": c["Customer_ID"]
            for c in customers
        }
        sel_cust_label = st.selectbox("Select Customer", list(cust_id_map.keys()))
        sel_cust_id    = cust_id_map[sel_cust_label]
        sel_cust       = next(c for c in customers if c["Customer_ID"] == sel_cust_id)

        if role == "admin":
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

# ── Foil Types ────────────────────────────────────────────────

with TAB_CALIB:
    st.header("Foil Types")
    st.write("Add foil types with their core and unit weights.")

    with st.form("add_ft_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            brand = st.selectbox("Brand", list(db.FOIL_BRANDS.keys()),
                                 help="The manufacturer of the vinyl foil.")
        with c2:
            product_line = st.selectbox("Product Line", db.FOIL_BRANDS[brand],
                                        help="The specific product series within the brand.")

        color_catalog = db.FOIL_COLORS.get(brand, {}).get(product_line, [])
        if color_catalog:
            color_options = {f"{name} ({code})": (code, name) for code, name in color_catalog}
            chosen_label = st.selectbox(
                "Color / Finish",
                list(color_options.keys()),
                help="Select the color from the manufacturer's catalog.",
            )
            code, name = color_options[chosen_label]
            mat_name = f"{brand} {product_line} - {name} ({code})"
        else:
            color_free = st.text_input(
                "Color / Finish",
                placeholder="e.g. Matte Black, Chrome Silver",
                help="No catalog available for this product line — type the color manually.",
            )
            mat_name = f"{brand} {product_line} - {color_free.strip()}" if color_free.strip() else f"{brand} {product_line}"

        st.caption(f"Will be saved as: **{mat_name}**")

        c3, c4 = st.columns(2)
        with c3:
            core_w = st.number_input("Core Weight (g)", min_value=0.0, step=0.5, format="%.1f",
                                     help="Weight of the empty cardboard tube with no foil on it. Weigh the bare core once and record it here.")
        with c4:
            unit_w = st.number_input("Unit Weight (g/m)", min_value=0.01, step=0.1, format="%.2f",
                                     help="How much one metre of this foil weighs in grams. Used to calculate remaining length from a scale reading. Measure a known length and divide weight by metres.")
        ft_notes = st.text_area("Notes", height=60)
        add_ft = st.form_submit_button("Save Foil Type",
                                       help="Saves this foil type so rolls of this material can be added to inventory.")

    if add_ft:
        ft = db.create_foil_type(mat_name, core_w, unit_w, ft_notes or None)
        push_undo({"type": "create_foil_type", "label": f"New foil type — {mat_name}", "foil_type_id": ft.foil_type_id})
        st.success(f"{mat_name} saved.")
        st.rerun()

    st.divider()
    st.subheader("Configured Foil Types")

    foil_types = db.read_all_foil_types()
    if foil_types:
        st.dataframe(pd.DataFrame(foil_types), height=300)

        if can_delete_foil:
            st.divider()
            ft_del_map = {f["Material Name"]: f["foil_type_id"] for f in foil_types}
            del_name = st.selectbox("Select foil type to delete", list(ft_del_map.keys()))
            if st.button("Delete Foil Type",
                         help="Removes this foil type. Blocked if any rolls in inventory still reference it — delete those rolls first."):
                try:
                    db.delete_foil_type(ft_del_map[del_name])
                    st.success(f"{del_name} deleted.")
                    st.rerun()
                except RuntimeError as exc:
                    st.error(str(exc))
    else:
        st.info("No foil types yet.")

# ── Foil Inventory ────────────────────────────────────────────

with TAB_INV:
    st.header("Foil Inventory")

    foil_opts = db.get_foil_type_options()

    if not foil_opts:
        st.warning("No foil types configured. Go to Foil Types first.")
    else:
        with st.form("add_roll_form", clear_on_submit=True):
            st.subheader("Add New Roll")
            ft_map = {f["name"]: f["id"] for f in foil_opts}
            c1, c2 = st.columns(2)
            with c1:
                chosen_ft = st.selectbox("Foil Type", list(ft_map.keys()),
                                         help="The calibrated material this roll is made of. Add new materials in the Foil Types tab.")
            with c2:
                roll_label = st.text_input(
                    "Roll Label *",
                    placeholder=f"e.g. {list(ft_map.keys())[0]} - Red",
                    help="Required. Give this roll a descriptive name, e.g. 'Oracal 651 RA - Red'. Shown in the Roll Check-in dropdown.",
                )
            total_weight = st.number_input("Total Weight (g)", min_value=0.0, step=0.1, format="%.1f",
                                           help="Place the roll on the scale and enter the reading here. Include the cardboard core — the app subtracts the core weight automatically.")
            roll_notes = st.text_area("Notes", height=60)
            add_roll = st.form_submit_button("Add Roll",
                                             help="Adds this roll to inventory and calculates its remaining length based on the foil type calibration.")

        if add_roll:
            if not roll_label.strip():
                st.error("Roll label is required. Give the roll a descriptive name, e.g. 'Oracal 651 RA - Red'.")
            else:
                try:
                    nr = db.create_foil_roll(
                        foil_type_id=ft_map[chosen_ft],
                        current_total_weight=total_weight,
                        roll_label=roll_label.strip(),
                        notes=roll_notes or None,
                    )
                    push_undo({"type": "create_foil_roll", "label": f"New roll — {roll_label.strip()}", "roll_id": nr.roll_id})
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

            if can_delete_foil:
                st.divider()
                del_id = st.selectbox("Select Roll ID to delete", [r["Roll ID"] for r in rolls])
                if st.button("Delete Roll",
                             help="Permanently removes this roll from inventory. Use this when a roll is fully used or discarded."):
                    db.delete_foil_roll(del_id)
                    st.success(f"Roll {del_id} deleted.")
                    st.rerun()
        else:
            st.info("No rolls yet.")

# ── Roll Check-in ─────────────────────────────────────────────

with TAB_CHECKIN:
    st.header("Roll Check-in")
    st.info(
        "After using foil from a roll, place it on the scale and enter the new weight below. "
        "The app recalculates the remaining length and updates the inventory automatically. "
        "Rolls are added and managed in the **Foil Inventory** tab."
    )

    roll_opts = db.get_roll_options()

    if not roll_opts:
        st.warning("No rolls in inventory. Add rolls in the Foil Inventory tab first.")
    else:
        disp_map = {r["display"]: r["id"] for r in roll_opts}

        with st.form("checkin_form", clear_on_submit=True):
            chosen = st.selectbox("Which roll did you use?", list(disp_map.keys()))
            weight = st.number_input("Scale Reading (g)", min_value=0.0, step=0.1, format="%.1f")
            ci_notes = st.text_input("Notes (optional)")
            ci_btn = st.form_submit_button("Confirm Check-in")

        if ci_btn:
            rolls_all = db.read_all_foil_rolls()
            prev = next((r for r in rolls_all if r["Roll ID"] == disp_map[chosen]), None)
            prev_weight = prev["Total Weight (g)"] if prev else None
            try:
                updated = db.update_foil_roll_weight(disp_map[chosen], weight, ci_notes or None)
                nl = updated.calculated_length
                roll_short = chosen.split(" — ")[0]
                if prev_weight is not None:
                    push_undo({"type": "checkin_roll", "label": f"Check-in — {roll_short}",
                               "roll_id": disp_map[chosen], "prev_weight": prev_weight})
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

# ── Overview ──────────────────────────────────────────────────

with TAB_PBI:
    st.header("Overview")

    kpi = reporting.get_kpi_snapshot()

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Jobs",         kpi["job_count"])
    k2.metric("Revenue",      f"€ {kpi['total_revenue']:,.2f}")
    k3.metric("Total Costs",  f"€ {kpi['total_costs']:,.2f}")
    k4.metric("Gross Profit", f"€ {kpi['gross_profit']:,.2f}")
    k5.metric("Margin %",     f"{kpi['margin_pct']:.1f} %")

    weekly  = reporting.build_summary_weekly()
    monthly = reporting.build_summary_monthly()

    st.divider()
    st.subheader("Revenue by Week")
    if not weekly.empty:
        st.bar_chart(weekly.set_index("Week_Label")[["Revenue", "Gross_Profit"]])
    else:
        st.info("No data yet.")

    st.divider()
    st.subheader("Revenue by Month")
    if not monthly.empty:
        st.bar_chart(monthly.set_index("Month_Name")[["Revenue", "Gross_Profit"]])
    else:
        st.info("No data yet.")

    st.divider()
    st.subheader("Weekly Detail")
    if not weekly.empty:
        with st.expander("Show table"):
            st.dataframe(weekly, height=300)
    else:
        st.info("No data yet.")

    st.subheader("Monthly Detail")
    if not monthly.empty:
        with st.expander("Show table"):
            st.dataframe(monthly, height=300)
    else:
        st.info("No data yet.")

    st.divider()
    st.subheader("Export for Power BI")
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
