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
    
    # 1. Table y'Ibikoresho
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            category TEXT,
            quantity INTEGER NOT NULL,
            unit TEXT,
            min_alert INTEGER
        )
    """)
    
    # 2. Table y'Inyandiko z'Ibyinjira n'Ibyasohoka zose (Store Card Ledger)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS store_ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            date_time TEXT NOT NULL,
            transaction_type TEXT NOT NULL, -- 'Stock In' cyangwa 'Stock Out'
            quantity_in INTEGER DEFAULT 0,
            quantity_out INTEGER DEFAULT 0,
            balance INTEGER NOT NULL,
            person_in_charge TEXT NOT NULL,
            reference_notes TEXT
        )
    """)
    
    # 3. Table y'Ubusabe bw'Ibyasabwe (Requests)
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
    
    # Data z'icyitegererezo niba database ari nshya
    cursor.execute("SELECT COUNT(*) FROM stock")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO stock (name, category, quantity, unit, min_alert) VALUES ('Pens', 'Office', 50, 'pcs', 5)")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO store_ledger (item_name, date_time, transaction_type, quantity_in, quantity_out, balance, person_in_charge, reference_notes)
            VALUES ('Pens', ?, 'Stock In', 50, 0, 50, 'Initial Stock', 'Kubanza kwinjiza mu bubiko')
        """, (now,))
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
                    
        st.info("💡 **Konti zo kugerageza:**\n* Admin: `admin` / `123`\n* Staff: `staff` / `123`")

# --- MAIN APP (AFTER LOGIN) ---
else:
    st.markdown("<h1>🏫 GS Rurembo - Stock Management System</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: #27ae60; font-size: 15px;'>Mwaraho, <b>{st.session_state.username}</b> mwageze muri System.</p>", unsafe_allow_html=True)
    st.markdown("---")

    # Navigation Sidebar
    st.sidebar.markdown(f"👤 **Uwinjiye:** {st.session_state.username}")
    if st.sidebar.button("🚪 Gusohoka (Logout)"):
        st.session_state.logged_in = False
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown("## 🧭 Menu Nkuru")

    if st.session_state.role == "Staff":
        menu = ["📝 Gusaba Igikoresho", "📜 Store Card (Fiche de Stock)", "📦 Reba Ibiri mu Bubiko"]
    else:
        menu = ["📊 Dashboard", "📜 Store Card (Fiche de Stock)", "📥 Kwandika Ibyinjira (Stock In)", "✅ Kwemeza Ibyasabwe", "📦 Stock Status (Mu Bubiko)", "📤 Gusohora Ibikoresho"]

    choice = st.sidebar.selectbox("Hitamo igice:", menu)

    conn = sqlite3.connect("stock_management.db")
    cursor = conn.cursor()

    # 1. STORE CARD (FICHE DE STOCK)
    if choice == "📜 Store Card (Fiche de Stock)":
        st.subheader("📜 Store Ledger Card (Fiche de Stock / Inyandiko y'Igikoresho)")
        
        cursor.execute("SELECT name FROM stock")
        stock_items = [r[0] for r in cursor.fetchall()]
        
        if stock_items:
            selected_card_item = st.selectbox("Hitamo Igikoresho ukeneye kurebera Fiche de Stock:", stock_items)
            
            # Fetch item current stock
            cursor.execute("SELECT quantity, unit, min_alert, category FROM stock WHERE name = ?", (selected_card_item,))
            item_info = cursor.fetchone()
            
            if item_info:
                curr_qty, unit, min_alert, category = item_info
                
                # Card Metrics Summary
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Izina ry'Igikoresho", f"{selected_card_item} ({category})")
                col_b.metric("Ingano iri mu Bubiko ubu", f"{curr_qty} {unit}")
                col_c.metric("Uragereranyo rwa Min Alert", f"{min_alert} {unit}")
                
                st.markdown("---")
                st.markdown(f"#### 📄 Amateka yose y'Ibyinjiriye n'Ibyasohotse kuri **{selected_card_item}**")
                
                cursor.execute("""
                    SELECT date_time, transaction_type, quantity_in, quantity_out, balance, person_in_charge, reference_notes 
                    FROM store_ledger 
                    WHERE item_name = ? 
                    ORDER BY id ASC
                """, (selected_card_item,))
                ledger_rows = cursor.fetchall()
                
                card_data = []
                for r in ledger_rows:
                    card_data.append({
                        "Itariki n'Isaha": r[0],
                        "Ubwoko (Type)": r[1],
                        "Ibyinjiriye (+)": r[2] if r[2] > 0 else "-",
                        "Ibyasohotse (-)": r[3] if r[3] > 0 else "-",
                        "Balance (Igirasigaye)": r[4],
                        "Ufite Inshingano / Uwakiriye": r[5],
                        "Ibisobanuro / Note": r[6]
                    })
                
                if card_data:
                    st.dataframe(card_data, use_container_width=True)
                else:
                    st.info("Nta nyandiko iratunganywa kuri uyu muhatsi.")
        else:
            st.warning("Nta bikoresho biraba mu bubiko.")

    # 2. KWANDIKA IBYINJIRA (STOCK IN - ADMIN)
    elif choice == "📥 Kwandika Ibyinjira (Stock In)":
        st.subheader("📥 Kwandika Igikoresho Gishyashya cyangwa Icyinjiriye mu Bubiko")
        
        cursor.execute("SELECT name FROM stock")
        existing_items = [r[0] for r in cursor.fetchall()]
        
        tab1, tab2 = st.tabs(["Kongera Ingano ku Gikoresho Gisanzweho", "Kwandika Igikoresho Gishyashya"])
        
        with tab1:
            if existing_items:
                with st.form("add_stock_form"):
                    item_name = st.selectbox("Hitamo Igikoresho", existing_items)
                    add_qty = st.number_input("Ingano yinjijwe", min_value=1, step=1)
                    supplier_or_note = st.text_input("Isoko / Umuguzi / Note (Urugero: Supplier XYZ)")
                    
                    if st.form_submit_button("Bika Ibyinjiriye"):
                        cursor.execute("SELECT quantity FROM stock WHERE name = ?", (item_name,))
                        curr = cursor.fetchone()[0]
                        new_balance = curr + add_qty
                        
                        # Update Stock
                        cursor.execute("UPDATE stock SET quantity = ? WHERE name = ?", (new_balance, item_name))
                        
                        # Record in Store Ledger
                        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        cursor.execute("""
                            INSERT INTO store_ledger (item_name, date_time, transaction_type, quantity_in, quantity_out, balance, person_in_charge, reference_notes)
                            VALUES (?, ?, 'Stock In', ?, 0, ?, ?, ?)
                        """, (item_name, now, add_qty, new_balance, st.session_state.username, supplier_or_note))
                        
                        conn.commit()
                        st.success(f"✅ Ingano ya {item_name} yongereweho {add_qty}! Balance nshya ni {new_balance}.")
                        st.rerun()
            else:
                st.info("Nta bikoresho birabaho muri system.")

        with tab2:
            with st.form("new_item_form"):
                new_item_name = st.text_input("Izina ry'Igikoresho Gishyashya")
                category = st.text_input("Icyiciro (Category - Urugero: Office, Class)")
                init_qty = st.number_input("Ingano y'Ibanze (Initial Quantity)", min_value=1, step=1)
                unit = st.text_input("Igipimo (Unit - Urugero: pcs, reams, boxes)", value="pcs")
                min_alert = st.number_input("Min Alert Threshold", min_value=1, value=5)
                
                if st.form_submit_button("Bika Igikoresho Gishyashya"):
                    if new_item_name.strip() != "":
                        try:
                            cursor.execute("INSERT INTO stock (name, category, quantity, unit, min_alert) VALUES (?, ?, ?, ?, ?)",
                                           (new_item_name, category, init_qty, unit, min_alert))
                            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            cursor.execute("""
                                INSERT INTO store_ledger (item_name, date_time, transaction_type, quantity_in, quantity_out, balance, person_in_charge, reference_notes)
                                VALUES (?, ?, 'Stock In', ?, 0, ?, ?, 'New Item Created')
                            """, (new_item_name, now, init_qty, init_qty, st.session_state.username))
                            conn.commit()
                            st.success(f"✅ Igikoresho {new_item_name} cyanditswe neza!")
                            st.rerun()
                        except sqlite3.IntegrityError:
                            st.error("❌ Igikoresho gisa n'iki gisanzwe gihari!")
                    else:
                        st.warning("⚠️ Wandike izina ry'igikoresho.")

    # 3. GUSABA IGIKORESHO (STAFF)
    elif choice == "📝 Gusaba Igikoresho":
        st.subheader("📝 Form yo Gusaba Igikoresho mu Bubiko")
        cursor.execute("SELECT name FROM stock")
        items = [r[0] for r in cursor.fetchall()]
        
        with st.form("request_form"):
            selected_item = st.selectbox("Hitamo Igikoresho", items)
            qty = st.number_input("Ingano Usaba (Quantity)", min_value=1, step=1)
            dept = st.text_input("Ishami / Department (Urugero: Primary, O'Level)")
            
            if st.form_submit_button("Ohereza Ubusabe"):
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute(
                    "INSERT INTO requests (item_name, quantity, requester, department, status, date_time) VALUES (?, ?, ?, ?, 'Pending', ?)",
                    (selected_item, qty, st.session_state.username, dept, now)
                )
                conn.commit()
                st.success("✅ Ubusabe bwawe bwoherejwe neza kuri Admin!")

    # 4. DASHBOARD (ADMIN)
    elif choice == "📊 Dashboard":
        st.subheader("Incamake y'Ububiko")
        cursor.execute("SELECT COUNT(*) FROM stock")
        total_items = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM requests WHERE status = 'Pending'")
        pending_requests = cursor.fetchone()[0]
        
        col1, col2 = st.columns(2)
        col1.metric(label="Ibikoresho Byose mu Bubiko", value=total_items)
        col2.metric(label="Ubusabe Butegereje Kwemezwa", value=pending_requests)

    # 5. KWEMEZA IBYSABWE (ADMIN)
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
                                new_balance = stock_res[0] - qty
                                cursor.execute("UPDATE stock SET quantity = ? WHERE name = ?", (new_balance, item_name))
                                cursor.execute("UPDATE requests SET status = 'Approved' WHERE id = ?", (req_id,))
                                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                
                                # Record in Store Ledger
                                cursor.execute("""
                                    INSERT INTO store_ledger (item_name, date_time, transaction_type, quantity_in, quantity_out, balance, person_in_charge, reference_notes)
                                    VALUES (?, ?, 'Stock Out', 0, ?, ?, ?, ?)
                                """, (item_name, now, qty, new_balance, requester, f"Approved for {dept}"))
                                
                                conn.commit()
                                st.success("Ubusabe bwemejwe neza kandi bwanditswe mu Store Card!")
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

    # 6. STOCK STATUS
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

    # 7. GUSOHORA IBIKORESHO (ADMIN)
    elif choice == "📤 Gusohora Ibikoresho":
        st.subheader("📤 Gusohora Igikoresho Ako kanya (Direct Stock Out)")
        cursor.execute("SELECT name FROM stock")
        items = [r[0] for r in cursor.fetchall()]
        
        with st.form("direct_out"):
            selected_item = st.selectbox("Hitamo Igikoresho", items)
            qty = st.number_input("Ingano", min_value=1, step=1)
            receiver = st.text_input("Izina ry'Uwakiriye")
            dept = st.text_input("Department / Note")
            
            if st.form_submit_button("Bika Ibyasohotse"):
                cursor.execute("SELECT quantity FROM stock WHERE name = ?", (selected_item,))
                curr = cursor.fetchone()[0]
                if curr >= qty:
                    new_balance = curr - qty
                    cursor.execute("UPDATE stock SET quantity = ? WHERE name = ?", (new_balance, selected_item))
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Record in Store Ledger
                    cursor.execute("""
                        INSERT INTO store_ledger (item_name, date_time, transaction_type, quantity_in, quantity_out, balance, person_in_charge, reference_notes)
                        VALUES (?, ?, 'Stock Out', 0, ?, ?, ?, ?)
                    """, (selected_item, now, qty, new_balance, receiver, dept))
                    
                    conn.commit()
                    st.success("Igikoresho cyasohowe neza kandi cyanditswe mu Store Card!")
                else:
                    st.error("Ingano irasumba iyiri mu bubiko!")

    conn.close()