import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import time

# --- CONFIGURATION ---
st.set_page_config(page_title="Routine Tracker - Emerald & Onyx", page_icon="💎", layout="wide")

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('database.db', check_same_thread=False)
    c = conn.cursor()
    # Habits table
    c.execute('''CREATE TABLE IF NOT EXISTS habits 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, is_custom INTEGER)''')
    # Completions table
    c.execute('''CREATE TABLE IF NOT EXISTS completions 
                 (date TEXT, habit_name TEXT, completed INTEGER, PRIMARY KEY (date, habit_name))''')
    # Challenge table
    c.execute('''CREATE TABLE IF NOT EXISTS challenge 
                 (habit_name TEXT, start_date TEXT, last_updated TEXT, progress INTEGER)''')
    
    # Pre-populate core habits
    core_habits = [
        "Cardio / Exercise", "Spirituality / Meditation", "Studies", 
        "Coding / Programming", "Reading", "Journaling", 
        "Healthy Eating", "Sleep Tracking", "Skill Learning", 
        "Digital Detox / Less Screen Time"
    ]
    for habit in core_habits:
        c.execute("INSERT OR IGNORE INTO habits (name, is_custom) VALUES (?, 0)", (habit,))
    
    conn.commit()
    return conn

conn = init_db()

# --- HELPER FUNCTIONS ---
def get_habits():
    df = pd.read_sql("SELECT name, is_custom FROM habits", conn)
    return df

def add_custom_habit(name):
    c = conn.cursor()
    try:
        c.execute("INSERT INTO habits (name, is_custom) VALUES (?, 1)", (name,))
        conn.commit()
        return True
    except:
        return False

def mark_completion(date, habit_name, completed):
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO completions (date, habit_name, completed) VALUES (?, ?, ?)", 
              (date, habit_name, 1 if completed else 0))
    conn.commit()

def get_completions(date):
    df = pd.read_sql(f"SELECT habit_name, completed FROM completions WHERE date='{date}'", conn)
    return dict(zip(df['habit_name'], df['completed']))

def get_streak(habit_name):
    df = pd.read_sql(f"SELECT date, completed FROM completions WHERE habit_name='{habit_name}' ORDER BY date DESC", conn)
    if df.empty: return 0
    streak = 0
    today = datetime.now().date()
    dates = pd.to_datetime(df['date']).dt.date.tolist()
    completions = df['completed'].tolist()
    
    if today not in dates and (today - timedelta(days=1)) not in dates:
        return 0
        
    for i in range(len(dates)):
        if completions[i] == 1:
            streak += 1
        else:
            break
    return streak

def get_challenge():
    c = conn.cursor()
    c.execute("SELECT habit_name, start_date, last_updated, progress FROM challenge LIMIT 1")
    return c.fetchone()

def update_challenge(habit_name, start_date, last_updated, progress):
    c = conn.cursor()
    c.execute("DELETE FROM challenge") 
    c.execute("INSERT INTO challenge (habit_name, start_date, last_updated, progress) VALUES (?, ?, ?, ?)", 
              (habit_name, start_date, last_updated, progress))
    conn.commit()

def reset_challenge():
    c = conn.cursor()
    c.execute("DELETE FROM challenge")
    conn.commit()

