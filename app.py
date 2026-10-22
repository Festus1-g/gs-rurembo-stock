import streamlit as st
import pandas as pd
import sqlite3
import datetime

# ---------------------------------------------------------
# 1. SETUP PAGE CONFIG & DATABASE (SQLite Local)
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
    # Table y'abakozi
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
    # Table ya stock
    c.execute('''
        CREATE TABLE IF NOT EXISTS stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT,
            category TEXT,
            quantity INTEGER,
            unit TEXT
        )
    ''')
    # Table ya payroll / imishahara
    c.execute('''
        CREATE TABLE IF NOT EXISTS payroll (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            month_year TEXT,
            full_name TEXT,
            basic_salary REAL,
            allowances REAL,
            deductions REAL,
            net_salary REAL,
            payment_date TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Custom CSS yo kunonosora ishusho
st.markdown("""
    <style>
    .main-header { font-size: 26px; font-weight: bold; color: #1E88E5; }
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. SIDEBAR NAVIGATION
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
    st.title("Admin (Admin)")
    
    if st.button("Log out"):
        st.info("Urakoze gukoresha sisitemu!")

    st.markdown("---")
    st.subheader("Hitamo Igice (Menu)")
    
    menu = st.selectbox(
        "Hitamo Igice:",
        [
            "Dashboard",
            "Abakozi n'Amasezerano", 
            "Payroll / Imishahara",
            "Stock / Ububiko", 
            "Raporo"
        ]
    )

# ---------------------------------------------------------
# 3. PAGE 1: DASHBOARD
# ---------------------------------------------------------
if menu == "Dashboard":
    st.title("🏫 GS Rurembo - Dashboard nshingiro")
    st.write("Aha ni ku nshamake no ku mbonerahamwe y'ibikorwa byose muri Sisitemu.")
    st.markdown("---")
    
    conn = sqlite3.connect(DB_FILE)
    df_emp = pd.read_sql_query("SELECT * FROM employees", conn)
    df_stock = pd.read_sql_query("SELECT * FROM stock", conn)
    df_pay = pd.read_sql_query("SELECT * FROM payroll", conn)
    conn.close()

    # Metrics za Dashboard
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(label="👥 Abakozi Bose", value=len(df_emp))
    with c2:
        cdi_count = len(df_emp[df_emp['contract_type'] == "CDI (Permanent)"]) if not df_emp.empty else 0
        st.metric(label="📜 Abafite CDI", value=cdi_count)
    with c3:
        st.metric(label="📦 Ubwoko bwa Stock", value=len(df_stock))
    with c4:
        total_qty = df_stock['quantity'].sum() if not df_stock.empty and 'quantity' in df_stock.columns else 0
        st.metric(label="📊 Ingano y'Ibintu muri Stock", value=int(total_qty))

    st.markdown("---")
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📋 Abakozi ba Hafi Banditse")
        if not df_emp.empty:
            st.dataframe(df_emp[['full_name', 'position', 'basic_salary']].tail(5), use_container_width=True)
        else:
            st.info("Nta mukozi urabandikwa muri sisitemu.")
            
    with col_right:
        st.subheader("📦 Ibicuruzwa bya Nyuma muri Stock")
        if not df_stock.empty:
            st.dataframe(df_stock[['item_name', 'category', 'quantity', 'unit']].tail(5), use_container_width=True)
        else:
            st.info("Nta gicuruzwa kiragera muri stock.")

# ---------------------------------------------------------
# 4. PAGE 2: ABAKOZI N'AMASEZERANO
# ---------------------------------------------------------
elif menu == "Abakozi n'Amasezerano":
    st.title("👨‍💼 Icungamutungo ry'Abakozi n'Amasezerano")
    st.write("Aha ushobora kwandika umukozi mushya no kureba urutonde rw'abakozi basanzwe muri GS Rurembo.")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["📄 Urutonde rw'Amasezerano", "➕ Wandika Umukozi Mushya"])
    
    with tab1:
        st.subheader("📋 Urutonde rw'Abakozi Banditse")
        conn = sqlite3.connect(DB_FILE)
        df_emp = pd.read_sql_query("SELECT * FROM employees", conn)
        conn.close()
        
        if df_emp.empty:
            st.info("Nta mukozi urabandikwa muri sisitemu.")
        else:
            st.dataframe(df_emp, use_container_width=True)
            
            csv_data = df_emp.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Kurura Urutonde (Download CSV / Excel)",
                data=csv_data,
                file_name="Abakozi_GS_Rurembo.csv",
                mime="text/csv"
            )

    with tab2:
        st.subheader("✍️ Form yo Kwandika Umukozi Mushya")
        
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

        if st.button("💾 Bika Umukozi"):
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
                    
                    st.success(f"Umukozi **{full_name}** yanditswe neza muri Sisitemu!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Harimo ikosa mu kubika: {e}")
            else:
                st.warning("Nyamuneka uzuza nibura Izina ry'umukozi!")

# ---------------------------------------------------------
# 5. PAGE 3: PAYROLL / IMISHAHARA
# ---------------------------------------------------------
elif menu == "Payroll / Imishahara":
    st.title("💰 Icungamutungo ry'Imishahara (Payroll)")
    st.write("Aha ushobora gutegura imishahara y'abakozi, ibihumbi n'inyongera buri kwezi.")
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
            st.download_button(
                label="📥 Kurura Raporo y'Imishahara (CSV)",
                data=csv_pay,
                file_name="Imishahara_GS_Rurembo.csv",
                mime="text/csv"
            )
            
    with tab_p2:
        st.subheader("Gutunganya no Kubika Umushahara w'Umukozi")
        
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
                basic_salary = st.number_input("Umushahara w'Ibanze (Frw)", value=default_salary, step=1000.0)
                allowances = st.number_input("Inyongera / Agahimbazamusyi (Allowances Frw)", min_value=0.0, step=500.0)
                
            with c2:
                deductions = st.number_input("Ikatwa / Ibindi (Deductions Frw)", min_value=0.0, step=500.0)
                payment_date = st.date_input("Itariki yo Gutangira / Kwishyura")
                
                # Net salary calculation
                net_salary = (basic_salary + allowances) - deductions
                st.info(f"**Umushahara w'Umusaruro (Net Salary):** {net_salary:,.2f} Frw")
                
            if st.button("💾 Bika Umushahara"):
                if month_year:
                    try:
                        conn = sqlite3.connect(DB_FILE)
                        c = conn.cursor()
                        c.execute('''
                            INSERT INTO payroll (month_year, full_name, basic_salary, allowances, deductions, net_salary, payment_date)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (month_year, selected_emp, basic_salary, allowances, deductions, net_salary, payment_date.strftime("%Y-%m-%d")))
                        
                        conn.commit()
                        conn.close()
                        
                        st.success(f"Umushahara wa **{selected_emp}** w'ukwezi kwa **{month_year}** ubikiwe neza!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Harimo ikosa mu kubika umushahara: {e}")
                else:
                    st.warning("Nyamuneka andika ukwezi n'umwaka (Urugero: October 2026)!")

