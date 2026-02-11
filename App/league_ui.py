# App/league_ui.py - FIXED VERSION WITH STABLE SELECTIONS
import streamlit as st
import pandas as pd
from App.league_manager import league_manager
from App.lineup_manager import lineup_manager
from App.ui_components import render_selected_player
from App.config import TEAM_SIZE


def render_team_builder(player_pool, user_id=None):
    """Render the team builder interface with bench support - FIXED SELECTIONS"""
    if user_id is None:
        user_id = "current_user"

    # Initialize ALL session state keys at once
    state_keys = [
        f'{user_id}_selected_gk',
        f'{user_id}_selected_center',
        f'{user_id}_selected_fields',
        f'{user_id}_selected_bench'
    ]

    for key in state_keys:
        if key not in st.session_state:
            if 'fields' in key:
                st.session_state[key] = []
            elif 'bench' in key:
                st.session_state[key] = []
            else:
                st.session_state[key] = None

    # Get existing roster if any
    current_week = league_manager.matchup_manager.current_week
    existing_lineup = league_manager.get_lineup(user_id, current_week)

    # Pre-populate from existing lineup (only if no current selections)
    if existing_lineup and 'players' in existing_lineup and not st.session_state[f'{user_id}_selected_gk']:
        existing_roster = existing_lineup['players']
        if len(existing_roster) >= TEAM_SIZE['total']:
            # First 7 are starters
            starters = existing_roster[:TEAM_SIZE['starters']]
            bench = existing_roster[TEAM_SIZE['starters']:]

            # Find GK
            for player in starters:
                if player.get('position') == 'goalkeeper':
                    st.session_state[f'{user_id}_selected_gk'] = player
                    break

            # Find Center
            for player in starters:
                if player.get('position') == 'center':
                    st.session_state[f'{user_id}_selected_center'] = player
                    break

            # Find Field players
            field_players = [p for p in starters if p.get('position') == 'field']
            st.session_state[f'{user_id}_selected_fields'] = field_players[:5]

            # Bench players
            st.session_state[f'{user_id}_selected_bench'] = bench[:2]

    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    with col1:
        st.markdown("#### 🥅 Starters")
        st.markdown("**Goalkeeper (1)**")
    with col2:
        st.markdown("#### 🎯")
        st.markdown("**Center (1)**")
    with col3:
        st.markdown("#### 🏊")
        st.markdown("**Field Players (5)**")
    with col4:
        st.markdown("#### 🪑 Bench")
        st.markdown("**Any Position (2)**")

    # Filter and sort players
    goalkeepers = player_pool[player_pool['position'] == 'goalkeeper']
    centers = player_pool[player_pool['position'] == 'center']
    field_players = player_pool[player_pool['position'] == 'field']

    # Filter out 0-point players
    goalkeepers = goalkeepers[goalkeepers['fantasy_points'] > 0].sort_values('fantasy_points', ascending=False)
    centers = centers[centers['fantasy_points'] > 0].sort_values('fantasy_points', ascending=False)
    field_players = field_players[field_players['fantasy_points'] > 0].sort_values('fantasy_points', ascending=False)

    # ALL players for bench
    all_players = player_pool[player_pool['fantasy_points'] > 0].sort_values('fantasy_points', ascending=False)

    # === GOALKEEPER SELECTION ===
    with col1:
        # Create GK dropdown options
        gk_options = {}
        gk_display_names = []

        # Add default option
        gk_options["-- Select Goalkeeper --"] = None
        gk_display_names.append("-- Select Goalkeeper --")

        for idx, row in goalkeepers.iterrows():
            display_name = f"#{row['jersey']} {row['player'].replace(' (C)', '')} ({row['team_code']}) - {row['match_name']} - {row['fantasy_points']} pts"
            gk_options[display_name] = row.to_dict()
            gk_display_names.append(display_name)

        # Find current selection index
        current_gk = st.session_state[f'{user_id}_selected_gk']
        gk_default_idx = 0
        if current_gk and isinstance(current_gk, dict):
            for i, name in enumerate(gk_display_names):
                if name != "-- Select Goalkeeper --" and gk_options[name].get('player') == current_gk.get('player'):
                    gk_default_idx = i
                    break

        selected_gk = st.selectbox(
            "Select goalkeeper:",
            options=gk_display_names,
            index=gk_default_idx,
            key=f"{user_id}_gk_select",
            label_visibility="collapsed"
        )

        if selected_gk != "-- Select Goalkeeper --" and selected_gk in gk_options:
            st.session_state[f'{user_id}_selected_gk'] = gk_options[selected_gk]
            st.markdown(render_selected_player(gk_options[selected_gk], 'goalkeeper'), unsafe_allow_html=True)

    # === CENTER SELECTION ===
    with col2:
        # Create Center dropdown options
        center_options = {}
        center_display_names = []

        # Add default option
        center_options["-- Select Center --"] = None
        center_display_names.append("-- Select Center --")

        for idx, row in centers.iterrows():
            display_name = f"#{row['jersey']} {row['player'].replace(' (C)', '')} ({row['team_code']}) - {row['match_name']} - {row['fantasy_points']} pts"
            center_options[display_name] = row.to_dict()
            center_display_names.append(display_name)

        # Find current selection index
        current_center = st.session_state[f'{user_id}_selected_center']
        center_default_idx = 0
        if current_center and isinstance(current_center, dict):
            for i, name in enumerate(center_display_names):
                if name != "-- Select Center --" and center_options[name].get('player') == current_center.get('player'):
                    center_default_idx = i
                    break

        selected_center = st.selectbox(
            "Select center:",
            options=center_display_names,
            index=center_default_idx,
            key=f"{user_id}_center_select",
            label_visibility="collapsed"
        )

        if selected_center != "-- Select Center --" and selected_center in center_options:
            st.session_state[f'{user_id}_selected_center'] = center_options[selected_center]
            st.markdown(render_selected_player(center_options[selected_center], 'center'), unsafe_allow_html=True)

    # === FIELD PLAYERS SELECTION - FIXED ===
    with col3:
        # Create field player options
        field_options = {}
        field_display_names = []

        for idx, row in field_players.iterrows():
            display_name = f"#{row['jersey']} {row['player'].replace(' (C)', '')} ({row['team_code']}) - {row['match_name']} - {row['fantasy_points']} pts"
            field_options[display_name] = row.to_dict()
            field_display_names.append(display_name)

        # Get current selections as display names
        current_selections = []
        if st.session_state[f'{user_id}_selected_fields']:
            for player in st.session_state[f'{user_id}_selected_fields']:
                if isinstance(player, dict):
                    for display_name, player_data in field_options.items():
                        if player.get('player') == player_data.get('player'):
                            current_selections.append(display_name)
                            break

        # IMPORTANT: Use a unique key for the widget
        selected_fields = st.multiselect(
            "Select 5 field players:",
            options=field_display_names,
            default=current_selections,
            max_selections=5,
            key=f"{user_id}_field_select_{len(current_selections)}",  # Unique key based on count
            label_visibility="collapsed"
        )

        # Update session state
        new_selected = [field_options[name] for name in selected_fields if name in field_options]
        st.session_state[f'{user_id}_selected_fields'] = new_selected

        # Display selected field players
        if st.session_state[f'{user_id}_selected_fields']:
            st.markdown("**Selected:**")
            for player in st.session_state[f'{user_id}_selected_fields']:
                st.markdown(render_selected_player(player, 'field'), unsafe_allow_html=True)
        else:
            st.caption("No field players selected")

        st.caption(f"Selected: {len(selected_fields)}/5")

    # === BENCH SELECTION - FIXED ===
    with col4:
        # Create bench options
        bench_options = {}
        bench_display_names = []

        for idx, row in all_players.iterrows():
            position_symbol = "🥅" if row['position'] == 'goalkeeper' else "🎯" if row['position'] == 'center' else "🏊"
            display_name = f"{position_symbol} #{row['jersey']} {row['player'].replace(' (C)', '')} ({row['team_code']}) - {row['match_name']} - {row['fantasy_points']} pts"
            bench_options[display_name] = row.to_dict()
            bench_display_names.append(display_name)

        # Get current bench selections as display names
        current_bench_selections = []
        if st.session_state[f'{user_id}_selected_bench']:
            for player in st.session_state[f'{user_id}_selected_bench']:
                if isinstance(player, dict):
                    for display_name, player_data in bench_options.items():
                        if player.get('player') == player_data.get('player'):
                            current_bench_selections.append(display_name)
                            break

        # IMPORTANT: Use a unique key for the widget
        selected_bench = st.multiselect(
            "Select 2 bench players:",
            options=bench_display_names,
            default=current_bench_selections,
            max_selections=2,
            key=f"{user_id}_bench_select_{len(current_bench_selections)}",  # Unique key based on count
            label_visibility="collapsed"
        )

        # Update session state
        new_bench_selected = [bench_options[name] for name in selected_bench if name in bench_options]
        st.session_state[f'{user_id}_selected_bench'] = new_bench_selected

        # Display selected bench players using render_selected_player
        if st.session_state[f'{user_id}_selected_bench']:
            st.markdown("**Selected Bench:**")
            for player in st.session_state[f'{user_id}_selected_bench']:
                # Determine position type for display
                position_type = player.get('position', 'field')
                st.markdown(render_selected_player(player, position_type), unsafe_allow_html=True)
        else:
            st.caption("No bench players selected")

        st.caption(f"Bench: {len(selected_bench)}/2")

    # Save Roster Button
    st.markdown("---")
    col_save, col_reset = st.columns([3, 1])

    with col_save:
        if st.button("💾 Save Full Roster (Starters + Bench)", type="primary", use_container_width=True,
                     key=f"{user_id}_save"):
            save_current_roster(user_id)

    with col_reset:
        if st.button("🔄 Clear Selections", type="secondary", use_container_width=True, key=f"{user_id}_clear"):
            clear_selections(user_id)
            st.rerun()


