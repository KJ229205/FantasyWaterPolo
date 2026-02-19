# App/league_ui.py - ENHANCED VERSION with Waiver Wire & Search
import streamlit as st
import pandas as pd
from datetime import datetime
from App.league_manager import league_manager
from App.lineup_manager import lineup_manager
from App.ui_components import render_selected_player
from App.config import TEAM_SIZE


def render_team_builder(player_pool, user_id=None):
    """Render the team builder interface with bench support and player search"""
    if user_id is None:
        user_id = "current_user"

    # Add PLAYER SEARCH/FILTER at the top
    with st.expander("🔍 Player Search & Filter", expanded=False):
        col_search1, col_search2, col_search3 = st.columns(3)

        with col_search1:
            search_query = st.text_input("Search by name/team", placeholder="e.g., Smith or PRO",
                                         key=f"{user_id}_search")

        with col_search2:
            position_filter = st.selectbox("Position", ["All", "Goalkeeper", "Center", "Field"],
                                           key=f"{user_id}_pos_filter")

        with col_search3:
            min_points = st.number_input("Min Points", min_value=0, value=0, key=f"{user_id}_min_pts")

        # Apply filters
        filtered_pool = player_pool.copy()

        if search_query:
            filtered_pool = filtered_pool[
                filtered_pool['player'].str.contains(search_query, case=False, na=False) |
                filtered_pool['team_code'].str.contains(search_query, case=False, na=False)
                ]

        if position_filter != "All":
            pos_map = {"Goalkeeper": "goalkeeper", "Center": "center", "Field": "field"}
            filtered_pool = filtered_pool[filtered_pool['position'] == pos_map[position_filter]]

        if min_points > 0:
            filtered_pool = filtered_pool[filtered_pool['fantasy_points'] >= min_points]

        # Show filtered results
        if not filtered_pool.empty:
            st.markdown(f"**Found {len(filtered_pool)} players**")

            # Show top 10 results
            display_cols = ['player', 'team_code', 'position', 'fantasy_points', 'goals', 'assists', 'saves']
            result_df = filtered_pool.nlargest(10, 'fantasy_points')[display_cols].copy()
            result_df.columns = ['Player', 'Team', 'Pos', 'FP', 'G', 'A', 'SV']
            st.dataframe(result_df, use_container_width=True, hide_index=True)
        else:
            st.info("No players match your filters")

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
            field_players_list = [p for p in starters if p.get('position') == 'field']
            st.session_state[f'{user_id}_selected_fields'] = field_players_list[:5]

            # Bench players
            st.session_state[f'{user_id}_selected_bench'] = bench[:2]

    # === RESPONSIVE LAYOUT ===
    # Use expanders for mobile-friendly design
    use_expanders = st.checkbox("📱 Mobile View (Collapsible Sections)", value=False, key=f"{user_id}_mobile_view")

    if use_expanders:
        # Mobile-friendly expander view
        with st.expander("🥅 Goalkeeper (1)", expanded=True):
            _render_goalkeeper_section(player_pool, user_id)

        with st.expander("🎯 Center (1)", expanded=True):
            _render_center_section(player_pool, user_id)

        with st.expander("🏊 Field Players (5)", expanded=True):
            _render_field_section(player_pool, user_id)

        with st.expander("🪑 Bench (2)", expanded=True):
            _render_bench_section(player_pool, user_id)
    else:
        # Desktop 4-column layout
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

        with col1:
            st.markdown("#### 🥅 Goalkeeper (1)")
            _render_goalkeeper_section(player_pool, user_id)

        with col2:
            st.markdown("#### 🎯 Center (1)")
            _render_center_section(player_pool, user_id)

        with col3:
            st.markdown("#### 🏊 Field Players (5)")
            _render_field_section(player_pool, user_id)

        with col4:
            st.markdown("#### 🪑 Bench (2)")
            _render_bench_section(player_pool, user_id)

    # Save Roster Button
    st.markdown("---")

    if st.button("💾 Save Full Roster (Starters + Bench)", type="primary", use_container_width=True,
                 key=f"{user_id}_save"):
        save_current_roster(user_id)


