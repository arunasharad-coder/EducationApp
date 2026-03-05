import streamlit as st
from datetime import datetime

import sqlite3

# This creates the file 'chinmaya.db' if it doesn't exist
def init_db():
    conn = sqlite3.connect('chinmaya.db')
    c = conn.cursor()
    # Adding task1, task2, and task3 as columns (0 = unchecked, 1 = checked)
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

# This fetches points from the file
def get_user_data(username):
    conn = sqlite3.connect('chinmaya.db')
    c = conn.cursor()
    c.execute('SELECT points, task1, task2, task3 FROM users WHERE username = ?', (username,))
    row = c.fetchone()
    conn.close()
    # Returns (points, t1, t2, t3) or a default starting set
    return row if row else (120, 0, 0, 0)

# This saves points to the file
def update_points(username, new_points):
    conn = sqlite3.connect('chinmaya.db')
    c = conn.cursor()
    c.execute('UPDATE users SET points = ? WHERE username = ?', (new_points, username))
    conn.commit()
    conn.close()

# RUN THE BRAIN
init_db()

# 1. Page Config
st.set_page_config(page_title="Chinmaya Mission Portal", page_icon="🕉️", layout="wide")

# 2. Soothing Lighter Palette & Card Styling
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

# --- INITIALIZE STATE ---
if 'username' not in st.session_state:
    st.session_state.username = 'Student1' 

if 'karma_points' not in st.session_state:
    # Use the new function name here! 
    # It returns (points, t1, t2, t3), but we only need 'pts' for the metric right now.
    pts, t1, t2, t3 = get_user_data(st.session_state.username)
    st.session_state.karma_points = pts
    
# --- HEADER SECTION ---
col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.image("CMLogo.png", width=120) 
with col_title:
    st.title("Chinmaya Student Portal")
    st.subheader("Your path to wisdom and reflection.")

# --- SIDEBAR ---
st.sidebar.header("System Status")
st.sidebar.success("Database Models: LOADED")
st.sidebar.info("Curfew Rule: 10 PM - 7 AM")

# --- TOP ROW: POINTS & SYLLABUS ---
col_left, col_right = st.columns(2)

with col_left:
    with st.container(border=True):
        st.header("✨ My Karma Points")
        st.metric(label="Total Points", value=st.session_state.karma_points, delta="Activity tracked")
        progress_val = min(st.session_state.karma_points / 300, 1.0)
        st.progress(progress_val)
        st.write(f"{int(progress_val*100)}% to Level 2")

with col_right:
    with st.container(border=True):
        st.header("📖 Course Syllabus")
        # Get latest data from DB
        pts, t1_val, t2_val, t3_val = get_user_data(st.session_state.username)
        
        tab1, tab2 = st.tabs(["Current Progress", "Resources"])
        with tab1:
            st.write("Complete topics to earn points:")
            # We use bool() because SQLite stores 1/0, but Streamlit wants True/False
            check1 = st.checkbox("Intro to Vedanta", value=bool(t1_val), key="s1")
            check2 = st.checkbox("Gita Chapter 1", value=bool(t2_val), key="s2")
            check3 = st.checkbox("The 4 Paths of Yoga", value=bool(t3_val), key="s3")
            
            if st.button("Update Progress & Claim Points"):
                # 1. Calculate the new total based on checkboxes
                new_points = 120 + (sum([check1, check2, check3]) * 20)
                
                # 2. Update the Database File
                conn = sqlite3.connect('chinmaya.db')
                c = conn.cursor()
                c.execute('''UPDATE users 
                             SET points=?, task1=?, task2=?, task3=? 
                             WHERE username=?''', 
                          (new_points, int(check1), int(check2), int(check3), st.session_state.username))
                conn.commit()
                conn.close()

                # 3. Update the App Screen & Celebrate
                st.session_state.karma_points = new_points
                st.balloons() # Do this BEFORE rerun so it shows up!
                st.success(f"Progress saved! Total points: {new_points}")
                
                # 4. Refresh to show the new number in the top card
                st.rerun()

# --- MIDDLE ROW: CALENDAR & INSPIRATION ---
col_mid_l, col_mid_r = st.columns(2)

with col_mid_l:
    with st.container(border=True):
        st.header("📅 Class Calendar")
        
        # 1. Use text_input instead of date_input for custom formatting
        # We set a default value to today's date in MM/DD/YYYY format
        today_str = datetime.now().strftime('%m/%d/%Y')
        date_text = st.text_input("Enter Date (MM/DD/YYYY)", value=today_str)
        
        # 2. Add a small caption to help the student
        st.caption("Please use the MM/DD/YYYY format.")
        
        st.write(f"**Viewing schedule for:** {date_text}")
        st.info("**Upcoming:** Highschool Hangouts @ 2:00 PM")

with col_mid_r:
    with st.container(border=True):
        st.header("🕉️ Daily Inspiration")
        
        # 1. Try to read from your quotes.txt file
        try:
            with open("gurudev_quotes.txt", "r") as f:
                # This reads every line and removes extra spaces
                all_quotes = [line.strip() for line in f.readlines() if line.strip()]
            
            if all_quotes:
                # 2. Pick a quote based on the day of the year
                day_of_year = datetime.now().timetuple().tm_yday
                # The % ensures it cycles back to the start if you have fewer than 365
                daily_quote = all_quotes[day_of_year % len(all_quotes)]
                
                st.markdown(f"**Words of Pujya Gurudev:**")
                st.info(f"*{daily_quote}*")
            else:
                st.warning("The quotes.txt file is empty!")
                
        except FileNotFoundError:
            # Fallback if you haven't created the file yet
            st.error("Missing quotes.txt! Please create the file in your folder.")
            st.write("*'Plan out your work and work out your plan.'*")

        if st.button("Set Reflection Reminder"):
            st.toast("Take a moment to breathe and reflect.")

# --- BOTTOM SECTION: SOCIAL FEED ---
with st.container(border=True):
    st.header("💬 Community Social Feed")
    current_hour = datetime.now().hour
    if 7 <= current_hour < 22:
        st.success("☀️ Feed is OPEN. Share your thoughts!")
        st.text_input("What's on your mind?", placeholder="Post a reflection...")
        if st.button("Post to Feed"):
            st.balloons()
    else:
        st.error("🌙 Social Curfew Active (10 PM - 7 AM)")
        st.warning("The feed is currently read-only.")