def save_current_roster(user_id="current_user"):
    """Save the current team builder selections as a full roster"""
    roster_players = []

    # Add GK if selected
    gk_key = f'{user_id}_selected_gk'
    if gk_key in st.session_state and st.session_state[gk_key] is not None:
        gk_player = st.session_state[gk_key]
        roster_players.append(gk_player)

    # Add Center if selected
    center_key = f'{user_id}_selected_center'
    if center_key in st.session_state and st.session_state[center_key] is not None:
        center_player = st.session_state[center_key]
        roster_players.append(center_player)

    # Add Field players if selected
    fields_key = f'{user_id}_selected_fields'
    if fields_key in st.session_state:
        for field_player in st.session_state[fields_key]:
            if field_player is not None:
                roster_players.append(field_player)

    # Add Bench players if selected
    bench_key = f'{user_id}_selected_bench'
    if bench_key in st.session_state:
        for bench_player in st.session_state[bench_key]:
            if bench_player is not None:
                roster_players.append(bench_player)

    # Validate roster (starters + bench)
    is_valid, message = lineup_manager.validate_roster(roster_players)

    if is_valid and len(roster_players) == TEAM_SIZE['total']:
        # Ensure user exists
        if user_id not in league_manager.users:
            # Create a default user
            if user_id == "current_user":
                league_manager.add_user(user_id, "My Team Manager", "My Team")
            else:
                # For other users, use their name
                league_manager.add_user(user_id, user_id.replace("_", " ").title(),
                                        f"{user_id.replace('_', ' ').title()}'s Team")

        # Save the full roster
        current_week = league_manager.matchup_manager.current_week
        if league_manager.set_lineup(user_id, current_week, roster_players):
            st.success(f"✅ Full roster saved for Week {current_week}!")

            # Show roster summary WITH POINTS
            with st.expander("📋 View Your Roster", expanded=True):
                starters = roster_players[:TEAM_SIZE['starters']]
                bench = roster_players[TEAM_SIZE['starters']:]

                st.markdown("**Starters (7):**")

                # Calculate total points
                total_points = sum(p.get('fantasy_points', 0) for p in roster_players)
                starters_points = sum(p.get('fantasy_points', 0) for p in starters)
                bench_points = sum(p.get('fantasy_points', 0) for p in bench)

                # Show points summary
                col_points = st.columns(3)
                with col_points[0]:
                    st.metric("Total Points", f"{total_points}")
                with col_points[1]:
                    st.metric("Starters", f"{starters_points}")
                with col_points[2]:
                    st.metric("Bench", f"{bench_points}")

                # Player details
                col1, col2 = st.columns(2)
                with col1:
                    gks = [p for p in starters if p.get('position') == 'goalkeeper']
                    if gks:
                        st.write("• 🥅 **Goalkeeper:**")
                        for gk in gks:
                            st.write(
                                f"  #{gk.get('jersey', '?')} {gk.get('player', 'Unknown')} - **{gk.get('fantasy_points', 0)} pts**")

                    centers = [p for p in starters if p.get('position') == 'center']
                    if centers:
                        st.write("• 🎯 **Center:**")
                        for center in centers:
                            st.write(
                                f"  #{center.get('jersey', '?')} {center.get('player', 'Unknown')} - **{center.get('fantasy_points', 0)} pts**")

                with col2:
                    field_players = [p for p in starters if p.get('position') == 'field']
                    if field_players:
                        st.write(f"• 🏊 **Field Players ({len(field_players)}):**")
                        for fp in field_players:
                            st.write(
                                f"  #{fp.get('jersey', '?')} {fp.get('player', 'Unknown')} - **{fp.get('fantasy_points', 0)} pts**")

                if bench:
                    st.markdown(f"**Bench ({len(bench)}):**")
                    for bench_player in bench:
                        pos_symbol = "🥅" if bench_player.get('position') == 'goalkeeper' else "🎯" if bench_player.get(
                            'position') == 'center' else "🏊"
                        st.write(
                            f"{pos_symbol} #{bench_player.get('jersey', '?')} {bench_player.get('player', 'Unknown')} - **{bench_player.get('fantasy_points', 0)} pts**")
        else:
            st.error("❌ Failed to save roster")
    else:
        st.warning(f"❌ Cannot save roster: {message}")
        st.write(f"**Debug:** Found {len(roster_players)} players (need {TEAM_SIZE['total']})")


