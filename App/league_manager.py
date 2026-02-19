# App/league_manager.py
import streamlit as st
from datetime import datetime
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
                'scores': {},  # {week: {user_id: score}}
                'weekly_lineups': {},  # {week: {user_id: lineup}}
                'current_week': 1
            }

        league_data = st.session_state.fantasy_league
        self.users = league_data.get('users', {})
        self.matchup_manager.matchups = league_data.get('matchups', [])
        self.matchup_manager.scores = league_data.get('scores', {})
        self.matchup_manager.current_week = league_data.get('current_week', 1)

        # Load weekly lineups if they exist
        self.weekly_lineups = league_data.get('weekly_lineups', {})

    def save_to_session(self):
        """Save league data to Streamlit session state"""
        st.session_state.fantasy_league = {
            'users': self.users,
            'matchups': self.matchup_manager.matchups,
            'scores': self.matchup_manager.scores,
            'weekly_lineups': self.weekly_lineups,
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

    def set_lineup(self, user_id, week, lineup_data):
        """Set a user's lineup for a specific week"""
        if user_id in self.users:
            if 'lineups' not in self.users[user_id]:
                self.users[user_id]['lineups'] = {}

            self.users[user_id]['lineups'][week] = {
                'players': lineup_data,
                'set_time': datetime.now().isoformat()
            }

            # Also store in weekly_lineups for easy access
            if week not in self.weekly_lineups:
                self.weekly_lineups[week] = {}
            self.weekly_lineups[week][user_id] = lineup_data

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
        return self.weekly_lineups.get(week, {})

    def calculate_weekly_scores(self, week):
        """Calculate scores for all users in a week based on lineups"""
        scores = {}
        lineups = self.get_all_lineups(week)

        for user_id, lineup_data in lineups.items():
            if isinstance(lineup_data, dict) and 'players' in lineup_data:
                players = lineup_data['players']
            else:
                players = lineup_data  # Assume it's already a list

            total = 0
            # Only count starters (first 7)
            starters = players[:7] if len(players) >= 7 else players
            for player in starters:
                total += float(player.get('fantasy_points', 0))
            scores[user_id] = round(total, 1)

        # Store scores
        if week not in self.matchup_manager.scores:
            self.matchup_manager.scores[week] = {}
        self.matchup_manager.scores[week].update(scores)

        # Update matchup scores
        for matchup in self.matchup_manager.matchups:
            if matchup['week'] == week:
                if matchup['team1'] in scores:
                    matchup['team1_score'] = scores[matchup['team1']]
                if matchup['team2'] in scores:
                    matchup['team2_score'] = scores[matchup['team2']]
                matchup['completed'] = True

        self.save_to_session()
        return scores

    def create_weekly_matchups(self, week=None):
        """Create matchups for a week using round robin"""
        if week is None:
            week = self.matchup_manager.current_week

        user_ids = list(self.users.keys())

        # Simple round robin pairing
        matchups = []
        for i in range(0, len(user_ids), 2):
            if i + 1 < len(user_ids):
                matchups.append({
                    'week': week,
                    'team1': user_ids[i],
                    'team2': user_ids[i + 1],
                    'team1_score': 0,
                    'team2_score': 0,
                    'completed': False
                })
            else:
                # Bye week
                matchups.append({
                    'week': week,
                    'team1': user_ids[i],
                    'team2': None,
                    'team1_score': 0,
                    'team2_score': 0,
                    'completed': False
                })

        # Remove existing matchups for this week
        self.matchup_manager.matchups = [
            m for m in self.matchup_manager.matchups if m['week'] != week
        ]
        self.matchup_manager.matchups.extend(matchups)
        self.save_to_session()

        return matchups

    def get_weekly_matchups(self, week=None):
        """Get matchups for a specific week"""
        if week is None:
            week = self.matchup_manager.current_week
        return [m for m in self.matchup_manager.matchups if m['week'] == week]

    def get_user_matchup(self, user_id, week=None):
        """Get a specific user's matchup for a week"""
        if week is None:
            week = self.matchup_manager.current_week

        for matchup in self.matchup_manager.matchups:
            if matchup['week'] == week:
                if matchup['team1'] == user_id or matchup['team2'] == user_id:
                    return matchup
        return None

    def get_standings(self):
        """Get current league standings based on matchups"""
        standings = []

        for user_id, user_data in self.users.items():
            wins = 0
            losses = 0
            total_points = 0

            # Calculate from matchups
            for matchup in self.matchup_manager.matchups:
                if matchup.get('completed', False):
                    if matchup['team1'] == user_id:
                        total_points += matchup['team1_score']
                        if matchup['team2']:
                            if matchup['team1_score'] > matchup['team2_score']:
                                wins += 1
                            elif matchup['team1_score'] < matchup['team2_score']:
                                losses += 1
                    elif matchup['team2'] == user_id:
                        total_points += matchup['team2_score']
                        if matchup['team1']:
                            if matchup['team2_score'] > matchup['team1_score']:
                                wins += 1
                            elif matchup['team2_score'] < matchup['team1_score']:
                                losses += 1

            standings.append({
                'user_id': user_id,
                'name': user_data['name'],
                'team_name': user_data['team_name'],
                'wins': wins,
                'losses': losses,
                'win_pct': wins / (wins + losses) if (wins + losses) > 0 else 0,
                'total_points': total_points
            })

        # Sort by wins, then points
        standings.sort(key=lambda x: (-x['wins'], -x['total_points']))
        return standings


# Create a singleton instance
league_manager = FantasyLeague()