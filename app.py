import streamlit as st
from datetime import datetime
import sqlite3
import pandas as pd

# --- 1. DATABASE FUNCTIONS (Keep these at the top) ---
def init_db():
    conn = sqlite3.connect('chinmaya.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, 
                  points INTEGER,
                  task1 INTEGER DEFAULT 0,
                  task2 INTEGER DEFAULT 0,
                  task3 INTEGER DEFAULT 0)''')
    c.execute('INSERT OR IGNORE INTO users (username, points, task1, task2, task3) VALUES (?, ?, ?, ?, ?)', 
              ('Student1', 120, 0, 0, 0))
    conn.commit()
    conn.close()

def get_user_data(username):
    conn = sqlite3.connect('chinmaya.db')
    c = conn.cursor()
    c.execute('SELECT points, task1, task2, task3 FROM users WHERE username = ?', (username,))
    row = c.fetchone()
    conn.close()
    return row if row else (120, 0, 0, 0)

# Initialize the DB once when the script starts
init_db()

# --- 2. PAGE CONFIG & STYLING ---
st.set_page_config(page_title="Chinmaya Mission Portal", page_icon="🕉️", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFDF5; }
    div[data-testid="stContainer"] {
        background-color: #FFFFFF !important;
        border-radius: 15px !important;
        border: 1px solid #E0D5C1 !important;
        padding: 30px !important;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.05) !important;
        margin-bottom: 25px !important;
    }
    h1, h2, h3 { color: #8B4513 !important; font-family: 'Georgia', serif; }
    p, label, li, .stMarkdown { color: #4A4A4A !important; font-weight: 500 !important; }
    [data-testid="stMetricValue"] { color: #D35400 !important; font-weight: 800 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR ROLE SELECTION ---
st.sidebar.title("🧘 Portal Navigation")
role = st.sidebar.radio("Select Your Role:", ["Student Portal", "Guru Dashboard"])

# --- 4. GURU (TEACHER) DASHBOARD ---
if role == "Guru Dashboard":
    st.title("👩‍🏫 Guru Dashboard")
    st.subheader("Manage Shishya Progress")
    
    password = st.sidebar.text_input("Enter Teacher Access Code", type="password")
    
    if password == "CMS123":
        st.success("Access Granted. You can now edit student data directly.")
        
        conn = sqlite3.connect('chinmaya.db')
        # We load all columns so the teacher can see everything
        df = pd.read_sql_query("SELECT * FROM users", conn)
        
        with st.container(border=True):
            st.write("### Student Data Editor")
            st.caption("Double-click any cell to edit points or task status (1=Done, 0=Not Done).")
            
            # The Magic: Data Editor allows inline editing
            edited_df = st.data_editor(df, use_container_width=True, hide_index=True)
            
            if st.button("💾 Save All Changes to Database"):
                edited_df.to_sql('users', conn, if_exists='replace', index=False)
                st.success("Database updated! The students will see these changes immediately.")
        conn.close()
    
    elif password == "":
        st.info("Please enter the access code in the sidebar to view data.")
    else:
        st.error("Incorrect Access Code")

# --- 5. STUDENT PORTAL (Your Original Code) ---
else:
    # Initialize session state for student
    if 'username' not in st.session_state:
        st.session_state.username = 'Student1' 

    pts, t1, t2, t3 = get_user_data(st.session_state.username)
    if 'karma_points' not in st.session_state:
        st.session_state.karma_points = pts
        
    # --- HEADER ---
    col_logo, col_title = st.columns([1, 5])
    with col_logo:
        st.image("CMLogo.png", width=120) 
    with col_title:
        st.title("Chinmaya Student Portal")
        st.subheader("Your path to wisdom and reflection.")

    # --- SIDEBAR STATUS ---
    st.sidebar.header("System Status")
    st.sidebar.success("Database: ONLINE")
    st.sidebar.info("Curfew Rule: 10 PM - 7 AM")

    # --- TOP ROW: POINTS & SYLLABUS ---
    col_left, col_right = st.columns(2)

    with col_left:
        with st.container(border=True):
            st.header("✨ My Karma Points")
            st.metric(label="Total Points", value=st.session_state.karma_points)
            progress_val = min(st.session_state.karma_points / 300, 1.0)
            st.progress(progress_val)

    with col_right:
        with st.container(border=True):
            st.header("📖 Course Syllabus")
            # Get latest from DB
            pts, t1_val, t2_val, t3_val = get_user_data(st.session_state.username)
            
            check1 = st.checkbox("Intro to Vedanta", value=bool(t1_val), key="s1")
            check2 = st.checkbox("Gita Chapter 1", value=bool(t2_val), key="s2")
            check3 = st.checkbox("The 4 Paths of Yoga", value=bool(t3_val), key="s3")
            
            if st.button("Update Progress & Claim Points"):
                new_points = 120 + (sum([check1, check2, check3]) * 20)
                conn = sqlite3.connect('chinmaya.db')
                c = conn.cursor()
                c.execute('''UPDATE users SET points=?, task1=?, task2=?, task3=? WHERE username=?''', 
                          (new_points, int(check1), int(check2), int(check3), st.session_state.username))
                conn.commit()
                conn.close()
                st.session_state.karma_points = new_points
                st.balloons()
                st.rerun()

    # --- MIDDLE ROW: CALENDAR & INSPIRATION ---
    col_mid_l, col_mid_r = st.columns(2)
    with col_mid_l:
        with st.container(border=True):
            st.header("📅 Class Calendar")
            today_str = datetime.now().strftime('%m/%d/%Y')
            date_text = st.text_input("Enter Date (MM/DD/YYYY)", value=today_str)
            st.info(f"**Viewing schedule for:** {date_text}")

    with col_mid_r:
        with st.container(border=True):
            st.header("🕉️ Daily Inspiration")
            try:
                with open("gurudev_quotes.txt", "r") as f:
                    all_quotes = [line.strip() for line in f.readlines() if line.strip()]
                if all_quotes:
                    day_of_year = datetime.now().timetuple().tm_yday
                    daily_quote = all_quotes[day_of_year % len(all_quotes)]
                    st.info(f"*{daily_quote}*")
            except FileNotFoundError:
                st.error("Missing quotes.txt!")

    # --- BOTTOM SECTION: SOCIAL FEED ---
    with st.container(border=True):
        st.header("💬 Community Social Feed")
        current_hour = datetime.now().hour
        if 7 <= current_hour < 22:
            st.success("☀️ Feed is OPEN.")
            st.text_input("Post a reflection...", key="social_input")
        else:
            st.error("🌙 Social Curfew Active (10 PM - 7 AM)")