def clear_selections(user_id="current_user"):
    """Clear all selections for a user"""
    keys_to_clear = [
        f'{user_id}_selected_gk',
        f'{user_id}_selected_center',
        f'{user_id}_selected_fields',
        f'{user_id}_selected_bench'
    ]

    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]


def render_league_setup():
    """Render league setup UI"""
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Add New Manager")
        with st.form("add_manager_form"):
            manager_name = st.text_input("Manager Name", placeholder="e.g., John Doe")
            team_name = st.text_input("Team Name", placeholder="e.g., Water Polo Warriors")

            if st.form_submit_button("➕ Add to League", use_container_width=True):
                if manager_name:
                    # Create user ID from name
                    user_id = manager_name.lower().replace(" ", "_").replace(".", "")

                    # Check if user already exists
                    if user_id in league_manager.users:
                        st.warning(f"⚠️ {manager_name} is already in the league!")
                    else:
                        if league_manager.add_user(user_id, manager_name, team_name or f"{manager_name}'s Team"):
                            st.success(f"✅ Added {manager_name} to the league!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to add user - unknown error")
                else:
                    st.warning("⚠️ Please enter a manager name")

    with col2:
        st.markdown("#### Current League Members")
        if league_manager.users:
            st.markdown(f"**Total Managers:** {len(league_manager.users)}")
            for user_id, user_data in league_manager.users.items():
                st.markdown(f"• **{user_data['name']}** - {user_data['team_name']}")

                # Show if they have lineups set
                if user_data.get('lineups'):
                    weeks = list(user_data['lineups'].keys())
                    st.caption(f"  Lineups set for weeks: {', '.join(map(str, weeks))}")
        else:
            st.info("👥 No managers in the league yet. Add some above!")

    st.markdown("---")
    st.markdown("#### 🗓️ Generate Matchups")
    week_to_setup = st.number_input("Week Number", min_value=1, max_value=20,
                                    value=league_manager.matchup_manager.current_week)

    if st.button("🔄 Create Weekly Matchups", type="primary"):
        if len(league_manager.users) >= 2:
            matchups = league_manager.create_weekly_matchups(week_to_setup)
            if matchups:
                st.success(f"✅ Created {len(matchups)} matchups for Week {week_to_setup}!")

                # Show the matchups
                for i, matchup in enumerate(matchups):
                    team1_name = league_manager.users.get(matchup['team1'], {}).get('team_name', 'Unknown')
                    if matchup['team2']:
                        team2_name = league_manager.users.get(matchup['team2'], {}).get('team_name', 'Unknown')
                        st.write(f"**Matchup {i + 1}:** {team1_name} vs {team2_name}")
                    else:
                        st.write(f"**Bye Week:** {team1_name}")
            else:
                st.warning("⚠️ Could not create matchups")
        else:
            st.warning("⚠️ Need at least 2 teams to create matchups")


