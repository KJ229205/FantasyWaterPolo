# main.py - Fantasy Water Polo Multi-Page App - FIXED VERSION
import streamlit as st
import pandas as pd
import time
from App.data_manager import data_manager
from App.league_manager import league_manager
from App.lineup_manager import lineup_manager
from App.ui_components import render_player_card, render_selected_player
from App.config import CSS_STYLES, AVAILABLE_MATCHES, SCORING_RULES, TEAM_SIZE
from App import league_ui
from App.matchup_page import render_matchup_page

# Page config must be first
st.set_page_config(page_title="Fantasy Water Polo", page_icon="🏊", layout="wide")

# IMPROVED CSS - Mobile friendly and better text visibility
IMPROVED_CSS = """
<style>
    /* Main containers */
    .main-header {
        color: #0066CC !important;
        text-align: center;
        margin-bottom: 2rem;
    }

    .section-header {
        background: linear-gradient(135deg, #0066CC 0%, #004C99 100%);
        color: white !important;
        padding: 1rem;
        border-radius: 8px;
        margin: 1.5rem 0 1rem 0;
        font-weight: bold;
        font-size: 1.2rem;
    }

    .section-header * {
        color: white !important;
    }

    /* Player cards */
    .player-card {
        background: white;
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }

    .player-card:hover {
        border-color: #0066CC;
        box-shadow: 0 4px 12px rgba(0,102,204,0.2);
    }

    .player-card * {
        color: #1a1a1a !important;
    }

    /* Matchup scoreboard */
    .matchup-scoreboard {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    .score-display {
        font-size: 3.5rem;
        font-weight: bold;
        margin: 1rem 0;
    }

    .winner-score {
        color: #2E7D32 !important;
    }

    .loser-score {
        color: #666 !important;
    }

    /* Position headers */
    .position-header {
        background-color: #f0f2f6;
        padding: 0.8rem;
        border-radius: 6px;
        margin: 1.5rem 0 0.8rem 0;
        font-weight: bold;
        font-size: 1.1rem;
    }

    .position-header * {
        color: #1a1a1a !important;
    }

    /* Player comparison rows */
    .player-comparison {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #0066CC;
    }

    .player-comparison.winning {
        background: #e8f5e9;
        border-left-color: #2E7D32;
    }

    .player-comparison.losing {
        background: #fff3e0;
    }

    /* Metrics */
    .stMetric label, .stMetric div {
        color: #1a1a1a !important;
    }

    /* Buttons */
    .stButton > button {
        width: 100%;
    }

    /* Mobile responsive */
    @media (max-width: 768px) {
        .score-display {
            font-size: 2.5rem;
        }

        .matchup-scoreboard {
            padding: 1rem;
        }

        .player-card {
            padding: 0.8rem;
        }
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 0.5rem 1rem;
    }
</style>
"""

st.markdown(IMPROVED_CSS, unsafe_allow_html=True)

# Cache version
CACHE_VERSION = int(time.time())
st.cache_data.clear()


@st.cache_data
def load_match_data(match_id, refresh_counter=0):
    _ = CACHE_VERSION
    if match_id == "all":
        return data_manager.get_all_players_dataframe()
    return data_manager.get_match_dataframe(match_id)


@st.cache_data
def load_player_pool(refresh_counter=0):
    _ = CACHE_VERSION
    return data_manager.get_player_pool()


# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = "Home"
if 'refresh_counter' not in st.session_state:
    st.session_state.refresh_counter = 0


# ============ PAGE FUNCTIONS ============