# --- STYLING (Emerald & Onyx) ---
st.markdown("""
    <style>
    /* Global Onyx Background */
    .stApp {
        background-color: #0F0F0F;
        color: #E0E0E0;
    }
    
    /* Headers - Emerald Green */
    h1, h2, h3 {
        color: #50C878 !important;
        font-family: 'Montserrat', sans-serif;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }
    
    /* Professional Card Layout */
    .habit-card {
        background: linear-gradient(145deg, #1A1A1A, #121212);
        border: 1px solid #2A2A2A;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .habit-card:hover {
        border-color: #50C878;
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(80, 200, 120, 0.15);
    }
    
    /* Custom Checkbox Emerald Accent */
    .stCheckbox label {
        font-size: 1.1rem !important;
        font-weight: 500 !important;
        color: #FFFFFF !important;
    }
    
    /* Emerald Progress Bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #50C878, #2E8B57) !important;
        border-radius: 10px !important;
    }
    
    /* Emerald Primary Button */
    .stButton>button {
        background-color: #50C878 !important;
        color: #0F0F0F !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.75rem 2.5rem !important;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #2E8B57 !important;
        box-shadow: 0 0 15px rgba(80, 200, 120, 0.4);
    }
    
    /* Inputs - Onyx/Emerald Style */
    .stTextInput>div>div>input {
        background-color: #1A1A1A !important;
        color: #FFFFFF !important;
        border: 1px solid #2A2A2A !important;
        border-radius: 8px !important;
    }
    .stTextInput>div>div>input:focus {
        border-color: #50C878 !important;
    }
    
    /* Success Notifications */
    .stSuccess {
        background-color: rgba(80, 200, 120, 0.1) !important;
        color: #50C878 !important;
        border: 1px solid #50C878 !important;
        border-radius: 8px !important;
    }
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px 4px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
        color: #888 !important;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: transparent !important;
        color: #50C878 !important;
        border-bottom: 2px solid #50C878 !important;
    }

    /* Hide redundant elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom spacing */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- APP LAYOUT ---
st.title("💎 Routine Tracker Pro")
st.markdown("<p style='font-size: 1.2rem; color: #888;'>Excellence is a habit, not an act. Precision in tracking.</p>", unsafe_allow_html=True)

# Define Tabs (Multiple Pages)
tab1, tab2, tab3 = st.tabs(["📋 DAILY TRACKER", "🔥 21-DAY CHALLENGE", "📊 INSIGHTS & STATS"])

today = datetime.now().date().strftime("%Y-%m-%d")

with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Today's Focus")
        habits_df = get_habits()
        current_completions = get_completions(today)
        
        completed_count = 0
        total_habits = len(habits_df)
        
        for index, row in habits_df.iterrows():
            habit_name = row['name']
            is_completed = current_completions.get(habit_name, 0) == 1
            
            # Professionally Styled Cards
            st.markdown(f'<div class="habit-card">', unsafe_allow_html=True)
            c1, c2 = st.columns([5, 1])
            with c1:
                checked = st.checkbox(habit_name, value=is_completed, key=f"cb_{habit_name}")
                if checked != is_completed:
                    mark_completion(today, habit_name, checked)
                    st.rerun()
            with c2:
                streak = get_streak(habit_name)
                st.markdown(f"<h3 style='margin:0; text-align:right;'>🔥 {streak}</h3>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            if checked:
                completed_count += 1
    
    with col2:
        st.markdown("### Performance")
        progress_val = (completed_count / total_habits) if total_habits > 0 else 0
        
        # Centered Circle-like Progress
        st.markdown(f"""
            <div style="background: #1A1A1A; border: 1px solid #2A2A2A; border-radius: 12px; padding: 30px; text-align: center;">
                <h1 style="font-size: 3rem; margin-bottom: 0;">{int(progress_val * 100)}%</h1>
                <p style="color: #888;">Daily Mastery</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.progress(progress_val)
        
        if progress_val == 1.0:
            st.success("Flawless execution! 🏆")
        
        st.markdown("---")
        with st.expander("✨ Expand Routine"):
            new_habit = st.text_input("New habit name...", placeholder="e.g., Cold Plunge")
            if st.button("Add to Routine"):
                if new_habit:
                    if add_custom_habit(new_habit):
                        st.success(f"Routine updated!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Already exists.")

with tab2:
    st.markdown("### The 21-Day Transformation")
    challenge_data = get_challenge()
    
    if not challenge_data:
        col_c1, col_c2 = st.columns([2, 1])
        with col_c1:
            challenge_habit = st.text_input("What habit will you master in 21 days?", placeholder="e.g., No Sugar")
        with col_c2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Begin Challenge"):
                if challenge_habit:
                    update_challenge(challenge_habit, today, None, 0)
                    st.rerun()
    else:
        c_name, c_start, c_last, c_progress = challenge_data
        
        col_ch1, col_ch2 = st.columns([2, 1])
        with col_ch1:
            st.markdown(f"""
                <div class="habit-card" style="border-left: 4px solid #50C878;">
                    <h2 style="margin-top:0;">{c_name}</h2>
                    <p style="color: #888;">Started on: {c_start}</p>
                </div>
            """, unsafe_allow_html=True)
            
            progress_perc = min(c_progress / 21.0, 1.0)
            st.progress(progress_perc)
            st.write(f"Milestone: Day {c_progress} / 21")
            
            # Motivational messaging
            msgs = [
                "The first step is always the hardest. Keep going!",
                "Building momentum. Your brain is re-wiring.",
                "The habit is taking root. Don't break the chain!",
                "Almost there. The transformation is nearly complete."
            ]
            msg_idx = min(c_progress // 6, 3)
            st.info(msgs[msg_idx])
            
        with col_ch2:
            can_mark = c_last != today
            if c_progress < 21:
                if can_mark:
                    if st.button(f"Complete Day {c_progress + 1}"):
                        update_challenge(c_name, c_start, today, c_progress + 1)
                        st.balloons()
                        st.rerun()
                else:
                    st.markdown("""
                        <div style="background: rgba(80,200,120,0.1); padding: 20px; border-radius: 12px; text-align:center;">
                            <p style="color:#50C878; font-weight:bold; margin:0;">Daily Target Secured ⚡</p>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("Challenge Mastered! 🏅")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Reset Challenge", use_container_width=True):
                reset_challenge()
                st.rerun()

with tab3:
    st.markdown("### Analytics Dashboard")
    
    # Key Metrics
    m1, m2, m3 = st.columns(3)
    total_completed = pd.read_sql("SELECT SUM(completed) as total FROM completions", conn)['total'].iloc[0] or 0
    total_days = pd.read_sql("SELECT COUNT(DISTINCT date) FROM completions", conn).iloc[0, 0] or 1
    
    with m1:
        st.markdown(f"""
            <div style="background: #1A1A1A; border: 1px solid #2A2A2A; border-radius: 12px; padding: 20px; text-align: center;">
                <p style="color: #888; margin:0;">Total Reps</p>
                <h2 style="margin:0;">{total_completed}</h2>
            </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
            <div style="background: #1A1A1A; border: 1px solid #2A2A2A; border-radius: 12px; padding: 20px; text-align: center;">
                <p style="color: #888; margin:0;">Days Active</p>
                <h2 style="margin:0;">{total_days}</h2>
            </div>
        """, unsafe_allow_html=True)
    with m3:
        avg = round(total_completed / total_days, 1) if total_days > 0 else 0
        st.markdown(f"""
            <div style="background: #1A1A1A; border: 1px solid #2A2A2A; border-radius: 12px; padding: 20px; text-align: center;">
                <p style="color: #888; margin:0;">Daily Avg</p>
                <h2 style="margin:0;">{avg}</h2>
            </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Weekly Activity Chart
    st.markdown("#### Weekly Completion Activity")
    days_range = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]
    day_names = [(datetime.now() - timedelta(days=i)).strftime("%a") for i in range(6, -1, -1)]
    
    completion_data = []
    for d in days_range:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM completions WHERE date=? AND completed=1", (d,))
        completion_data.append(c.fetchone()[0])
        
    chart_df = pd.DataFrame({"Completions": completion_data}, index=day_names)
    st.bar_chart(chart_df, color="#50C878")
    
    # Daily Tip Box
    st.markdown("---")
    tips = [
        "Emerald energy flows where focus goes.",
        "Precision in your routine leads to precision in your life.",
        "Small, disciplined actions create massive results over time.",
        "The Onyx standard: No excuses, just execution.",
        "Your future self will thank you for today's discipline."
    ]
    tip_text = tips[int(time.time() / 86400) % len(tips)]
    st.markdown(f"""
        <div style="background: linear-gradient(90deg, #50C878, #1A1A1A); padding: 20px; border-radius: 12px; color: white;">
            <strong>Pro Tip:</strong> {tip_text}
        </div>
    """, unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("<br><br><div style='text-align: center; color: #444; font-size: 0.8rem;'>EMERALD & ONYX EDITION | Peak Performance Tracker</div>", unsafe_allow_html=True)