def render_lineup_management():
    """Render lineup management UI"""
    if not league_manager.users:
        st.warning("⚠️ No managers in the league. Add managers first.")
        return

    # Show all users with their lineups
    st.markdown("#### 📋 All Managers' Rosters")

    for user_id, user_data in league_manager.users.items():
        with st.expander(f"{user_data['name']} - {user_data['team_name']}"):
            week_to_view = st.number_input(
                f"View week for {user_data['name']}",
                min_value=1,
                max_value=20,
                value=league_manager.matchup_manager.current_week,
                key=f"week_view_{user_id}"
            )

            lineup = league_manager.get_lineup(user_id, week_to_view)
            if lineup and 'players' in lineup:
                roster_players = lineup['players']

                if len(roster_players) >= TEAM_SIZE['total']:
                    starters = roster_players[:TEAM_SIZE['starters']]
                    bench = roster_players[TEAM_SIZE['starters']:]

                    st.markdown(f"**Week {week_to_view} Roster:**")

                    # Calculate points
                    total_points = sum(p.get('fantasy_points', 0) for p in roster_players)
                    st.metric("Total Points", f"{total_points}")

                    # Organize by position
                    gks = [p for p in starters if p.get('position') == 'goalkeeper']
                    centers = [p for p in starters if p.get('position') == 'center']
                    field_players = [p for p in starters if p.get('position') == 'field']

                    col1, col2 = st.columns(2)
                    with col1:
                        if gks:
                            st.markdown("**Goalkeeper:**")
                            for gk in gks:
                                st.write(
                                    f"• #{gk.get('jersey', '?')} {gk.get('player', 'Unknown')} - {gk.get('fantasy_points', 0)} pts")

                        if centers:
                            st.markdown("**Center:**")
                            for center in centers:
                                st.write(
                                    f"• #{center.get('jersey', '?')} {center.get('player', 'Unknown')} - {center.get('fantasy_points', 0)} pts")

                    with col2:
                        if field_players:
                            st.markdown(f"**Field Players ({len(field_players)}):**")
                            for fp in field_players:
                                st.write(
                                    f"• #{fp.get('jersey', '?')} {fp.get('player', 'Unknown')} - {fp.get('fantasy_points', 0)} pts")

                    if bench:
                        st.markdown(f"**Bench ({len(bench)}):**")
                        for bench_player in bench:
                            pos_symbol = "🥅" if bench_player.get(
                                'position') == 'goalkeeper' else "🎯" if bench_player.get(
                                'position') == 'center' else "🏊"
                            st.write(
                                f"{pos_symbol} #{bench_player.get('jersey', '?')} {bench_player.get('player', 'Unknown')} - {bench_player.get('fantasy_points', 0)} pts")

                    # Show set time
                    if 'set_time' in lineup:
                        st.caption(f"Set on: {lineup['set_time']}")
                else:
                    st.info(f"Incomplete roster: {len(roster_players)}/{TEAM_SIZE['total']} players")
            else:
                st.info(f"No roster set for Week {week_to_view}")

    st.markdown("---")
    st.markdown("#### 💡 How to Save Your Roster")
    st.info("""
    1. Build your team using the **Team Builder** tabs
    2. Select: 1 Goalkeeper 🥅, 1 Center 🎯, 5 Field Players 🏊 (Starters)
    3. Select: 2 Bench Players 🪑 (any position)
    4. Click the **"💾 Save Full Roster (Starters + Bench)"** button
    5. Your roster will be saved for the current week
    """)