def _render_goalkeeper_section(player_pool, user_id):
    """Helper to render goalkeeper selection"""
    goalkeepers = player_pool[player_pool['position'] == 'goalkeeper']
    goalkeepers = goalkeepers[goalkeepers['fantasy_points'] > 0].sort_values('fantasy_points', ascending=False)

    gk_options = {"-- Select Goalkeeper --": None}
    gk_display_names = ["-- Select Goalkeeper --"]

    for idx, row in goalkeepers.iterrows():
        display_name = f"#{row['jersey']} {row['player'].replace(' (C)', '')} ({row['team_code']}) - {row['match_name']} - {row['fantasy_points']} pts"
        gk_options[display_name] = row.to_dict()
        gk_display_names.append(display_name)

    current_gk = st.session_state[f'{user_id}_selected_gk']
    widget_key = f"{user_id}_gk_select"

    default_idx = 0
    if current_gk and isinstance(current_gk, dict):
        for i, name in enumerate(gk_display_names):
            if name != "-- Select Goalkeeper --" and gk_options[name].get('player') == current_gk.get('player'):
                default_idx = i
                break

    selected_gk = st.selectbox(
        "Select goalkeeper:",
        options=gk_display_names,
        index=default_idx,
        key=widget_key,
        label_visibility="collapsed"
    )

    if selected_gk != "-- Select Goalkeeper --" and selected_gk in gk_options:
        st.session_state[f'{user_id}_selected_gk'] = gk_options[selected_gk]
        st.markdown(render_selected_player(gk_options[selected_gk], 'goalkeeper'), unsafe_allow_html=True)
    else:
        st.session_state[f'{user_id}_selected_gk'] = None
        st.caption("No goalkeeper selected")


def _render_center_section(player_pool, user_id):
    """Helper to render center selection"""
    centers = player_pool[player_pool['position'] == 'center']
    centers = centers[centers['fantasy_points'] > 0].sort_values('fantasy_points', ascending=False)

    center_options = {"-- Select Center --": None}
    center_display_names = ["-- Select Center --"]

    for idx, row in centers.iterrows():
        display_name = f"#{row['jersey']} {row['player'].replace(' (C)', '')} ({row['team_code']}) - {row['match_name']} - {row['fantasy_points']} pts"
        center_options[display_name] = row.to_dict()
        center_display_names.append(display_name)

    current_center = st.session_state[f'{user_id}_selected_center']
    widget_key = f"{user_id}_center_select"

    default_idx = 0
    if current_center and isinstance(current_center, dict):
        for i, name in enumerate(center_display_names):
            if name != "-- Select Center --" and center_options[name].get('player') == current_center.get('player'):
                default_idx = i
                break

    selected_center = st.selectbox(
        "Select center:",
        options=center_display_names,
        index=default_idx,
        key=widget_key,
        label_visibility="collapsed"
    )

    if selected_center != "-- Select Center --" and selected_center in center_options:
        st.session_state[f'{user_id}_selected_center'] = center_options[selected_center]
        st.markdown(render_selected_player(center_options[selected_center], 'center'), unsafe_allow_html=True)
    else:
        st.session_state[f'{user_id}_selected_center'] = None
        st.caption("No center selected")


def _render_field_section(player_pool, user_id):
    """Helper to render field players selection"""
    field_players_df = player_pool[player_pool['position'] == 'field']
    field_players_df = field_players_df[field_players_df['fantasy_points'] > 0].sort_values('fantasy_points',
                                                                                            ascending=False)

    field_options = {"-- Select Field Player --": None}
    field_display_names = ["-- Select Field Player --"]

    for idx, row in field_players_df.iterrows():
        display_name = f"#{row['jersey']} {row['player'].replace(' (C)', '')} ({row['team_code']}) - {row['match_name']} - {row['fantasy_points']} pts"
        field_options[display_name] = row.to_dict()
        field_display_names.append(display_name)

    if f'{user_id}_field_1' not in st.session_state:
        for i in range(1, 6):
            st.session_state[f'{user_id}_field_{i}'] = "-- Select Field Player --"

    selected_field_players = []
    for i in range(1, 6):
        current_value = st.session_state[f'{user_id}_field_{i}']

        if current_value in field_display_names:
            default_idx = field_display_names.index(current_value)
        else:
            default_idx = 0
            st.session_state[f'{user_id}_field_{i}'] = "-- Select Field Player --"

        selected = st.selectbox(
            f"Field Player {i}",
            options=field_display_names,
            index=default_idx,
            key=f"{user_id}_field_select_{i}",
            label_visibility="collapsed"
        )

        st.session_state[f'{user_id}_field_{i}'] = selected

        if selected != "-- Select Field Player --" and selected in field_options:
            selected_field_players.append(field_options[selected])
            st.markdown(render_selected_player(field_options[selected], 'field'), unsafe_allow_html=True)
        else:
            st.caption(f"Slot {i}: Empty")

    st.session_state[f'{user_id}_selected_fields'] = selected_field_players
    st.caption(f"Selected: {len(selected_field_players)}/5")


