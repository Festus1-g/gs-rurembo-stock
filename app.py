import streamlit as st
import pandas as pd
import os

# ---------------------------------------------------------
# 1. PARAMETERS & CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="GS Rurembo Management System",
    page_icon="🏫",
    layout="wide"
)

# Amadosiye ya Excel abikamo amakuru
FILE_ABAKOZI = "abakozi.xlsx"
FILE_STOCK = "stock.xlsx"

# Gukora idosiye y'Abakozi niba itariko
if not os.path.exists(FILE_ABAKOZI):
    df_abakozi = pd.DataFrame(columns=[
        "Indangamuntu (ID)", "Amazina Yombi", "Umurimo / Post", 
        "Telefoni", "Umushahara (Frw)", "Itariki Amasezerano Atangirira"
    ])
    df_abakozi.to_excel(FILE_ABAKOZI, index=False, engine="openpyxl")

# Gukora idosiye ya Stock niba itariko
if not os.path.exists(FILE_STOCK):
    df_stock = pd.DataFrame(columns=["Izina ry'Ibicuruzwa", "Ingano (Quantity)", "Igiciro (Frw)"])
    df_stock.to_excel(FILE_STOCK, index=False, engine="openpyxl")


# ---------------------------------------------------------
# 2. SIDEBAR & NAVIGATION MENU
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
    st.title("Admin (Admin)")
    
    if st.button("Log out"):
        st.info("Urakoze gukoresha sisitemu!")

    st.markdown("---")
    st.subheader("Hitamo Igice (Menu)")
    
    # Menu ihuye neza n'iri mu ifoto yawe
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
# 3. PAGES IMPLEMENTATION
# ---------------------------------------------------------

# --- PAGE 1: ABAKOZI N'AMASEZERANO ---
if menu == "Abakozi n'Amasezerano":
    st.title("👨‍💼 Icungamutungo ry'Abakozi n'Amasezerano")
    st.write("Aha ushobora kwandika umukozi mushya, kureba urutonde rw'abakozi basanzwe, n'ibindi.")
    
    tab1, tab2 = st.tabs(["📋 Urutonde rw'Abakozi", "➕ Wandika Umukozi Mushya"])
    
    # TAB 1: Urutonde rw'Abakozi
    with tab1:
        st.subheader("Urutonde rw'Abakozi Basanzwe Muri Excel")
        try:
            df_abakozi = pd.read_excel(FILE_ABAKOZI, engine="openpyxl")
            if df_abakozi.empty:
                st.warning("Nta mukozi urabandikwa muri sisitemu.")
            else:
                st.dataframe(df_abakozi, use_container_width=True)
                
                # Button yo gukurura Excel
                with open(FILE_ABAKOZI, "rb") as f:
                    st.download_button(
                        label="📥 Kurura Urutonde lwa Excel (Download)",
                        data=f,
                        file_name="Abakozi_GS_Rurembo.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
        except Exception as e:
            st.error(f"Harimo ikosa mu gusoma idosiye: {e}")

    # TAB 2: Kwandika Umukozi Mushya
    with tab2:
        st.subheader("Form yo Kwandika Umukozi Mushya")
        
        with st.form(key="form_umukozi", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                amazina = st.text_input("Amazina Yombi ya Umukozi *")
                id_no = st.text_input("Numero y'Indangamuntu (ID) *")
                phone = st.text_input("Numero ya Telefoni")
                
            with col2:
                post = st.text_input("Umurimo / Post (Urugero: Umuzamu, Umutetsi, Accountant...)")
                umushahara = st.number_input("Umushahara w'Ukwezi (Frw)", min_value=0, step=1000)
                date_start = st.date_input("Itariki y'Amasezerano")
            
            btn_save = st.form_submit_button("💾 Bika Umukozi muri Excel")
            
            if btn_save:
                if not amazina or not id_no:
                    st.error("Ushobora kuba wataye Amazina cyangwa Indangamuntu! Nyamuneka uzuzuze.")
                else:
                    df_old = pd.read_excel(FILE_ABAKOZI, engine="openpyxl")
                    new_data = pd.DataFrame([{
                        "Indangamuntu (ID)": str(id_no),
                        "Amazina Yombi": amazina,
                        "Umurimo / Post": post,
                        "Telefoni": str(phone),
                        "Umushahara (Frw)": umushahara,
                        "Itariki Amasezerano Atangirira": str(date_start)
                    }])
                    
                    df_updated = pd.concat([df_old, new_data], ignore_index=True)
                    df_updated.to_excel(FILE_ABAKOZI, index=False, engine="openpyxl")
                    
                    st.success(f"Umukozi **{amazina}** yabitswe neza muri Excel!")
                    st.rerun()

# --- PAGE 2: DASHBOARD ---
elif menu == "Dashboard":
    st.title("🏫 GS Rurembo - Dashboard")
    st.write("Murakaza neza mu sisitemu yo gucunga amakuru ya GS Rurembo.")
    
    col1, col2 = st.columns(2)
    with col1:
        df_a = pd.read_excel(FILE_ABAKOZI, engine="openpyxl")
        st.metric(label="Bose Hamwe Abakozi Banditse", value=len(df_a))
    with col2:
        df_s = pd.read_excel(FILE_STOCK, engine="openpyxl")
        st.metric(label="Ibicuruzwa Biri muri Stock", value=len(df_s))

# --- PAGE 3: STOCK ---
elif menu == "Stock / Ububiko":
    st.title("📦 Gucunga Stock / Ububiko")
    df_stock = pd.read_excel(FILE_STOCK, engine="openpyxl")
    st.dataframe(df_stock, use_container_width=True)

# --- PAGE 4: RAPORO ---
elif menu == "Raporo":
    st.title("📊 Raporo n'Imbonerahamwe")
    st.info("Iyi page ifite raporo z'ubucungamutungo na Stock.")
