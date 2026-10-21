import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="GS Rurembo - HR & Payroll System", layout="wide", page_icon="👥")

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

# Helper function to calculate Rwandan TPR / PAYE Tax
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
# LOGIN PAGE
# ---------------------------------------------------------
if not st.session_state.logged_in:
    st.title("🔒 GS Rurembo - HR & Payroll System Login")
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
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
                st.error("Username cyangwa Password sibyo!")
    st.stop()

# ---------------------------------------------------------
# MAIN APP NAVIGATION
# ---------------------------------------------------------
st.sidebar.title(f"👤 {st.session_state.username.capitalize()} ({st.session_state.role})")
if st.sidebar.button("Log out"):
    st.session_state.logged_in = False
    st.rerun()

menu = st.sidebar.radio("Navigasiyo HR", [
    "📌 HR Dashboard", 
    "👨‍💼 Abakozi n'Amasezerano", 
    "📝 Gusaba Impushya (Leaves)", 
    "💵 Imishahara (Payroll & Payslip)"
])

# ---------------------------------------------------------
# 1. HR DASHBOARD
# ---------------------------------------------------------
if menu == "📌 HR Dashboard":
    st.title("📊 GS Rurembo - HR & Staff Dashboard")
    
    df_emp = fetch_data("employees")
    df_leave = fetch_data("leaves")
    
    col1, col2, col3 = st.columns(3)
    
    total_emp = len(df_emp) if not df_emp.empty else 0
    pending_leaves = len(df_leave[df_leave["status"] == "Pending"]) if not df_leave.empty and "status" in df_leave.columns else 0
    total_payroll = df_emp["basic_salary"].sum() if not df_emp.empty and "basic_salary" in df_emp.columns else 0
    
    col1.metric("Bose Hamwe (Total Staff)", total_emp)
    col2.metric("Impushya Zitegerejwe (Pending Leaves)", pending_leaves)
    col3.metric("Igiteranyo cy'Imishahara (Basic)", f"{total_payroll:,.0f} RWF")

    st.markdown("---")
    st.subheader("📋 Urutonde rw'Abakozi ba GS Rurembo")
    if not df_emp.empty:
        st.dataframe(df_emp, use_container_width=True)
    else:
        st.info("Nta mukozi urajya muri Supabase database. Jya kuri 'Abakozi n'Amasezerano' umwandike.")

# ---------------------------------------------------------
# 2. ABAKOZI N'AMASEZERANO (EMPLOYEES & CONTRACTS)
# ---------------------------------------------------------
elif menu == "👨‍💼 Abakozi n'Amasezerano":
    st.title("👨‍💼 Management y'Abakozi n'Amasezerano")
    
    if st.session_state.role == "Admin":
        with st.expander("➕ Ongeza Umukozi Gishya / Amasezerano (Add Staff)"):
            c1, c2 = st.columns(2)
            with c1:
                emp_id = st.text_input("National ID / Code y'Umukozi")
                full_name = st.text_input("Amazina YombI (Full Name)")
                phone = st.text_input("Telefoni")
                position = st.text_input("Umwanya (Position/Job Title e.g. Teacher, Bursar)")
            with c2:
                contract_type = st.selectbox("Ubwoko bw'Amasezerano", ["CDI (Permanent)", "CDD (Contract)", "Part-time"])
                basic_salary = st.number_input("Umushahara w'Ibanze (Basic Salary RWF)", min_value=0, value=100000, step=5000)
                start_date = st.date_input("Itariki y'Itangiriro (Start Date)")
                end_date = st.date_input("Itariki y'Iherezo (End Date / Leave blank if CDI)")
            
            if st.button("Bika Umukozi (Save Staff)"):
                if full_name and emp_id:
                    emp_data = {
                        "emp_id": emp_id,
                        "full_name": full_name,
                        "phone": phone,
                        "position": position,
                        "contract_type": contract_type,
                        "basic_salary": basic_salary,
                        "start_date": str(start_date),
                        "end_date": str(end_date) if contract_type != "CDI (Permanent)" else "N/A"
                    }
                    supabase.table("employees").insert(emp_data).execute()
                    st.success(f"Umukozi {full_name} yanditswe neza!")
                    st.rerun()

    st.subheader("📄 Urutonde lw'Amasezerano y'Abakozi")
    df_emp = fetch_data("employees")
    if not df_emp.empty:
        st.dataframe(df_emp, use_container_width=True)
    else:
        st.info("Nta bakozi barandikwa.")

