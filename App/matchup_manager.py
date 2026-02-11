# App/matchup_manager.py
import streamlit as st
import pandas as pd
from datetime import datetime

class MatchupManager:
    """Manages weekly matchups and scoring"""

    def __init__(self):
        self.matchups = []
        self.scores = {}
        self.current_week = 1

    # In matchup_manager.py, update the create_round_robin_matchups method:
    def create_round_robin_matchups(self, user_ids, week=None):
        """Create round-robin matchups for a week - works with any even number"""
        if week is None:
            week = self.current_week

        if len(user_ids) < 2:
            return []

        matchups = []

        # Make a copy to avoid modifying original
        working_ids = user_ids.copy()

        # If odd number, one team gets bye
        if len(working_ids) % 2 == 1:
            matchups.append({
                'week': week,
                'team1': working_ids[-1],
                'team2': None,  # Bye week
                'team1_score': 0,
                'team2_score': 0,
                'completed': True,
                'is_bye': True,
                'created_at': datetime.now().isoformat()
            })
            working_ids = working_ids[:-1]  # Remove the bye team from pairing

        # Pair remaining teams
        for i in range(0, len(working_ids), 2):
            if i + 1 < len(working_ids):
                matchup = {
                    'week': week,
                    'team1': working_ids[i],
                    'team2': working_ids[i + 1],
                    'team1_score': 0,
                    'team2_score': 0,
                    'completed': False,
                    'is_bye': False,
                    'created_at': datetime.now().isoformat()
                }
                matchups.append(matchup)

        # Ensure matchups are saved to session
        if hasattr(self, 'save_to_session'):
            self.save_to_session()

        return matchups

    def calculate_matchup_scores(self, week, users, lineups, player_points_data):
        """Calculate scores for all matchups in a week"""
        if week not in self.scores:
            self.scores[week] = {}

        # Calculate each user's score
        for user_id in users:
            lineup = lineups.get(user_id, {}).get(week, {}).get('players', [])
            total_points = 0

            for player in lineup:
                player_name = player.get('player')
                team_code = player.get('team_code')

                if player_name and team_code:
                    key = (player_name, team_code)
                    total_points += player_points_data.get(key, 0)

            self.scores[week][user_id] = total_points

        # Update matchup scores
        for matchup in self.matchups:
            if matchup['week'] == week:
                matchup['team1_score'] = self.scores[week].get(matchup['team1'], 0)
                if matchup['team2']:
                    matchup['team2_score'] = self.scores[week].get(matchup['team2'], 0)
                    matchup['completed'] = True

        return self.scores[week]

    def get_weekly_matchups(self, week=None):
        """Get matchups for a specific week"""
        if week is None:
            week = self.current_week

        return [m for m in self.matchups if m['week'] == week]

    def get_user_matchup(self, user_id, week=None):
        """Get a specific user's matchup for a week"""
        if week is None:
            week = self.current_week

        for matchup in self.matchups:
            if matchup['week'] == week:
                if matchup['team1'] == user_id or matchup['team2'] == user_id:
                    return matchup
        return None

    def get_standings(self, users, matchups):
        """Calculate league standings"""
        standings = []

        for user_id, user_data in users.items():
            total_points = 0
            wins = 0
            losses = 0

            # Calculate total points from all weeks
            for week, scores in self.scores.items():
                if user_id in scores:
                    total_points += scores[user_id]

            # Calculate wins/losses from matchups
            for matchup in matchups:
                if matchup.get('completed') and matchup.get('team2'):
                    if matchup['team1'] == user_id:
                        if matchup['team1_score'] > matchup['team2_score']:
                            wins += 1
                        elif matchup['team1_score'] < matchup['team2_score']:
                            losses += 1
                    elif matchup['team2'] == user_id:
                        if matchup['team2_score'] > matchup['team1_score']:
                            wins += 1
                        elif matchup['team2_score'] < matchup['team1_score']:
                            losses += 1

            standings.append({
                'user_id': user_id,
                'name': user_data.get('name', 'Unknown'),
                'team_name': user_data.get('team_name', 'Unknown'),
                'total_points': total_points,
                'wins': wins,
                'losses': losses,
                'win_pct': wins / max(wins + losses, 1)
            })

        # Sort by wins, then points
        standings.sort(key=lambda x: (x['wins'], x['total_points']), reverse=True)

        return standings