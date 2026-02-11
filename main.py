# main.py - Main Application Entry Point
import streamlit as st
import pandas as pd
import time
CACHE_VERSION = int(time.time())

st.cache_data.clear()

from App.data_manager import data_manager
from App.league_manager import league_manager
from App.lineup_manager import lineup_manager
from App.ui_components import (
    render_player_card, render_team_summary,
    create_position_dropdown, render_selected_player
)
from App.config import CSS_STYLES, AVAILABLE_MATCHES, SCORING_RULES
from App import league_ui

# Page configuration
st.set_page_config(page_title="Fantasy Water Polo", page_icon="🏊", layout="wide")
st.markdown(CSS_STYLES, unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">🏆 Fantasy Water Polo Manager</h1>', unsafe_allow_html=True)
st.markdown("### *LEN Champions League Fantasy Game*")

# Sidebar
with st.sidebar:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.header("⚙️ Game Settings")
    st.markdown('</div>', unsafe_allow_html=True)

    # Match selection
    match_names = [m[0] for m in AVAILABLE_MATCHES]
    match_ids = {m[0]: m[1] for m in AVAILABLE_MATCHES}
    selected_match_name = st.selectbox("**Select Match to View:**", match_names, index=0)
    selected_match_id = match_ids[selected_match_name]

    st.markdown("---")
    st.markdown("### 📊 Scoring Rules")
    for rule, points in SCORING_RULES.items():
        st.markdown(f"**{rule}**: {points} pts")

    st.markdown("---")
    st.markdown("### 👥 Team Composition")
    st.markdown(
        "• 1 Goalkeeper (GK)<br>• 1 Center (C)<br>• 5 Field Players<br>• 2 Bench Players (any position)<br>*Total: 9 players*",
        unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📈 Current Week")
    current_week = st.number_input("Set Current Week:", min_value=1, max_value=20,
                                   value=league_manager.matchup_manager.current_week)
    if current_week != league_manager.matchup_manager.current_week:
        league_manager.matchup_manager.current_week = current_week
        league_manager.save_to_session()
        st.success(f"Week updated to {current_week}")
        st.rerun()

    st.markdown("---")
    if 'refresh_counter' not in st.session_state:
        st.session_state.refresh_counter = 0
    if st.button("🔄 **Refresh Data**", type="primary", use_container_width=True):
        st.session_state.refresh_counter += 1
        st.rerun()


@st.cache_data
def load_selected_match_data(match_id, refresh_counter=0):
    # Add cache version to ensure fresh data on restart
    _ = CACHE_VERSION
    if match_id == "all":
        return data_manager.get_all_players_dataframe()
    else:
        return data_manager.get_match_dataframe(match_id)

@st.cache_data
def load_player_pool(refresh_counter=0):
    _ = CACHE_VERSION
    return data_manager.get_player_pool()

# Load data
match_data = load_selected_match_data(selected_match_id, st.session_state.refresh_counter)
player_pool = load_player_pool(st.session_state.refresh_counter)


# Display match info
if selected_match_id != "all":
    match_info = data_manager.get_match_info(selected_match_id)
    st.markdown(f"## 📈 Match Analysis: {match_info['name']}")
    st.markdown(
        f"*{match_info['date']} • Final Score: {match_info['teams'][0]} {match_info['score']} {match_info['teams'][1]}*")
else:
    st.markdown("## 📈 Weekly Summary: All Matches")
    st.markdown(f"*Week {current_week} - All Available Matches*")

# Layout columns
col1, col2, col3 = st.columns([2, 1, 1])

# Leaderboard
with col1:
    st.markdown('<div class="section-header">🏆 Player Leaderboard</div>', unsafe_allow_html=True)
    if not match_data.empty:
        if selected_match_id == "all":
            # For "All Matches" view
            display_columns = ['player', 'fantasy_points', 'goals', 'assists', 'steals', 'blocks',
                               'saves', 'team_code', 'match_name']
            display_df = match_data[display_columns].copy()
            display_df.columns = ['Player', 'Points', 'G', 'A', 'ST', 'BL', 'SV', 'Team', 'Match']

            # Reorder columns for better readability
            display_df = display_df[['Player', 'Points', 'G', 'A', 'ST', 'BL', 'SV', 'Team', 'Match']]
        else:
            # For single match view
            display_columns = ['player', 'fantasy_points', 'goals', 'assists', 'steals', 'blocks',
                               'saves', 'team_code']
            display_df = match_data[display_columns].copy()
            display_df.columns = ['Player', 'Points', 'G', 'A', 'ST', 'BL', 'SV', 'Team']

            # Reorder columns for better readability
            display_df = display_df[['Player', 'Points', 'G', 'A', 'ST', 'BL', 'SV', 'Team']]

        st.dataframe(
            display_df.reset_index(drop=True),
            use_container_width=True,
            height=500,
            hide_index=True,
            column_config={
                "Player": st.column_config.TextColumn(width="large"),
                "Points": st.column_config.NumberColumn(format="%d", width="small"),
                "G": st.column_config.NumberColumn(width="small"),
                "A": st.column_config.NumberColumn(width="small"),
                "ST": st.column_config.NumberColumn(width="small"),
                "BL": st.column_config.NumberColumn(width="small"),
                "SV": st.column_config.NumberColumn(width="small"),
                "Team": st.column_config.TextColumn(width="small"),
                "Match": st.column_config.TextColumn(width="medium")
            }
        )
    else:
        st.info("No match data available")

# Top Performers
with col2:
    st.markdown('<div class="section-header">⭐ Top Performers</div>', unsafe_allow_html=True)
    if not match_data.empty:
        top_players = match_data.head(3)
        for _, player in top_players.iterrows():
            st.markdown(render_player_card(player), unsafe_allow_html=True)

# Match Summary with DETAILED STATS
with col3:
    st.markdown('<div class="section-header">📊 Match Summary</div>', unsafe_allow_html=True)
    if not match_data.empty and selected_match_id != "all":
        # Calculate team stats for the specific match
        team_stats = match_data.groupby(['team_code', 'team_full']).agg({
            'fantasy_points': 'sum',
            'goals': 'sum',
            'assists': 'sum',
            'steals': 'sum',
            'blocks': 'sum',
            'saves': 'sum'
        }).reset_index()

        if len(team_stats) >= 2:
            # Calculate goal differential
            team1_goals = team_stats.iloc[0]['goals']
            team2_goals = team_stats.iloc[1]['goals']
            goal_differential = team1_goals - team2_goals

            for idx, team in team_stats.iterrows():
                col_a, col_b = st.columns([3, 2])
                with col_a:
                    team_name_display = team['team_full'].split()[-1]
                    st.markdown(f"**{team_name_display}**")
                    st.caption(f"Total fantasy points")
                with col_b:
                    if idx == 0:
                        delta_value = f"+{goal_differential}"
                        delta_color = "normal"
                    else:
                        delta_value = f"-{goal_differential}"
                        delta_color = "inverse"
                    st.metric(
                        label="Total Points",
                        value=f"{team['fantasy_points']}",
                        delta=f"{delta_value} goals",
                        delta_color=delta_color,
                        label_visibility="collapsed"
                    )

                # MINI STATS EXPANDER
                with st.expander(f"View {team_name_display} details"):
                    cols = st.columns(2)
                    cols[0].metric("Goals", team['goals'])
                    cols[1].metric("Assists", team['assists'])
                    cols = st.columns(2)
                    cols[0].metric("Steals", team['steals'])
                    cols[1].metric("Blocks", team.get('blocks', 0))
                    if team['saves'] > 0:
                        cols = st.columns(2)
                        cols[0].metric("Saves", team['saves'])

    elif selected_match_id == "all":
        # Weekly summary for all matches
        total_players = len(match_data)
        total_points = match_data['fantasy_points'].sum()
        avg_points = match_data['fantasy_points'].mean()

        st.metric("Total Players", f"{total_players}")
        st.metric("Total Fantasy Points", f"{total_points}")
        st.metric("Average per Player", f"{avg_points:.1f}")

        with st.expander("View match details"):
            match_counts = match_data['match_name'].value_counts()
            for match_name, count in match_counts.items():
                st.write(f"**{match_name}**: {count} players")

# Team Builder Section
st.markdown("---")
st.markdown('<div class="section-header">👥 Team Builder</div>', unsafe_allow_html=True)

# First, let users add custom teams
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

# Get all teams from league_manager
all_users = list(league_manager.users.keys())

# Create tabs for ALL teams
all_tab_names = []
user_id_mapping = {}

# Add "My Team" first
all_tab_names.append("My Team")
user_id_mapping["My Team"] = "current_user"

# Add all other teams from league_manager
for user_id, user_data in league_manager.users.items():
    if user_id != "current_user":  # Skip if it's the current user (handled above)
        tab_name = user_data.get('team_name', f"Team {user_id}")
        all_tab_names.append(tab_name)
        user_id_mapping[tab_name] = user_id

# Always ensure at least 4 tabs for new users
while len(all_tab_names) < 4:
    tab_num = len(all_tab_names) + 1
    tab_name = f"Team {tab_num}"
    all_tab_names.append(tab_name)
    user_id_mapping[tab_name] = f"team_{tab_num}"

# Create the tabs
team_tabs = st.tabs(all_tab_names)

for i, tab in enumerate(team_tabs):
    with tab:
        tab_name = all_tab_names[i]
        user_id = user_id_mapping.get(tab_name)

        if user_id:
            st.markdown(f"### 🎯 Build {tab_name}")

            # Check if user exists, create if not (for default teams)
            if user_id not in league_manager.users and user_id.startswith("team_"):
                league_manager.add_user(user_id, f"Manager {i}", tab_name)

            # Render team builder for this user
            league_ui.render_team_builder(player_pool, user_id)

# League Management Section
st.markdown("---")
st.markdown('<div class="section-header">🏆 Fantasy League Manager</div>', unsafe_allow_html=True)

# Create tabs for different league functions
tab1, tab2, tab3, tab4 = st.tabs(["👥 League Setup", "📝 Manage Rosters", "⚔️ Weekly Matchups", "📊 Standings"])

with tab1:
    league_ui.render_league_setup()

with tab2:
    league_ui.render_lineup_management()

with tab3:
    week_to_view = st.number_input(
        "View Week",
        min_value=1,
        max_value=20,
        value=league_manager.matchup_manager.current_week,
        key="matchup_week_view"
    )

    # Calculate scores button
    if st.button("📊 Calculate Week Scores", type="primary", key="calc_scores_btn"):
        player_points = lineup_manager.get_player_points_dict(match_data)
        if player_points:
            weekly_scores = league_manager.calculate_weekly_scores(week_to_view, player_points)
            st.success(f"✅ Calculated scores for {len(weekly_scores)} teams!")

    # Show matchups
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
                    st.metric("Score", matchup['team1_score'])
                with col2:
                    st.markdown("**VS**")
                    if matchup.get('completed'):
                        if matchup['team1_score'] > matchup['team2_score']:
                            st.success("🏆")
                        elif matchup['team2_score'] > matchup['team1_score']:
                            st.error("🏆")
                with col3:
                    st.markdown(f"**{team2_name}**")
                    st.metric("Score", matchup['team2_score'])
            else:
                st.markdown(f"**{team1_name}** - BYE WEEK")
    else:
        st.info("No matchups scheduled for this week")

with tab4:
    league_ui.render_standings()

# Footer
st.markdown("---")
st.markdown("*Fantasy Water Polo Manager • Developed for LEN Champions League • Data updates automatically*")


# FUNCTION for better matchup display
def render_matchup_display_with_scores():
    """Render matchup management with proper head-to-head display"""
    week_to_view = st.number_input(
        "View Week",
        min_value=1,
        max_value=20,
        value=league_manager.matchup_manager.current_week,
        key="matchup_week_view"
    )

    # Calculate scores button
    col_calc, col_gen = st.columns(2)
    with col_calc:
        if st.button("📊 Calculate Week Scores", type="primary", use_container_width=True, key="calc_scores_btn"):
            player_points = lineup_manager.get_player_points_dict(match_data)
            if player_points:
                weekly_scores = league_manager.calculate_weekly_scores(week_to_view, player_points)
                st.success(f"✅ Calculated scores for {len(weekly_scores)} teams!")
                st.rerun()

    with col_gen:
        if st.button("🔄 Generate Matchups", type="secondary", use_container_width=True, key="gen_matchups_btn"):
            matchups = league_manager.create_weekly_matchups(week_to_view)
            st.success(f"✅ Created {len(matchups)} matchups!")
            st.rerun()

    # Show matchups with IMPROVED DISPLAY
    st.markdown(f"### 🏆 Week {week_to_view} Matchups")
    week_matchups = league_manager.get_weekly_matchups(week_to_view)

    if week_matchups:
        for matchup_idx, matchup in enumerate(week_matchups):
            team1_data = league_manager.users.get(matchup['team1'], {})
            team1_name = team1_data.get('team_name', 'Unknown')
            team1_manager = team1_data.get('name', 'Unknown')

            if matchup.get('team2'):
                team2_data = league_manager.users.get(matchup['team2'], {})
                team2_name = team2_data.get('team_name', 'Unknown')
                team2_manager = team2_data.get('name', 'Unknown')

                # Get lineups for both teams
                team1_lineup = league_manager.get_lineup(matchup['team1'], week_to_view)
                team2_lineup = league_manager.get_lineup(matchup['team2'], week_to_view)

                # Create a nice matchup card
                with st.container():
                    st.markdown("---")

                    # Header with team names
                    col_header = st.columns([1, 2, 2, 1])
                    with col_header[1]:
                        st.markdown(f"### {team1_name}")
                        st.caption(f"Manager: {team1_manager}")
                    with col_header[2]:
                        st.markdown(f"### {team2_name}")
                        st.caption(f"Manager: {team2_manager}")

                    # Scores
                    col_scores = st.columns([1, 2, 2, 1])
                    with col_scores[1]:
                        score_display = f"{matchup['team1_score']} pts" if matchup.get('team1_score',
                                                                                       0) > 0 else "No score"
                        st.metric("", score_display)
                    with col_scores[2]:
                        score_display = f"{matchup['team2_score']} pts" if matchup.get('team2_score',
                                                                                       0) > 0 else "No score"
                        st.metric("", score_display)

                    # Winner indicator
                    if matchup.get('completed') and matchup['team1_score'] != matchup['team2_score']:
                        col_winner = st.columns([1, 2, 2, 1])
                        winner_idx = 1 if matchup['team1_score'] > matchup['team2_score'] else 2
                        with col_winner[winner_idx]:
                            st.success("🏆 **WINNER**")

                    # Lineup details in expanders
                    col_details = st.columns(2)
                    with col_details[0]:
                        with st.expander(f"View {team1_name} Lineup", expanded=False):
                            if team1_lineup and 'players' in team1_lineup:
                                render_lineup_details(team1_lineup['players'])
                            else:
                                st.info("No lineup set")

                    with col_details[1]:
                        with st.expander(f"View {team2_name} Lineup", expanded=False):
                            if team2_lineup and 'players' in team2_lineup:
                                render_lineup_details(team2_lineup['players'])
                            else:
                                st.info("No lineup set")
            else:
                # Bye week
                st.markdown("---")
                st.markdown(f"### 🏖️ **{team1_name}** - BYE WEEK")
                st.info(f"{team1_name} gets a bye this week")

    else:
        st.info("No matchups scheduled for this week. Use 'Generate Matchups' button above.")

    # Team scores table
    st.markdown("### 📈 Team Scores This Week")
    weekly_scores = league_manager.matchup_manager.scores.get(week_to_view, {})

    if weekly_scores:
        scores_data = []
        for user_id, score in weekly_scores.items():
            user_data = league_manager.users.get(user_id, {})
            scores_data.append({
                'Team': user_data.get('team_name', 'Unknown'),
                'Manager': user_data.get('name', 'Unknown'),
                'Score': score
            })

        scores_df = pd.DataFrame(scores_data).sort_values('Score', ascending=False)
        st.dataframe(
            scores_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                'Team': st.column_config.TextColumn(width="medium"),
                'Manager': st.column_config.TextColumn(width="medium"),
                'Score': st.column_config.NumberColumn(width="small")
            }
        )
    else:
        st.info("No scores calculated yet. Click 'Calculate Week Scores' above.")


def render_lineup_details(players):
    """Render lineup details for a team"""
    from App.config import TEAM_SIZE

    if len(players) >= TEAM_SIZE['starters']:
        starters = players[:TEAM_SIZE['starters']]
        bench = players[TEAM_SIZE['starters']:]

        st.markdown("**Starters:**")
        for player in starters:
            position_symbol = "🥅" if player.get('position') == 'goalkeeper' else "🎯" if player.get(
                'position') == 'center' else "🏊"
            st.write(
                f"{position_symbol} #{player.get('jersey', '?')} {player.get('player', 'Unknown')} - {player.get('fantasy_points', 0)} pts")

        if bench:
            st.markdown("**Bench:**")
            for player in bench:
                position_symbol = "🥅" if player.get('position') == 'goalkeeper' else "🎯" if player.get(
                    'position') == 'center' else "🏊"
                st.write(f"{position_symbol} #{player.get('jersey', '?')} {player.get('player', 'Unknown')}")
    else:
        st.write("Incomplete lineup")