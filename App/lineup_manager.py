# App/lineup_manager.py
import streamlit as st
from App.config import REQUIRED_POSITIONS, TEAM_SIZE, POSITION_FLEXIBILITY


class LineupManager:
    """Manages lineup creation and validation"""

    def __init__(self):
        self.required_positions = REQUIRED_POSITIONS
        self.team_size = TEAM_SIZE
        self.position_flexibility = POSITION_FLEXIBILITY

    def validate_roster(self, roster_players):
        """Validate if roster meets requirements including bench"""
        if len(roster_players) != self.team_size['total']:
            return False, f"Need exactly {self.team_size['total']} players (7 starters + 2 bench), got {len(roster_players)}"

        # Separate starters and bench (first 7 are starters, last 2 are bench)
        starters = roster_players[:self.team_size['starters']]
        bench = roster_players[self.team_size['starters']:]

        # Validate starters
        position_counts = {'goalkeeper': 0, 'center': 0, 'field': 0}

        for player in starters:
            position = player.get('position')
            if position in position_counts:
                position_counts[position] += 1

        # Check starter requirements
        for pos, required in self.required_positions.items():
            if position_counts[pos] != required:
                return False, f"Starters need exactly {required} {pos}(s), got {position_counts[pos]}"

        # Check total position limits (starters + bench)
        total_counts = {'goalkeeper': 0, 'center': 0, 'field': 0}
        for player in roster_players:
            position = player.get('position')
            if position in total_counts:
                total_counts[position] += 1

        for pos, max_allowed in self.position_flexibility['max_per_position'].items():
            if total_counts[pos] > max_allowed:
                return False, f"Maximum {max_allowed} {pos}(s) allowed, got {total_counts[pos]}"

        return True, "Roster is valid"

    def validate_lineup(self, lineup_players):
        """Validate if lineup (starters only) meets requirements"""
        if len(lineup_players) != self.team_size['starters']:
            return False, f"Need exactly {self.team_size['starters']} starters, got {len(lineup_players)}"

        position_counts = {'goalkeeper': 0, 'center': 0, 'field': 0}

        for player in lineup_players:
            position = player.get('position')
            if position in position_counts:
                position_counts[position] += 1

        # Check requirements
        for pos, required in self.required_positions.items():
            if position_counts[pos] != required:
                return False, f"Need exactly {required} {pos}(s), got {position_counts[pos]}"

        return True, "Lineup is valid"

    def calculate_lineup_points(self, lineup_players, player_points_data):
        """Calculate total points for a lineup"""
        total_points = 0
        player_details = []

        for player in lineup_players:
            player_name = player.get('player')
            team_code = player.get('team_code')

            if player_name and team_code:
                key = (player_name, team_code)
                points = player_points_data.get(key, 0)
                total_points += points

                player_details.append({
                    'player': player_name,
                    'team': team_code,
                    'position': player.get('position'),
                    'points': points
                })

        return total_points, player_details

    def get_player_points_dict(self, player_data):
        """Create a dictionary for quick player points lookup"""
        points_dict = {}

        if player_data is not None and not player_data.empty:
            for _, row in player_data.iterrows():
                key = (row['player'], row['team_code'])
                points_dict[key] = row['fantasy_points']

        return points_dict


# Create a singleton instance
lineup_manager = LineupManager()