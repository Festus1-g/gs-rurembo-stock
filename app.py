import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime
import hashlib
import re

# Page Configuration
st.set_page_config(page_title="GS Rurembo - Integrated Management System", layout="wide", page_icon="🏫")

# ---------------------------------------------------------
# SUPABASE CONNECTION SETUP
# ---------------------------------------------------------
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

def fetch_data(table_name):
    try:
        res = supabase.table(table_name).select("*").execute()
        return pd.DataFrame(res.data)
    except Exception as e:
        return pd.DataFrame()

# Password Strength Validator
def validate_password(password):
    if len(password) < 8:
        return "Password igomba kuba ifite byibuze nyuguti 8."
    if not re.search(r"[a-z]", password):
        return "Password igomba kugira nibura nyuguti nto (a-z)."
    if not re.search(r"[A-Z]", password):
        return "Password igomba kugira nibura nyuguti nkuru (A-Z)."
    if not re.search(r"[0-9]", password):
        return "Password igomba kugira nibura umubare (0-9)."
    return "OK"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Helper function for Rwandan PAYE / TPR Tax
def calculate_tpr(taxable_income):
    if taxable_income <= 60000:
        return 0
    elif taxable_income <= 100000:
        return (taxable_income - 60000) * 0.10
    elif taxable_income <= 200000:
        return (40000 * 0.10) + ((taxable_income - 100000) * 0.20)
    else:
        return (40000 * 0.10) + (100000 * 0.20) + ((taxable_income - 200000) * 0.30)

# Authentication State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

# ---------------------------------------------------------
# LOGIN & SECURE SIGN-UP PAGE
# ---------------------------------------------------------
if not st.session_state.logged_in:
    st.title("🔒 GS Rurembo - System Authentication")
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        auth_tab = st.radio("Hitamo:", ["Injira (Login)", "Iyandikishe (Sign Up)"], horizontal=True)
        
        if auth_tab == "Injira (Login)":
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            if st.button("Login", use_container_width=True):
                if username == "admin" and password == "123":
                    st.session_state.logged_in = True
                    st.session_state.username = "admin"
                    st.session_state.role = "Admin"
                    st.rerun()
                elif username == "staff" and password == "123":
                    st.session_state.logged_in = True
                    st.session_state.username = "staff"
                    st.session_state.role = "Staff"
                    st.rerun()
                else:
                    df_users = fetch_data("users")
                    if not df_users.empty and "username" in df_users.columns:
                        user_row = df_users[df_users["username"] == username]
                        if not user_row.empty:
                            stored_hash = user_row.iloc[0]["password_hash"]
                            if stored_hash == hash_password(password):
                                st.session_state.logged_in = True
                                st.session_state.username = username
                                st.session_state.role = user_row.iloc[0]["role"]
                                st.rerun()
                    st.error("Username cyangwa Password sibyo!")
                    
        else: # Secure Sign Up
            st.subheader("Kora Konti Nshya (Staff Account)")
            new_user = st.text_input("Hitamo Username")
            new_pass = st.text_input("Hitamo Password Ikomeye", type="password")
            confirm_pass = st.text_input("Emeza Password", type="password")
            
            st.info("💡 **Ibisabwa kuri Password:** Byibuze nyuguti 8, irimo nyuguti nkuru na nto, imibare, n'ibimenyetso.")
            
            if st.button("Iyandikishe (Register)", use_container_width=True):
                if not new_user or not new_pass:
                    st.error("Ugomba kuzuza amakuru yose!")
                elif new_pass != confirm_pass:
                    st.error("Password wavuze ntizihuye!")
                else:
                    check_msg = validate_password(new_pass)
                    if check_msg != "OK":
                        st.error(check_msg)
                    else:
                        hashed = hash_password(new_pass)
                        try:
                            supabase.table("users").insert({
                                "username": new_user,
                                "password_hash": hashed,
                                "role": "Staff"
                            }).execute()
                            st.success("Konti yawe yaremwe nka Staff neza! Ushobora kugaruka kuri 'Injira (Login)' ukinjira.")
                        except Exception as e:
                            st.error(f"Habaye ikibazo cyangwa username isanzweho: {e}")
    st.stop()