def home_page():
    """Home Dashboard - General Stats & LEN Match Analysis"""
    st.markdown('<h1 class="main-header">🏆 Fantasy Water Polo</h1>', unsafe_allow_html=True)
    st.markdown("### *LEN Champions League Fantasy Game*")

    # Load all matches data
    match_data = load_match_data("all", st.session_state.refresh_counter)

    # Weekly Summary Stats
    st.markdown('<div class="section-header">📊 Weekly Summary</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Players", len(match_data))
    with col2:
        st.metric("Total Fantasy Points", f"{match_data['fantasy_points'].sum():,}")
    with col3:
        st.metric("Average per Player", f"{match_data['fantasy_points'].mean():.1f}")

    # Top Performers
    st.markdown('<div class="section-header">⭐ Top Performers</div>', unsafe_allow_html=True)
    top_players = match_data.nlargest(5, 'fantasy_points')
    cols = st.columns(5)
    for i, (_, player) in enumerate(top_players.iterrows()):
        with cols[i]:
            st.markdown(render_player_card(player), unsafe_allow_html=True)

    # Match Scores Table
    st.markdown('<div class="section-header">📋 LEN Match Scores</div>', unsafe_allow_html=True)
    matches = []
    for match_id in data_manager.get_match_ids():
        match_info = data_manager.get_match_info(match_id)
        match_df = load_match_data(match_id, st.session_state.refresh_counter)
        if not match_df.empty:
            team_totals = match_df.groupby('team_full')['fantasy_points'].sum()
            if len(team_totals) >= 2:
                matches.append({
                    "Match": match_info['name'],
                    "Score": match_info['score'],
                    team_totals.index[0]: f"{team_totals.iloc[0]} pts",
                    team_totals.index[1]: f"{team_totals.iloc[1]} pts"
                })

    if matches:
        st.dataframe(pd.DataFrame(matches), use_container_width=True, hide_index=True)

    # Full Match Analysis Expander
    with st.expander("📊 View Detailed Match Analysis", expanded=False):
        st.markdown("### LEN Champions League - Match Details")

        # Match selector
        match_names = [m[0] for m in AVAILABLE_MATCHES if m[0] != "All Matches (Week 1)"]
        match_ids = {m[0]: m[1] for m in AVAILABLE_MATCHES}

        selected_match_name = st.selectbox("Select Match to Analyze:", match_names, key="home_match_select")
        selected_match_id = match_ids[selected_match_name]

        # Load selected match data
        match_df = load_match_data(selected_match_id, st.session_state.refresh_counter)
        match_info = data_manager.get_match_info(selected_match_id)

        # Match header
        st.markdown(f"**{match_info['name']}** • {match_info['score']}")

        # Team comparison
        team1_stats = match_df[match_df['team_full'] == match_info['teams'][0]]
        team2_stats = match_df[match_df['team_full'] == match_info['teams'][1]]

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**{match_info['teams'][0]}**")
            st.metric("Total Fantasy Points", f"{team1_stats['fantasy_points'].sum()} pts")

        with col2:
            st.markdown(f"**{match_info['teams'][1]}**")
            st.metric("Total Fantasy Points", f"{team2_stats['fantasy_points'].sum()} pts")

        # Player leaderboard for selected match
        st.markdown("#### Player Leaderboard")
        display_df = match_df[['player', 'fantasy_points', 'goals', 'assists', 'steals',
                               'blocks', 'saves', 'team_code']].copy()
        display_df.columns = ['Player', 'Pts', 'G', 'A', 'ST', 'BL', 'SV', 'Team']
        st.dataframe(display_df, use_container_width=True, hide_index=True)


def roster_page():
    """Team Builder Page"""
    st.markdown('<h1 class="main-header">👥 Team Builder</h1>', unsafe_allow_html=True)

    # Load player pool
    player_pool = load_player_pool(st.session_state.refresh_counter)

    # Add Custom Team Expander
    with st.expander("➕ Add Custom Team", expanded=False):
        col1, col2 = st.columns([2, 1])
        with col1:
            custom_manager = st.text_input("Manager Name", placeholder="e.g., Joe Smith", key="custom_manager_input")
            custom_team = st.text_input("Team Name", placeholder="e.g., Aqua Warriors", key="custom_team_input")
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Add Team", type="primary", key="add_custom_team_btn"):
                if custom_manager and custom_team:
                    user_id = f"custom_{custom_manager.lower().replace(' ', '_')}"
                    if league_manager.add_user(user_id, custom_manager, custom_team):
                        st.success(f"Added {custom_manager}'s {custom_team}!")
                        st.rerun()
                    else:
                        st.warning("Team already exists or error occurred")

    # Team Selection Tabs
    all_users = list(league_manager.users.keys())
    all_tab_names = []
    user_id_mapping = {}

    all_tab_names.append("My Team")
    user_id_mapping["My Team"] = "current_user"

    for user_id, user_data in league_manager.users.items():
        if user_id != "current_user":
            tab_name = user_data.get('team_name', f"Team {user_id}")
            all_tab_names.append(tab_name)
            user_id_mapping[tab_name] = user_id

    while len(all_tab_names) < 4:
        tab_num = len(all_tab_names) + 1
        tab_name = f"Team {tab_num}"
        all_tab_names.append(tab_name)
        user_id_mapping[tab_name] = f"team_{tab_num}"

    team_tabs = st.tabs(all_tab_names)

    for i, tab in enumerate(team_tabs):
        with tab:
            tab_name = all_tab_names[i]
            user_id = user_id_mapping.get(tab_name)

            if user_id:
                st.markdown(f"### 🎯 Build {tab_name}")
                if user_id not in league_manager.users and user_id.startswith("team_"):
                    league_manager.add_user(user_id, f"Manager {i}", tab_name)
                league_ui.render_team_builder(player_pool, user_id)


def league_page():
    """League Management Hub"""
    st.markdown('<h1 class="main-header">🏆 League Manager</h1>', unsafe_allow_html=True)

    league_tabs = st.tabs(["👥 League Setup", "📝 League Rosters", "⚔️ Weekly Matchups", "📊 Standings"])

    with league_tabs[0]:
        league_ui.render_league_setup()

    with league_tabs[1]:
        league_ui.render_lineup_management()

    with league_tabs[2]:
        week_to_view = st.number_input("View Week", min_value=1, max_value=20,
                                       value=league_manager.matchup_manager.current_week,
                                       key="matchup_week_view")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 Calculate Week Scores", type="primary", use_container_width=True):
                # Use the centralized scoring method
                scores = league_manager.calculate_weekly_scores(week_to_view)
                st.success(f"✅ Calculated scores for {len(scores)} teams!")
                st.rerun()

        with col2:
            if st.button("🔄 Generate Matchups", type="secondary", use_container_width=True):
                matchups = league_manager.create_weekly_matchups(week_to_view)
                st.success(f"✅ Created {len(matchups)} matchups!")
                st.rerun()

        st.markdown(f"#### Week {week_to_view} Matchups")
        week_matchups = league_manager.get_weekly_matchups(week_to_view)

        if week_matchups:
            for matchup in week_matchups:
                team1_data = league_manager.users.get(matchup['team1'], {})
                team1_name = team1_data.get('team_name', 'Unknown')

                if matchup.get('team2'):
                    team2_data = league_manager.users.get(matchup['team2'], {})
                    team2_name = team2_data.get('team_name', 'Unknown')

                    col1, col2, col3 = st.columns([2, 1, 2])
                    with col1:
                        st.markdown(f"**{team1_name}**")
                        st.metric("Score", matchup.get('team1_score', 0))
                    with col2:
                        st.markdown("**VS**")
                        if matchup.get('completed'):
                            if matchup['team1_score'] > matchup['team2_score']:
                                st.success("🏆")
                            elif matchup['team2_score'] > matchup['team1_score']:
                                st.error("🏆")
                    with col3:
                        st.markdown(f"**{team2_name}**")
                        st.metric("Score", matchup.get('team2_score', 0))
                else:
                    st.markdown(f"**{team1_name}** - BYE WEEK")
                st.markdown("---")
        else:
            st.info("No matchups scheduled for this week")

    with league_tabs[3]:
        standings = league_manager.get_standings()

        if standings:
            standings_data = []
            for i, team in enumerate(standings, 1):
                standings_data.append({
                    'Rank': i,
                    'Team': team['team_name'],
                    'Manager': team['name'],
                    'W': team['wins'],
                    'L': team['losses'],
                    'PCT': f"{team['win_pct']:.3f}",
                    'Total Pts': team['total_points']
                })

            st.markdown("### 🏆 League Standings")
            st.dataframe(pd.DataFrame(standings_data), use_container_width=True, hide_index=True)

            # Top teams
            if len(standings) >= 1:
                st.markdown("### 🥇 Top Teams")
                cols = st.columns(3)
                for i, col in enumerate(cols):
                    if i < len(standings):
                        with col:
                            st.metric(f"{i + 1}st Place", standings[i]['team_name'],
                                      f"{standings[i]['total_points']} pts")
        else:
            st.info("No standings data yet. Calculate scores first!")


def settings_page():
    """Settings Page"""
    st.markdown('<h1 class="main-header">⚙️ Settings</h1>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📊 Scoring Rules")
        for rule, points in SCORING_RULES.items():
            st.markdown(f"**{rule}**: {points} pts")

        st.markdown("### 👥 Team Composition")
        st.markdown(f"""
        • 1 Goalkeeper (GK)
        • 1 Center (C)
        • 5 Field Players
        • 2 Bench Players (any position)
        *Total: {TEAM_SIZE['total']} players*
        """)

    with col2:
        st.markdown("### 📈 Current Week")
        current_week = st.number_input("Set Current Week:", min_value=1, max_value=20,
                                       value=league_manager.matchup_manager.current_week)
        if current_week != league_manager.matchup_manager.current_week:
            league_manager.matchup_manager.current_week = current_week
            league_manager.save_to_session()
            st.success(f"Week updated to {current_week}")
            st.rerun()

        st.markdown("### 🔄 Data Refresh")
        if st.button("🔄 **Refresh Data**", type="primary", use_container_width=True):
            st.session_state.refresh_counter += 1
            st.rerun()


# ============ MAIN NAVIGATION ============

# Sidebar Navigation
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <span style="font-size: 3rem;">🏊</span>
        <h2 style="margin-top: 0; color: #0066CC !important;">Fantasy<br>Water Polo</h2>
    </div>
    """, unsafe_allow_html=True)

    # Navigation buttons
    nav_items = {
        "Home": "🏠 Home",
        "Roster": "👥 Team Builder",
        "Matchup": "⚔️ My Matchup",
        "League": "🏆 League Manager",
        "Settings": "⚙️ Settings"
    }

    for page_key, page_label in nav_items.items():
        if st.button(page_label, use_container_width=True,
                     type="primary" if st.session_state.page == page_key else "secondary",
                     key=f"nav_{page_key}"):
            st.session_state.page = page_key
            st.rerun()

    st.markdown("---")
    st.markdown(f"**Week {league_manager.matchup_manager.current_week}**")
    st.markdown("*LEN Champions League*")
    st.markdown(f"**Users:** {len(league_manager.users)}")

# ============ PAGE ROUTER ============

pages = {
    "Home": home_page,
    "Roster": roster_page,
    "Matchup": lambda: render_matchup_page(load_match_data),
    "League": league_page,
    "Settings": settings_page
}

# Run selected page
pages[st.session_state.page]()