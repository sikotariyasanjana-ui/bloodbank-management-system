import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
import os

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="Blood Bank Management System",
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db.sqlite3')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    # Ensure tables exist even on fresh deploy
    cur.execute("""
    CREATE TABLE IF NOT EXISTS blood_stock (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bloodgroup VARCHAR(10) NOT NULL UNIQUE,
        unit INTEGER NOT NULL DEFAULT 0
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS donor_blooddonate (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        donor_name VARCHAR(50),
        disease VARCHAR(100) DEFAULT 'Nothing',
        age INTEGER NOT NULL,
        bloodgroup VARCHAR(10) NOT NULL,
        unit INTEGER NOT NULL DEFAULT 0,
        status VARCHAR(20) DEFAULT 'Pending',
        date DATE,
        donor_id INTEGER
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS blood_bloodrequest (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name VARCHAR(30) NOT NULL,
        patient_age INTEGER NOT NULL,
        reason VARCHAR(500) NOT NULL,
        bloodgroup VARCHAR(10) NOT NULL,
        unit INTEGER NOT NULL DEFAULT 0,
        status VARCHAR(20) DEFAULT 'Pending',
        date DATE,
        request_by_donor_id INTEGER,
        request_by_patient_id INTEGER
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS donor_donor (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        profile_pic VARCHAR(100),
        bloodgroup VARCHAR(10) NOT NULL,
        address VARCHAR(40) NOT NULL,
        mobile VARCHAR(20) NOT NULL,
        user_id INTEGER
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS patient_patient (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        profile_pic VARCHAR(100),
        age INTEGER NOT NULL,
        bloodgroup VARCHAR(10) NOT NULL,
        disease VARCHAR(100) NOT NULL,
        doctorname VARCHAR(50) NOT NULL,
        address VARCHAR(40) NOT NULL,
        mobile VARCHAR(20) NOT NULL,
        user_id INTEGER
    )
    """)
    
    # Initialize default stock if empty
    cur.execute("SELECT COUNT(*) as count FROM blood_stock")
    if cur.fetchone()['count'] == 0:
        default_groups = [('A+', 0), ('A-', 0), ('B+', 0), ('B-', 0), ('AB+', 0), ('AB-', 0), ('O+', 0), ('O-', 0)]
        cur.executemany("INSERT OR IGNORE INTO blood_stock (bloodgroup, unit) VALUES (?, ?)", default_groups)
    
    conn.commit()
    conn.close()

init_db()

# Custom CSS for polished styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 18px;
        border-left: 5px solid #dc3545;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .blood-badge {
        font-size: 1.1rem;
        font-weight: bold;
        color: #dc3545;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("🩸 Blood Bank System")
menu = st.sidebar.radio(
    "Navigation Menu",
    [
        "📊 Dashboard",
        "🩸 Donate Blood",
        "📋 Donation Management",
        "🏥 Request Blood",
        "📄 Request Management",
        "👥 Donors Directory",
        "🩺 Patients Directory",
        "⚙️ Stock Management"
    ]
)

