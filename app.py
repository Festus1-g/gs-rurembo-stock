from datetime import datetime
import sqlite3
import streamlit as st

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="GS Rurembo Stock System",
    page_icon="📦",
    layout="wide"
)

# --- CUSTOM CSS STYLING ---
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stSidebar {
        background-color: #2c3e50;
    }
    h1 {
        color: #2c3e50;
        font-weight: 700;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 5px solid #2980b9;
        margin-bottom: 20px;
    }
    .alert-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 5px solid #e74c3c;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect("stock_management.db")
    cursor = conn.cursor()
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
    # Data y'icyitegererezo niba ari nshya
    cursor.execute("SELECT COUNT(*) FROM stock")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO stock (name, category, quantity, unit, min_alert) VALUES ('Pens', 'Office', 47, 'pcs', 5)")
        cursor.execute("INSERT INTO stock (name, category, quantity, unit, min_alert) VALUES ('A4 Papers', 'Office', 3, 'ream', 10)")
        cursor.execute("INSERT INTO stock (name, category, quantity, unit, min_alert) VALUES ('Chalk', 'Classroom', 2, 'boxes', 5)")
        conn.commit()
    conn.close()

init_db()

# --- HEADER TITLE ---
st.markdown("<h1>🏫 GS Rurembo - Stock Management System</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #7f8c8d; font-size: 16px;'>Ubutuganya n'Ubugenzuzi bw'Ibikoresho by'Ikigo</p>", unsafe_allow_html=True)
st.markdown("---")

# --- SIDEBAR NAVIGATION ---
st.sidebar.markdown("## 🧭 Menu Nkuru")
menu = ["📊 Dashboard", "📦 Stock Status (Mu Bubiko)", "📤 Kwandika Ibyasohoka (Stock Out)", "📋 Raporo n'Amasinya"]
choice = st.sidebar.selectbox("Hitamo igice wifuza:", menu)

conn = sqlite3.connect("stock_management.db")
cursor = conn.cursor()

# ==========================================
# 1. DASHBOARD
# ==========================================
if choice == "📊 Dashboard":
    st.subheader("Incamake y'Ububiko muri rusange")
    
    cursor.execute("SELECT COUNT(*) FROM stock")
    total_items = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM stock WHERE quantity <= min_alert")
    low_stock_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM stock_out")
    total_issued = cursor.fetchone()[0]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <h3>Ibikoresho Byose</h3>
                <h1 style="color: #2980b9;">{total_items}</h1>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
            <div class="alert-card">
                <h3>Ibiri munsi y'Urugero (Low Stock)</h3>
                <h1 style="color: #e74c3c;">{low_stock_count}</h1>
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <h3>Inshuro Zasohotse</h3>
                <h1 style="color: #27ae60;">{total_issued}</h1>
            </div>
        """, unsafe_allow_html=True)

# ==========================================
# 2. STOCK STATUS
# ==========================================
elif choice == "📦 Stock Status (Mu Bubiko)":
    st.subheader("📦 Urutonde rw'Ibikoresho biri mu Bubiko")
    
    search_query = st.text_input("🔍 Shakisha igikoresho...", "")
    
    if search_query:
        cursor.execute("SELECT id, name, category, quantity, unit, min_alert FROM stock WHERE name LIKE ?", (f"%{search_query}%",))
    else:
        cursor.execute("SELECT id, name, category, quantity, unit, min_alert FROM stock")
        
    rows = cursor.fetchall()
    
    # Kugaragaza nk'imbonerahamwe nziza (Table)
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
    
    if table_data:
        st.dataframe(table_data, use_container_width=True)
    else:
        st.info("Nta bikoresho bibonetse.")

# ==========================================
# 3. STOCK OUT (KWANDIKA IBYASOHOKA)
# ==========================================
elif choice == "📤 Kwandika Ibyasohoka (Stock Out)":
    st.subheader("📤 Gusohora Igikoresho mu Bubiko n'Uwakiriye")
    
    cursor.execute("SELECT name FROM stock")
    items = [r[0] for r in cursor.fetchall()]
    
    with st.form("stock_out_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            selected_item = st.selectbox("Hitamo Igikoresho", items)
            qty = st.number_input("Ingano ihabwa (Quantity)", min_value=1, step=1)
            
        with col2:
            receiver = st.text_input("Izina ry'Uwakiriye (Received By)")
            dept = st.text_input("Icyo akora / Department")
            
        submitted = st.form_submit_button("Bika Ibyasohotse (Save)")
        
        if submitted:
            if receiver.strip() != "":
                cursor.execute("SELECT quantity FROM stock WHERE name = ?", (selected_item,))
                current_qty = cursor.fetchone()[0]
                
                if current_qty >= qty:
                    new_qty = current_qty - qty
                    cursor.execute("UPDATE stock SET quantity = ? WHERE name = ?", (new_qty, selected_item))
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cursor.execute(
                        "INSERT INTO stock_out (item_name, quantity, received_by, department, date_time) VALUES (?, ?, ?, ?, ?)", 
                        (selected_item, qty, receiver, dept, now)
                    )
                    conn.commit()
                    st.success(f"✅ Igikoresho ({selected_item}) cyatanzwe neza kuri {receiver}!")
                else:
                    st.error("❌ Ingano ushaka gutanga irasumba iziri mu bubiko!")
            else:
                st.warning("⚠️ Nyamuneka shyiramo izina ry'uwakiriye.")

# ==========================================
# 4. RAPORO N'AMASINYA
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
        
    if history_data:
        st.dataframe(history_data, use_container_width=True)
    else:
        st.info("Nta mateka y'ibyasohotse araboneka.")

conn.close()