# main.py - Fantasy Water Polo Multi-Page App
import streamlit as st
import pandas as pd
import time
from App.data_manager import data_manager
from App.league_manager import league_manager
from App.lineup_manager import lineup_manager
from App.ui_components import render_player_card, render_selected_player
from App.config import CSS_STYLES, AVAILABLE_MATCHES, SCORING_RULES, TEAM_SIZE
from App import league_ui

# Page config must be first
st.set_page_config(page_title="Fantasy Water Polo", page_icon="🏊", layout="wide")
st.markdown(CSS_STYLES, unsafe_allow_html=True)

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
        match_data = load_match_data("all", st.session_state.refresh_counter)
        week_to_view = st.number_input("View Week", min_value=1, max_value=20,
                                       value=league_manager.matchup_manager.current_week,
                                       key="matchup_week_view")

        if st.button("📊 Calculate Week Scores", type="primary", key="calc_scores_btn"):
            player_points = lineup_manager.get_player_points_dict(match_data)
            if player_points:
                weekly_scores = league_manager.calculate_weekly_scores(week_to_view, player_points)
                st.success(f"✅ Calculated scores for {len(weekly_scores)} teams!")

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
        else:
            st.info("No matchups scheduled for this week")

    with league_tabs[3]:
        league_ui.render_standings()


def matches_page():
    """Match Analysis Page (Redirect to Home - kept for navigation)"""
    st.markdown("Redirecting to Home...")
    st.session_state.page = "Home"
    st.rerun()


