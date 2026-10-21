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
    
    # 2. Gusaba ibikoresho (Requests)
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

# --- SESSION STATE FOR LOGIN ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

# --- LOGIN SCREEN ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; color: #2c3e50;'>🏫 GS Rurembo - Stock Management System</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #7f8c8d;'>Nyamuneka Injira muri System</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("🔑 Injira (Login)")
            
            if submit:
                # Urugero rwa Konti zashyizwemo
                if username == "admin" and password == "123":
                    st.session_state.logged_in = True
                    st.session_state.username = "Admin (Bursar)"
                    st.session_state.role = "Admin"
                    st.success("Winjiriye neza!")
                    st.rerun()
                elif username == "staff" and password == "123":
                    st.session_state.logged_in = True
                    st.session_state.username = "Staff (Teacher)"
                    st.session_state.role = "Staff"
                    st.success("Winjiriye neza!")
                    st.rerun()
                else:
                    st.error("❌ Username cyangwa Password si byo!")
                    
        st.info("💡 **Gerageza kwinjira ukoresha:**\n* Admin: `admin` / `123`\n* Staff: `staff` / `123`")

# --- MAIN APP (NYUMA YO KWINJIRA) ---
else:
    # Header Title
    st.markdown("<h1>🏫 GS Rurembo - Stock Management System</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: #27ae60; font-size: 15px;'>Mwaraho, <b>{st.session_state.username}</b> mwageze muri System.</p>", unsafe_allow_html=True)
    st.markdown("---")

    # Sidebar Navigation bitewe na Role
    st.sidebar.markdown(f"👤 **Uwinjiye:** {st.session_state.username}")
    if st.sidebar.button("🚪 Gusohoka (Logout)"):
        st.session_state.logged_in = False
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown("## 🧭 Menu Nkuru")

    if st.session_state.role == "Staff":
        menu = ["📝 Gusaba Igikoresho", "📦 Reba Ibiri mu Bubiko"]
    else:
        menu = ["📊 Dashboard", "✅ Kwemeza Ibyasabwe", "📦 Stock Status (Mu Bubiko)", "📤 Gusohora Ibikoresho", "📋 Raporo n'Amasinya"]

    choice = st.sidebar.selectbox("Hitamo igice:", menu)

    conn = sqlite3.connect("stock_management.db")
    cursor = conn.cursor()

    # 1. GUSABA IGIKORESHO (STAFF)
    if choice == "📝 Gusaba Igikoresho":
        st.subheader("📝 Form yo Gusaba Igikoresho mu Bubiko")
        
        cursor.execute("SELECT name FROM stock")
        items = [r[0] for r in cursor.fetchall()]
        
        with st.form("request_form"):
            selected_item = st.selectbox("Hitamo Igikoresho", items)
            qty = st.number_input("Ingano Usaba (Quantity)", min_value=1, step=1)
            dept = st.text_input("Ishami / Department (Urugero: Primary, O'Level)")
            
            submitted = st.form_submit_button("Ohereza Ubusabe")
            
            if submitted:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute(
                    "INSERT INTO requests (item_name, quantity, requester, department, status, date_time) VALUES (?, ?, ?, ?, 'Pending', ?)",
                    (selected_item, qty, st.session_state.username, dept, now)
                )
                conn.commit()
                st.success("✅ Ubusabe bwawe bwoherejwe neza kuri Admin!")

    # 2. DASHBOARD (ADMIN)
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
            st.metric(label="Ubusabe Butegereje Kwemezwa", value=pending_requests)

    # 3. KWEMEZA IBYSABWE (APPROVE / REJECT - ADMIN)
    elif choice == "✅ Kwemeza Ibyasabwe":
        st.subheader("✅ Gusuzuma no Kwemeza Ubusabe bw'Abakozi")
        
        cursor.execute("SELECT id, item_name, quantity, requester, department, date_time FROM requests WHERE status = 'Pending'")
        pending_rows = cursor.fetchall()
        
        if pending_rows:
            for r in pending_rows:
                req_id, item_name, qty, requester, dept, date_time = r
                with st.expander(f"📦 {item_name} ({qty} pcs) - Yasabwe na {requester}"):
                    st.write(f"📅 Itariki: {date_time} | Department: {dept}")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button(f"✅ Emeza #{req_id}", key=f"app_{req_id}"):
                            cursor.execute("SELECT quantity FROM stock WHERE name = ?", (item_name,))
                            stock_res = cursor.fetchone()
                            if stock_res and stock_res[0] >= qty:
                                new_qty = stock_res[0] - qty
                                cursor.execute("UPDATE stock SET quantity = ? WHERE name = ?", (new_qty, item_name))
                                cursor.execute("UPDATE requests SET status = 'Approved' WHERE id = ?", (req_id,))
                                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                cursor.execute(
                                    "INSERT INTO stock_out (item_name, quantity, received_by, department, date_time) VALUES (?, ?, ?, ?, ?)",
                                    (item_name, qty, requester, dept, now)
                                )
                                conn.commit()
                                st.success("Ubusabe bwemejwe neza!")
                                st.rerun()
                            else:
                                st.error("❌ Ingano iri mu bubiko iratoya kuruta iyasabwe!")
                    with col_b:
                        if st.button(f"❌ Anga #{req_id}", key=f"rej_{req_id}"):
                            cursor.execute("UPDATE requests SET status = 'Rejected' WHERE id = ?", (req_id,))
                            conn.commit()
                            st.warning("Ubusabe bwanzwe.")
                            st.rerun()
        else:
            st.info("Nta busabe bushya butegereje.")

    # 4. STOCK STATUS
    elif choice == "📦 Stock Status (Mu Bubiko)" or choice == "📦 Reba Ibiri mu Bubiko":
        st.subheader("📦 Urutonde rw'Ibikoresho biri mu Bubiko")
        cursor.execute("SELECT id, name, category, quantity, unit, min_alert FROM stock")
        rows = cursor.fetchall()
        
        table_data = []
        for r in rows:
            status = "⚠️ Byenda gushira" if r[3] <= r[5] else "✅ Bihagije"
            table_data.append({
                "ID": r[0], "Izina": r[1], "Icyiciro": r[2],
                "Ingano": f"{r[3]} {r[4]}", "Min Alert": r[5], "Imiterere": status
            })
        st.dataframe(table_data, use_container_width=True)

    # 5. GUSOHORA IBIKORESHO (ADMIN)
    elif choice == "📤 Gusohora Ibikoresho":
        st.subheader("📤 Gusohora Igikoresho Ako kanya")
        cursor.execute("SELECT name FROM stock")
        items = [r[0] for r in cursor.fetchall()]
        
        with st.form("direct_out"):
            selected_item = st.selectbox("Hitamo Igikoresho", items)
            qty = st.number_input("Ingano", min_value=1, step=1)
            receiver = st.text_input("Izina ry'Uwakiriye")
            dept = st.text_input("Department")
            
            if st.form_submit_button("Bika Ibyasohotse"):
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

    # 6. RAPORO N'AMASINYA
    elif choice == "📋 Raporo n'Amasinya":
        st.subheader("📋 Amateka y'Ibikoresho Byasohotse n'Ababyakiye")
        cursor.execute("SELECT id, item_name, quantity, received_by, department, date_time FROM stock_out ORDER BY id DESC")
        rows = cursor.fetchall()
        
        history_data = []
        for r in rows:
            history_data.append({
                "ID": r[0], "Igikoresho": r[1], "Ingano": r[2],
                "Uwakiriye": r[3], "Department": r[4], "Itariki": r[5], "Gusinya": "......................"
            })
        st.dataframe(history_data, use_container_width=True)

    conn.close()