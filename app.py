from datetime import datetime
import sqlite3
import streamlit as st

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="GS Rurembo Stock System",
    page_icon="📦",
    layout="wide"
)

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect("stock_management.db")
    cursor = conn.cursor()
    
    # 1. Ibikoresho biri mu bubiko
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            quantity INTEGER NOT NULL,
            unit TEXT,
            min_alert INTEGER
        )
    """)
    
    # 2. Gusaba ibikoresho (Requests) n'ibyemejwe (Approval)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            requester TEXT NOT NULL,
            department TEXT,
            status TEXT DEFAULT 'Pending',
            date_time TEXT NOT NULL
        )
    """)
    
    # 3. Ibyasohotse byemewe (Stock Out History)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_out (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            received_by TEXT NOT NULL,
            department TEXT,
            date_time TEXT NOT NULL
        )
    """)
    
    # Data z'icyitegererezo
    cursor.execute("SELECT COUNT(*) FROM stock")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO stock (name, category, quantity, unit, min_alert) VALUES ('Pens', 'Office', 47, 'pcs', 5)")
        cursor.execute("INSERT INTO stock (name, category, quantity, unit, min_alert) VALUES ('A4 Papers', 'Office', 15, 'ream', 10)")
        conn.commit()
    conn.close()

init_db()

# --- HEADER TITLE ---
st.markdown("<h1>🏫 GS Rurembo - Stock Management System</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #7f8c8d; font-size: 16px;'>Ubutuganya n'Ubugenzuzi bw'Ibikoresho by'Ikigo</p>", unsafe_allow_html=True)
st.markdown("---")

# --- SIDEBAR: USER ROLE & NAVIGATION ---
st.sidebar.markdown("## 🔐 Hitamo Uwinjira (Role)")
user_role = st.sidebar.selectbox("Uuri gukoresha App:", ["Teacher / Staff (Gusaba)", "Admin / Bursar (Kubigenzura)"])

st.sidebar.markdown("---")
st.sidebar.markdown("## 🧭 Menu")

if user_role == "Teacher / Staff (Gusaba)":
    menu = ["📝 Gusaba Igikoresho (Request)", "📦 Reba Ibiri mu Bubiko"]
else:
    menu = ["📊 Dashboard", "✅ Kwemeza Ibyasabwe (Approvals)", "📦 Stock Status (Mu Bubiko)", "📤 Gusohora Ibikoresho", "📋 Raporo n'Amasinya"]

choice = st.sidebar.selectbox("Hitamo igice:", menu)

conn = sqlite3.connect("stock_management.db")
cursor = conn.cursor()

# ==========================================
# 1. GUSABA IGIKORESHO (STAFF / TEACHER)
# ==========================================
if choice == "📝 Gusaba Igikoresho (Request)":
    st.subheader("📝 Form yo Gusaba Igikoresho mu Bubiko")
    
    cursor.execute("SELECT name FROM stock")
    items = [r[0] for r in cursor.fetchall()]
    
    with st.form("request_form"):
        col1, col2 = st.columns(2)
        with col1:
            selected_item = st.selectbox("Hitamo Igikoresho", items)
            qty = st.number_input("Ingano Usaba (Quantity)", min_value=1, step=1)
        with col2:
            requester = st.text_input("Izina ryawe (Requester Name)")
            dept = st.text_input("Ishami / Department (Urugero: Primary, O'Level)")
            
        submitted = st.form_submit_button("Ohereza Ubusabe (Submit Request)")
        
        if submitted:
            if requester.strip() != "":
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute(
                    "INSERT INTO requests (item_name, quantity, requester, department, status, date_time) VALUES (?, ?, ?, ?, 'Pending', ?)",
                    (selected_item, qty, requester, dept, now)
                )
                conn.commit()
                st.success("✅ Ubusabe bwawe bwoherejwe neza! Tegereza ko Admin abyemeza.")
            else:
                st.warning("⚠️ Nyamuneka shyiramo izina ryawe.")

# ==========================================
# 2. DASHBOARD (ADMIN)
# ==========================================
elif choice == "📊 Dashboard":
    st.subheader("Incamake y'Ububiko")
    
    cursor.execute("SELECT COUNT(*) FROM stock")
    total_items = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM requests WHERE status = 'Pending'")
    pending_requests = cursor.fetchone()[0]
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Ibikoresho Byose mu Bubiko", value=total_items)
    with col2:
        st.metric(label="Ubusabe Butegereje Kwemezwa (Pending)", value=pending_requests)

# ==========================================
# 3. KWEMEZA IBYSABWE (APPROVALS - ADMIN)
# ==========================================
elif choice == "✅ Kwemeza Ibyasabwe (Approvals)":
    st.subheader("✅ Gusuzuma no Kwemeza Ubusabe bw'Abakozi (Approve / Reject)")
    
    cursor.execute("SELECT id, item_name, quantity, requester, department, date_time FROM requests WHERE status = 'Pending'")
    pending_rows = cursor.fetchall()
    
    if pending_rows:
        for r in pending_rows:
            req_id, item_name, qty, requester, dept, date_time = r
            
            with st.expander(f"📦 {item_name} ({qty} pcs) - Yasabwe na {requester} ({dept})"):
                st.write(Est := f"📅 Itariki: {date_time}")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button(f"✅ Emeza (Approve) #{req_id}", key=f"app_{req_id}"):
                        # Reba niba ibikoresho bihagije mu bubiko
                        cursor.execute("SELECT quantity FROM stock WHERE name = ?", (item_name,))
                        stock_res = cursor.fetchone()
                        
                        if stock_res and stock_res[0] >= qty:
                            new_qty = stock_res[0] - qty
                            # Hindura stock
                            cursor.execute("UPDATE stock SET quantity = ? WHERE name = ?", (new_qty, item_name))
                            # Hindura status ya request iba Approved
                            cursor.execute("UPDATE requests SET status = 'Approved' WHERE id = ?", (req_id,))
                            # Bika muri stock_out ngo bifatire n'amageza/amasinya
                            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            cursor.execute(
                                "INSERT INTO stock_out (item_name, quantity, received_by, department, date_time) VALUES (?, ?, ?, ?, ?)",
                                (item_name, qty, requester, dept, now)
                            )
                            conn.commit()
                            st.success(f"Ubusabe bwemejwe kandi ibikoresho byasohowe mu bubiko!")
                            st.rerun()
                        else:
                            st.error("❌ Ntibyashobotse: Ingano iri mu bubiko iratoya kuruta iyasabwe!")
                            
                with col_b:
                    if st.button(f"❌ Anga (Reject) #{req_id}", key=f"rej_{req_id}"):
                        cursor.execute("UPDATE requests SET status = 'Rejected' WHERE id = ?", (req_id,))
                        conn.commit()
                        st.warning("Ubusabe bwanzwe.")
                        st.rerun()
    else:
        st.info("Nta busabe bushya butegereje kwemezwa.")

# ==========================================
# 4. STOCK STATUS (MU BUBIKO)
# ==========================================
elif choice == "📦 Stock Status (Mu Bubiko)" or choice == "📦 Reba Ibiri mu Bubiko":
    st.subheader("📦 Urutonde rw'Ibikoresho biri mu Bubiko")
    
    cursor.execute("SELECT id, name, category, quantity, unit, min_alert FROM stock")
    rows = cursor.fetchall()
    
    table_data = []
    for r in rows:
        status = "⚠️ Byenda gushira" if r[3] <= r[5] else "✅ Bihagije"
        table_data.append({
            "ID": r[0],
            "Izina ry'Igikoresho": r[1],
            "Icyiciro": r[2],
            "Ingano": f"{r[3]} {r[4]}",
            "Min Alert": r[5],
            "Imiterere": status
        })
    st.dataframe(table_data, use_container_width=True)

# ==========================================
# 5. GUSOHORA IBIKORESHO (DIRECT STOCK OUT - ADMIN)
# ==========================================
elif choice == "📤 Gusohora Ibikoresho":
    st.subheader("📤 Gusohora Igikoresho Ako kanya (Direct Stock Out)")
    
    cursor.execute("SELECT name FROM stock")
    items = [r[0] for r in cursor.fetchall()]
    
    with st.form("direct_out"):
        selected_item = st.selectbox("Hitamo Igikoresho", items)
        qty = st.number_input("Ingano", min_value=1, step=1)
        receiver = st.text_input("Izina ry'Uwakiriye")
        dept = st.text_input("Department")
        
        submitted = st.form_submit_button("Bika Ibyasohotse")
        if submitted:
            cursor.execute("SELECT quantity FROM stock WHERE name = ?", (selected_item,))
            curr = cursor.fetchone()[0]
            if curr >= qty:
                cursor.execute("UPDATE stock SET quantity = ? WHERE name = ?", (curr - qty, selected_item))
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("INSERT INTO stock_out (item_name, quantity, received_by, department, date_time) VALUES (?, ?, ?, ?, ?)", 
                               (selected_item, qty, receiver, dept, now))
                conn.commit()
                st.success("Igikoresho cyasohowe neza!")
            else:
                st.error("Ingano irasumba iyiri mu bubiko!")

# ==========================================
# 6. RAPORO N'AMASINYA
# ==========================================
elif choice == "📋 Raporo n'Amasinya":
    st.subheader("📋 Amateka y'Ibikoresho Byasohotse n'Ababyakiye")
    
    cursor.execute("SELECT id, item_name, quantity, received_by, department, date_time FROM stock_out ORDER BY id DESC")
    rows = cursor.fetchall()
    
    history_data = []
    for r in rows:
        history_data.append({
            "ID": r[0],
            "Igikoresho": r[1],
            "Ingano": r[2],
            "Uwakiriye": r[3],
            "Department": r[4],
            "Itariki n'Isaha": r[5],
            "Umwanya wo Gusinya": "......................"
        })
    st.dataframe(history_data, use_container_width=True)

conn.close()