# ----------------- 1. DASHBOARD -----------------
if menu == "📊 Dashboard":
    st.title("🩸 Blood Bank Dashboard")
    st.write("Welcome to the Blood Bank Management System. Monitor stock levels, donor contributions, and emergency requests.")

    conn = get_connection()
    
    # Summary Metrics
    stock_df = pd.read_sql_query("SELECT bloodgroup, unit FROM blood_stock ORDER BY id", conn)
    total_units = stock_df['unit'].sum() if not stock_df.empty else 0
    
    donors_count = conn.execute("SELECT COUNT(DISTINCT donor_name) FROM donor_blooddonate WHERE status='Approved'").fetchone()[0]
    total_requests = conn.execute("SELECT COUNT(*) FROM blood_bloodrequest").fetchone()[0]
    approved_requests = conn.execute("SELECT COUNT(*) FROM blood_bloodrequest WHERE status='Approved'").fetchone()[0]
    conn.close()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total Blood Units in Stock", value=f"{total_units} Units")
    with col2:
        st.metric(label="Total Active Donors", value=donors_count)
    with col3:
        st.metric(label="Total Requests Made", value=total_requests)
    with col4:
        st.metric(label="Approved Requests", value=approved_requests)

    st.markdown("---")
    st.subheader("🩸 Current Blood Stock Availability")

    if not stock_df.empty:
        cols = st.columns(4)
        for i, row in stock_df.iterrows():
            with cols[i % 4]:
                st.markdown(
                    f"""
                    <div class="metric-card" style="margin-bottom: 15px;">
                        <span class="blood-badge">{row['bloodgroup']}</span>
                        <h2 style="margin: 5px 0 0 0; color: {'#28a745' if row['unit'] > 0 else '#dc3545'};">
                            {row['unit']} <small style="font-size: 0.9rem; color: #666;">Units</small>
                        </h2>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        st.markdown("### Inventory Chart")
        st.bar_chart(data=stock_df.set_index('bloodgroup')['unit'])
    else:
        st.info("No blood stock records found.")

# ----------------- 2. DONATE BLOOD -----------------
elif menu == "🩸 Donate Blood":
    st.title("🩸 Blood Donation Form")
    st.write("Fill out this form to record a blood donation entry.")

    with st.form("donate_blood_form", clear_on_submit=True):
        donor_name = st.text_input("Donor Full Name*", placeholder="e.g. John Doe")
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age*", min_value=18, max_value=65, value=25)
            bloodgroup = st.selectbox("Blood Group*", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
        with col2:
            unit = st.number_input("Units of Blood*", min_value=1, max_value=5, value=1)
            disease = st.text_input("Any Medical Conditions / Disease", value="Nothing")
        
        submitted = st.form_submit_button("Submit Donation Entry")
        if submitted:
            if not donor_name.strip():
                st.error("Please enter the donor's name.")
            else:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO donor_blooddonate (donor_name, disease, age, bloodgroup, unit, status, date)
                    VALUES (?, ?, ?, ?, ?, 'Pending', ?)
                    """,
                    (donor_name.strip(), disease.strip(), age, bloodgroup, unit, date.today().isoformat())
                )
                conn.commit()
                conn.close()
                st.success(f"Thank you, {donor_name}! Your donation of {unit} unit(s) of {bloodgroup} has been submitted for approval.")

# ----------------- 3. DONATION MANAGEMENT -----------------
elif menu == "📋 Donation Management":
    st.title("📋 Blood Donation Approvals & History")
    
    conn = get_connection()
    donations = pd.read_sql_query(
        "SELECT id, donor_name, age, bloodgroup, unit, disease, status, date FROM donor_blooddonate ORDER BY id DESC",
        conn
    )
    conn.close()

    if donations.empty:
        st.info("No donation records found.")
    else:
        pending_donations = donations[donations['status'] == 'Pending']
        completed_donations = donations[donations['status'] != 'Pending']

        st.subheader(f"⏳ Pending Approvals ({len(pending_donations)})")
        if pending_donations.empty:
            st.success("No pending donations awaiting approval.")
        else:
            for _, row in pending_donations.iterrows():
                with st.expander(f"Donation #{row['id']} - {row['donor_name']} ({row['bloodgroup']}) | {row['unit']} Unit(s)", expanded=True):
                    c1, c2, c3 = st.columns([3, 1, 1])
                    with c1:
                        st.write(f"**Donor:** {row['donor_name']} | **Age:** {row['age']} | **Disease:** {row['disease']}")
                        st.write(f"**Date:** {row['date']} | **Blood Group:** {row['bloodgroup']} | **Units:** {row['unit']}")
                    with c2:
                        if st.button("✅ Approve", key=f"app_don_{row['id']}"):
                            conn = get_connection()
                            cur = conn.cursor()
                            # Increase stock
                            cur.execute("UPDATE blood_stock SET unit = unit + ? WHERE bloodgroup = ?", (row['unit'], row['bloodgroup']))
                            # Update donation status
                            cur.execute("UPDATE donor_blooddonate SET status = 'Approved' WHERE id = ?", (row['id'],))
                            conn.commit()
                            conn.close()
                            st.success(f"Approved donation #{row['id']}. Stock updated!")
                            st.rerun()
                    with c3:
                        if st.button("❌ Reject", key=f"rej_don_{row['id']}"):
                            conn = get_connection()
                            cur = conn.cursor()
                            cur.execute("UPDATE donor_blooddonate SET status = 'Rejected' WHERE id = ?", (row['id'],))
                            conn.commit()
                            conn.close()
                            st.warning(f"Rejected donation #{row['id']}.")
                            st.rerun()

        st.markdown("---")
        st.subheader("📜 All Donation Records")
        st.dataframe(donations, use_container_width=True)