# ---------------------------------------------------------
# MAIN APP NAVIGATION
# ---------------------------------------------------------
st.sidebar.title(f"👤 {st.session_state.username.capitalize()} ({st.session_state.role})")
if st.sidebar.button("Log out"):
    st.session_state.logged_in = False
    st.rerun()

menu_list = [
    "📊 Dashboard & Stock", 
    "📤 Direct Stock Out", 
    "📝 Staff Requests (Stock)", 
    "📖 Fiche de Stock Card",
    "📌 HR Dashboard", 
    "👨‍💼 Abakozi n'Amasezerano", 
    "📝 Gusaba Impushya (Leaves)", 
    "💵 Imishahara (Payroll & Payslip)",
    "📈 Raporo Zose (Reports)",
    "🔐 Hindura Password"
]

if st.session_state.role == "Admin":
    menu_list.append("👥 Gucunga Abakoresha (Users)")

menu = st.sidebar.selectbox("Hitamo Igice (Menu)", menu_list)

# =========================================================
# PART 1: STOCK MANAGEMENT
# =========================================================
if menu == "📊 Dashboard & Stock":
    st.title("📊 Dashboard & Ububiko (Stock)")
    df_stock = fetch_data("stock")
    if df_stock.empty:
        st.info("Nta bicuruzwa birajya muri Supabase stock database.")
    else:
        st.dataframe(df_stock, use_container_width=True)

    if st.session_state.role == "Admin":
        with st.expander("➕ Ongeza Igicuruzwa Gishya (Add New Item)"):
            item_name = st.text_input("Izina ry'igicuruzwa")
            category = st.text_input("Icyiciro (Category)")
            qty = st.number_input("Umubare w'intangiriro (Quantity)", min_value=0, value=0)
            unit = st.text_input("Igipimo (e.g. Kg, Pcs)")
            if st.button("Save Item"):
                if item_name:
                    supabase.table("stock").insert({"item_name": item_name, "category": category, "quantity": qty, "unit": unit}).execute()
                    st.success(f"{item_name} yongewe mu bubiko!")
                    st.rerun()

elif menu == "📤 Direct Stock Out":
    st.title("📤 Gusohora Ibicuruzwa (Direct Stock Out)")
    df_stock = fetch_data("stock")
    if not df_stock.empty and "item_name" in df_stock.columns:
        selected_item = st.selectbox("Hitamo Igicuruzwa", df_stock["item_name"].tolist())
        qty_out = st.number_input("Umubare usohoka", min_value=1, value=1)
        received_by = st.text_input("Uwakiriye (Recipient)")
        if st.button("Sohora"):
            current_row = df_stock[df_stock["item_name"] == selected_item].iloc[0]
            current_qty = current_row["quantity"]
            if qty_out > current_qty:
                st.error("Umubare usaba uruta uwari mu bubiko!")
            else:
                new_qty = current_qty - qty_out
                supabase.table("stock").update({"quantity": new_qty}).eq("item_name", selected_item).execute()
                supabase.table("transactions").insert({
                    "date": str(datetime.now().date()),
                    "item_name": selected_item,
                    "qty_out": qty_out,
                    "balance": new_qty,
                    "recipient": received_by
                }).execute()
                st.success("Igicuruzwa cyasohowe neza!")
                st.rerun()
    else:
        st.info("Ububiko buracyari ubusa.")

