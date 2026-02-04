# simple_scrape.py
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# Direct URL from your copy-paste
url = "https://championsleague.europeanaquatics.org/match-details-2526/?c=ASM&g=1&t=A01&gr=2&s1=NBG&s2=JSP&st=2&sch=02122025"

# Try with minimal headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'text/html',
}

print("Fetching page...")
response = requests.get(url, headers=headers, timeout=30)
print(f"Status: {response.status_code}")

# Save the HTML
with open('match_page_full.html', 'w', encoding='utf-8') as f:
    f.write(response.text)
print("Saved HTML to 'match_page_full.html'")

# Parse with BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser')

# Let's extract data from the HTML you pasted
players = []

# Find team sections
team_sections = soup.find_all(string=re.compile(r'VK NOVI BEOGRAD|VK JADRAN SPLIT', re.I))
print(f"Found {len(team_sections)} team sections")

# Look for tables after team names
all_tables = soup.find_all('table')
print(f"Found {len(all_tables)} total tables")

# Manually parse based on the HTML you showed
# The tables have this structure:
# N. PLAYER MIN TOTAL % A C X 6M PS CA PSO AS TF ST BL SP 18C 18F 2EX P EX 4EX

for table in all_tables:
    # Get all rows
    rows = table.find_all('tr')

    # Skip tables with too few rows (not player tables)
    if len(rows) < 5:
        continue

    # Check if first row has headers that look like player stats
    first_row = rows[0].get_text()
    if any(word in first_row for word in ['N.', 'PLAYER', 'TOTAL', 'A', 'ST', 'BL']):
        print(f"Found player table with {len(rows)} rows")

        # Determine team
        team_text = ''
        # Look for team name in previous elements
        prev_elem = table.find_previous(string=re.compile(r'VK|NBG|JSP', re.I))
        if prev_elem:
            team_text = prev_elem.get_text(strip=True)

        team_code = 'NBG' if 'NBG' in team_text else 'JSP' if 'JSP' in team_text else 'UNK'
        team_full = 'VK Novi Beograd' if 'NOVI' in team_text.upper() else 'VK Jadran Split' if 'JADRAN' in team_text.upper() else 'Unknown'

        # Parse each player row (skip header row)
        for row in rows[1:]:
            cells = row.find_all('td')
            if len(cells) >= 3:  # Need at least jersey, name, and some stats
                try:
                    jersey = cells[0].get_text(strip=True)
                    player_name = cells[1].get_text(strip=True)

                    # Try to extract goals from TOTAL column (format: "4/6")
                    goals_text = cells[3].get_text(strip=True) if len(cells) > 3 else "0/0"
                    if '/' in goals_text:
                        goals = int(goals_text.split('/')[0])
                    else:
                        goals = 0

                    # Extract assists (AS column)
                    assists = 0
                    if len(cells) > 11:  # AS is column index 11 based on your HTML
                        assists_text = cells[11].get_text(strip=True)
                        assists = int(assists_text) if assists_text.isdigit() else 0

                    # Extract steals (ST column)
                    steals = 0
                    if len(cells) > 13:  # ST is column index 13
                        steals_text = cells[13].get_text(strip=True)
                        steals = int(steals_text) if steals_text.isdigit() else 0

                    # Extract blocks (BL column)
                    blocks = 0
                    if len(cells) > 14:  # BL is column index 14
                        blocks_text = cells[14].get_text(strip=True)
                        blocks = int(blocks_text) if blocks_text.isdigit() else 0

                    # Determine position - check for (C) in name or goalkeeper
                    position = 'field'
                    if '(C)' in player_name:
                        position = 'center'
                    elif 'GLUSAC' in player_name.upper() or 'CELAR' in player_name.upper() or 'PAJKOVIC' in player_name.upper():
                        position = 'goalkeeper'

                    player_data = {
                        'jersey': jersey,
                        'player': player_name.replace(' (C)', ''),  # Remove (C) from name
                        'team_code': team_code,
                        'team_full': team_full,
                        'goals': goals,
                        'assists': assists,
                        'steals': steals,
                        'blocks': blocks,
                        'saves': 0,  # Field players have 0 saves
                        'position': position
                    }

                    players.append(player_data)
                    print(f"  Added: #{jersey} {player_name} - {goals}G {assists}A {steals}ST")

                except (IndexError, ValueError) as e:
                    continue

# Also look for goalkeeper tables
gk_tables = soup.find_all('table')
for table in gk_tables:
    # Check if it's a goalkeeper table by looking for "GOALKEEPERS" text before it
    prev_text = table.find_previous(string=re.compile(r'GOALKEEPERS', re.I))
    if prev_text:
        print("Found goalkeeper table")

        rows = table.find_all('tr')
        for row in rows[1:]:  # Skip header
            cells = row.find_all('td')
            if len(cells) >= 3:
                jersey = cells[0].get_text(strip=True)
                player_name = cells[1].get_text(strip=True)

                # Extract saves from TOTAL column (format: "10/20")
                saves_text = cells[2].get_text(strip=True) if len(cells) > 2 else "0/0"
                if '/' in saves_text:
                    saves = int(saves_text.split('/')[0])
                else:
                    saves = 0

                # Find and update existing goalkeeper player
                for player in players:
                    if player['player'] == player_name:
                        player['saves'] = saves
                        player['position'] = 'goalkeeper'
                        print(f"  Updated goalkeeper: {player_name} - {saves} saves")
                        break

# Create DataFrame
df = pd.DataFrame(players)

if not df.empty:
    print(f"\n✓ Successfully extracted {len(df)} players")
    print("\nSample of data:")
    print(df[['jersey', 'player', 'team_code', 'goals', 'assists', 'steals', 'saves']].head(10))

    # Save to CSV
    df.to_csv('simple_scraped_data.csv', index=False)
    print("\nSaved to 'simple_scraped_data.csv'")

    # Compare with expected data
    print("\n=== Comparison with Hardcoded Data ===")
    expected_top = ['CUK Milos', 'PERKOVIC Miroslav', 'MARTINOVIC Vasilije', 'BUTIC Zvonimir',
                    'BEREHULAK Marcus Julian']
    for player_name in expected_top:
        if player_name in df['player'].values:
            player_row = df[df['player'] == player_name].iloc[0]
            print(f"✓ {player_name}: {player_row['goals']}G {player_row['assists']}A {player_row['steals']}ST")
        else:
            print(f"✗ {player_name}: Not found")
else:
    print("No players extracted - check the saved HTML file")

print("\nDone!")