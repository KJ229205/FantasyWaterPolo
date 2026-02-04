# App/data_manager.py
import pandas as pd
import re


class MatchDataManager:
    """Manages match data from multiple games"""

    def __init__(self):
        self.all_matches = {}
        self.load_default_matches()
        print(f"DEBUG: Initialized with {len(self.all_matches)} matches")

    def load_default_matches(self):
        """Load the three matches we have data for"""
        # Match 1: NBG vs JSP (already in main.py)
        match1_players = [
            # NBG Players - EXACT from website (with (C) for centers)
            ['1', 'GLUSAC Milan', 'NBG', 0, 0, 0, 0, 10, 'goalkeeper', 'VK Novi Beograd'],
            ['2', 'PLJEVANCIC Luka', 'NBG', 0, 0, 0, 0, 0, 'field', 'VK Novi Beograd'],
            ['3', 'UROSEVIC Viktor', 'NBG', 0, 0, 0, 0, 0, 'field', 'VK Novi Beograd'],
            ['4', 'GLADOVIC Luka', 'NBG', 0, 0, 0, 0, 0, 'field', 'VK Novi Beograd'],
            ['5', 'CUK Milos (C)', 'NBG', 4, 0, 0, 0, 0, 'center', 'VK Novi Beograd'],
            ['6', 'JANKOVIC Filip', 'NBG', 0, 0, 0, 0, 0, 'field', 'VK Novi Beograd'],
            ['7', 'TRTOVIC Dusan', 'NBG', 2, 0, 0, 0, 0, 'field', 'VK Novi Beograd'],
            ['8', 'DIMITRIJEVIC Marko', 'NBG', 1, 0, 2, 0, 0, 'field', 'VK Novi Beograd'],
            ['9', 'PERKOVIC Miroslav', 'NBG', 4, 0, 0, 0, 0, 'field', 'VK Novi Beograd'],
            ['10', 'MARTINOVIC Vasilije', 'NBG', 3, 1, 1, 0, 0, 'field', 'VK Novi Beograd'],
            ['11', 'LUKIC Nikola', 'NBG', 1, 2, 2, 0, 0, 'field', 'VK Novi Beograd'],
            ['12', 'GRGUREVIC Goran', 'NBG', 0, 0, 0, 0, 0, 'field', 'VK Novi Beograd'],
            ['13', 'PAJKOVIC Petar', 'NBG', 0, 0, 0, 0, 0, 'goalkeeper', 'VK Novi Beograd'],
            ['14', 'MILOJEVIC Vuk', 'NBG', 0, 0, 3, 0, 0, 'field', 'VK Novi Beograd'],

            # JSP Players - EXACT from website (with (C) for centers)
            ['1', 'CELAR Martin', 'JSP', 0, 0, 0, 0, 5, 'goalkeeper', 'VK Jadran Split'],
            ['2', 'MATKOVIC Dusan', 'JSP', 0, 0, 0, 0, 0, 'field', 'VK Jadran Split'],
            ['3', 'MARINIC KRAGIC Jerko', 'JSP', 2, 0, 0, 0, 0, 'field', 'VK Jadran Split'],
            ['4', 'RADAN Toni', 'JSP', 0, 0, 0, 0, 0, 'field', 'VK Jadran Split'],
            ['5', 'BUTIC Zvonimir (C)', 'JSP', 2, 3, 1, 1, 0, 'center', 'VK Jadran Split'],
            ['6', 'PEJKOVIC Duje', 'JSP', 0, 0, 1, 0, 0, 'field', 'VK Jadran Split'],
            ['7', 'TOMASOVIC Marin', 'JSP', 0, 0, 0, 0, 0, 'field', 'VK Jadran Split'],
            ['8', 'ZOVIC Ivan Domagoj', 'JSP', 0, 0, 0, 0, 0, 'field', 'VK Jadran Split'],
            ['9', 'BEREHULAK Marcus Julian', 'JSP', 4, 0, 0, 0, 0, 'field', 'VK Jadran Split'],
            ['10', 'NEMET Toni Josef', 'JSP', 0, 0, 0, 0, 0, 'field', 'VK Jadran Split'],
            ['11', 'FATOVIC Loren', 'JSP', 1, 2, 2, 1, 0, 'field', 'VK Jadran Split'],
            ['12', 'DUZEVIC Antonio', 'JSP', 0, 0, 0, 0, 0, 'field', 'VK Jadran Split'],
            ['14', 'CURKOVIC Mislav', 'JSP', 1, 1, 1, 0, 0, 'field', 'VK Jadran Split'],
        ]

        # Match 2: FTC vs Brescia (from your HTML) - CORRECTED data structure
        match2_players = [
            # FTC Players
            ['1', 'LEVAI Marton', 'FTC', 0, 0, 0, 0, 3, 'goalkeeper', 'FTC Telekom Waterpolo'],
            ['2', 'MANDIC Dusan', 'FTC', 0, 0, 0, 0, 0, 'field', 'FTC Telekom Waterpolo'],
            ['3', 'MANHERCZ Krisztian Peter', 'FTC', 3, 0, 0, 0, 0, 'field', 'FTC Telekom Waterpolo'],
            ['4', 'NAGY Akos', 'FTC', 0, 0, 0, 0, 0, 'field', 'FTC Telekom Waterpolo'],
            ['5', 'VAMOS Marton Gyorgy', 'FTC', 2, 0, 0, 0, 0, 'field', 'FTC Telekom Waterpolo'],
            ['6', 'DI SOMMA Edoardo', 'FTC', 2, 0, 0, 0, 0, 'field', 'FTC Telekom Waterpolo'],
            ['7', 'FEKETE Gergo Janos', 'FTC', 0, 0, 0, 0, 0, 'field', 'FTC Telekom Waterpolo'],
            ['8', 'ARGYROPOULOS KANAKAKIS Stylianos', 'FTC', 2, 0, 0, 0, 0, 'field', 'FTC Telekom Waterpolo'],
            ['9', 'VARGA Vince Daniel', 'FTC', 1, 0, 0, 0, 0, 'field', 'FTC Telekom Waterpolo'],
            ['10', 'VIGVARI Vendel Csaba', 'FTC', 0, 0, 0, 0, 0, 'field', 'FTC Telekom Waterpolo'],
            ['11', 'JANSIK Szilard', 'FTC', 1, 0, 0, 0, 0, 'field', 'FTC Telekom Waterpolo'],
            ['12', 'DE TORO DOMINGUEZ Miguel', 'FTC', 1, 0, 0, 0, 0, 'field', 'FTC Telekom Waterpolo'],
            ['13', 'VOGEL Soma (C)', 'FTC', 0, 0, 0, 0, 11, 'goalkeeper', 'FTC Telekom Waterpolo'],
            ['14', 'VISMEG Zsombor Vajk', 'FTC', 0, 0, 0, 0, 0, 'field', 'FTC Telekom Waterpolo'],

            # Brescia Players
            ['1', 'BAGGI NECCHI Tommaso', 'BRE', 0, 0, 0, 0, 14, 'goalkeeper', 'AN Brescia'],
            ['2', 'DEL BASSO Mario', 'BRE', 2, 0, 0, 0, 0, 'field', 'AN Brescia'],
            ['4', 'LODI Filippo', 'BRE', 0, 0, 0, 0, 0, 'field', 'AN Brescia'],
            ['5', 'FERRERO Filippo', 'BRE', 0, 0, 0, 0, 0, 'field', 'AN Brescia'],
            ['6', 'POPADIC Vlado', 'BRE', 3, 0, 0, 0, 0, 'field', 'AN Brescia'],
            ['7', 'DOLCE Vincenzo', 'BRE', 2, 0, 0, 0, 0, 'field', 'AN Brescia'],
            ['8', 'GIANAZZA Tommaso', 'BRE', 1, 0, 0, 0, 0, 'field', 'AN Brescia'],
            ['9', 'ALESIANI Jacopo (C)', 'BRE', 1, 0, 0, 0, 0, 'center', 'AN Brescia'],
            ['10', 'VISKOVIC Ante', 'BRE', 2, 0, 0, 0, 0, 'field', 'AN Brescia'],
            ['11', 'CASANOVA Nicolo', 'BRE', 0, 0, 0, 0, 0, 'field', 'AN Brescia'],
            ['12', 'GIRI Mateo', 'BRE', 0, 0, 0, 0, 0, 'field', 'AN Brescia'],
            ['13', 'MASSENZA MILANI Francesco', 'BRE', 0, 0, 0, 0, 0, 'goalkeeper', 'AN Brescia'],
            ['14', 'BALZARINI Alessandro', 'BRE', 1, 0, 0, 0, 0, 'field', 'AN Brescia'],
        ]

        # Match 3: KOT vs ORA (from your HTML) - FIXED: Only center positions have (C)
        match3_players = [
            # KOT Players
            ['1', 'RISTICEVIC Dimitrije', 'KOT', 0, 0, 1, 0, 6, 'goalkeeper', 'VPK Primorac Kotor'],
            ['2', 'BRGULJAN Drasko (C)', 'KOT', 1, 1, 2, 0, 0, 'center', 'VPK Primorac Kotor'],
            ['3', 'CETKOVIC Savo', 'KOT', 3, 1, 0, 0, 0, 'field', 'VPK Primorac Kotor'],
            ['4', 'INABA Yusuke', 'KOT', 0, 1, 3, 0, 0, 'field', 'VPK Primorac Kotor'],
            ['5', 'MRSIC Marko', 'KOT', 4, 0, 1, 0, 0, 'field', 'VPK Primorac Kotor'],
            ['6', 'MURISIC Luka', 'KOT', 1, 1, 1, 0, 0, 'field', 'VPK Primorac Kotor'],
            ['7', 'VIDOVIC Stefan', 'KOT', 1, 2, 0, 0, 0, 'field', 'VPK Primorac Kotor'],
            ['8', 'VUCKOVIC Balsa', 'KOT', 3, 2, 2, 0, 0, 'field', 'VPK Primorac Kotor'],
            ['9', 'VICO Nemanja', 'KOT', 1, 0, 0, 0, 0, 'field', 'VPK Primorac Kotor'],
            ['10', 'BRKIC Nikola', 'KOT', 0, 0, 0, 0, 0, 'field', 'VPK Primorac Kotor'],
            ['11', 'CETKOVIC Petar', 'KOT', 0, 0, 0, 0, 0, 'field', 'VPK Primorac Kotor'],
            ['12', 'STANOJEVIC Dordije', 'KOT', 1, 1, 2, 0, 0, 'field', 'VPK Primorac Kotor'],
            ['13', 'PEJOVIC Marko', 'KOT', 0, 0, 0, 0, 0, 'goalkeeper', 'VPK Primorac Kotor'],
            ['14', 'PEROV Tim', 'KOT', 0, 0, 0, 0, 0, 'field', 'VPK Primorac Kotor'],

            # ORA Players - FIXED: Only one center position
            ['1', 'DOBOZANOV Lazar', 'ORA', 0, 0, 1, 0, 10, 'goalkeeper', 'CSM Oradea'],
            ['2', 'BELENYESI David', 'ORA', 0, 1, 1, 0, 0, 'field', 'CSM Oradea'],
            ['3', 'NEGREAN Tiberiu (C)', 'ORA', 0, 0, 1, 2, 0, 'center', 'CSM Oradea'],
            ['4', 'LUNCAN Darian', 'ORA', 0, 0, 0, 0, 0, 'field', 'CSM Oradea'],
            ['5', 'OLTEAN Sebastian', 'ORA', 0, 0, 0, 0, 0, 'field', 'CSM Oradea'],
            ['6', 'ILISIE Flavius Nichita', 'ORA', 1, 1, 0, 0, 0, 'field', 'CSM Oradea'],
            ['7', 'GUSAROV Ivan', 'ORA', 0, 1, 0, 0, 0, 'field', 'CSM Oradea'],
            ['8', 'GARDASEVIC Filip', 'ORA', 5, 1, 0, 2, 0, 'field', 'CSM Oradea'],
            ['9', 'REMES Bogdan', 'ORA', 0, 0, 0, 0, 0, 'field', 'CSM Oradea'],
            ['10', 'VANCSIK Levente', 'ORA', 2, 0, 1, 0, 0, 'field', 'CSM Oradea'],  # REMOVED (C) from position
            ['11', 'CZENK Ferenc Istvan', 'ORA', 1, 1, 0, 0, 0, 'field', 'CSM Oradea'],
            ['12', 'VELKIC Petar', 'ORA', 2, 0, 0, 0, 0, 'field', 'CSM Oradea'],
            ['13', 'GAVRIS Raul Ionut', 'ORA', 0, 0, 0, 0, 0, 'goalkeeper', 'CSM Oradea'],
            ['14', 'BINDEA Raul Alexandru', 'ORA', 0, 0, 1, 0, 0, 'field', 'CSM Oradea'],
        ]

        # Store all matches
        self.all_matches = {
            'nbg_jsp': {
                'id': 'nbg_jsp',
                'name': 'NBG vs JSP',
                'date': '2025-12-02',
                'score': '15-10',
                'teams': ['VK Novi Beograd', 'VK Jadran Split'],
                'players': match1_players
            },
            'ftc_bre': {
                'id': 'ftc_bre',
                'name': 'FTC vs Brescia',
                'date': '2025-12-02',
                'score': '13-16',
                'teams': ['FTC Telekom Waterpolo', 'AN Brescia'],
                'players': match2_players
            },
            'kot_ora': {
                'id': 'kot_ora',
                'name': 'KOT vs ORA',
                'date': '2025-12-02',
                'score': '15-11',
                'teams': ['VPK Primorac Kotor', 'CSM Oradea'],
                'players': match3_players
            }
        }

        print(f"DEBUG: Loaded matches - {list(self.all_matches.keys())}")
        print(f"DEBUG: KOT vs ORA has {len(match3_players)} players")

    def get_match_ids(self):
        """Return list of available match IDs"""
        return list(self.all_matches.keys())

    def get_match_info(self, match_id):
        """Get information about a specific match"""
        if match_id in self.all_matches:
            return self.all_matches[match_id]
        return None

    def get_match_dataframe(self, match_id):
        """Get match data as pandas DataFrame with fantasy points calculated"""
        if match_id not in self.all_matches:
            print(f"ERROR: Match ID '{match_id}' not found")
            return pd.DataFrame()

        match = self.all_matches[match_id]
        players = match['players']

        df = pd.DataFrame(players, columns=[
            'jersey', 'player', 'team_code', 'goals', 'assists', 'steals',
            'blocks', 'saves', 'position', 'team_full'
        ])

        # Calculate fantasy points
        df['fantasy_points'] = (
                df['goals'] * 5 +
                df['assists'] * 3 +
                df['steals'] * 2 +
                df['blocks'] * 2 +
                df['saves'] * 2
        )

        # Sort by points
        df = df.sort_values(['fantasy_points', 'goals', 'assists'], ascending=[False, False, False])

        print(f"DEBUG: Loaded match '{match_id}' with {len(df)} players")

        return df

    def get_all_players_dataframe(self):
        """Get all players from all matches combined - SORTED GLOBALLY"""
        print("DEBUG: Getting ALL players dataframe")
        all_dfs = []
        for match_id in self.get_match_ids():
            match = self.all_matches[match_id]
            players = match['players']

            # Create DataFrame for this match
            df = pd.DataFrame(players, columns=[
                'jersey', 'player', 'team_code', 'goals', 'assists', 'steals',
                'blocks', 'saves', 'position', 'team_full'
            ])

            # Calculate fantasy points
            df['fantasy_points'] = (
                    df['goals'] * 5 +
                    df['assists'] * 3 +
                    df['steals'] * 2 +
                    df['blocks'] * 2 +
                    df['saves'] * 2
            )

            df['match_id'] = match_id
            df['match_name'] = match['name']
            all_dfs.append(df)
            print(f"DEBUG: Added {len(df)} players from {match['name']}")

        if all_dfs:
            combined_df = pd.concat(all_dfs, ignore_index=True)
            # Sort ALL players by fantasy points GLOBALLY
            combined_df = combined_df.sort_values(
                ['fantasy_points', 'goals', 'assists', 'steals', 'saves'],
                ascending=[False, False, False, False, False]
            ).reset_index(drop=True)
            print(f"DEBUG: Combined total players: {len(combined_df)}")
            print(f"DEBUG: Matches in combined: {combined_df['match_name'].unique()}")
            return combined_df
        print("DEBUG: No dataframes to combine")
        return pd.DataFrame()

    def get_player_pool(self):
        """Get combined player pool from all matches for team building"""
        print("DEBUG: Getting player pool")
        df = self.get_all_players_dataframe()
        if not df.empty:
            print(f"DEBUG: Player pool has {len(df)} players")
            print(f"DEBUG: Matches in pool: {df['match_name'].unique()}")
        else:
            print("DEBUG: Player pool is empty!")
        return df

    def calculate_weekly_totals(self, selected_players):
        """
        Calculate total fantasy points for selected players across all matches
        selected_players: list of (player_name, team_code) tuples
        """
        all_players_df = self.get_all_players_dataframe()

        total_points = 0
        player_details = []

        for player_name, team_code in selected_players:
            player_data = all_players_df[
                (all_players_df['player'] == player_name) &
                (all_players_df['team_code'] == team_code)
                ]

            if not player_data.empty:
                player_row = player_data.iloc[0]
                total_points += player_row['fantasy_points']
                player_details.append({
                    'player': player_name,
                    'team': team_code,
                    'points': player_row['fantasy_points'],
                    'match': player_row['match_name']
                })

        return total_points, player_details


# Create a singleton instance
data_manager = MatchDataManager()