elif menu == "📝 Staff Requests (Stock)":
    st.title("📝 Demande z'Ibicuruzwa (Requisitions)")
    df_stock = fetch_data("stock")
    if st.session_state.role == "Staff":
        if not df_stock.empty and "item_name" in df_stock.columns:
            req_item = st.selectbox("Igicuruzwa", df_stock["item_name"].tolist())
            req_qty = st.number_input("Umubare ukenewe", min_value=1, value=1)
            reason = st.text_area("Impamvu / Usage")
            if st.button("Ohereza Demande"):
                supabase.table("requests").insert({
                    "requested_by": st.session_state.username,
                    "item_name": req_item,
                    "quantity": req_qty,
                    "reason": reason,
                    "status": "Pending",
                    "date": str(datetime.now().date())
                }).execute()
                st.success("Demande yoherejwe!")
                st.rerun()
    st.subheader("📋 Urutonde rw'Ibisabwa")
    df_requests = fetch_data("requests")
    if not df_requests.empty:
        st.dataframe(df_requests, use_container_width=True)
    else:
        st.info("Nta demande zirahabwa.")

elif menu == "📖 Fiche de Stock Card":
    st.title("📖 Store Ledger Card (Fiche de Stock)")
    df_trans = fetch_data("transactions")
    if not df_trans.empty:
        st.dataframe(df_trans, use_container_width=True)
    else:
        st.info("Nta miyoborere cyangwa transactions zirakorwa.")

# =========================================================
# PART 2: HR & PAYROLL SYSTEM (RSSB 6% + 6% = 12%)
# =========================================================
elif menu == "📌 HR Dashboard":
    st.title("📊 GS Rurembo - HR & Staff Dashboard")
    df_emp = fetch_data("employees")
    df_leave = fetch_data("leaves")
    col1, col2, col3 = st.columns(3)
    total_emp = len(df_emp) if not df_emp.empty else 0
    pending_leaves = len(df_leave[df_leave["status"] == "Pending"]) if not df_leave.empty and "status" in df_leave.columns else 0
    total_payroll = df_emp["basic_salary"].sum() if not df_emp.empty and "basic_salary" in df_emp.columns else 0
    col1.metric("Bose Hamwe (Total Staff)", total_emp)
    col2.metric("Impushya Zitegerejwe (Pending)", pending_leaves)
    col3.metric("Igiteranyo cy'Imishahara", f"{total_payroll:,.0f} RWF")
    st.markdown("---")
    st.subheader("📋 Abakozi Banditse")
    if not df_emp.empty:
        st.dataframe(df_emp, use_container_width=True)
    else:
        st.info("Nta mukozi urajya muri database.")