def matchup_page():
    """My Fantasy Matchup - This Week's Head-to-Head"""

    # Add CSS fix for text color
    st.markdown("""
    <style>
        .player-card, div[data-testid="stVerticalBlock"] div {
            color: #000000 !important;
        }
        .player-card div, .player-card span {
            color: #000000 !important;
        }
        .stMetric label, .stMetric div {
            color: #000000 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 class="main-header">⚔️ My Matchup</h1>', unsafe_allow_html=True)

    current_week = league_manager.matchup_manager.current_week
    st.markdown(f"### Week {current_week}")

    # Find current user's matchup for this week
    my_user_id = "current_user"
    my_matchup = None
    opponent_id = None

    week_matchups = league_manager.get_weekly_matchups(current_week)
    if week_matchups:
        for matchup in week_matchups:
            if matchup['team1'] == my_user_id:
                my_matchup = matchup
                opponent_id = matchup['team2']
                break
            elif matchup['team2'] == my_user_id:
                my_matchup = matchup
                opponent_id = matchup['team1']
                break

    if not my_matchup or not opponent_id:
        st.warning("⚠️ No matchup scheduled for your team this week.")
        st.info("Go to League Manager → League Setup → Create Weekly Matchups to generate matchups.")

        # Show all teams for debugging/development
        with st.expander("🔧 Dev Tools - Create Test Matchup", expanded=True):
            st.markdown("**Available Teams:**")
            team_options = {}
            for uid, user_data in league_manager.users.items():
                if uid != my_user_id:
                    team_options[user_data.get('team_name', uid)] = uid

            if team_options:
                selected_opponent = st.selectbox("Select opponent for test matchup:",
                                                 options=list(team_options.keys()))
                if st.button("⚔️ Create Test Matchup", type="primary"):
                    opponent_id = team_options[selected_opponent]
                    # Create a simple matchup
                    test_matchup = {
                        'week': current_week,
                        'team1': my_user_id,
                        'team2': opponent_id,
                        'team1_score': 0,
                        'team2_score': 0,
                        'completed': False
                    }
                    # Remove any existing matchups for this week
                    league_manager.matchup_manager.matchups = [
                        m for m in league_manager.matchup_manager.matchups
                        if m['week'] != current_week
                    ]
                    league_manager.matchup_manager.matchups.append(test_matchup)
                    league_manager.save_to_session()
                    st.success(f"Created test matchup: My Team vs {selected_opponent}")
                    st.rerun()
            else:
                st.info("No other teams available. Create teams in Team Builder first.")
        return

    # Get team data
    my_team_data = league_manager.users.get(my_user_id, {})
    my_team_name = my_team_data.get('team_name', 'My Team')
    opponent_data = league_manager.users.get(opponent_id, {})
    opponent_name = opponent_data.get('team_name', 'Unknown')

    # Get lineups
    my_lineup = league_manager.get_lineup(my_user_id, current_week)
    opponent_lineup = league_manager.get_lineup(opponent_id, current_week)

    # Calculate scores
    my_score = my_matchup.get('team1_score' if my_matchup['team1'] == my_user_id else 'team2_score', 0)
    opponent_score = my_matchup.get('team2_score' if my_matchup['team1'] == my_user_id else 'team1_score', 0)

    # HEADER - Scoreboard
    col1, col2, col3 = st.columns([2, 1, 2])

    with col1:
        score_color = "#2E7D32" if my_score > opponent_score else "#333"
        winner_badge = "🏆 " if my_score > opponent_score else ""
        st.markdown(f"""
        <div style="background: white; padding: 2rem; border-radius: 12px; border: 2px solid #0066CC; text-align: center;">
            <span style="font-size: 2.5rem;">👤</span>
            <h2 style="margin: 0.5rem 0; color: #0066CC;">{winner_badge}{my_team_name}</h2>
            <div style="font-size: 3rem; font-weight: bold; color: {score_color};">{my_score}</div>
            <div style="color: #666;">Current Score</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center; height: 100%;">
            <span style="font-size: 2rem; font-weight: bold; color: #666;">VS</span>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        score_color = "#CC3333" if opponent_score > my_score else "#333"
        winner_badge = "🏆 " if opponent_score > my_score else ""
        st.markdown(f"""
        <div style="background: white; padding: 2rem; border-radius: 12px; border: 1px solid #e0e0e0; text-align: center;">
            <span style="font-size: 2.5rem;">🏊</span>
            <h2 style="margin: 0.5rem 0;">{winner_badge}{opponent_name}</h2>
            <div style="font-size: 3rem; font-weight: bold; color: {score_color};">{opponent_score}</div>
            <div style="color: #666;">Current Score</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ROSTER COMPARISON
    st.markdown("### 📋 Starting Lineups")

    if not my_lineup or 'players' not in my_lineup:
        st.warning("⚠️ You haven't set your lineup yet. Go to Team Builder to set your roster.")
    else:
        my_players = my_lineup['players'][:TEAM_SIZE['starters']]  # Starters only
        opponent_players = opponent_lineup['players'][
            :TEAM_SIZE['starters']] if opponent_lineup and 'players' in opponent_lineup else []

        # Position order
        position_order = {'goalkeeper': 0, 'center': 1, 'field': 2}

        # Sort both lineups by position
        my_players.sort(key=lambda x: position_order.get(x.get('position', 'field'), 3))
        opponent_players.sort(key=lambda x: position_order.get(x.get('position', 'field'), 3))

        # Create position headers
        st.markdown("""
        <style>
            .position-header {
                background-color: #f0f2f6;
                padding: 0.5rem;
                border-radius: 4px;
                margin: 1rem 0 0.5rem 0;
                font-weight: bold;
                color: black !important;
            }
            .player-row {
                display: flex;
                justify-content: space-between;
                padding: 0.5rem;
                border-bottom: 1px solid #e0e0e0;
            }
        </style>
        """, unsafe_allow_html=True)

        # Track which positions we've shown
        shown_positions = set()

        # Show all players in position order
        for i in range(max(len(my_players), len(opponent_players))):
            my_player = my_players[i] if i < len(my_players) else None
            opp_player = opponent_players[i] if i < len(opponent_players) else None

            # Get position for header
            current_pos = None
            if my_player:
                current_pos = my_player.get('position')
            elif opp_player:
                current_pos = opp_player.get('position')

            # Show position header if not shown yet
            if current_pos and current_pos not in shown_positions:
                position_emoji = "🥅" if current_pos == 'goalkeeper' else "🎯" if current_pos == 'center' else "🏊"
                position_name = "Goalkeeper" if current_pos == 'goalkeeper' else "Center" if current_pos == 'center' else "Field Player"
                st.markdown(f"<div class='position-header'>{position_emoji} {position_name}</div>",
                            unsafe_allow_html=True)
                shown_positions.add(current_pos)

            # Create side-by-side comparison
            col_left, col_mid, col_right = st.columns([2.4, 0.2, 2.4])

            with col_left:
                if my_player:
                    st.markdown(f"""
                    <div style="background: {'#e8f5e9' if my_player.get('fantasy_points', 0) > (opp_player.get('fantasy_points', 0) if opp_player else 0) else 'white'}; 
                                padding: 0.8rem; border-radius: 8px; border-left: 4px solid #0066CC;">
                        <div style="font-weight: bold; color: black;">#{my_player.get('jersey', '?')} {my_player.get('player', 'Unknown')}</div>
                        <div style="color: #666; font-size: 0.9rem;">{my_player.get('team_code', '?')}</div>
                        <div style="color: #2E7D32; font-weight: bold; font-size: 1.2rem;">{my_player.get('fantasy_points', 0)} pts</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("<div style='padding: 0.8rem; color: #999; text-align: center;'>— Empty —</div>",
                                unsafe_allow_html=True)

            with col_mid:
                st.markdown(
                    "<div style='height: 100%; display: flex; align-items: center; justify-content: center; color: black;'>⚔️</div>",
                    unsafe_allow_html=True)

            with col_right:
                if opp_player:
                    st.markdown(f"""
                    <div style="background: {'#ffebee' if opp_player.get('fantasy_points', 0) > (my_player.get('fantasy_points', 0) if my_player else 0) else 'white'}; 
                                padding: 0.8rem; border-radius: 8px; border-left: 4px solid #CC3333;">
                        <div style="font-weight: bold; color: black;">#{opp_player.get('jersey', '?')} {opp_player.get('player', 'Unknown')}</div>
                        <div style="color: #666; font-size: 0.9rem;">{opp_player.get('team_code', '?')}</div>
                        <div style="color: #CC3333; font-weight: bold; font-size: 1.2rem;">{opp_player.get('fantasy_points', 0)} pts</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("<div style='padding: 0.8rem; color: #999; text-align: center;'>— Empty —</div>",
                                unsafe_allow_html=True)

    # BENCH SECTION
    st.markdown("---")
    st.markdown("### 🪑 Bench")

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown(f"**{my_team_name}**")
        if my_lineup and 'players' in my_lineup and len(my_lineup['players']) > TEAM_SIZE['starters']:
            bench_players = my_lineup['players'][TEAM_SIZE['starters']:]
            for player in bench_players:
                pos_symbol = "🥅" if player.get('position') == 'goalkeeper' else "🎯" if player.get(
                    'position') == 'center' else "🏊"
                st.markdown(f"""
                <div style="padding: 0.5rem; border-bottom: 1px solid #e0e0e0; color: black;">
                    {pos_symbol} #{player.get('jersey', '?')} {player.get('player', 'Unknown')} - {player.get('team_code', '?')}
                    <span style="float: right; color: #666;">{player.get('fantasy_points', 0)} pts</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No bench players")

    with col_right:
        st.markdown(f"**{opponent_name}**")
        if opponent_lineup and 'players' in opponent_lineup and len(opponent_lineup['players']) > TEAM_SIZE['starters']:
            bench_players = opponent_lineup['players'][TEAM_SIZE['starters']:]
            for player in bench_players:
                pos_symbol = "🥅" if player.get('position') == 'goalkeeper' else "🎯" if player.get(
                    'position') == 'center' else "🏊"
                st.markdown(f"""
                <div style="padding: 0.5rem; border-bottom: 1px solid #e0e0e0; color: black;">
                    {pos_symbol} #{player.get('jersey', '?')} {player.get('player', 'Unknown')} - {player.get('team_code', '?')}
                    <span style="float: right; color: #666;">{player.get('fantasy_points', 0)} pts</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No bench players")

    # Calculate Scores Button
    st.markdown("---")
    if st.button("📊 Refresh Scores", type="primary", use_container_width=True):
        match_data = load_match_data("all", st.session_state.refresh_counter)
        player_points = lineup_manager.get_player_points_dict(match_data)
        if player_points:
            weekly_scores = league_manager.calculate_weekly_scores(current_week, player_points)
            st.success("✅ Scores updated!")
            st.rerun()


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
        <h2 style="margin-top: 0; color: #0066CC;">Fantasy<br>Water Polo</h2>
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
    "Matchup": matchup_page,
    "League": league_page,
    "Settings": settings_page
}

# Run selected page
pages[st.session_state.page]()