def render_matchup_management(match_data):
    """Render matchup management UI"""
    week_to_view = st.number_input("View Week", min_value=1, max_value=20,
                                   value=league_manager.matchup_manager.current_week)

    # DEBUG: Show current data
    with st.expander("🔧 Debug Info", expanded=False):
        st.write(f"Current Week: {week_to_view}")
        st.write(f"Total Users: {len(league_manager.users)}")
        st.write(f"Users: {list(league_manager.users.keys())}")

        # Check lineups
        lineups = league_manager.get_all_lineups(week_to_view)
        st.write(f"Lineups for week {week_to_view}: {len(lineups)}")
        for user_id, lineup in lineups.items():
            st.write(f"  {user_id}: {len(lineup.get('players', []))} players")

        # Check matchups
        week_matchups = league_manager.get_weekly_matchups(week_to_view)
        st.write(f"Matchups for week {week_to_view}: {len(week_matchups)}")

    # Calculate scores button
    if st.button("📊 Calculate Week Scores", type="primary"):
        player_points = lineup_manager.get_player_points_dict(match_data)
        st.info(f"Player points data: {len(player_points)} players")

        if player_points:
            weekly_scores = league_manager.calculate_weekly_scores(week_to_view, player_points)
            st.success(f"✅ Calculated scores for {len(weekly_scores)} teams!")

            # Show the actual scores
            with st.expander("📊 View Calculated Scores"):
                for user_id, score in weekly_scores.items():
                    user_data = league_manager.users.get(user_id, {})
                    st.write(f"{user_data.get('team_name', user_id)}: {score} points")
        else:
            st.error("No player points data available!")

    # Show matchups
    st.markdown(f"#### Week {week_to_view} Results")
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
                    # Show actual score or 0
                    score1 = matchup.get('team1_score', 0)
                    st.metric("Score", score1)
                with col2:
                    st.markdown("**VS**")
                    if matchup.get('completed'):
                        if score1 > matchup.get('team2_score', 0):
                            st.success("🏆")
                        elif matchup.get('team2_score', 0) > score1:
                            st.error("🏆")
                with col3:
                    st.markdown(f"**{team2_name}**")
                    score2 = matchup.get('team2_score', 0)
                    st.metric("Score", score2)
            else:
                st.markdown(f"**{team1_name}** - BYE WEEK")
    else:
        st.info("No matchups scheduled")

