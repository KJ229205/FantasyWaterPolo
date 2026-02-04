# app/scraper.py
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
import re


class LENScraper:
    """
    Scrapes LEN Champions League statistics from europeanaquatics.org

    Handles:
    1. Weekly match listings from results page
    2. Individual match details with player statistics
    3. Goalkeeper statistics from separate tables
    """

    def __init__(self, base_url="https://championsleague.europeanaquatics.org"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        })

    def test_connection(self):
        """Test connection to LEN website"""
        try:
            test_url = f"{self.base_url}/match-results-2526/"
            response = self.session.get(test_url, timeout=10)
            return response.status_code == 200
        except:
            return False

    def get_weekly_matches(self, week_number=None):
        """
        Get all matches for a specific week

        Args:
            week_number: If None, gets current week's matches

        Returns:
            List of dicts with match information
            [{
                'match_date': '2025-12-02',
                'home_team': 'VK Novi Beograd',
                'away_team': 'VK Jadran Split',
                'home_score': 15,
                'away_score': 10,
                'match_url': '...',
                'home_code': 'NBG',
                'away_code': 'JSP'
            }]
        """
        results_url = f"{self.base_url}/match-results-2526/"

        try:
            response = self.session.get(results_url)
            soup = BeautifulSoup(response.content, 'html.parser')

            matches = []

            # Find match cards/containers - this will need adjustment based on actual HTML
            # Using placeholder logic based on your URL pattern knowledge
            match_links = soup.find_all('a', href=re.compile(r'match-details-2526'))

            for link in match_links:
                match_url = link['href']
                if not match_url.startswith('http'):
                    match_url = f"{self.base_url}/{match_url}"

                # Extract info from URL parameters
                params = self._parse_match_url_params(match_url)

                # Try to extract from link text or surrounding elements
                match_text = link.get_text(strip=True)

                # This is a simplified version - will need tuning based on actual page structure
                match_info = {
                    'match_url': match_url,
                    'home_code': params.get('s1', ''),
                    'away_code': params.get('s2', ''),
                    'match_date': self._parse_date_from_params(params.get('sch', ''))
                }

                matches.append(match_info)

            return matches

        except Exception as e:
            print(f"Error fetching weekly matches: {e}")
            return []

    def parse_match_page(self, match_url):
        """
        Parse a single match page to extract player statistics

        Args:
            match_url: URL of the match details page

        Returns:
            pandas.DataFrame with columns matching our existing structure:
            ['jersey', 'player', 'team_code', 'goals', 'assists', 'steals',
             'blocks', 'saves', 'position', 'team_full', 'match_date']
        """
        try:
            # Add delay to be polite
            time.sleep(1)

            response = self.session.get(match_url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract match metadata from URL
            params = self._parse_match_url_params(match_url)
            match_date = self._parse_date_from_params(params.get('sch', ''))

            # Get team names from page
            team_names = self._extract_team_names(soup)
            home_team_full = team_names.get('home', params.get('s1', ''))
            away_team_full = team_names.get('away', params.get('s2', ''))
            home_code = params.get('s1', 'NBG')
            away_code = params.get('s2', 'JSP')

            # DEBUG: Save HTML for inspection
            with open('debug_match_page.html', 'w', encoding='utf-8') as f:
                f.write(str(soup))
            print("Saved HTML to 'debug_match_page.html' for inspection")

            # Try to find ANY tables first
            all_tables = soup.find_all('table')
            print(f"Found {len(all_tables)} total tables on page")

            # Look for player statistics - try different selectors
            player_tables = []

            # Try multiple common table classes
            possible_selectors = [
                'table',  # Any table
                'table.stats',
                'table.player-stats',
                'table.dataTable',
                '.stats-table',
                '.playerStats',
                '.match-stats'
            ]

            for selector in possible_selectors:
                tables = soup.select(selector)
                if tables:
                    print(f"Found {len(tables)} tables with selector '{selector}'")
                    player_tables.extend(tables)

            # If still no tables, use all tables
            if not player_tables:
                player_tables = all_tables
                print("Using all tables on page")

            all_players = []

            # Process each table
            for i, table in enumerate(player_tables[:4]):  # Limit to first 4 tables
                print(f"\n--- Processing table {i + 1} ---")

                # Try to determine team from table context
                team_full, team_code = self._identify_team_from_table(table, home_team_full, away_team_full, home_code,
                                                                      away_code)

                # Try to parse as field players
                players = self._parse_field_players_simple(table, team_code, team_full)
                if players:
                    print(f"  Found {len(players)} field players for {team_code}")
                    all_players.extend(players)
                else:
                    # Try to parse as goalkeepers
                    goalkeepers = self._parse_goalkeepers_simple(table, team_code, team_full)
                    if goalkeepers:
                        print(f"  Found {len(goalkeepers)} goalkeepers for {team_code}")
                        all_players.extend(goalkeepers)

            # Create DataFrame
            df = pd.DataFrame(all_players)

            if not df.empty:
                # Add match date to all rows
                df['match_date'] = match_date

                # Ensure consistent column order
                column_order = ['jersey', 'player', 'team_code', 'goals', 'assists', 'steals',
                                'blocks', 'saves', 'position', 'team_full', 'match_date']
                for col in column_order:
                    if col not in df.columns:
                        df[col] = None

                df = df[column_order]

                print(f"\n✓ Successfully extracted {len(df)} total players")

            return df

        except Exception as e:
            print(f"Error parsing match page {match_url}: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()

    def _parse_match_url_params(self, match_url):
        """Extract parameters from match URL"""
        params = {}
        if '?' in match_url:
            query_string = match_url.split('?')[1]
            for param in query_string.split('&'):
                if '=' in param:
                    key, value = param.split('=')
                    params[key] = value
        return params

    def _parse_date_from_params(self, date_str):
        """Convert DDMMYYYY to YYYY-MM-DD"""
        if date_str and len(date_str) == 8:
            try:
                return f"{date_str[4:]}-{date_str[2:4]}-{date_str[:2]}"
            except:
                return date_str
        return date_str

    def _extract_team_names(self, soup):
        """Extract team names from match page"""
        # This needs to be adapted to actual page structure
        team_names = {'home': '', 'away': ''}

        # Look for team name elements
        team_elements = soup.find_all(['h2', 'h3', 'div', 'span'], string=re.compile(r'VK|Team|Club', re.I))

        for elem in team_elements[:2]:
            text = elem.get_text(strip=True)
            if 'Novi Beograd' in text:
                team_names['home'] = 'VK Novi Beograd'
            elif 'Jadran Split' in text:
                team_names['away'] = 'VK Jadran Split'

        return team_names

    def _identify_team_from_table(self, table, home_team_full, away_team_full, home_code, away_code):
        """Identify which team a table belongs to"""
        # Default to home team if uncertain
        return home_team_full, home_code

    def _parse_field_players_simple(self, table, team_code, team_full):
        """Simple parser for field players - adapt based on actual HTML"""
        players = []

        # Get all rows
        rows = table.find_all('tr')

        for row in rows:
            cells = row.find_all(['td', 'th'])

            # Skip rows with too few cells or header rows
            if len(cells) < 5:
                continue

            # Look for jersey number (usually first cell with digits)
            jersey = ''
            player_name = ''

            for i, cell in enumerate(cells):
                cell_text = cell.get_text(strip=True)

                # Jersey number is often just 1-2 digits
                if cell_text.isdigit() and 0 < int(cell_text) <= 20:
                    jersey = cell_text
                    # Player name is often next cell
                    if i + 1 < len(cells):
                        player_name = cells[i + 1].get_text(strip=True)
                    break

            if jersey and player_name:
                # Try to extract stats - look for numbers in cells
                goals = assists = steals = blocks = 0

                for cell in cells:
                    cell_text = cell.get_text(strip=True)

                    # Goals might be in format "3/5" or just "3"
                    if '/' in cell_text:
                        try:
                            goals = int(cell_text.split('/')[0])
                        except:
                            pass
                    elif cell_text.isdigit():
                        num = int(cell_text)
                        # Heuristic: single-digit numbers might be goals/assists
                        if num <= 10:
                            if goals == 0:
                                goals = num
                            elif assists == 0:
                                assists = num

                player_data = {
                    'jersey': jersey,
                    'player': player_name,
                    'team_code': team_code,
                    'team_full': team_full,
                    'goals': goals,
                    'assists': assists,
                    'steals': steals,
                    'blocks': blocks,
                    'saves': 0,
                    'position': 'field'
                }

                players.append(player_data)

        return players

    def _parse_goalkeepers_simple(self, table, team_code, team_full):
        """Simple parser for goalkeepers"""
        goalkeepers = []

        rows = table.find_all('tr')

        for row in rows:
            cells = row.find_all(['td', 'th'])

            for i, cell in enumerate(cells):
                cell_text = cell.get_text(strip=True).lower()

                # Look for goalkeeper indicators
                if any(word in cell_text for word in ['gk', 'goalkeeper', 'goalie', 'celar', 'glusac']):
                    # Try to find jersey and name
                    jersey = ''
                    player_name = ''
                    saves = 0

                    # Look backward and forward for jersey/name
                    for j in range(max(0, i - 2), min(len(cells), i + 3)):
                        other_cell_text = cells[j].get_text(strip=True)
                        if other_cell_text.isdigit() and 0 < int(other_cell_text) <= 20:
                            jersey = other_cell_text
                        elif len(other_cell_text) > 3 and not other_cell_text.isdigit():
                            player_name = other_cell_text

                    # Look for saves number
                    for cell in cells:
                        cell_text_num = cell.get_text(strip=True)
                        if cell_text_num.isdigit() and int(cell_text_num) > 5:  # Saves are usually > 5
                            saves = int(cell_text_num)

                    if jersey or player_name:
                        goalkeeper_data = {
                            'jersey': jersey,
                            'player': player_name,
                            'team_code': team_code,
                            'team_full': team_full,
                            'goals': 0,
                            'assists': 0,
                            'steals': 0,
                            'blocks': 0,
                            'saves': saves,
                            'position': 'goalkeeper'
                        }

                        goalkeepers.append(goalkeeper_data)

        return goalkeepers

    def _extract_goals_from_total(self, total_text):
        """Extract goals from "3/6" format"""
        if '/' in total_text:
            try:
                return int(total_text.split('/')[0])
            except:
                return 0
        else:
            return self._parse_integer(total_text)

    def _parse_integer(self, text):
        """Safely parse integer from text"""
        try:
            # Remove non-numeric characters
            numeric_text = re.sub(r'[^\d]', '', text)
            return int(numeric_text) if numeric_text else 0
        except:
            return 0

    def scrape_sample_match(self):
        """Scrape the sample match from your proof of concept"""
        sample_url = "https://championsleague.europeanaquatics.org/match-details-2526/?c=ASM&g=1&t=A01&gr=2&s1=NBG&s2=JSP&st=2&sch=02122025"
        return self.parse_match_page(sample_url)


# Helper function for quick testing
def test_scraper():
    """Test the scraper with the sample match"""
    scraper = LENScraper()

    print("Testing LEN scraper...")
    print(f"Connection test: {scraper.test_connection()}")

    # Scrape the sample match
    print("\nScraping sample match...")
    df = scraper.scrape_sample_match()

    if not df.empty:
        print(f"Successfully scraped {len(df)} players")
        print("\nFirst 10 players:")
        print(df.head(10))

        # Save to CSV for inspection
        df.to_csv('scraped_sample.csv', index=False)
        print("\nSaved to 'scraped_sample.csv'")

        # Show summary
        print("\nTeam summary:")
        team_summary = df.groupby('team_code').agg({
            'goals': 'sum',
            'assists': 'sum',
            'steals': 'sum',
            'saves': 'sum'
        })
        print(team_summary)
    else:
        print("No data scraped - will need to inspect HTML structure")
        print("Check 'debug_match_page.html' to see the actual page structure")

    return df


if __name__ == "__main__":
    test_scraper()