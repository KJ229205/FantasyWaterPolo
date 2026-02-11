# App/config.py
SCORING_RULES = {
    "Goal": 5,
    "Assist": 3,
    "Steal": 2,
    "Block": 2,
    "Save": 2,
    "Exclusion Drawn": 1
}

REQUIRED_POSITIONS = {
    'goalkeeper': 1,
    'center': 1,
    'field': 5
}

TEAM_COLORS = {
    'blue_teams': ['NBG', 'FTC', 'PRI', 'RAD', 'OLY', 'REC', 'SAB', 'HAN'],
    'red_teams': ['JAD', 'BRE', 'ORA', 'MAR', 'BAR', 'MLA', 'VAS', 'JHN'],
    'blue_color': "#0066CC",
    'red_color': "#CC3333",
    'default_color': "#666666"
}

CSS_STYLES = """
<style>
    .main-header {
        font-size: 2.8rem;
        color: #0066CC;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
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
    .team-rating-a { color: #198754; font-weight: bold; }
    .team-rating-b { color: #0dcaf0; font-weight: bold; }
    .team-rating-c { color: #fd7e14; font-weight: bold; }
    .team-rating-d { color: #dc3545; font-weight: bold; }
</style>
"""

AVAILABLE_MATCHES = [
    ("All Matches (Week 1)", "all"),
    ("Novi Beograd vs Jadran", "nbg_jad"),
    ("FTC vs Brescia", "ftc_bre"),
    ("Primorac vs Oradea", "pri_ora"),
    ("Marseille vs Barceloneta", "mar_bar"),
    ("Radnicki vs Mladost", "rad_mla"),
    ("Olympiacos vs Vasas", "oly_vas"),
    ("Jadran HN vs Pro Recco", "jhn_rec"),
    ("Sabadell vs Hannover", "sab_han")
]

# TEAM COMPOSITION
TEAM_SIZE = {
    'starters': 7,  # 1 GK + 1 C + 5 Field
    'bench': 2,     # 2 bench spots
    'total': 9      # Total roster size
}

POSITION_FLEXIBILITY = {
    'bench': ['goalkeeper', 'center', 'field'],  # Bench can be any position
    'max_per_position': {
        'goalkeeper': 2,  # Max 2 GKs total (1 starter + 1 bench)
        'center': 2,      # Max 2 Cs total
        'field': 7        # Max 7 Field total (5 starters + 2 bench)
    }
}