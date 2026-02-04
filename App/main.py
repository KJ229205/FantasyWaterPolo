# App/main.py
import streamlit as st
import pandas as pd
from data_manager import data_manager

# Page configuration
st.set_page_config(
    page_title="Fantasy Water Polo",
    page_icon="🏊",
    layout="wide"
)

# Custom CSS for MUCH better appearance
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        color: #0066CC;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .match-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid #0066CC;
    }
    .player-card {
        background-color: white;
        padding: 0.8rem;
        margin: 0.3rem 0;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .section-header {
        font-size: 1.5rem;
        color: #333;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #0066CC;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        text-align: center;
    }
    .position-badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-right: 0.3rem;
    }
    .gk-badge { background-color: #FF6B6B; color: white; }
    .c-badge { background-color: #4ECDC4; color: white; }
    .field-badge { background-color: #45B7D1; color: white; }
</style>
""", unsafe_allow_html=True)

# Title with emoji
st.markdown('<h1 class="main-header">🏆 Fantasy Water Polo Manager</h1>', unsafe_allow_html=True)
st.markdown("### *LEN Champions League Fantasy Game*")

# Sidebar - UPDATED with match selection
with st.sidebar:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.header("⚙️ Game Settings")
    st.markdown('</div>', unsafe_allow_html=True)

    # Match selection
    available_matches = [
        ("NBG vs JSP", "nbg_jsp"),
        ("FTC vs Brescia", "ftc_bre"),
        ("All Matches (Week 1)", "all")
    ]

    match_names = [m[0] for m in available_matches]
    match_ids = {m[0]: m[1] for m in available_matches}

    selected_match_name = st.selectbox(
        "**Select Match to View:**",
        match_names
    )

    selected_match_id = match_ids[selected_match_name]

    st.markdown("---")
    st.markdown("### 📊 Scoring Rules")

    scoring_rules = {
        "Goal": 5,
        "Assist": 3,
        "Steal": 2,
        "Block": 2,
        "Save": 2,
        "Exclusion Drawn": 1
    }

    for rule, points in scoring_rules.items():
        st.markdown(f"**{rule}**: {points} pts")

    st.markdown("---")
    st.markdown("### 👥 Team Composition")
    st.markdown("**Required Positions:**")
    st.markdown("• 1 Goalkeeper (GK)")
    st.markdown("• 1 Center (C)")
    st.markdown("• 5 Field Players")
    st.markdown("*Total: 7 players*")

    st.markdown("---")
    if st.button("🔄 **Refresh Data**", type="primary", use_container_width=True):
        st.rerun()


# Main content - UPDATED for multi-match support
@st.cache_data
def load_selected_match_data(match_id):
    """Load data for the selected match"""
    if match_id == "all":
        # Get all players from all matches
        df = data_manager.get_all_players_dataframe()
    else:
        # Get data for specific match
        df = data_manager.get_match_dataframe(match_id)

    return df


@st.cache_data
def load_player_pool():
    """Load all players for team building"""
    return data_manager.get_player_pool()


# Get selected match data
match_data = load_selected_match_data(selected_match_id)

# Get match info for display
if selected_match_id != "all":
    match_info = data_manager.get_match_info(selected_match_id)
    match_title = match_info['name']
    match_date = match_info['date']
    match_score = match_info['score']
    team1, team2 = match_info['teams']

    st.markdown(f"## 📈 Match Analysis: {match_title}")
    st.markdown(f"*{match_date} • Final Score: {team1} {match_score} {team2}*")
else:
    st.markdown("## 📈 Weekly Summary: All Matches")
    st.markdown("*Week 1 - December 2, 2025*")

# Create three columns for layout
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.markdown('<div class="section-header">🏆 Player Leaderboard</div>', unsafe_allow_html=True)

    if not match_data.empty:
        # Format dataframe for display
        if selected_match_id == "all":
            display_columns = ['match_name', 'jersey', 'player', 'team_code', 'goals', 'assists', 'steals', 'saves',
                               'fantasy_points']
            display_df = match_data[display_columns].copy()
            display_df.columns = ['Match', '#', 'Player', 'Team', 'Goals', 'Assists', 'Steals', 'Saves',
                                  'Fantasy Points']
        else:
            display_columns = ['jersey', 'player', 'team_code', 'goals', 'assists', 'steals', 'saves', 'fantasy_points']
            display_df = match_data[display_columns].copy()
            display_df.columns = ['#', 'Player', 'Team', 'Goals', 'Assists', 'Steals', 'Saves', 'Fantasy Points']

        # Reset index
        display_df = display_df.reset_index(drop=True)

        # Display with better formatting
        st.dataframe(
            display_df,
            use_container_width=True,
            height=500,
            hide_index=True,
            column_config={
                "#": st.column_config.TextColumn(width="small"),
                "Player": st.column_config.TextColumn(width="large"),
                "Team": st.column_config.TextColumn(width="small"),
                "Fantasy Points": st.column_config.NumberColumn(
                    format="%d pts",
                    width="medium"
                )
            }
        )
    else:
        st.info("No match data available")

with col2:
    st.markdown('<div class="section-header">⭐ Top Performers</div>', unsafe_allow_html=True)

    if not match_data.empty:
        # Top 3 players with better styling
        top_players = match_data.head(3)
        for idx, player in top_players.iterrows():
            # Determine team color - expand this based on actual teams
            if player['team_code'] in ['NBG', 'FTC']:
                team_color = "#0066CC"  # Blue for NBG/FTC
            elif player['team_code'] in ['JSP', 'BRE']:
                team_color = "#CC3333"  # Red for JSP/Brescia
            else:
                team_color = "#666666"  # Gray for others

            stats_text = f"{player['goals']} goals"
            if player['assists'] > 0:
                stats_text += f" • {player['assists']} assists"
            if player['steals'] > 0:
                stats_text += f" • {player['steals']} steals"
            if player['saves'] > 0:
                stats_text += f" • {player['saves']} saves"

            # Position badge
            position_badge = ""
            if player['position'] == 'goalkeeper':
                position_badge = '<span class="position-badge gk-badge">GK</span>'
            elif player['position'] == 'center':
                position_badge = '<span class="position-badge c-badge">C</span>'
            else:
                position_badge = '<span class="position-badge field-badge">F</span>'

            st.markdown(f"""
            <div class="player-card">
                <div style="color: {team_color}; font-weight: bold; font-size: 1.1rem;">
                    #{player['jersey']} {player['player']} {position_badge}
                </div>
                <div style="color: #666; font-size: 0.9rem;">
                    {player['team_full']}
                </div>
                <div style="color: #2E7D32; font-weight: bold; font-size: 1.2rem; margin-top: 0.5rem;">
                    {player['fantasy_points']} fantasy points
                </div>
                <div style="color: #555; font-size: 0.85rem; margin-top: 0.3rem;">
                    {stats_text}
                </div>
            </div>
            """, unsafe_allow_html=True)

with col3:
    st.markdown('<div class="section-header">📊 Match Summary</div>', unsafe_allow_html=True)

    if not match_data.empty and selected_match_id != "all":
        # Calculate team stats for the specific match
        team_stats = match_data.groupby(['team_code', 'team_full']).agg({
            'fantasy_points': 'sum',
            'goals': 'sum',
            'assists': 'sum',
            'steals': 'sum',
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
                    team_name_display = team['team_full'].split()[-1]  # Just show last word
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

                # Mini stats
                with st.expander(f"View {team_name_display} details"):
                    cols = st.columns(2)
                    cols[0].metric("Goals", team['goals'])
                    cols[1].metric("Assists", team['assists'])
                    cols = st.columns(2)
                    cols[0].metric("Steals", team['steals'])
                    if team['saves'] > 0:
                        cols[1].metric("Saves", team['saves'])
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

# TEAM BUILDER SECTION - Using ALL players from both matches
st.markdown("---")
st.markdown('<div class="section-header">👥 Build Your Weekly Fantasy Team</div>', unsafe_allow_html=True)

st.markdown("### 🎯 Weekly Team Builder")
st.markdown("Select players from **ANY** match for your weekly fantasy team (1 GK, 1 C, 5 Field Players)")

# Get player pool for team building
player_pool = load_player_pool()

if not player_pool.empty:
    # Create columns for the positions
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### 🥅 Goalkeeper")

    with col2:
        st.markdown("#### 🎯 Center")

    with col3:
        st.markdown("#### 🏊 Field Players")

    # Filter players by position
    goalkeepers = player_pool[player_pool['position'] == 'goalkeeper']
    centers = player_pool[player_pool['position'] == 'center']
    field_players = player_pool[player_pool['position'] == 'field']

    # Create selection boxes with NO defaults
    with col1:
        gk_options = {}
        # Add empty option first
        gk_options["-- Select Goalkeeper --"] = None

        for _, row in goalkeepers.iterrows():
            display_name = f"#{row['jersey']} {row['player'].replace(' (C)', '')} ({row['team_code']}) - {row['match_name']}"
            gk_options[display_name] = row

        selected_gk = st.selectbox(
            "Select goalkeeper:",
            options=list(gk_options.keys()),
            index=0,  # Default to empty option
            key="weekly_gk",
            label_visibility="collapsed"
        )

        if selected_gk != "-- Select Goalkeeper --" and selected_gk in gk_options and gk_options[
            selected_gk] is not None:
            gk_data = gk_options[selected_gk]
            # Determine team color
            if gk_data['team_code'] in ['NBG', 'FTC']:
                team_color = "#0066CC"
            elif gk_data['team_code'] in ['JSP', 'BRE']:
                team_color = "#CC3333"
            else:
                team_color = "#666666"

            st.markdown(f"""
            <div style="background-color: white; padding: 1rem; border-radius: 8px; border-left: 4px solid {team_color}; margin-top: 0.5rem;">
                <div style="font-weight: bold; color: {team_color};">
                    #{gk_data['jersey']} {gk_data['player'].replace(' (C)', '')}
                </div>
                <div style="color: #666; font-size: 0.9rem;">
                    {gk_data['team_code']} • {gk_data['match_name']}
                </div>
                <div style="color: #2E7D32; font-weight: bold; margin-top: 0.5rem;">
                    {gk_data['fantasy_points']} pts
                </div>
                <div style="color: #555; font-size: 0.85rem;">
                    {gk_data['saves']} saves
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 8px; border: 2px dashed #dee2e6; margin-top: 0.5rem; text-align: center; color: #6c757d;">
                <div style="font-size: 2rem;">🥅</div>
                <div>Select a goalkeeper</div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        center_options = {}
        # Add empty option first
        center_options["-- Select Center --"] = None

        for _, row in centers.iterrows():
            display_name = f"#{row['jersey']} {row['player'].replace(' (C)', '')} ({row['team_code']}) - {row['match_name']}"
            center_options[display_name] = row

        selected_center = st.selectbox(
            "Select center:",
            options=list(center_options.keys()),
            index=0,  # Default to empty option
            key="weekly_center",
            label_visibility="collapsed"
        )

        if selected_center != "-- Select Center --" and selected_center in center_options and center_options[
            selected_center] is not None:
            center_data = center_options[selected_center]
            # Determine team color
            if center_data['team_code'] in ['NBG', 'FTC']:
                team_color = "#0066CC"
            elif center_data['team_code'] in ['JSP', 'BRE']:
                team_color = "#CC3333"
            else:
                team_color = "#666666"

            st.markdown(f"""
            <div style="background-color: white; padding: 1rem; border-radius: 8px; border-left: 4px solid {team_color}; margin-top: 0.5rem;">
                <div style="font-weight: bold; color: {team_color};">
                    #{center_data['jersey']} {center_data['player'].replace(' (C)', '')}
                </div>
                <div style="color: #666; font-size: 0.9rem;">
                    {center_data['team_code']} • {center_data['match_name']}
                </div>
                <div style="color: #2E7D32; font-weight: bold; margin-top: 0.5rem;">
                    {center_data['fantasy_points']} pts
                </div>
                <div style="color: #555; font-size: 0.85rem;">
                    {center_data['goals']}G {center_data['assists']}A
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 8px; border: 2px dashed #dee2e6; margin-top: 0.5rem; text-align: center; color: #6c757d;">
                <div style="font-size: 2rem;">🎯</div>
                <div>Select a center</div>
            </div>
            """, unsafe_allow_html=True)

    with col3:
        # Field players in 2 columns within this column
        field_col1, field_col2 = st.columns(2)

        field_options = {}
        for _, row in field_players.iterrows():
            display_name = f"#{row['jersey']} {row['player'].replace(' (C)', '')} ({row['team_code']}) - {row['match_name']}"
            field_options[display_name] = row

        selected_fields = st.multiselect(
            "Select 5 field players:",
            options=list(field_options.keys()),
            default=[],  # Empty default
            max_selections=5,
            key="weekly_field",
            label_visibility="collapsed"
        )

        # Display selected field players or placeholder
        if selected_fields:
            for i, field_name in enumerate(selected_fields):
                field_data = field_options[field_name]
                # Determine team color
                if field_data['team_code'] in ['NBG', 'FTC']:
                    team_color = "#0066CC"
                elif field_data['team_code'] in ['JSP', 'BRE']:
                    team_color = "#CC3333"
                else:
                    team_color = "#666666"

                # Alternate between two columns
                target_col = field_col1 if i % 2 == 0 else field_col2

                with target_col:
                    st.markdown(f"""
                    <div style="background-color: white; padding: 0.8rem; border-radius: 8px; border-left: 3px solid {team_color}; margin-bottom: 0.5rem;">
                        <div style="font-weight: bold; color: {team_color}; font-size: 0.9rem;">
                            #{field_data['jersey']} {field_data['player'].replace(' (C)', '')}
                        </div>
                        <div style="color: #666; font-size: 0.8rem;">
                            {field_data['team_code']} • {field_data['match_name']}
                        </div>
                        <div style="color: #2E7D32; font-weight: bold; font-size: 0.9rem;">
                            {field_data['fantasy_points']} pts
                        </div>
                        <div style="color: #555; font-size: 0.75rem;">
                            {field_data['goals']}G {field_data['assists']}A {field_data['steals']}ST
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            # Fill remaining slots with placeholders
            for i in range(len(selected_fields), 5):
                target_col = field_col1 if i % 2 == 0 else field_col2
                with target_col:
                    st.markdown(f"""
                    <div style="background-color: #f8f9fa; padding: 0.8rem; border-radius: 8px; border: 1px dashed #dee2e6; margin-bottom: 0.5rem; text-align: center; color: #6c757d;">
                        <div style="font-size: 1.2rem;">🏊</div>
                        <div style="font-size: 0.7rem;">Slot {i + 1}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            # Show all 5 empty slots
            for i in range(5):
                target_col = field_col1 if i % 2 == 0 else field_col2
                with target_col:
                    st.markdown(f"""
                    <div style="background-color: #f8f9fa; padding: 0.8rem; border-radius: 8px; border: 1px dashed #dee2e6; margin-bottom: 0.5rem; text-align: center; color: #6c757d;">
                        <div style="font-size: 1.2rem;">🏊</div>
                        <div style="font-size: 0.7rem;">Slot {i + 1}</div>
                    </div>
                    """, unsafe_allow_html=True)

    # Calculate team summary
    has_gk = selected_gk != "-- Select Goalkeeper --" and selected_gk in gk_options and gk_options[
        selected_gk] is not None
    has_center = selected_center != "-- Select Center --" and selected_center in center_options and center_options[
        selected_center] is not None
    has_5_fields = len(selected_fields) == 5

    if has_gk and has_center and has_5_fields:
        # Get all selected player data
        all_selected_data = []

        if has_gk:
            all_selected_data.append(gk_options[selected_gk])

        if has_center:
            all_selected_data.append(center_options[selected_center])

        for field_name in selected_fields:
            if field_name in field_options:
                all_selected_data.append(field_options[field_name])

        if len(all_selected_data) == 7:
            # Create DataFrame from selected data
            selected_df = pd.DataFrame([{
                'jersey': row['jersey'],
                'player': row['player'],
                'team_code': row['team_code'],
                'goals': row['goals'],
                'assists': row['assists'],
                'steals': row['steals'],
                'fantasy_points': row['fantasy_points'],
                'position': row['position'],
                'match_name': row['match_name']
            } for row in all_selected_data])

            total_points = selected_df['fantasy_points'].sum()
            avg_points = total_points / 7

            # Calculate team rating
            max_possible = 140  # Theoretical max with perfect picks
            min_possible = 35  # Theoretical min with worst picks
            team_percentage = ((total_points - min_possible) / (max_possible - min_possible)) * 100

            if team_percentage >= 80:
                rating = "A+"
                rating_color = "#198754"  # Green
            elif team_percentage >= 65:
                rating = "A"
                rating_color = "#20c997"  # Teal
            elif team_percentage >= 50:
                rating = "B+"
                rating_color = "#0dcaf0"  # Cyan
            elif team_percentage >= 35:
                rating = "B"
                rating_color = "#6f42c1"  # Purple
            elif team_percentage >= 20:
                rating = "C+"
                rating_color = "#fd7e14"  # Orange
            elif team_percentage >= 10:
                rating = "C"
                rating_color = "#dc3545"  # Red
            else:
                rating = "D"
                rating_color = "#6c757d"  # Gray

            st.markdown("---")
            st.markdown("### 📊 Team Summary")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Fantasy Points", f"{total_points}")
            with col2:
                st.metric("Average per Player", f"{avg_points:.1f}")
            with col3:
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 1.2rem; font-weight: bold; color: {rating_color};">
                        {rating}
                    </div>
                    <div style="font-size: 0.8rem; color: #666;">
                        Team Rating
                    </div>
                    <div style="font-size: 0.7rem; color: #999;">
                        ({team_percentage:.1f}% of max)
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Position breakdown
            st.markdown("#### Position Breakdown:")
            pos_cols = st.columns(3)
            with pos_cols[0]:
                st.success(f"🥅 Goalkeeper: 1/1")
            with pos_cols[1]:
                st.success(f"🎯 Center: 1/1")
            with pos_cols[2]:
                st.success(f"🏊 Field Players: 5/5")

            # Team analysis
            st.markdown("#### Team Analysis:")
            analysis_col1, analysis_col2 = st.columns(2)

            with analysis_col1:
                # Best player
                best_player = selected_df.loc[selected_df['fantasy_points'].idxmax()]
                st.info(
                    f"⭐ **Top Performer:** #{best_player['jersey']} {best_player['player']} ({best_player['fantasy_points']} pts)")

            with analysis_col2:
                # Match distribution
                match_counts = selected_df['match_name'].value_counts()
                match_text = ", ".join([f"{count} from {match}" for match, count in match_counts.items()])
                st.info(f"📊 **Match Selection:** {match_text}")

            st.success("✅ Team composition is valid!")
        else:
            st.warning("⚠️ Please select all required positions")
    else:
        # Show what's missing
        missing = []
        if not has_gk:
            missing.append("Goalkeeper")
        if not has_center:
            missing.append("Center")
        if not has_5_fields:
            missing.append(f"{5 - len(selected_fields)} more field players")

        if missing:
            st.info(f"👆 Select: {', '.join(missing)} to build your team")
        else:
            st.info("👆 Select 1 goalkeeper, 1 center, and 5 field players to build your team")

else:
    st.warning("No player data available for team building")

# Footer with next steps
st.markdown("---")
st.success("""
### ✅ **Fantasy Water Polo - Multi-Match Ready!**

**Features Complete:**
- **Two matches** (NBG vs JSP, FTC vs Brescia) loaded
- **Match selector** to view individual or all matches
- **Weekly team builder** mixing players from different matches
- **Improved team rating** system

**Ready for Next Features:**
1. **Add more weeks** as matches happen
2. **User authentication** to save teams
3. **Weekly leaderboards** comparing teams
4. **Auto-scraping** from LEN website

**Try it out:** Build a team mixing players from both matches for maximum points!
""")