# ---------------------------------------------------------
# 6. PAGE 4: STOCK / UBUBIKO
# ---------------------------------------------------------
elif menu == "Stock / Ububiko":
    st.title("📦 Gucunga Stock / Ububiko")
    st.markdown("---")
    
    tab_s1, tab_s2 = st.tabs(["📋 Urutonde lwa Stock", "➕ Wandika Igicuruzwa Mushya"])
    
    with tab_s1:
        st.subheader("Urutonde rw'Ibicuruzwa Biri muri Stock")
        conn = sqlite3.connect(DB_FILE)
        df_stock = pd.read_sql_query("SELECT * FROM stock", conn)
        conn.close()
        
        if df_stock.empty:
            st.info("Nta gicuruzwa kiragera muri stock.")
        else:
            st.dataframe(df_stock, use_container_width=True)
            
            csv_stock = df_stock.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Kurura Urutonde lwa Stock (Download CSV)",
                data=csv_stock,
                file_name="Stock_GS_Rurembo.csv",
                mime="text/csv"
            )
            
    with tab_s2:
        st.subheader("Form yo Gushyira Igicuruzwa muri Stock")
        col1, col2 = st.columns(2)
        
        with col1:
            item_name = st.text_input("Izina ry'Igicuruzwa *")
            category = st.text_input("Icyiciro (Category / Urugero: Isukari, Ibipapuro...)")
            
        with col2:
            qty = st.number_input("Ingano (Quantity)", min_value=0, step=1)
            unit = st.text_input("Igipimo (e.g. Kg, Pcs, Liters)")
            
        if st.button("💾 Save Item"):
            if item_name:
                try:
                    conn = sqlite3.connect(DB_FILE)
                    c = conn.cursor()
                    c.execute('''
                        INSERT INTO stock (item_name, category, quantity, unit)
                        VALUES (?, ?, ?, ?)
                    ''', (item_name, category, int(qty), unit))
                    
                    conn.commit()
                    conn.close()
                    
                    st.success(f"Igicuruzwa **{item_name}** kiyongereye muri Stock neza!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Harimo ikosa mu kubika igicuruzwa: {e}")
            else:
                st.warning("Nyamuneka uzuza izina ry'igicuruzwa!")

# ---------------------------------------------------------
# 7. PAGE 5: RAPORO
# ---------------------------------------------------------
elif menu == "Raporo":
    st.title("📊 Raporo n'Imbonerahamwe rusange")
    st.info("Aha haba hari raporo zose z'ibigo n'imbonerahamwe za GS Rurembo.")
