import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="GS Rurembo Stock Management", layout="wide", page_icon="📦")

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

# Authentication State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

# ---------------------------------------------------------
# LOGIN PAGE
# ---------------------------------------------------------
if not st.session_state.logged_in:
    st.title("🔒 GS Rurembo - Stock Management System Login")
    
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

menu = st.sidebar.radio("Navigasiyo", ["Dashboard & Stock", "Direct Stock Out", "Staff Requests", "Fiche de Stock Card"])

# ---------------------------------------------------------
# 1. DASHBOARD & STOCK STATUS
# ---------------------------------------------------------
if menu == "Dashboard & Stock":
    st.title("📊 Dashboard & Ububiko (Stock)")
    
    df_stock = fetch_data("stock")
    
    if df_stock.empty:
        st.info("Nta bicuruzwa birajya muri Supabase stock database. Ongera igicuruzwa gishya munsi.")
    else:
        st.dataframe(df_stock, use_container_width=True)

    if st.session_state.role == "Admin":
        with st.expander("➕ Ongeza Igicuruzwa Gishya (Add New Item)"):
            item_name = st.text_input("Izina ry'igicuruzwa (Item Name)")
            category = st.text_input("Icyiciro (Category)")
            qty = st.number_input("Umubare w'intangiriro (Quantity)", min_value=0, value=0)
            unit = st.text_input("Igipimo (Unit - e.g. Kg, Pcs, Boxes)")
            
            if st.button("Save Item"):
                if item_name:
                    data = {
                        "item_name": item_name,
                        "category": category,
                        "quantity": qty,
                        "unit": unit
                    }
                    supabase.table("stock").insert(data).execute()
                    st.success(f"{item_name} yongewe mu bubiko neza!")
                    st.rerun()

# ---------------------------------------------------------
# 2. DIRECT STOCK OUT
# ---------------------------------------------------------
elif menu == "Direct Stock Out":
    st.title("📤 Gusohora Ibicuruzwa (Direct Stock Out)")
    
    df_stock = fetch_data("stock")
    if not df_stock.empty and "item_name" in df_stock.columns:
        item_list = df_stock["item_name"].tolist()
        selected_item = st.selectbox("Hitamo Igicuruzwa", item_list)
        qty_out = st.number_input("Umubare usohoka", min_value=1, value=1)
        received_by = st.text_input("Uwakiriye (Recipient)")
        
        if st.button("Sohora"):
            current_row = df_stock[df_stock["item_name"] == selected_item].iloc[0]
            current_qty = current_row["quantity"]
            
            if qty_out > current_qty:
                st.error("Umubare usaba ni mwinshi kurenza uli mu bubiko!")
            else:
                new_qty = current_qty - qty_out
                supabase.table("stock").update({"quantity": new_qty}).eq("item_name", selected_item).execute()
                
                trans_data = {
                    "date": str(datetime.now().date()),
                    "item_name": selected_item,
                    "qty_out": qty_out,
                    "balance": new_qty,
                    "recipient": received_by
                }
                supabase.table("transactions").insert(trans_data).execute()
                
                st.success("Igicuruzwa cyasohowe neza!")
                st.rerun()
    else:
        st.info("Ububiko buracyari ubusa cyangwa nta bikoresho birimo.")

# ---------------------------------------------------------
# 3. STAFF REQUESTS & APPROVALS
# ---------------------------------------------------------
elif menu == "Staff Requests":
    st.title("📝 Demande z'Ibicuruzwa (Requisitions)")
    
    df_stock = fetch_data("stock")
    
    if st.session_state.role == "Staff":
        st.subheader("Saba Igicuruzwa")
        if not df_stock.empty and "item_name" in df_stock.columns:
            req_item = st.selectbox("Igicuruzwa", df_stock["item_name"].tolist())
            req_qty = st.number_input("Umubare ukenewe", min_value=1, value=1)
            reason = st.text_area("Impamvu / Usage")
            
            if st.button("Ohereza Demande"):
                req_data = {
                    "requested_by": st.session_state.username,
                    "item_name": req_item,
                    "quantity": req_qty,
                    "reason": reason,
                    "status": "Pending",
                    "date": str(datetime.now().date())
                }
                supabase.table("requests").insert(req_data).execute()
                st.success("Demande yawe yoherejwe neza!")
                st.rerun()

    st.subheader("📋 Urutonde rw'Ibisabwa (Requests)")
    df_requests = fetch_data("requests")
    if not df_requests.empty:
        st.dataframe(df_requests, use_container_width=True)
    else:
        st.info("Nta demande zirahabwa.")

# ---------------------------------------------------------
# 4. FICHE DE STOCK CARD
# ---------------------------------------------------------
elif menu == "Fiche de Stock Card":
    st.title("📖 Store Ledger Card (Fiche de Stock)")
    
    df_trans = fetch_data("transactions")
    if not df_trans.empty:
        st.dataframe(df_trans, use_container_width=True)
    else:
        st.info("Nta miyoborere cyangwa izindi transactions zirakorwa.")
