# App/league_matchups.py - Centralized matchup display
import streamlit as st
from App.league_manager import league_manager
from App.config import TEAM_SIZE


def render_weekly_matchups(week):
    """Render all matchups for a given week"""
    st.markdown(f"#### Week {week} Matchups")

    week_matchups = league_manager.get_weekly_matchups(week)

    if not week_matchups:
        st.info("No matchups scheduled for this week")
        return

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


def render_matchup_summary():
    """Render a summary of current week's matchups for home page"""
    current_week = league_manager.matchup_manager.current_week
    week_matchups = league_manager.get_weekly_matchups(current_week)

    if not week_matchups:
        st.info("No matchups this week")
        return

    for matchup in week_matchups[:2]:  # Show first 2 matchups
        team1 = league_manager.users.get(matchup['team1'], {}).get('team_name', 'Unknown')
        if matchup.get('team2'):
            team2 = league_manager.users.get(matchup['team2'], {}).get('team_name', 'Unknown')
            st.write(f"**{team1}** vs **{team2}**")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("", matchup.get('team1_score', 0))
            with col2:
                st.metric("", matchup.get('team2_score', 0))
        else:
            st.write(f"**{team1}** - BYE")