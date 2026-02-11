# App/league_manager.py
import streamlit as st
from datetime import datetime  # ADD THIS IMPORT
from App.matchup_manager import MatchupManager


class FantasyLeague:
    """Manages fantasy league with users and lineups"""

    def __init__(self, league_name="Fantasy Water Polo League"):
        self.league_name = league_name
        self.users = {}  # {user_id: {name: "", team_name: "", lineups: {}}}
        self.matchup_manager = MatchupManager()
        self.load_from_session()

    def load_from_session(self):
        """Load league data from Streamlit session state"""
        if 'fantasy_league' not in st.session_state:
            st.session_state.fantasy_league = {
                'users': {},
                'matchups': [],
                'scores': {},
                'current_week': 1
            }

        league_data = st.session_state.fantasy_league
        self.users = league_data.get('users', {})
        self.matchup_manager.matchups = league_data.get('matchups', [])
        self.matchup_manager.scores = league_data.get('scores', {})
        self.matchup_manager.current_week = league_data.get('current_week', 1)

    def save_to_session(self):
        """Save league data to Streamlit session state"""
        st.session_state.fantasy_league = {
            'users': self.users,
            'matchups': self.matchup_manager.matchups,
            'scores': self.matchup_manager.scores,
            'current_week': self.matchup_manager.current_week
        }

    def add_user(self, user_id, name, team_name=""):
        """Add a new user to the league"""
        if not team_name:
            team_name = f"{name}'s Team"

        if user_id not in self.users:
            self.users[user_id] = {
                'name': name,
                'team_name': team_name,
                'lineups': {},  # {week: lineup_data}
                'total_points': 0,
                'wins': 0,
                'losses': 0
            }
            self.save_to_session()
            return True
        return False

    def remove_user(self, user_id):
        """Remove a user from the league"""
        if user_id in self.users:
            del self.users[user_id]
            self.save_to_session()
            return True
        return False

    def set_lineup(self, user_id, week, lineup_data):
        """Set a user's lineup for a specific week"""
        if user_id in self.users:
            if 'lineups' not in self.users[user_id]:
                self.users[user_id]['lineups'] = {}

            self.users[user_id]['lineups'][week] = {
                'players': lineup_data,
                'set_time': datetime.now().isoformat()
            }
            self.save_to_session()
            return True
        return False

    def get_lineup(self, user_id, week):
        """Get a user's lineup for a specific week"""
        if user_id in self.users and week in self.users[user_id].get('lineups', {}):
            return self.users[user_id]['lineups'][week]
        return None

    def get_all_lineups(self, week):
        """Get all lineups for a specific week"""
        week_lineups = {}
        for user_id, user_data in self.users.items():
            lineup = self.get_lineup(user_id, week)
            if lineup:
                week_lineups[user_id] = lineup
        return week_lineups

    def create_weekly_matchups(self, week=None):
        """Create matchups for a week"""
        user_ids = list(self.users.keys())
        matchups = self.matchup_manager.create_round_robin_matchups(user_ids, week)

        # Store matchups
        if week is not None:
            # Remove existing matchups for this week
            self.matchup_manager.matchups = [
                m for m in self.matchup_manager.matchups if m['week'] != week
            ]

        self.matchup_manager.matchups.extend(matchups)
        self.save_to_session()

        return matchups

    def calculate_weekly_scores(self, week, player_points_data):
        """Calculate scores for all users in a week"""
        lineups = {}
        for user_id in self.users:
            lineup_data = self.get_lineup(user_id, week)
            if lineup_data:
                lineups[user_id] = lineup_data

        scores = self.matchup_manager.calculate_matchup_scores(
            week,
            list(self.users.keys()),
            lineups,
            player_points_data
        )
        self.save_to_session()
        return scores

    def get_standings(self):
        """Get current league standings"""
        return self.matchup_manager.get_standings(self.users, self.matchup_manager.matchups)

    def get_weekly_matchups(self, week=None):
        """Get matchups for a specific week"""
        return self.matchup_manager.get_weekly_matchups(week)

    def get_user_matchup(self, user_id, week=None):
        """Get a specific user's matchup for a week"""
        return self.matchup_manager.get_user_matchup(user_id, week)


# Create a singleton instance
league_manager = FantasyLeague()