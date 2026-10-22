import streamlit as st
import pandas as pd
import sqlite3
import os

# ---------------------------------------------------------
# 1. SETUP DATABASE (SQLite Local Database)
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
    
    # Table ya Stock
    c.execute('''
        CREATE TABLE IF NOT EXISTS stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT,
            category TEXT,
            quantity INTEGER,
            unit TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

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
            "Abakozi n'Amasezerano", 
            "Dashboard", 
            "Stock / Ububiko", 
            "Raporo"
        ]
    )

# ---------------------------------------------------------
# 3. ABAKOZI N'AMASEZERANO
# ---------------------------------------------------------
if menu == "Abakozi n'Amasezerano":
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
            basic_salary = st.number_input("Umushahara (Basic Salary Frw)", min_value=0, step=1000)
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
# 4. DASHBOARD
# ---------------------------------------------------------
elif menu == "Dashboard":
    st.title("🏫 GS Rurembo - Dashboard")
    conn = sqlite3.connect(DB_FILE)
    df_emp = pd.read_sql_query("SELECT * FROM employees", conn)
    df_stock = pd.read_sql_query("SELECT * FROM stock", conn)
    conn.close()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Bose Hamwe Abakozi Banditse", value=len(df_emp))
    with col2:
        st.metric(label="Ibicuruzwa Biri muri Stock", value=len(df_stock))

# ---------------------------------------------------------
# 5. STOCK / UBUBIKO
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
# 6. RAPORO
# ---------------------------------------------------------
elif menu == "Raporo":
    st.title("📊 Raporo n'Imbonerahamwe")
    st.info("Aha haba hari raporo n'imbonerahamwe z'ibintu byose muri GS Rurembo.")
