# App/ui_components.py
import streamlit as st
import pandas as pd
from App.config import TEAM_COLORS


def render_player_card(player, show_stats=True):
    """Render a player card with consistent styling"""
    # Determine team color
    if player['team_code'] in TEAM_COLORS['blue_teams']:
        team_color = TEAM_COLORS['blue_color']
    elif player['team_code'] in TEAM_COLORS['red_teams']:
        team_color = TEAM_COLORS['red_color']
    else:
        team_color = TEAM_COLORS['default_color']

    # Position badge
    position_badge = ""
    if player['position'] == 'goalkeeper':
        position_badge = '<span class="position-badge gk-badge">GK</span>'
    elif player['position'] == 'center':
        position_badge = '<span class="position-badge c-badge">C</span>'
    else:
        position_badge = '<span class="position-badge field-badge">F</span>'

    # Stats text
    stats_text = ""
    if show_stats:
        stats_text = f"{player['goals']} goals"
        if player['assists'] > 0:
            stats_text += f" • {player['assists']} assists"
        if player['steals'] > 0:
            stats_text += f" • {player['steals']} steals"
        if player['blocks'] > 0:
            stats_text += f" • {player['blocks']} blocks"
        if player['saves'] > 0:
            stats_text += f" • {player['saves']} saves"

    card_html = f"""
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
        {f'<div style="color: #555; font-size: 0.85rem; margin-top: 0.3rem;">{stats_text}</div>' if stats_text else ''}
    </div>
    """

    return card_html


def render_team_summary(selected_df, goalkeepers, centers, field_players):
    """Render team summary with rating"""
    total_points = selected_df['fantasy_points'].sum()
    avg_points = total_points / 7

    # Calculate rating
    top_gk = goalkeepers.iloc[0]['fantasy_points'] if not goalkeepers.empty else 0
    top_center = centers.iloc[0]['fantasy_points'] if not centers.empty else 0
    top_fields = field_players.head(5)['fantasy_points'].sum() if len(field_players) >= 5 else 0
    max_possible = top_gk + top_center + top_fields

    worst_gk = goalkeepers.iloc[-1]['fantasy_points'] if not goalkeepers.empty else 0
    worst_center = centers.iloc[-1]['fantasy_points'] if not centers.empty else 0
    worst_fields = field_players.tail(5)['fantasy_points'].sum() if len(field_players) >= 5 else 0
    min_possible = worst_gk + worst_center + worst_fields

    if max_possible > min_possible:
        team_percentage = ((total_points - min_possible) / (max_possible - min_possible)) * 100
    else:
        team_percentage = 50

    # Determine rating
    if team_percentage >= 90:
        rating = "A+";
        rating_class = "team-rating-a"
    elif team_percentage >= 80:
        rating = "A";
        rating_class = "team-rating-a"
    elif team_percentage >= 70:
        rating = "B+";
        rating_class = "team-rating-b"
    elif team_percentage >= 60:
        rating = "B";
        rating_class = "team-rating-b"
    elif team_percentage >= 50:
        rating = "C+";
        rating_class = "team-rating-c"
    elif team_percentage >= 40:
        rating = "C";
        rating_class = "team-rating-c"
    elif team_percentage >= 30:
        rating = "D+";
        rating_class = "team-rating-d"
    else:
        rating = "D";
        rating_class = "team-rating-d"

    return {
        'total_points': total_points,
        'avg_points': avg_points,
        'rating': rating,
        'rating_class': rating_class,
        'max_possible': max_possible,
        'team_percentage': team_percentage
    }


def create_position_dropdown(players, position_name, key_suffix):
    """Create a dropdown for selecting players by position"""
    options = {}
    options[f"-- Select {position_name} --"] = None

    for _, row in players.iterrows():
        display_name = f"#{row['jersey']} {row['player'].replace(' (C)', '')} ({row['team_code']}) - {row['match_name']} - {row['fantasy_points']} pts"
        options[display_name] = row

    selected = st.selectbox(
        f"Select {position_name.lower()}:",
        options=list(options.keys()),
        index=0,
        key=f"{position_name.lower()}_{key_suffix}",
        label_visibility="collapsed"
    )

    return selected, options


def render_selected_player(player_data, position_type):
    """Render a selected player's card"""
    from App.config import TEAM_COLORS

    if player_data['team_code'] in TEAM_COLORS['blue_teams']:
        team_color = TEAM_COLORS['blue_color']
    elif player_data['team_code'] in TEAM_COLORS['red_teams']:
        team_color = TEAM_COLORS['red_color']
    else:
        team_color = TEAM_COLORS['default_color']

    if position_type == 'goalkeeper':
        stats_html = f"<div style='color: #555; font-size: 0.85rem;'>{player_data['saves']} saves</div>"
    elif position_type == 'center':
        stats_html = f"<div style='color: #555; font-size: 0.85rem;'>{player_data['goals']}G {player_data['assists']}A</div>"
    else:  # field
        stats_html = f"<div style='color: #555; font-size: 0.85rem;'>{player_data['goals']}G {player_data['assists']}A {player_data['steals']}ST {player_data['blocks']}BLK</div>"

    return f"""
    <div style="background-color: white; padding: 1rem; border-radius: 8px; border-left: 4px solid {team_color}; margin-top: 0.5rem;">
        <div style="font-weight: bold; color: {team_color};">
            #{player_data['jersey']} {player_data['player'].replace(' (C)', '')}
        </div>
        <div style="color: #666; font-size: 0.9rem;">
            {player_data['team_code']} • {player_data['match_name']}
        </div>
        <div style="color: #2E7D32; font-weight: bold; margin-top: 0.5rem;">
            {player_data['fantasy_points']} pts
        </div>
        {stats_html}
    </div>
    """