# ---------------------------------------------------------
# 3. GUSABA IMPUSHYA (LEAVE MANAGEMENT)
# ---------------------------------------------------------
elif menu == "📝 Gusaba Impushya (Leaves)":
    st.title("📝 Icungamungudeko ry'Impushya (Leave Management)")
    
    df_emp = fetch_data("employees")
    
    # Staff or Admin Request Form
    st.subheader("Saba Uruhushya")
    c1, c2 = st.columns(2)
    with c1:
        if not df_emp.empty and "full_name" in df_emp.columns:
            applicant_name = st.selectbox("Izina ryawe", df_emp["full_name"].tolist())
        else:
            applicant_name = st.text_input("Izina ryawe")
        leave_type = st.selectbox("Ubwoko bw'Uruhushya", ["Conge y'Uburwayi (Sick Leave)", "Conge y'Annee (Annual Leave)", "Conge y'Ibyago (Maternity/Paternity/Special)"])
    with c2:
        start_l = st.date_input("Kuzatengira ku wa")
        end_l = st.date_input("Kuzasozwa ku wa")
        reason = st.text_area("Impamvu y'Uruhushya")
        
    if st.button("Ohereza Demande y'Uruhushya"):
        if applicant_name:
            days = (end_l - start_l).days + 1
            leave_data = {
                "emp_name": applicant_name,
                "leave_type": leave_type,
                "start_date": str(start_l),
                "end_date": str(end_l),
                "days": days if days > 0 else 1,
                "reason": reason,
                "status": "Pending",
                "request_date": str(datetime.now().date())
            }
            supabase.table("leaves").insert(leave_data).execute()
            st.success("Demande y'uruhushya yoherejwe neza!")
            st.rerun()

    st.markdown("---")
    st.subheader("📋 Urutonde rw'Ibisabwa no Kwemeza (Approvals)")
    df_leave = fetch_data("leaves")
    
    if not df_leave.empty:
        st.dataframe(df_leave, use_container_width=True)
        
        if st.session_state.role == "Admin":
            st.write("### ⚖️ Admin Action: Emeza cyangwa Wange Uruhushya")
            pending_df = df_leave[df_leave["status"] == "Pending"]
            
            if not pending_df.empty:
                req_to_approve = st.selectbox("Hitamo Uruhushya ushaka kwemeza/kwanga", pending_df["emp_name"].tolist())
                action = st.radio("Icyemezo", ["Approved", "Rejected"])
                
                if st.button("Update Status"):
                    supabase.table("leaves").update({"status": action}).eq("emp_name", req_to_approve).execute()
                    st.success(f"Uruhushya rwa {req_to_approve} rwahinduwe ruhawe 'STATUS: {action}'!")
                    st.rerun()
    else:
        st.info("Nta demande z'impushya zirahabwa.")

# ---------------------------------------------------------
# 4. PAYROLL & PAYSLIP GENERATOR
# ---------------------------------------------------------
elif menu == "💵 Imishahara (Payroll & Payslip)":
    st.title("💵 Icungomutungo w'Imishahara (Payroll System)")
    
    df_emp = fetch_data("employees")
    
    if df_emp.empty:
        st.warning("Banza wandike abakozi muri menu ya 'Abakozi n'Amasezerano' kabona ukora Payroll.")
    else:
        st.subheader("🧮 Kubarura Imishahara y'Ukwezi (Rwanda Tax & Deductions)")
        month = st.selectbox("Hitamo Ukwezi", ["Okitobure 2026", "Novemburu 2026", "Ukuboza 2026", "Mutarama 2027"])
        
        payroll_list = []
        for index, row in df_emp.iterrows():
            basic = float(row.get("basic_salary", 0))
            
            # Rwandan Deductions standard structure
            rssb_employee = basic * 0.03  # RSSB Pension 3%
            rama_cbhi = basic * 0.005     # Health insurance / CBHI 0.5%
            taxable_income = basic - rssb_employee
            paye_tpr = calculate_tpr(taxable_income)
            
            total_deductions = rssb_employee + rama_cbhi + paye_tpr
            net_salary = basic - total_deductions
            
            payroll_list.append({
                "Amazina": row.get("full_name"),
                "Position": row.get("position"),
                "Basic Salary": basic,
                "RSSB (3%)": rssb_employee,
                "RAMA/CBHI": rama_cbhi,
                "PAYE / TPR Tax": paye_tpr,
                "Total Deductions": total_deductions,
                "Net Salary (RWF)": net_salary
            })
            
        df_payroll = pd.DataFrame(payroll_list)
        st.dataframe(df_payroll.style.format({
            "Basic Salary": "{:,.0f}",
            "RSSB (3%)": "{:,.0f}",
            "RAMA/CBHI": "{:,.0f}",
            "PAYE / TPR Tax": "{:,.0f}",
            "Total Deductions": "{:,.0f}",
            "Net Salary (RWF)": "{:,.0f}"
        }), use_container_width=True)

        st.markdown("---")
        st.subheader("📄 Reba no Gusohora Fiche de Paie (Payslip)")
        selected_staff = st.selectbox("Hitamo Umukozi ushaka gukorera Payslip", df_payroll["Amazina"].tolist())
        
        if st.button("Gana Payslip"):
            staff_row = df_payroll[df_payroll["Amazina"] == selected_staff].iloc[0]
            
            st.info(f"""
            ### 🏫 **GS RUREMBO - PAYSLIP / FICHE DE PAIE**
            **Ukwezi:** {month}
            
            * **Izina ry'Umukozi:** {staff_row['Amazina']}
            * **Umwanya:** {staff_row['Position']}
            
            ---
            * 💰 **Umushahara w'Ibanze (Basic Salary):** {staff_row['Basic Salary']:,.0f} RWF
            * 📉 **RSSB Pension (3%):** -{staff_row['RSSB (3%)']:,.0f} RWF
            * 📉 **RAMA / CBHI:** -{staff_row['RAMA/CBHI']:,.0f} RWF
            * 📉 **TPR / Umusoro ku Mishahara (PAYE):** -{staff_row['PAYE / TPR Tax']:,.0f} RWF
            ---
            * 🛑 **Igiteranyo cy'Imisoro n'Ubwiteganyirize:** -{staff_row['Total Deductions']:,.0f} RWF
            ### 💵 **NET SALARY (Ayahabwa Umukozi):** {staff_row['Net Salary (RWF)']:,.0f} RWF
            """)
