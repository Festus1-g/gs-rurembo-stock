import streamlit as st
import pandas as pd
from supabase import create_client, Client
import datetime

# ---------------------------------------------------------
# 1. SETUP PAGE CONFIG & SUPABASE CLIENT
# ---------------------------------------------------------
st.set_page_config(
    page_title="GS Rurembo Management System",
    page_icon="🏫",
    layout="wide"
)

# Guhamagara Supabase Credentials muri Secrets
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error("Harimo ikosa mu kureba Secrets za Supabase. Reba ko SUPABASE_URL na SUPABASE_KEY birimo neza.")

# Helper function yo gukurura data muri Supabase
def fetch_data(table_name):
    try:
        response = supabase.table(table_name).select("*").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Harimo ikosa mu gusoma table ya '{table_name}': {e}")
        return pd.DataFrame()

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
# 3. PAGE 1: ABAKOZI N'AMASEZERANO
# ---------------------------------------------------------
if menu == "Abakozi n'Amasezerano":
    st.title("👨‍💼 Icungamutungo ry'Abakozi n'Amasezerano")
    st.write("Aha ushobora kwandika umukozi mushya no kureba urutonde rw'abakozi basanzwe muri GS Rurembo.")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["📄 Urutonde rw'Amasezerano", "➕ Wandika Umukozi Mushya"])
    
    # TAB 1: KUREBA ABAKOZI
    with tab1:
        st.subheader("📋 Urutonde rw'Abakozi Banditse")
        df_emp = fetch_data("employees")
        if not df_emp.empty:
            st.dataframe(df_emp, use_container_width=True)
            
            # Button yo gukurura Excel/CSV
            csv_data = df_emp.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Kurura Urutonde (Download CSV / Excel)",
                data=csv_data,
                file_name="Abakozi_GS_Rurembo.csv",
                mime="text/csv"
            )
        else:
            st.info("Nta mukozi urabandikwa muri sisitemu.")

    # TAB 2: KWANDIKA UMUKOZI MUSHYA
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
                    # Gucungira hafi amatariki ngo ahuye na PostgreSQL Date
                    start_str = start_date.isoformat() if start_date else None
                    end_str = end_date.isoformat() if contract_type != "CDI (Permanent)" and end_date else None

                    supabase.table("employees").insert({
                        "emp_id": str(emp_id),
                        "full_name": str(full_name),
                        "phone": str(phone),
                        "position": str(position),
                        "contract_type": str(contract_type),
                        "basic_salary": float(basic_salary),
                        "start_date": start_str,
                        "end_date": end_str
                    }).execute()
                    
                    st.success(f"Umukozi **{full_name}** yanditswe neza muri Supabase!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Harimo ikosa mu kubika umukozi: {e}")
            else:
                st.warning("Nyamuneka uzuza nibura Izina ry'umukozi!")

# ---------------------------------------------------------
# 4. PAGE 2: DASHBOARD
# ---------------------------------------------------------
elif menu == "Dashboard":
    st.title("🏫 GS Rurembo - Dashboard")
    st.write("Aha ni ku nshamake y'ibiri muri Sisitemu.")
    
    col1, col2 = st.columns(2)
    with col1:
        df_a = fetch_data("employees")
        st.metric(label="Bose Hamwe Abakozi Banditse", value=len(df_a) if not df_a.empty else 0)
    with col2:
        df_s = fetch_data("stock")
        st.metric(label="Ibicuruzwa Biri muri Stock", value=len(df_s) if not df_s.empty else 0)

# ---------------------------------------------------------
# 5. PAGE 3: STOCK / UBUBIKO
# ---------------------------------------------------------
elif menu == "Stock / Ububiko":
    st.title("📦 Gucunga Stock / Ububiko")
    st.markdown("---")
    
    tab_s1, tab_s2 = st.tabs(["📋 Urutonde lwa Stock", "➕ Wandika Igicuruzwa Mushya"])
    
    with tab_s1:
        st.subheader("Urutonde rw'Ibicuruzwa Biri muri Stock")
        df_stock = fetch_data("stock")
        if not df_stock.empty:
            st.dataframe(df_stock, use_container_width=True)
        else:
            st.info("Nta gicuruzwa kiragera muri stock.")
            
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
                    supabase.table("stock").insert({
                        "item_name": str(item_name),
                        "category": str(category),
                        "quantity": int(qty),
                        "unit": str(unit)
                    }).execute()
                    
                    st.success(f"Igicuruzwa **{item_name}** kiyongereye muri Stock neza!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Harimo ikosa mu kubika igicuruzwa: {e}")
            else:
                st.warning("Nyamuneka uzuza izina ry'igicuruzwa!")

# ---------------------------------------------------------
# 6. PAGE 4: RAPORO
# ---------------------------------------------------------
elif menu == "Raporo":
    st.title("📊 Raporo n'Imbonerahamwe")
    st.info("Aha haba hari raporo n'imbonerahamwe z'ibintu byose muri GS Rurembo.")
