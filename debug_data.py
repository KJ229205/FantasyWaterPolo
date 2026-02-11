# debug_data.py
from App.data_manager import data_manager

# Test FTC vs Brescia match
print("Testing FTC vs Brescia data...")
match_df = data_manager.get_match_dataframe('ftc_bre')

print(f"\nTotal players: {len(match_df)}")
print(f"Columns: {match_df.columns.tolist()}")

# Check FTC players
ftc_players = match_df[match_df['team_code'] == 'FTC']
print(f"\nFTC Players: {len(ftc_players)}")

# Check specific player
manhercz = match_df[match_df['player'].str.contains('MANHERCZ')]
if not manhercz.empty:
    print(f"\nMANHERCZ data:")
    print(f"  Goals: {manhercz.iloc[0]['goals']}")
    print(f"  Assists: {manhercz.iloc[0]['assists']}")
    print(f"  Steals: {manhercz.iloc[0]['steals']}")
    print(f"  Blocks: {manhercz.iloc[0]['blocks']}")
    print(f"  Fantasy Points: {manhercz.iloc[0]['fantasy_points']}")

    # Calculate expected points
    expected_points = (manhercz.iloc[0]['goals'] * 5 +
                       manhercz.iloc[0]['assists'] * 3 +
                       manhercz.iloc[0]['steals'] * 2 +
                       manhercz.iloc[0]['blocks'] * 2)
    print(f"  Expected Points: {expected_points}")

# Calculate team totals
ftc_total = ftc_players['fantasy_points'].sum()
bre_total = match_df[match_df['team_code'] == 'BRE']['fantasy_points'].sum()

print(f"\nFTC Total Fantasy Points: {ftc_total}")
print(f"BRE Total Fantasy Points: {bre_total}")
print(f"Match Total: {ftc_total + bre_total}")

# Show top 5 players
print("\nTop 5 Players:")
for idx, row in match_df.head().iterrows():
    print(f"  {row['player']}: {row['fantasy_points']} pts "
          f"({row['goals']}G {row['assists']}A {row['steals']}ST {row['blocks']}BLK)")