def render_standings():
    """Render standings UI"""
    standings = league_manager.get_standings()

    # DEBUG: Show what standings returns
    with st.expander("🔧 Standings Debug", expanded=False):
        st.write(f"Standings data type: {type(standings)}")
        if standings:
            st.write(f"Number of teams in standings: {len(standings)}")
            for i, team in enumerate(standings):
                st.write(f"Team {i + 1}: {team.get('team_name', 'Unknown')} - {team.get('total_points', 0)} pts")
        else:
            st.write("No standings data returned")

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

        standings_df = pd.DataFrame(standings_data)

        # Format the display
        st.markdown("### 🏆 League Standings")
        st.dataframe(
            standings_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                'Rank': st.column_config.NumberColumn(width="small"),
                'Team': st.column_config.TextColumn(width="medium"),
                'Manager': st.column_config.TextColumn(width="medium"),
                'W': st.column_config.NumberColumn(width="small"),
                'L': st.column_config.NumberColumn(width="small"),
                'PCT': st.column_config.TextColumn(width="small"),
                'Total Pts': st.column_config.NumberColumn(width="small")
            }
        )

        # Also show as metrics
        st.markdown("### 🥇 Top Teams")
        col1, col2, col3 = st.columns(3)
        if len(standings) >= 1:
            with col1:
                st.metric("1st Place", standings[0]['team_name'], f"{standings[0]['total_points']} pts")
        if len(standings) >= 2:
            with col2:
                st.metric("2nd Place", standings[1]['team_name'], f"{standings[1]['total_points']} pts")
        if len(standings) >= 3:
            with col3:
                st.metric("3rd Place", standings[2]['team_name'], f"{standings[2]['total_points']} pts")
    else:
        st.info("No standings data yet. Calculate scores first!")

        # Show how to get standings
        st.markdown("### 📋 How to Generate Standings")
        st.info("""
        1. **Build Teams**: Create rosters for each team in the Team Builder tabs
        2. **Set Matchups**: Go to League Setup → Create Weekly Matchups
        3. **Calculate Scores**: Go to Weekly Matchups → Calculate Week Scores
        4. **View Standings**: Return here to see the updated standings
        """)