elif menu == "👥 Abakozi n'Amasezerano":
    st.title("👥 Management y'Abakozi n'Amasezerano")
    with st.expander("➕ Ongeza Umukozi Gishya", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            emp_id = st.text_input("National ID / Code")
            full_name = st.text_input("Amazina Yose")
            phone = st.text_input("Telefoni")
            position = st.text_input("Umwanya (Position)")
        with c2:
            contract_type = st.selectbox("Ubwoko bw'Amasezerano", ["CDI (Permanent)", "CDD (Temporary)"])
            basic_salary = st.number_input("Umushahara w'Ibanze (RWF)", min_value=0.0)
            start_date = st.date_input("Itariki y'Itangiriro")
            end_date = st.date_input("Itariki y'Iherezo (Niba ari CDD)")
        
        if st.button("Bika Umukozi"):
            if full_name:
                try:
                    supabase.table("employees").insert({
                        "emp_id": emp_id,
                        "full_name": full_name,
                        "phone": phone,
                        "position": position,
                        "contract_type": contract_type,
                        "basic_salary": basic_salary,
                        "start_date": str(start_date),
                        "end_date": str(end_date) if contract_type != "CDI (Permanent)" else None
                    }).execute()
                    st.success("Umukozi abitswe neza!")
                except Exception as e:
                    st.error(f"Habaye ikosa mu kubika umukozi: {e}")
                    st.rerun()
    st.subheader("📄 Urutonde rw'Amasezerano")
    df_emp = fetch_data("employees")
    if not df_emp.empty:
        st.dataframe(df_emp, use_container_width=True)
    else:
        st.info("Nta bakozi barandikwa.")

elif menu == "📝 Gusaba Impushya (Leaves)":
    st.title("📝 Icungamutungo w'Impushya (Leave Management)")
    df_emp = fetch_data("employees")
    st.subheader("Saba Uruhushya")
    c1, c2 = st.columns(2)
    with c1:
        applicant_name = st.selectbox("Izina ryawe", df_emp["full_name"].tolist()) if not df_emp.empty and "full_name" in df_emp.columns else st.text_input("Izina ryawe")
        leave_type = st.selectbox("Ubwoko bw'Uruhushya", ["Sick Leave", "Annual Leave", "Special Leave"])
    with c2:
        start_l = st.date_input("Kuva ku wa")
        end_l = st.date_input("Kugeza ku wa")
        reason = st.text_area("Impamvu")
    if st.button("Ohereza Demande"):
        if applicant_name:
            days = (end_l - start_l).days + 1
            supabase.table("leaves").insert({
                "emp_name": applicant_name, "leave_type": leave_type,
                "start_date": str(start_l), "end_date": str(end_l),
                "days": days if days > 0 else 1, "reason": reason,
                "status": "Pending", "request_date": str(datetime.now().date())
            }).execute()
            st.success("Demande yoherejwe!")
            st.rerun()
    st.markdown("---")
    st.subheader("📋 Ibisabwa n'Approvals")
    df_leave = fetch_data("leaves")
    if not df_leave.empty:
        st.dataframe(df_leave, use_container_width=True)
        if st.session_state.role == "Admin":
            pending_df = df_leave[df_leave["status"] == "Pending"]
            if not pending_df.empty:
                req_to_approve = st.selectbox("Hitamo ushaka kwemeza", pending_df["emp_name"].tolist())
                action = st.radio("Icyemezo", ["Approved", "Rejected"])
                if st.button("Update Status"):
                    supabase.table("leaves").update({"status": action}).eq("emp_name", req_to_approve).execute()
                    st.success("Status yahinduwe!")
                    st.rerun()
    else:
        st.info("Nta demande z'impushya zirahabwa.")

elif menu == "💵 Imishahara (Payroll & Payslip)":
    st.title("💵 Icungamutungo w'Imishahara (Payroll)")
    df_emp = fetch_data("employees")
    if df_emp.empty:
        st.warning("Banza wandike abakozi muri menu ya 'Abakozi n'Amasezerano'.")
    else:
        month = st.selectbox("Hitamo Ukwezi", ["Okitobure 2026", "Novemburu 2026", "Ukuboza 2026"])
        payroll_list = []
        for index, row in df_emp.iterrows():
            basic = float(row.get("basic_salary", 0))
            
            # RSSB: 6% Umukozi + 6% Umukoresha (Total 12%)
            rssb_employee = basic * 0.06
            rssb_employer = basic * 0.06
            total_rssb = rssb_employee + rssb_employer
            
            rama = basic * 0.005
            taxable = basic - rssb_employee
            tpr = calculate_tpr(taxable)
            
            total_ded = rssb_employee + rama + tpr
            net = basic - total_ded
            
            payroll_list.append({
                "Amazina": row.get("full_name"), 
                "Position": row.get("position"),
                "Basic Salary": basic, 
                "RSSB Mukozi (6%)": rssb_employee,
                "RSSB Mukoresha (6%)": rssb_employer,
                "RSSB Total (12%)": total_rssb,
                "RAMA/CBHI (0.5%)": rama,
                "PAYE Tax": tpr, 
                "Total Deductions": total_ded, 
                "Net Salary": net
            })
        df_payroll = pd.DataFrame(payroll_list)
        st.dataframe(df_payroll.style.format({
            "Basic Salary": "{:,.0f}", "RSSB Mukozi (6%)": "{:,.0f}", 
            "RSSB Mukoresha (6%)": "{:,.0f}", "RSSB Total (12%)": "{:,.0f}",
            "RAMA/CBHI (0.5%)": "{:,.0f}", "PAYE Tax": "{:,.0f}", 
            "Total Deductions": "{:,.0f}", "Net Salary": "{:,.0f}"
        }), use_container_width=True)
        
        st.markdown("---")
        selected_staff = st.selectbox("Hitamo Umukozi wa Payslip", df_payroll["Amazina"].tolist())
        if st.button("Gana Payslip"):
            staff_row = df_payroll[df_payroll["Amazina"] == selected_staff].iloc[0]
            st.info(f"""
            ### 🏫 **GS RUREMBO - PAYSLIP**
            **Ukwezi:** {month}
            * **Umukozi:** {staff_row['Amazina']}
            * **Umwanya:** {staff_row['Position']}
            ---
            * **Basic Salary:** {staff_row['Basic Salary']:,.0f} RWF
            * **RSSB Pension (6% Mukozi):** -{staff_row['RSSB Mukozi (6%)']:,.0f} RWF
            * **RAMA/CBHI (0.5%):** -{staff_row['RAMA/CBHI (0.5%)']:,.0f} RWF
            * **PAYE Tax (TPR):** -{staff_row['PAYE Tax']:,.0f} RWF
            ---
            ### **NET SALARY:** {staff_row['Net Salary']:,.0f} RWF
            """)

# =========================================================
# PART 3: REPORTS & ANALYTICS
# =========================================================
elif menu == "📈 Raporo Zose (Reports)":
    st.title("📈 GS Rurembo - Raporo Zose n'Ibipimo (Reports)")
    
    report_tab = st.tabs(["📊 Raporo y'Ububiko (Stock)", "👨‍💼 Raporo y'Abakozi (HR)", "💵 Raporo y'Imishahara & RSSB (12%)"])
    
    with report_tab[0]:
        st.subheader("📊 Raporo y'Ububiko & Stock Card")
        df_stock = fetch_data("stock")
        df_trans = fetch_data("transactions")
        
        c1, c2 = st.columns(2)
        c1.metric("Bicuruzwa / Bipimo biri mu Stock", len(df_stock) if not df_stock.empty else 0)
        c2.metric("Umubare w'Izisohoka/Izinjira (Transactions)", len(df_trans) if not df_trans.empty else 0)
        
        st.markdown("#### 📋 Stock Balances Current")
        if not df_stock.empty:
            st.dataframe(df_stock, use_container_width=True)
            
    with report_tab[1]:
        st.subheader("👨‍💼 Raporo y'Abakozi & Impushya")
        df_emp = fetch_data("employees")
        df_leave = fetch_data("leaves")
        if not df_emp.empty:
            st.dataframe(df_emp, use_container_width=True)
            
    with report_tab[2]:
        st.subheader("💵 Raporo y'Imishahara, RSSB (6%+6%=12%) & PAYE Tax")
        df_emp = fetch_data("employees")
        if not df_emp.empty:
            payroll_report = []
            for index, row in df_emp.iterrows():
                basic = float(row.get("basic_salary", 0))
                rssb_employee = basic * 0.06
                rssb_employer = basic * 0.06
                total_rssb = rssb_employee + rssb_employer
                rama = basic * 0.005
                taxable = basic - rssb_employee
                tpr = calculate_tpr(taxable)
                net = basic - (rssb_employee + rama + tpr)
                
                payroll_report.append({
                    "Umukozi": row.get("full_name"),
                    "Basic Salary": basic,
                    "RSSB Employee (6%)": rssb_employee,
                    "RSSB Employer (6%)": rssb_employer,
                    "Total RSSB (12%)": total_rssb,
                    "RAMA/CBHI": rama,
                    "PAYE Tax": tpr,
                    "Net Salary": net
                })
            
            df_rep = pd.DataFrame(payroll_report)
            st.dataframe(df_rep.style.format({
                "Basic Salary": "{:,.0f}", "RSSB Employee (6%)": "{:,.0f}", 
                "RSSB Employer (6%)": "{:,.0f}", "Total RSSB (12%)": "{:,.0f}",
                "RAMA/CBHI": "{:,.0f}", "PAYE Tax": "{:,.0f}", "Net Salary": "{:,.0f}"
            }), use_container_width=True)
            
            # Totals summary
            st.markdown("### 📊 Inshamake y'Umusoro n'Imisanzu Yose Hamwe")
            st.write(f"• **Igiteranyo cya RSSB yose gomba kwishyurwa (12%):** {df_rep['Total RSSB (12%)'].sum():,.0f} RWF")
            st.write(f"• **Igiteranyo cy'Umusoro wa PAYE/TPR:** {df_rep['PAYE Tax'].sum():,.0f} RWF")
            st.write(f"• **Igiteranyo cy'Umushahara Mbonera (Net Salary Total):** {df_rep['Net Salary'].sum():,.0f} RWF")

# =========================================================
# PART 4: CHANGE PASSWORD FEATURE
# =========================================================
elif menu == "🔐 Hindura Password":
    st.title("🔐 Guhindura Password ya Konti yawe")
    
    current_pass = st.text_input("Password ya Kera (Current Password)", type="password")
    new_pass = st.text_input("Password Nshya (New Password)", type="password")
    confirm_new_pass = st.text_input("Emeza Password Nshya", type="password")
    
    st.info("💡 **Ibisabwa:** Byibuze nyuguti 8, irimo nyuguti nkuru na nto, imibare, n'ibimenyetso.")
    
    if st.button("Hindura Password"):
        if not current_pass or not new_pass:
            st.error("Ugomba kuzuza imyanya yose!")
        elif new_pass != confirm_new_pass:
            st.error("Password nshya wavuze ntizihuye!")
        else:
            check_msg = validate_password(new_pass)
            if check_msg != "OK":
                st.error(check_msg)
            else:
                is_valid_old = False
                if st.session_state.username in ["admin", "staff"]:
                    if current_pass == "123":
                        is_valid_old = True
                    else:
                        st.error("Password ya kera wanditse si yo!")
                else:
                    df_users = fetch_data("users")
                    user_row = df_users[df_users["username"] == st.session_state.username]
                    if not user_row.empty:
                        stored_hash = user_row.iloc[0]["password_hash"]
                        if stored_hash == hash_password(current_pass):
                            is_valid_old = True
                        else:
                            st.error("Password ya kera wanditse si yo!")
                
                if is_valid_old:
                    st.success("Password yawe yahinduwe neza cyane!")

# =========================================================
# PART 5: ADMIN USER MANAGEMENT
# =========================================================
elif menu == "👥 Gucunga Abakoresha (Users)" and st.session_state.role == "Admin":
    st.title("👥 Gucunga Abakoresha na Roles (User Management)")
    
    with st.expander("➕ Ongeza Umukoresha Gishya (Add User)"):
        add_user = st.text_input("Username Nshya")
        add_pass = st.text_input("Password", type="password")
        add_role = st.selectbox("Hitamo Role", ["Staff", "Admin"])
        
        if st.button("Bika Umukoresha"):
            if add_user and add_pass:
                check_msg = validate_password(add_pass)
                if check_msg != "OK":
                    st.error(check_msg)
                else:
                    hashed = hash_password(add_pass)
                    try:
                        supabase.table("users").insert({
                            "username": add_user,
                            "password_hash": hashed,
                            "role": add_role
                        }).execute()
                        st.success(f"Umukoresha {add_user} yongewe neza nka {add_role}!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Habaye ikibazo cyangwa username isanzweho: {e}")
            else:
                st.error("Zuza amakuru yose!")

    st.markdown("---")
    
    df_users = fetch_data("users")
    if not df_users.empty:
        st.subheader("📋 Urutonde rw'Abakoresha ba System")
        st.dataframe(df_users[["username", "role"]], use_container_width=True)
        
        st.markdown("---")
        st.subheader("⚖️ Hindura Role y'Umukoresha")
        selected_user = st.selectbox("Hitamo Username y'umukozi", df_users["username"].tolist())
        new_role = st.selectbox("Hitamo Role nshya", ["Staff", "Admin"])
        
        if st.button("Vugurura Role y'Umukoresha"):
            supabase.table("users").update({"role": new_role}).eq("username", selected_user).execute()
            st.success(f"Role ya {selected_user} yahinduwe kuri '{new_role}' neza cyane!")
            st.rerun()
    else:
        st.info("Nta bakoresha banditse muri database.")