def _render_bench_section(player_pool, user_id):
    """Helper to render bench selection"""
    all_players = player_pool[player_pool['fantasy_points'] > 0].sort_values('fantasy_points', ascending=False)

    bench_options = {"-- Select Bench Player --": None}
    bench_display_names = ["-- Select Bench Player --"]

    for idx, row in all_players.iterrows():
        position_symbol = "🥅" if row['position'] == 'goalkeeper' else "🎯" if row['position'] == 'center' else "🏊"
        display_name = f"{position_symbol} #{row['jersey']} {row['player'].replace(' (C)', '')} ({row['team_code']}) - {row['match_name']} - {row['fantasy_points']} pts"
        bench_options[display_name] = row.to_dict()
        bench_display_names.append(display_name)

    if f'{user_id}_bench_1' not in st.session_state:
        st.session_state[f'{user_id}_bench_1'] = "-- Select Bench Player --"
        st.session_state[f'{user_id}_bench_2'] = "-- Select Bench Player --"

    selected_bench_players = []
    for i in range(1, 3):
        current_value = st.session_state[f'{user_id}_bench_{i}']

        if current_value in bench_display_names:
            default_idx = bench_display_names.index(current_value)
        else:
            default_idx = 0
            st.session_state[f'{user_id}_bench_{i}'] = "-- Select Bench Player --"

        selected = st.selectbox(
            f"Bench {i}",
            options=bench_display_names,
            index=default_idx,
            key=f"{user_id}_bench_select_{i}",
            label_visibility="collapsed"
        )

        st.session_state[f'{user_id}_bench_{i}'] = selected

        if selected != "-- Select Bench Player --" and selected in bench_options:
            selected_bench_players.append(bench_options[selected])
            position_type = bench_options[selected].get('position', 'field')
            st.markdown(render_selected_player(bench_options[selected], position_type), unsafe_allow_html=True)
        else:
            st.caption(f"Bench {i}: Empty")

    st.session_state[f'{user_id}_selected_bench'] = selected_bench_players
    st.caption(f"Bench: {len(selected_bench_players)}/2")


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
            if user_id == "current_user":
                league_manager.add_user(user_id, "My Team Manager", "My Team")
            else:
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


