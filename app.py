import streamlit as st
import pandas as pd
import sqlite3
import datetime
import io

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
    
    # Table ya Payroll (Imishahara & RSSB / CBHI)
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
    
    # Kureba niba table ya payroll ifite columns zose
    for col in ["pension REAL", "cbhi REAL", "maternity REAL", "other_loans REAL", "total_deductions REAL"]:
        try:
            c.execute(f"ALTER TABLE payroll ADD COLUMN {col}")
        except:
            pass

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
# UBURYO BWO KUREMA EXCEL IFITE AMABARA (PROFESSIONAL EXCEL)
# ---------------------------------------------------------
def generate_colored_excel(df, sheet_name="Report"):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]

        from openpyxl.styles import PatternFill, Font, Alignment, Border, Side

        header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        
        thin_border = Border(
            left=Side(style='thin', color='D9D9D9'),
            right=Side(style='thin', color='D9D9D9'),
            top=Side(style='thin', color='D9D9D9'),
            bottom=Side(style='thin', color='D9D9D9')
        )
        data_font = Font(name="Calibri", size=11)
        zebra_fill = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")

        for col_num in range(1, len(df.columns) + 1):
            cell = worksheet.cell(row=1, column=col_num)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        for row_num in range(2, len(df) + 2):
            for col_num in range(1, len(df.columns) + 1):
                cell = worksheet.cell(row=row_num, column=col_num)
                cell.font = data_font
                cell.border = thin_border
                cell.alignment = Alignment(vertical="center")
                if row_num % 2 == 0:
                    cell.fill = zebra_fill

        for col in worksheet.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = col[0].column_letter
            worksheet.column_dimensions[col_letter].width = max(max_len + 3, 12)

    return output.getvalue()


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
    
    with tab_s1:
        st.subheader("📋 Urutonde rw'Ibicuruzwa na Quantity iri muri Ububiko")
        conn = sqlite3.connect(DB_FILE)
        df_stock = pd.read_sql_query("SELECT * FROM stock", conn)
        conn.close()
        
        if df_stock.empty:
            st.info("Nta gicuruzwa kiragera muri stock.")
        else:
            st.dataframe(df_stock, use_container_width=True)
            df_export = df_stock[['item_name', 'category', 'quantity', 'unit']].copy()
            df_export.columns = ["Izina ry'Igicuruzwa", "Icyiciro (Category)", "Ingano (Quantity)", "Igipimo (Unit)"]
            
            excel_data = generate_colored_excel(df_export, sheet_name="Stock_Balance")
            st.download_button(
                label="📥 Kurura Stock Balance (Professional Excel ya Color)",
                data=excel_data,
                file_name=f"GS_Rurembo_Stock_{datetime.date.today()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    with tab_s2:
        st.subheader("📥 Ongeraho Igicuruzwa cyangwa Ingano Muri Stock")
        col1, col2 = st.columns(2)
        with col1:
            item_name = st.text_input("Izina ry'Igicuruzwa *")
            category = st.text_input("Icyiciro (Category / Urugero: Isukari, Ibipapuro...)")
        with col2:
            qty = st.number_input("Ingano Uyongereye (Quantity)", min_value=1, step=1)
            unit = st.text_input("Igipimo (e.g. Kg, Pcs, Liters)")
            
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
                        st.success("Ubusabe bwawe bwoherejwe neza! Mutegereze approval.")
                        st.rerun()
                else:
                    st.warning("Uzuza izina ry'usaba n'igicuruzwa!")

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
            df_emp_export = df_emp[['emp_id', 'full_name', 'phone', 'position', 'contract_type', 'basic_salary', 'start_date', 'end_date']].copy()
            df_emp_export.columns = ["Indangamuntu (ID)", "Amazina Yombi", "Telefoni", "Umwanya", "Amasezerano", "Umushahara w'Ibanze", "Itariki y'Itangiriro", "Itariki y'Iherezo"]
            
            excel_emp = generate_colored_excel(df_emp_export, sheet_name="Abakozi")
            st.download_button(
                label="📥 Kurura Urutonde rw'Abakozi (Professional Excel ya Color)",
                data=excel_emp,
                file_name=f"GS_Rurembo_Abakozi_{datetime.date.today()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    with tab2:
        st.subheader("✍️ Form yo Kwandika no Kubika Amasezerano y'Umukozi")
        col1, col2 = st.columns(2)
        with col1:
            emp_id = st.text_input("Numero y'Indangamuntu (ID)")
            full_name = st.text_input
