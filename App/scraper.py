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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
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
            response = self.session.get(match_url)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract match metadata from URL
            params = self._parse_match_url_params(match_url)
            match_date = self._parse_date_from_params(params.get('sch', ''))

            # Get team names from page
            team_names = self._extract_team_names(soup)
            home_team_full = team_names.get('home', params.get('s1', ''))
            away_team_full = team_names.get('away', params.get('s2', ''))
            home_code = params.get('s1', '')
            away_code = params.get('s2', '')

            # Find player statistics tables
            player_tables = soup.find_all('table', class_=re.compile(r'player-stats|stats-table', re.I))

            all_players = []

            # Process each table (typically 2 tables: one per team)
            for table in player_tables:
                # Determine which team this table belongs to
                team_full, team_code = self._identify_team_from_table(table, home_team_full, away_team_full, home_code,
                                                                      away_code)

                # Parse field players
                players = self._parse_field_players(table, team_code, team_full)
                all_players.extend(players)

                # Look for goalkeeper data (often in separate table or section)
                # This will be enhanced based on actual page structure

            # Try to find goalkeeper-specific tables
            gk_tables = soup.find_all('table', class_=re.compile(r'goalkeeper|gk', re.I))
            for gk_table in gk_tables:
                team_full, team_code = self._identify_team_from_table(gk_table, home_team_full, away_team_full,
                                                                      home_code, away_code)
                goalkeepers = self._parse_goalkeepers(gk_table, team_code, team_full)
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

            return df

        except Exception as e:
            print(f"Error parsing match page {match_url}: {e}")
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
        # Placeholder implementation
        team_names = {'home': '', 'away': ''}

        # Look for team name elements
        team_elements = soup.find_all(['h2', 'h3', 'div'], class_=re.compile(r'team-name|team-title', re.I))

        if len(team_elements) >= 2:
            team_names['home'] = team_elements[0].get_text(strip=True)
            team_names['away'] = team_elements[1].get_text(strip=True)

        return team_names

    def _identify_team_from_table(self, table, home_team_full, away_team_full, home_code, away_code):
        """Identify which team a table belongs to"""
        # Try to find team identifier in table or surrounding elements
        table_html = str(table)

        # Check for team codes in table
        if home_code and home_code in table_html:
            return home_team_full, home_code
        elif away_code and away_code in table_html:
            return away_team_full, away_code

        # Fallback to checking team names
        if home_team_full and home_team_full.split()[-1] in table_html:
            return home_team_full, home_code
        elif away_team_full and away_team_full.split()[-1] in table_html:
            return away_team_full, away_code

        # Default to home team if uncertain
        return home_team_full, home_code

    def _parse_field_players(self, table, team_code, team_full):
        """Parse field player statistics from a table row"""
        players = []

        # Find all rows (skip header if present)
        rows = table.find_all('tr')[1:]  # Skip header row

        for row in rows:
            cells = row.find_all('td')

            if len(cells) < 10:  # Need enough cells for stats
                continue

            try:
                # Extract jersey number (first cell)
                jersey = cells[0].get_text(strip=True)

                # Extract player name (second cell)
                player_name = cells[1].get_text(strip=True)

                # Extract stats based on column positions from your analysis
                # "TOTAL" column (goals/attempts) - format: "3/6"
                total_text = cells[3].get_text(strip=True)  # Adjust index based on actual table
                goals = self._extract_goals_from_total(total_text)

                # "AS" = Assists (adjust index based on actual table)
                assists = self._parse_integer(cells[6].get_text(strip=True))

                # "ST" = Steals (adjust index)
                steals = self._parse_integer(cells[13].get_text(strip=True))

                # "BL" = Blocked shots (adjust index)
                blocks = self._parse_integer(cells[14].get_text(strip=True))

                player_data = {
                    'jersey': jersey,
                    'player': player_name,
                    'team_code': team_code,
                    'team_full': team_full,
                    'goals': goals,
                    'assists': assists,
                    'steals': steals,
                    'blocks': blocks,
                    'saves': 0,  # Field players have 0 saves
                    'position': 'field'
                }

                players.append(player_data)

            except (IndexError, ValueError) as e:
                # Skip rows that don't match expected format
                continue

        return players

    def _parse_goalkeepers(self, table, team_code, team_full):
        """Parse goalkeeper statistics"""
        goalkeepers = []

        rows = table.find_all('tr')[1:]  # Skip header

        for row in rows:
            cells = row.find_all('td')

            if len(cells) < 5:
                continue

            try:
                jersey = cells[0].get_text(strip=True)
                player_name = cells[1].get_text(strip=True)

                # Extract saves - need to identify correct column
                # Look for saves data in cells
                saves = 0
                for i, cell in enumerate(cells):
                    cell_text = cell.get_text(strip=True).lower()
                    if 'saves' in cell_text or 'sv' in cell_text:
                        # Try to parse saves from this or next cell
                        saves = self._parse_integer(cell_text)
                        if saves == 0 and i + 1 < len(cells):
                            saves = self._parse_integer(cells[i + 1].get_text(strip=True))

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

            except (IndexError, ValueError):
                continue

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
        print("\nFirst 5 players:")
        print(df.head())

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
        print("No data scraped - may need to adjust selectors based on actual HTML")

    return df


if __name__ == "__main__":
    test_scraper()