# ----------------- 4. REQUEST BLOOD -----------------
elif menu == "🏥 Request Blood":
    st.title("🏥 Request Blood")
    st.write("Submit an emergency or routine request for blood units.")

    with st.form("request_blood_form", clear_on_submit=True):
        patient_name = st.text_input("Patient Full Name*", placeholder="e.g. Jane Smith")
        col1, col2 = st.columns(2)
        with col1:
            patient_age = st.number_input("Patient Age*", min_value=1, max_value=120, value=30)
            bloodgroup = st.selectbox("Required Blood Group*", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
        with col2:
            unit = st.number_input("Units Required*", min_value=1, max_value=10, value=1)
            reason = st.text_input("Reason / Medical Purpose*", placeholder="e.g. Surgery, Accident, Anemia")
        
        submitted = st.form_submit_button("Submit Blood Request")
        if submitted:
            if not patient_name.strip() or not reason.strip():
                st.error("Please fill in both Patient Name and Reason.")
            else:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO blood_bloodrequest (patient_name, patient_age, reason, bloodgroup, unit, status, date)
                    VALUES (?, ?, ?, ?, ?, 'Pending', ?)
                    """,
                    (patient_name.strip(), patient_age, reason.strip(), bloodgroup, unit, date.today().isoformat())
                )
                conn.commit()
                conn.close()
                st.success(f"Blood request for {patient_name} ({unit} unit(s) of {bloodgroup}) submitted successfully!")

# ----------------- 5. REQUEST MANAGEMENT -----------------
elif menu == "📄 Request Management":
    st.title("📄 Blood Requests Approvals & History")
    
    conn = get_connection()
    requests = pd.read_sql_query(
        "SELECT id, patient_name, patient_age, reason, bloodgroup, unit, status, date FROM blood_bloodrequest ORDER BY id DESC",
        conn
    )
    conn.close()

    if requests.empty:
        st.info("No blood requests found.")
    else:
        pending_requests = requests[requests['status'] == 'Pending']
        
        st.subheader(f"⏳ Pending Requests ({len(pending_requests)})")
        if pending_requests.empty:
            st.success("No pending blood requests.")
        else:
            for _, row in pending_requests.iterrows():
                with st.expander(f"Request #{row['id']} - {row['patient_name']} ({row['bloodgroup']}) | {row['unit']} Unit(s)", expanded=True):
                    # Check current stock
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute("SELECT unit FROM blood_stock WHERE bloodgroup = ?", (row['bloodgroup'],))
                    res = cur.fetchone()
                    available_units = res['unit'] if res else 0
                    conn.close()

                    c1, c2, c3 = st.columns([3, 1, 1])
                    with c1:
                        st.write(f"**Patient:** {row['patient_name']} | **Age:** {row['patient_age']}")
                        st.write(f"**Reason:** {row['reason']} | **Date:** {row['date']}")
                        st.write(f"**Required:** {row['unit']} Unit(s) of **{row['bloodgroup']}**")
                        st.write(f"**Current Stock:** `{available_units} Unit(s) available`")
                    with c2:
                        if st.button("✅ Approve", key=f"app_req_{row['id']}"):
                            if available_units >= row['unit']:
                                conn = get_connection()
                                cur = conn.cursor()
                                cur.execute("UPDATE blood_stock SET unit = unit - ? WHERE bloodgroup = ?", (row['unit'], row['bloodgroup']))
                                cur.execute("UPDATE blood_bloodrequest SET status = 'Approved' WHERE id = ?", (row['id'],))
                                conn.commit()
                                conn.close()
                                st.success(f"Approved request #{row['id']}! Deducted {row['unit']} unit(s) from stock.")
                                st.rerun()
                            else:
                                st.error(f"Insufficient stock! Only {available_units} unit(s) available.")
                    with c3:
                        if st.button("❌ Reject", key=f"rej_req_{row['id']}"):
                            conn = get_connection()
                            cur = conn.cursor()
                            cur.execute("UPDATE blood_bloodrequest SET status = 'Rejected' WHERE id = ?", (row['id'],))
                            conn.commit()
                            conn.close()
                            st.warning(f"Rejected request #{row['id']}.")
                            st.rerun()

        st.markdown("---")
        st.subheader("📜 All Request Records")
        st.dataframe(requests, use_container_width=True)

# ----------------- 6. DONORS DIRECTORY -----------------
elif menu == "👥 Donors Directory":
    st.title("👥 Registered Donors Directory")
    
    conn = get_connection()
    donors = pd.read_sql_query(
        """
        SELECT d.id, u.first_name, u.last_name, u.username, d.bloodgroup, d.mobile, d.address
        FROM donor_donor d
        LEFT JOIN auth_user u ON d.user_id = u.id
        """,
        conn
    )
    conn.close()

    if donors.empty:
        st.info("No registered donors found.")
    else:
        st.dataframe(donors, use_container_width=True)

# ----------------- 7. PATIENTS DIRECTORY -----------------
elif menu == "🩺 Patients Directory":
    st.title("🩺 Registered Patients Directory")
    
    conn = get_connection()
    patients = pd.read_sql_query(
        """
        SELECT p.id, u.first_name, u.last_name, p.age, p.bloodgroup, p.disease, p.doctorname, p.mobile, p.address
        FROM patient_patient p
        LEFT JOIN auth_user u ON p.user_id = u.id
        """,
        conn
    )
    conn.close()

    if patients.empty:
        st.info("No registered patients found.")
    else:
        st.dataframe(patients, use_container_width=True)

# ----------------- 8. STOCK MANAGEMENT -----------------
elif menu == "⚙️ Stock Management":
    st.title("⚙️ Blood Stock Adjustments")
    st.write("Manually adjust or audit blood stock quantities in the bank.")

    conn = get_connection()
    stock_df = pd.read_sql_query("SELECT id, bloodgroup, unit FROM blood_stock ORDER BY id", conn)
    conn.close()

    if not stock_df.empty:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("Current Stock Table")
            st.dataframe(stock_df, use_container_width=True)
        with col2:
            st.subheader("Modify Stock")
            target_group = st.selectbox("Select Blood Group", stock_df['bloodgroup'].tolist())
            current_unit = int(stock_df[stock_df['bloodgroup'] == target_group]['unit'].values[0])
            new_unit = st.number_input(f"New Unit Count for {target_group}", min_value=0, max_value=500, value=current_unit)
            if st.button("Update Stock"):
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("UPDATE blood_stock SET unit = ? WHERE bloodgroup = ?", (new_unit, target_group))
                conn.commit()
                conn.close()
                st.success(f"Stock for {target_group} updated to {new_unit} units!")
                st.rerun()