def render_waiver_wire(player_pool, user_id="current_user"):
    """NEW: Render waiver wire for dropping/adding players"""
    st.markdown("### 🔄 Waiver Wire - Add/Drop Players")

    current_week = league_manager.matchup_manager.current_week
    my_lineup = league_manager.get_lineup(user_id, current_week)

    if not my_lineup or 'players' not in my_lineup:
        st.warning("⚠️ Set your initial roster first in Team Builder")
        return

    my_players = my_lineup['players']

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🗑️ Drop Player")

        # Create dropdown of current players
        drop_options = ["-- Select Player to Drop --"]
        drop_mapping = {}

        for i, player in enumerate(my_players):
            pos_symbol = "🥅" if player.get('position') == 'goalkeeper' else "🎯" if player.get(
                'position') == 'center' else "🏊"
            display = f"{pos_symbol} #{player.get('jersey')} {player.get('player')} - {player.get('fantasy_points')} pts"
            drop_options.append(display)
            drop_mapping[display] = i

        selected_drop = st.selectbox("Select player to drop:", drop_options, key=f"{user_id}_drop_player")

        if selected_drop != "-- Select Player to Drop --":
            player_idx = drop_mapping[selected_drop]
            st.info(f"Will drop: {selected_drop}")

    with col2:
        st.markdown("#### ➕ Add Player")

        # Show available players (not on current roster)
        my_player_names = [p.get('player') for p in my_players]
        available_players = player_pool[~player_pool['player'].isin(my_player_names)]
        available_players = available_players[available_players['fantasy_points'] > 0].sort_values('fantasy_points',
                                                                                                   ascending=False)

        # Filter options
        filter_pos = st.selectbox("Filter by position:", ["All", "Goalkeeper", "Center", "Field"],
                                  key=f"{user_id}_waiver_filter")

        if filter_pos != "All":
            pos_map = {"Goalkeeper": "goalkeeper", "Center": "center", "Field": "field"}
            available_players = available_players[available_players['position'] == pos_map[filter_pos]]

        # Create dropdown
        add_options = ["-- Select Player to Add --"]
        add_mapping = {}

        for idx, row in available_players.head(50).iterrows():
            pos_symbol = "🥅" if row['position'] == 'goalkeeper' else "🎯" if row['position'] == 'center' else "🏊"
            display = f"{pos_symbol} #{row['jersey']} {row['player']} ({row['team_code']}) - {row['fantasy_points']} pts"
            add_options.append(display)
            add_mapping[display] = row.to_dict()

        selected_add = st.selectbox("Select player to add:", add_options, key=f"{user_id}_add_player")

        if selected_add != "-- Select Player to Add --":
            st.success(f"Will add: {selected_add}")

    # Execute transaction
    if st.button("🔄 Execute Add/Drop Transaction", type="primary", use_container_width=True):
        if selected_drop == "-- Select Player to Drop --" or selected_add == "-- Select Player to Add --":
            st.warning("⚠️ Must select both a player to drop and a player to add")
        else:
            # Get indices
            drop_idx = drop_mapping[selected_drop]
            new_player = add_mapping[selected_add]

            # Update roster
            updated_roster = my_players.copy()
            updated_roster[drop_idx] = new_player

            # Validate new roster
            is_valid, message = lineup_manager.validate_roster(updated_roster)

            if is_valid:
                # Save updated lineup
                if league_manager.set_lineup(user_id, current_week, updated_roster):
                    st.success(
                        f"✅ Transaction complete! Dropped {my_players[drop_idx].get('player')}, Added {new_player.get('player')}")
                    st.rerun()
                else:
                    st.error("❌ Failed to save updated roster")
            else:
                st.error(f"❌ Invalid roster after transaction: {message}")


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
                    user_id = manager_name.lower().replace(" ", "_").replace(".", "")

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
    """Render lineup management UI (View Only)"""
    if not league_manager.users:
        st.warning("⚠️ No managers in the league. Add managers first.")
        return

    st.info("👁️ **View Only** - You can see other managers' rosters but cannot edit them.")

    st.markdown("#### 📋 League Rosters")

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

                    total_points = sum(p.get('fantasy_points', 0) for p in roster_players)
                    st.metric("Total Points", f"{total_points}")

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

                    if 'set_time' in lineup:
                        st.caption(f"Set on: {lineup['set_time']}")
                else:
                    st.info(f"Incomplete roster: {len(roster_players)}/{TEAM_SIZE['total']} players")
            else:
                st.info(f"No roster set for Week {week_to_view}")

    st.markdown("---")
    st.markdown("#### 💡 How to Set Your Roster")
    st.info("""
    1. Go to **Team Builder** tab
    2. Select: 1 Goalkeeper 🥅, 1 Center 🎯, 5 Field Players 🏊 (Starters)
    3. Select: 2 Bench Players 🪑 (any position)
    4. Click **"Save Full Roster"**
    """)


def render_standings():
    """Render standings UI"""
    standings = league_manager.get_standings()

    if not standings or len(standings) == 0:
        st.info("📊 No standings data yet. Calculate scores first!")

        with st.expander("🧪 Preview (Development Mode)", expanded=True):
            sample_data = []
            for i, (user_id, user_data) in enumerate(league_manager.users.items(), 1):
                sample_data.append({
                    'Rank': i,
                    'Team': user_data.get('team_name', 'Unknown'),
                    'Manager': user_data.get('name', 'Unknown'),
                    'W': 0,
                    'L': 0,
                    'PCT': '.000',
                    'Total Pts': 0
                })

            if sample_data:
                st.dataframe(pd.DataFrame(sample_data), use_container_width=True, hide_index=True)

        st.markdown("### 📋 How to Generate Standings")
        st.info("""
        1. **Set Lineups** for all teams in Team Builder
        2. **Create Matchups** in League Setup
        3. **Calculate Scores** in Weekly Matchups
        4. Standings will appear here automatically
        """)
        return

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

    if len(standings) >= 1:
        st.markdown("### 🥇 Top Teams")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("1st Place", standings[0]['team_name'], f"{standings[0]['total_points']} pts")
        if len(standings) >= 2:
            with col2:
                st.metric("2nd Place", standings[1]['team_name'], f"{standings[1]['total_points']} pts")
        if len(standings) >= 3:
            with col3:
                st.metric("3rd Place", standings[2]['team_name'], f"{standings[2]['total_points']} pts")