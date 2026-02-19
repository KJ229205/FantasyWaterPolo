# App/matchup_page.py - Dedicated Matchup Page
import streamlit as st
from App.league_manager import league_manager
from App.config import TEAM_SIZE


def ensure_test_matchup():
    """Ensure there's a test matchup available"""
    current_week = league_manager.matchup_manager.current_week
    my_user_id = "current_user"

    # Find if we already have a matchup
    my_matchup = league_manager.get_user_matchup(my_user_id, current_week)
    if my_matchup:
        return my_matchup

    # No matchup found, create one with the first available opponent
    opponent_id = None
    for uid in league_manager.users:
        if uid != my_user_id:
            opponent_id = uid
            break

    if not opponent_id:
        # Create a default opponent if none exists
        league_manager.add_user("opponent_team", "Test Opponent", "Opponent Team")
        opponent_id = "opponent_team"

    # Create all matchups for the week
    league_manager.create_weekly_matchups(current_week)

    return league_manager.get_user_matchup(my_user_id, current_week)


def render_matchup_page(load_match_data_func):
    """My Fantasy Matchup - This Week's Head-to-Head"""

    # CSS styling
    st.markdown("""
    <style>
        section[data-testid="stSidebar"] ~ div .stMarkdown * {
            color: #FFFFFF !important;
        }
        .main-header {
            color: #FFFFFF !important;
            text-align: center;
            margin-bottom: 2rem;
        }
        .position-header {
            background-color: #2D2D2D !important;
            color: #FFFFFF !important;
            border-bottom: 2px solid #0066CC;
            padding: 0.8rem;
            border-radius: 6px;
            margin: 1.5rem 0 0.8rem 0;
            font-weight: bold;
        }
        .stAlert {
            background-color: #2D2D2D !important;
            color: #FFFFFF !important;
            border-left-color: #0066CC !important;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 class="main-header">⚔️ My Matchup</h1>', unsafe_allow_html=True)

    current_week = league_manager.matchup_manager.current_week
    my_user_id = "current_user"

    # Ensure we have a test matchup
    my_matchup = ensure_test_matchup()

    if not my_matchup:
        st.warning("No matchup available")
        return

    # Find opponent
    opponent_id = my_matchup['team2'] if my_matchup['team1'] == my_user_id else my_matchup['team1']

    st.markdown(f"### Week {current_week}")

    # Get team data
    my_team_data = league_manager.users.get(my_user_id, {})
    my_team_name = my_team_data.get('team_name', 'My Team')
    opponent_data = league_manager.users.get(opponent_id, {})
    opponent_name = opponent_data.get('team_name', 'Unknown')

    # Get scores from the matchup (already calculated)
    if my_matchup['team1'] == my_user_id:
        my_score = my_matchup.get('team1_score', 0)
        opponent_score = my_matchup.get('team2_score', 0)
    else:
        my_score = my_matchup.get('team2_score', 0)
        opponent_score = my_matchup.get('team1_score', 0)

    # Get lineups for display
    my_lineup = league_manager.get_lineup(my_user_id, current_week)
    opponent_lineup = league_manager.get_lineup(opponent_id, current_week)

    # HEADER - Scoreboard
    col1, col2, col3 = st.columns([2, 1, 2])

    with col1:
        winner_badge = "🏆 " if my_score > opponent_score else ""
        st.markdown(f"""
        <div style="background: #1E1E1E; padding: 2rem; border-radius: 12px; border: 2px solid #0066CC; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
            <span style="font-size: 2.5rem; color: #FFFFFF;">👤</span>
            <h2 style="margin: 0.5rem 0; color: #FFFFFF !important;">{winner_badge}{my_team_name}</h2>
            <div style="font-size: 3rem; font-weight: bold; color: {'#4CAF50' if my_score > opponent_score else '#FFFFFF'} !important;">{my_score}</div>
            <div style="color: #AAAAAA !important;">Current Score</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center; height: 100%;">
            <span style="font-size: 2rem; font-weight: bold; color: #FFFFFF !important; background: #2D2D2D; padding: 1rem; border-radius: 50%;">VS</span>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        winner_badge = "🏆 " if opponent_score > my_score else ""
        st.markdown(f"""
        <div style="background: #1E1E1E; padding: 2rem; border-radius: 12px; border: 2px solid #CC3333; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
            <span style="font-size: 2.5rem; color: #FFFFFF;">🏊</span>
            <h2 style="margin: 0.5rem 0; color: #FFFFFF !important;">{winner_badge}{opponent_name}</h2>
            <div style="font-size: 3rem; font-weight: bold; color: {'#F44336' if opponent_score > my_score else '#FFFFFF'} !important;">{opponent_score}</div>
            <div style="color: #AAAAAA !important;">Current Score</div>
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
                    my_pts = my_player.get('fantasy_points', 0)
                    opp_pts = opp_player.get('fantasy_points', 0) if opp_player else 0
                    bg_color = "#1E3A2E" if my_pts > opp_pts else "#2D2D2D"
                    st.markdown(f"""
                    <div style="background: {bg_color}; padding: 1rem; border-radius: 8px; border-left: 4px solid #0066CC; margin-bottom: 0.5rem;">
                        <div style="font-weight: bold; color: #FFFFFF !important;">#{my_player.get('jersey', '?')} {my_player.get('player', 'Unknown')}</div>
                        <div style="color: #AAAAAA !important; font-size: 0.9rem;">{my_player.get('team_code', '?')}</div>
                        <div style="color: #4CAF50 !important; font-weight: bold; font-size: 1.2rem;">{my_pts} pts</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(
                        "<div style='padding: 1rem; color: #AAAAAA !important; text-align: center; background: #2D2D2D; border-radius: 8px;'>— Empty —</div>",
                        unsafe_allow_html=True)

            with col_mid:
                st.markdown(
                    "<div style='height: 100%; display: flex; align-items: center; justify-content: center;'><span style='color: #FFFFFF !important;'>⚔️</span></div>",
                    unsafe_allow_html=True)

            with col_right:
                if opp_player:
                    my_pts = my_player.get('fantasy_points', 0) if my_player else 0
                    opp_pts = opp_player.get('fantasy_points', 0)
                    bg_color = "#3A2E2E" if opp_pts > my_pts else "#2D2D2D"
                    st.markdown(f"""
                    <div style="background: {bg_color}; padding: 1rem; border-radius: 8px; border-left: 4px solid #CC3333; margin-bottom: 0.5rem;">
                        <div style="font-weight: bold; color: #FFFFFF !important;">#{opp_player.get('jersey', '?')} {opp_player.get('player', 'Unknown')}</div>
                        <div style="color: #AAAAAA !important; font-size: 0.9rem;">{opp_player.get('team_code', '?')}</div>
                        <div style="color: #F44336 !important; font-weight: bold; font-size: 1.2rem;">{opp_pts} pts</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(
                        "<div style='padding: 1rem; color: #AAAAAA !important; text-align: center; background: #2D2D2D; border-radius: 8px;'>— Empty —</div>",
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
                <div style="padding: 0.5rem; border-bottom: 1px solid #444; color: #FFFFFF !important;">
                    {pos_symbol} #{player.get('jersey', '?')} {player.get('player', 'Unknown')} - {player.get('team_code', '?')}
                    <span style="float: right; color: #AAAAAA !important;">{player.get('fantasy_points', 0)} pts</span>
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
                <div style="padding: 0.5rem; border-bottom: 1px solid #444; color: #FFFFFF !important;">
                    {pos_symbol} #{player.get('jersey', '?')} {player.get('player', 'Unknown')} - {player.get('team_code', '?')}
                    <span style="float: right; color: #AAAAAA !important;">{player.get('fantasy_points', 0)} pts</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No bench players")

    # Score Breakdown
    st.markdown("---")
    with st.expander("🔍 Score Breakdown", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**{my_team_name} - {my_score} pts**")
            if my_lineup and 'players' in my_lineup:
                for p in my_lineup['players'][:TEAM_SIZE['starters']]:
                    st.write(f"• {p.get('player')}: {p.get('fantasy_points')} pts")

        with col2:
            st.markdown(f"**{opponent_name} - {opponent_score} pts**")
            if opponent_lineup and 'players' in opponent_lineup:
                for p in opponent_lineup['players'][:TEAM_SIZE['starters']]:
                    st.write(f"• {p.get('player')}: {p.get('fantasy_points')} pts")

    # Recalculate button
    st.markdown("---")
    if st.button("🔄 Recalculate All Scores", type="primary", use_container_width=True):
        scores = league_manager.calculate_weekly_scores(current_week)
        st.success(f"Recalculated scores for {len(scores)} teams!")
        st.rerun()