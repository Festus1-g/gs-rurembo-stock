import streamlit as st
import pandas as pd
import sqlite3
import datetime

# ---------------------------------------------------------
# 1. SETUP PAGE CONFIG & DATABASE STRUCTURE
# ---------------------------------------------------------
st.set_page_config(
    page_title="GS Rurembo Management System",
    page_icon="🏫",
    layout="wide"
)

DB_FILE = "gs_rurembo.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Table y'abakozi n'Amasezerano
    c.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT,
            full_name TEXT,
            phone TEXT,
            position TEXT,
            contract_type TEXT,
            basic_salary REAL,
            start_date TEXT,
            end_date TEXT
        )
    ''')
    
    # Table ya Stock (Ububiko)
    c.execute('''
        CREATE TABLE IF NOT EXISTS stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT UNIQUE,
            category TEXT,
            quantity INTEGER,
            unit TEXT
        )
    ''')
    
    # Table y'Ibyasabwe muri Stock (Stock Requests & Approvals)
    c.execute('''
        CREATE TABLE IF NOT EXISTS stock_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            requester_name TEXT,
            item_name TEXT,
            requested_qty INTEGER,
            reason TEXT,
            status TEXT DEFAULT 'PENDING',
            request_date TEXT
        )
    ''')
    
    # Table ya Payroll (Imishahara & RSSB)
    c.execute('''
        CREATE TABLE IF NOT EXISTS payroll (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            month_year TEXT,
            full_name TEXT,
            basic_salary REAL,
            allowances REAL,
            pension REAL,
            cbhi REAL,
            maternity REAL,
            other_loans REAL,
            total_deductions REAL,
            net_salary REAL,
            payment_date TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

# Custom Styling
st.markdown("""
    <style>
    .main-header { font-size: 24px; font-weight: bold; color: #1E88E5; }
    .stMetric { background-color: #f8f9fa; padding: 12px; border-radius: 8px; border: 1px solid #e9ecef; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. SIDEBAR NAVIGATION
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
    st.title("GS Rurembo Admin")
    
    if st.button("Log out"):
        st.info("Urakoze gukoresha sisitemu!")

    st.markdown("---")
    st.subheader("Hitamo Igice (Menu)")
    
    menu = st.selectbox(
        "Hitamo Igice:",
        [
            "Dashboard",
            "Gucunga Stock / Ububiko",
            "Abakozi n'Amasezerano", 
            "Payroll / Imishahara",
            "Raporo"
        ]
    )

# ---------------------------------------------------------
# 3. DASHBOARD
# ---------------------------------------------------------
if menu == "Dashboard":
    st.title("🏫 GS Rurembo - Dashboard")
    st.write("Aha ni ku nshamake y'ibikorwa byose n'ububiko muri Sisitemu.")
    st.markdown("---")
    
    conn = sqlite3.connect(DB_FILE)
    df_emp = pd.read_sql_query("SELECT * FROM employees", conn)
    df_stock = pd.read_sql_query("SELECT * FROM stock", conn)
    df_req = pd.read_sql_query("SELECT * FROM stock_requests WHERE status='PENDING'", conn)
    conn.close()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(label="👥 Abakozi Bose", value=len(df_emp))
    with c2:
        st.metric(label="📦 Ubwoko bwa Stock", value=len(df_stock))
    with c3:
        st.metric(label="⏳ Pending Stock Requests", value=len(df_req))
    with c4:
        total_qty = df_stock['quantity'].sum() if not df_stock.empty and 'quantity' in df_stock.columns else 0
        st.metric(label="📊 Ingano y'Ibintu muri Stock", value=int(total_qty))

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📦 Ububiko Buri Muri Stock (Stock Balance)")
        if not df_stock.empty:
            st.dataframe(df_stock[['item_name', 'category', 'quantity', 'unit']], use_container_width=True)
        else:
            st.info("Nta gicuruzwa kiragera muri stock.")
    with col2:
        st.subheader("⏳ Ibyasabwe Bitaraprovingwa")
        if not df_req.empty:
            st.dataframe(df_req[['requester_name', 'item_name', 'requested_qty', 'request_date']], use_container_width=True)
        else:
            st.success("Nta busabe bw'ibintu bo muri stock buteregereje!")

# ---------------------------------------------------------
# 4. GUCUNGA STOCK / UBUBIKO (IN, REQUEST, APPROVE)
# ---------------------------------------------------------
elif menu == "Gucunga Stock / Ububiko":
    st.title("📦 Icungamutungo ry'Ububiko (Stock Workflow)")
    st.markdown("---")
    
    tab_s1, tab_s2, tab_s3, tab_s4 = st.tabs([
        "📊 Stock Balance", 
        "📥 Kwingiza Item (Stock In)", 
        "📝 Gusaba Item (Request)", 
        "✅ Kwapprova Ibyasabwe (Approvals)"
    ])
    
    # TAB 1: STOCK BALANCE
    with tab_s1:
        st.subheader("📋 Urutonde rw'Ibicuruzwa na Quantity iri muri Ububiko")
        conn = sqlite3.connect(DB_FILE)
        df_stock = pd.read_sql_query("SELECT * FROM stock", conn)
        conn.close()
        
        if df_stock.empty:
            st.info("Nta gicuruzwa kiragera muri stock.")
        else:
            st.dataframe(df_stock, use_container_width=True)
            csv_stock = df_stock.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Kurura Stock Balance (CSV)", data=csv_stock, file_name="Stock_GS_Rurembo.csv", mime="text/csv")

    # TAB 2: KWINGIZA ITEM (STOCK IN)
    with tab_s2:
        st.subheader("📥 Ongeraho Igicuruzwa cyangwa Ingano Muri Stock")
        col1, col2 = st.columns(2)
        
        with col1:
            item_name = st.text_input("Izina ry'Igicuruzwa *")
            category = st.text_input("Icyiciro (Category / Urugero: Isukari, Ibipapuro, Isabune...)")
            
        with col2:
            qty = st.number_input("Ingano Uyongereye (Quantity)", min_value=1, step=1)
            unit = st.text_input("Igipimo (e.g. Kg, Pcs, Liters, Cartons)")
            
        if st.button("💾 Bika / Ongeraho Muri Stock"):
            if item_name:
                try:
                    conn = sqlite3.connect(DB_FILE)
                    c = conn.cursor()
                    
                    c.execute("SELECT quantity FROM stock WHERE item_name = ?", (item_name,))
                    existing = c.fetchone()
                    
                    if existing:
                        new_qty = existing[0] + int(qty)
                        c.execute("UPDATE stock SET quantity = ?, category = ?, unit = ? WHERE item_name = ?", (new_qty, category, unit, item_name))
                        st.success(f"Ingano ya **{item_name}** yavuguruwe! Ingano nshya ni: **{new_qty} {unit}**")
                    else:
                        c.execute("INSERT INTO stock (item_name, category, quantity, unit) VALUES (?, ?, ?, ?)", (item_name, category, int(qty), unit))
                        st.success(f"Igicuruzwa **{item_name}** kiyongereye muri Stock neza!")
                    
                    conn.commit()
                    conn.close()
                    st.rerun()
                except Exception as e:
                    st.error(f"Harimo ikosa: {e}")
            else:
                st.warning("Uzuza izina ry'igicuruzwa!")

    # TAB 3: GUSABA ITEM
    with tab_s3:
        st.subheader("📝 Fomu yo Gusaba Igicuruzwa muri Stock")
        conn = sqlite3.connect(DB_FILE)
        df_stock = pd.read_sql_query("SELECT * FROM stock WHERE quantity > 0", conn)
        conn.close()
        
        if df_stock.empty:
            st.warning("Nta gicuruzwa kiri muri stock cyo gusabwa.")
        else:
            col1, col2 = st.columns(2)
            with col1:
                requester_name = st.text_input("Usaba Igicuruzwa (Izina ry'Umukozi / Igice) *")
                selected_item = st.selectbox("Hitamo Igicuruzwa Ukeneye", df_stock['item_name'].tolist())
                
            with col2:
                req_qty = st.number_input("Ingano Usaba", min_value=1, step=1)
                reason = st.text_area("Impamvu cyangwa Iyo Kigiye Gukora")
                
            if st.button("📤 Ohereza Ubusabe (Submit Request)"):
                if requester_name and selected_item:
                    item_info = df_stock[df_stock['item_name'] == selected_item].iloc[0]
                    available_qty = item_info['quantity']
                    
                    if req_qty > available_qty:
                        st.error(f"Ingano usaba ({req_qty}) iraruta iyiri muri stock ({available_qty} {item_info['unit']})!")
                    else:
                        conn = sqlite3.connect(DB_FILE)
                        c = conn.cursor()
                        today = datetime.date.today().strftime("%Y-%m-%d")
                        c.execute('''
                            INSERT INTO stock_requests (requester_name, item_name, requested_qty, reason, status, request_date)
                            VALUES (?, ?, ?, ?, 'PENDING', ?)
                        ''', (requester_name, selected_item, int(req_qty), reason, today))
                        conn.commit()
                        conn.close()
                        st.success("Ubusabe bwawe bworejwe neza! Mutegereze approval.")
                        st.rerun()
                else:
                    st.warning("Uzuza izina ry'usaba n'igicuruzwa!")

    # TAB 4: KWAPPROVA IBYASABWE (APPROVALS)
    with tab_s4:
        st.subheader("✅ Approve cyangwa Reject Ubusabe bw'Ibyasabwe")
        conn = sqlite3.connect(DB_FILE)
        df_pending = pd.read_sql_query("SELECT * FROM stock_requests WHERE status = 'PENDING'", conn)
        conn.close()
        
        if df_pending.empty:
            st.info("Nta busabe bw'ibintu buri gukenera Approval ubu.")
        else:
            st.dataframe(df_pending, use_container_width=True)
            
            for idx, row in df_pending.iterrows():
                with st.expander(f"📌 Request #{row['id']}: {row['requester_name']} asaba {row['requested_qty']} {row['item_name']}"):
                    st.write(f"**Impamvu:** {row['reason']}")
                    st.write(f"**Itariki:** {row['request_date']}")
                    
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        if st.button(f"✅ Approve #{row['id']}", key=f"app_{row['id']}"):
                            conn = sqlite3.connect(DB_FILE)
                            c = conn.cursor()
                            c.execute("UPDATE stock SET quantity = quantity - ? WHERE item_name = ?", (row['requested_qty'], row['item_name']))
                            c.execute("UPDATE stock_requests SET status = 'APPROVED' WHERE id = ?", (row['id'],))
                            conn.commit()
                            conn.close()
                            st.success("Ubusabe bwemejwe kandi inano yakatwe muri Stock Balance!")
                            st.rerun()
                            
                    with btn_col2:
                        if st.button(f"❌ Reject #{row['id']}", key=f"rej_{row['id']}"):
                            conn = sqlite3.connect(DB_FILE)
                            c = conn.cursor()
                            c.execute("UPDATE stock_requests SET status = 'REJECTED' WHERE id = ?", (row['id'],))
                            conn.commit()
                            conn.close()
                            st.warning("Ubusabe bwanzwe (Rejected).")
                            st.rerun()

# ---------------------------------------------------------
# 5. ABAKOZI N'AMASEZERANO
# ---------------------------------------------------------
elif menu == "Abakozi n'Amasezerano":
    st.title("👨‍💼 Icungamutungo ry'Abakozi n'Amasezerano")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["📄 Urutonde rw'Amasezerano", "➕ Kurema & Kubika Amasezerano"])
    
    with tab1:
        st.subheader("📋 Urutonde rw'Abakozi na Amasezerano")
        conn = sqlite3.connect(DB_FILE)
        df_emp = pd.read_sql_query("SELECT * FROM employees", conn)
        conn.close()
        
        if df_emp.empty:
            st.info("Nta mukozi urabandikwa muri sisitemu.")
        else:
            st.dataframe(df_emp, use_container_width=True)
            csv_data = df_emp.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Kurura Urutonde (CSV / Excel)", data=csv_data, file_name="Abakozi_GS_Rurembo.csv", mime="text/csv")

    with tab2:
        st.subheader("✍️ Form yo Kwandika no Kubika Amasezerano y'Umukozi")
        col1, col2 = st.columns(2)
        
        with col1:
            emp_id = st.text_input("Numero y'Indangamuntu (ID)")
            full_name = st.text_input("Amazina Yombi ya Umukozi *")
            phone = st.text_input("Numero ya Telefoni")
            position = st.text_input("Umwanya (Position / Urugero: Umutetsi, Umuzamu...)")
            
        with col2:
            contract_type = st.selectbox("Ibwoko bw'Amasezerano", ["CDI (Permanent)", "CDD (Amasezerano y'Igihe)"])
            basic_salary = st.number_input("Umushahara w'Ibanze (Basic Salary Frw)", min_value=0.0, step=1000.0)
            start_date = st.date_input("Itariki y'Itangiriro")
            end_date = st.date_input("Itariki y'Iherezo (Niba ari CDD)")

        if st.button("💾 Bika Amasezerano y'Umukozi"):
            if full_name:
                try:
                    conn = sqlite3.connect(DB_FILE)
                    c = conn.cursor()
                    
                    start_str = start_date.strftime("%Y-%m-%d") if start_date else None
                    end_str = end_date.strftime("%Y-%m-%d") if contract_type != "CDI (Permanent)" and end_date else "N/A"
                    
                    c.execute('''
                        INSERT INTO employees (emp_id, full_name, phone, position, contract_type, basic_salary, start_date, end_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (emp_id, full_name, phone, position, contract_type, basic_salary, start_str, end_str))
                    
                    conn.commit()
                    conn.close()
                    st.success(f"Amasezerano ya **{full_name}** abikiwe neza muri Sisitemu!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Harimo ikosa mu kubika: {e}")
            else:
                st.warning("Uzuza nibura Izina ry'umukozi!")

# ---------------------------------------------------------
# 6. PAYROLL / IMISHAHARA (WITH PENSION 6%, CBHI, MATERNITY)
# ---------------------------------------------------------
elif menu == "Payroll / Imishahara":
    st.title("💰 Icungamutungo ry'Imishahara (Payroll)")
    st.markdown("---")
    
    tab_p1, tab_p2 = st.tabs(["📋 Urutonde rw'Imishahara Zatanzwe", "➕ Tunganya Umushahara Mushya"])
    
    with tab_p1:
        st.subheader("Imishahara yanditswe muri Sisitemu")
        conn = sqlite3.connect(DB_FILE)
        df_pay = pd.read_sql_query("SELECT * FROM payroll", conn)
        conn.close()
        
        if df_pay.empty:
            st.info("Nta mishahara irandikwa cyangwa ngo itangwe.")
        else:
            st.dataframe(df_pay, use_container_width=True)
            csv_pay = df_pay.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Kurura Raporo y'Imishahara (CSV)", data=csv_pay, file_name="Imishahara_GS_Rurembo.csv", mime="text/csv")
            
    with tab_p2:
        st.subheader("Tunganya no Kubika Umushahara n'Imisanzu (Pension 6%, CBHI, Maternity Leave)")
        conn = sqlite3.connect(DB_FILE)
        df_emp = pd.read_sql_query("SELECT * FROM employees", conn)
        conn.close()
        
        if df_emp.empty:
            st.warning("Banza wandike abakozi muri 'Abakozi n'Amasezerano' kugira ngo ubone uko ubahemba.")
        else:
            selected_emp = st.selectbox("Hitamo Umukozi", df_emp['full_name'].tolist())
            emp_row = df_emp[df_emp['full_name'] == selected_emp].iloc[0]
            default_salary = float(emp_row['basic_salary']) if 'basic_salary' in emp_row else 0.0
            
            c1, c2 = st.columns(2)
            with c1:
                month_year = st.text_input("Ukwezi n'Umwaka (Urugero: October 2026)")
                basic_salary = st.number_input("Umushahara w'Ibanze (Basic Salary Frw)", value=default_salary, step=1000.0)
                allowances = st.number_input("Inyongera / Agahimbazamusyi (Allowances Frw)", min_value=0.0, step=500.0)
                
            with c2:
                # 1. Pension (6%)
                auto_pension = basic_salary * 0.06
                pension_deduction = st.number_input("Pension (RSSB Pension 6%)", value=float(auto_pension), step=100.0)
                
                # 2. CBHI (Mituweli / Ubwishingizi)
                cbhi_deduction = st.number_input("CBHI / Ubwishingizi bw'Indwara (Frw)", value=0.0, step=100.0)
                
                # 3. Maternity Leave Contribution (0.3%)
                auto_maternity = basic_salary * 0.003
                maternity_deduction = st.number_input("Maternity Leave Contribution (Frw)", value=float(auto_maternity), step=50.0)
                
                other_loans = st.number_input("Ibindi bikatwa (Loans / Advance Frw)", min_value=0.0, step=500.0)
                payment_date = st.date_input("Itariki yo Kwishyura")
                
                # Calculation of Total Deductions & Net Salary
                total_deductions = pension_deduction + cbhi_deduction + maternity_deduction + other_loans
                net_salary = (basic_salary + allowances) - total_deductions
                
                st.info(f"**Igiteranyo cy'Ibyakatwe (Total Deductions):** {total_deductions:,.2f} Frw")
                st.info(f"**Umushahara w'Umusaruro (Net Salary):** {net_salary:,.2f} Frw")
                
            if st.button("💾 Bika Umushahara n'Imisanzu ya RSSB"):
                if month_year:
                    try:
                        conn = sqlite3.connect(DB_FILE)
                        c = conn.cursor()
                        c.execute('''
                            INSERT INTO payroll (month_year, full_name, basic_salary, allowances, pension, cbhi, maternity, other_loans, total_deductions, net_salary, payment_date)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (month_year, selected_emp, basic_salary, allowances, pension_deduction, cbhi_deduction, maternity_deduction, other_loans, total_deductions, net_salary, payment_date.strftime("%Y-%m-%d")))
                        conn.commit()
                        conn.close()
                        st.success(f"Umushahara wa **{selected_emp}** w'ukwezi kwa **{month_year}** ubarweho RSSB neza!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Harimo ikosa: {e}")
                else:
                    st.warning("Andika ukwezi n'umwaka!")

# ---------------------------------------------------------
# 7. RAPORO
# ---------------------------------------------------------
elif menu == "Raporo":
    st.title("📊 Raporo n'Imbonerahamwe")
    st.info("Aha haba hari raporo zose no gukurura amakuru ya GS Rurembo.")
