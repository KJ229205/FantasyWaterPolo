# App/data_manager.py - COMPLETE UPDATED VERSION WITH ALL STATS FROM WEBSITE
import pandas as pd


class MatchDataManager:
    """Manages match data from multiple games with ALL STATS"""

    def __init__(self):
        self.all_matches = {}
        self.load_default_matches()

    def load_default_matches(self):
        """Load all eight matches for Week 1 with complete stats"""

        # MATCH 1: Novi Beograd vs Jadran Split - COMPLETE STATS
        match1_players = [
            # NBG Players
            ['1', 'GLUSAC Milan', 'NBG', 0, 0, 0, 0, 10, 'goalkeeper', 'Novi Beograd'],
            ['2', 'PLJEVANCIC Luka', 'NBG', 0, 0, 0, 0, 0, 'field', 'Novi Beograd'],
            ['3', 'UROSEVIC Viktor', 'NBG', 0, 0, 0, 0, 0, 'field', 'Novi Beograd'],
            ['4', 'GLADOVIC Luka', 'NBG', 0, 0, 0, 0, 0, 'field', 'Novi Beograd'],
            ['5', 'CUK Milos (C)', 'NBG', 4, 0, 0, 0, 0, 'center', 'Novi Beograd'],
            ['6', 'JANKOVIC Filip', 'NBG', 0, 0, 0, 0, 0, 'field', 'Novi Beograd'],
            ['7', 'TRTOVIC Dusan', 'NBG', 2, 0, 0, 0, 0, 'field', 'Novi Beograd'],
            ['8', 'DIMITRIJEVIC Marko', 'NBG', 1, 0, 2, 0, 0, 'field', 'Novi Beograd'],
            ['9', 'PERKOVIC Miroslav', 'NBG', 4, 0, 0, 0, 0, 'field', 'Novi Beograd'],
            ['10', 'MARTINOVIC Vasilije', 'NBG', 3, 1, 1, 0, 0, 'field', 'Novi Beograd'],
            ['11', 'LUKIC Nikola', 'NBG', 1, 2, 2, 0, 0, 'field', 'Novi Beograd'],
            ['12', 'GRGUREVIC Goran', 'NBG', 0, 0, 0, 0, 0, 'field', 'Novi Beograd'],
            ['13', 'PAJKOVIC Petar', 'NBG', 0, 0, 0, 0, 0, 'goalkeeper', 'Novi Beograd'],
            ['14', 'MILOJEVIC Vuk', 'NBG', 0, 0, 3, 0, 0, 'field', 'Novi Beograd'],
            # JAD Players
            ['1', 'CELAR Martin', 'JAD', 0, 0, 0, 0, 5, 'goalkeeper', 'Jadran Split'],
            ['2', 'MATKOVIC Dusan', 'JAD', 0, 0, 0, 0, 0, 'field', 'Jadran Split'],
            ['3', 'MARINIC KRAGIC Jerko', 'JAD', 2, 0, 0, 0, 0, 'field', 'Jadran Split'],
            ['4', 'RADAN Toni', 'JAD', 0, 0, 0, 0, 0, 'field', 'Jadran Split'],
            ['5', 'BUTIC Zvonimir (C)', 'JAD', 2, 3, 1, 1, 0, 'center', 'Jadran Split'],
            ['6', 'PEJKOVIC Duje', 'JAD', 0, 0, 1, 0, 0, 'field', 'Jadran Split'],
            ['7', 'TOMASOVIC Marin', 'JAD', 0, 0, 0, 0, 0, 'field', 'Jadran Split'],
            ['8', 'ZOVIC Ivan Domagoj', 'JAD', 0, 0, 0, 0, 0, 'field', 'Jadran Split'],
            ['9', 'BEREHULAK Marcus Julian', 'JAD', 4, 0, 0, 0, 0, 'field', 'Jadran Split'],
            ['10', 'NEMET Toni Josef', 'JAD', 0, 0, 0, 0, 0, 'field', 'Jadran Split'],
            ['11', 'FATOVIC Loren', 'JAD', 1, 2, 2, 1, 0, 'field', 'Jadran Split'],
            ['12', 'DUZEVIC Antonio', 'JAD', 0, 0, 0, 0, 0, 'field', 'Jadran Split'],
            ['14', 'CURKOVIC Mislav', 'JAD', 1, 1, 1, 0, 0, 'field', 'Jadran Split'],
        ]

        # MATCH 2: FTC vs Brescia - COMPLETE STATS
        match2_players = [
            # FTC Players
            ['1', 'LEVAI Marton', 'FTC', 0, 0, 0, 0, 3, 'goalkeeper', 'FTC Telekom'],
            ['2', 'MANDIC Dusan', 'FTC', 0, 1, 1, 0, 0, 'field', 'FTC Telekom'],
            ['3', 'MANHERCZ Krisztian Peter', 'FTC', 3, 2, 1, 1, 0, 'field', 'FTC Telekom'],
            ['4', 'NAGY Akos', 'FTC', 0, 0, 0, 0, 0, 'field', 'FTC Telekom'],
            ['5', 'VAMOS Marton Gyorgy', 'FTC', 2, 0, 1, 1, 0, 'field', 'FTC Telekom'],
            ['6', 'DI SOMMA Edoardo', 'FTC', 2, 1, 1, 0, 0, 'field', 'FTC Telekom'],
            ['7', 'FEKETE Gergo Janos', 'FTC', 0, 0, 1, 1, 0, 'field', 'FTC Telekom'],
            ['8', 'ARGYROPOULOS KANAKAKIS Stylianos', 'FTC', 2, 0, 0, 1, 0, 'field', 'FTC Telekom'],
            ['9', 'VARGA Vince Daniel', 'FTC', 1, 0, 0, 0, 0, 'field', 'FTC Telekom'],
            ['10', 'VIGVARI Vendel Csaba', 'FTC', 0, 0, 1, 0, 0, 'field', 'FTC Telekom'],
            ['11', 'JANSIK Szilard', 'FTC', 1, 1, 1, 0, 0, 'field', 'FTC Telekom'],
            ['12', 'DE TORO DOMINGUEZ Miguel', 'FTC', 1, 0, 0, 0, 0, 'field', 'FTC Telekom'],
            ['13', 'VOGEL Soma (C)', 'FTC', 0, 0, 0, 0, 11, 'goalkeeper', 'FTC Telekom'],
            ['14', 'VISMEG Zsombor Vajk', 'FTC', 0, 0, 0, 0, 0, 'field', 'FTC Telekom'],
            # BRE Players
            ['1', 'BAGGI NECCHI Tommaso', 'BRE', 0, 0, 0, 0, 14, 'goalkeeper', 'Brescia'],
            ['2', 'DEL BASSO Mario', 'BRE', 2, 1, 1, 0, 0, 'field', 'Brescia'],
            ['4', 'LODI Filippo', 'BRE', 0, 0, 0, 0, 0, 'field', 'Brescia'],
            ['5', 'FERRERO Filippo', 'BRE', 0, 1, 2, 1, 0, 'field', 'Brescia'],
            ['6', 'POPADIC Vlado', 'BRE', 3, 0, 2, 0, 0, 'field', 'Brescia'],
            ['7', 'DOLCE Vincenzo', 'BRE', 2, 1, 1, 0, 0, 'field', 'Brescia'],
            ['8', 'GIANAZZA Tommaso', 'BRE', 1, 0, 4, 1, 0, 'field', 'Brescia'],
            ['9', 'ALESIANI Jacopo (C)', 'BRE', 1, 1, 2, 2, 0, 'center', 'Brescia'],
            ['10', 'VISKOVIC Ante', 'BRE', 2, 0, 2, 0, 0, 'field', 'Brescia'],
            ['11', 'CASANOVA Nicolo', 'BRE', 0, 0, 0, 0, 0, 'field', 'Brescia'],
            ['12', 'GIRI Mateo', 'BRE', 0, 0, 1, 0, 0, 'field', 'Brescia'],
            ['13', 'MASSENZA MILANI Francesco', 'BRE', 0, 0, 0, 0, 0, 'goalkeeper', 'Brescia'],
            ['14', 'BALZARINI Alessandro', 'BRE', 1, 1, 1, 0, 0, 'field', 'Brescia'],
        ]

        # MATCH 3: Primorac vs Oradea - COMPLETE STATS
        match3_players = [
            # PRI Players
            ['1', 'RISTICEVIC Dimitrije', 'PRI', 0, 0, 1, 0, 6, 'goalkeeper', 'Primorac'],
            ['2', 'BRGULJAN Drasko (C)', 'PRI', 1, 1, 2, 0, 0, 'center', 'Primorac'],
            ['3', 'CETKOVIC Savo', 'PRI', 3, 1, 0, 0, 0, 'field', 'Primorac'],
            ['4', 'INABA Yusuke', 'PRI', 0, 1, 3, 0, 0, 'field', 'Primorac'],
            ['5', 'MRSIC Marko', 'PRI', 4, 0, 1, 0, 0, 'field', 'Primorac'],
            ['6', 'MURISIC Luka', 'PRI', 1, 1, 1, 0, 0, 'field', 'Primorac'],
            ['7', 'VIDOVIC Stefan', 'PRI', 1, 2, 0, 0, 0, 'field', 'Primorac'],
            ['8', 'VUCKOVIC Balsa', 'PRI', 3, 2, 2, 0, 0, 'field', 'Primorac'],
            ['9', 'VICO Nemanja', 'PRI', 1, 0, 0, 0, 0, 'field', 'Primorac'],
            ['10', 'BRKIC Nikola', 'PRI', 0, 0, 0, 0, 0, 'field', 'Primorac'],
            ['11', 'CETKOVIC Petar', 'PRI', 0, 0, 0, 0, 0, 'field', 'Primorac'],
            ['12', 'STANOJEVIC Dordije', 'PRI', 1, 1, 2, 0, 0, 'field', 'Primorac'],
            ['13', 'PEJOVIC Marko', 'PRI', 0, 0, 0, 0, 0, 'goalkeeper', 'Primorac'],
            ['14', 'PEROV Tim', 'PRI', 0, 0, 0, 0, 0, 'field', 'Primorac'],
            # ORA Players
            ['1', 'DOBOZANOV Lazar', 'ORA', 0, 0, 1, 0, 10, 'goalkeeper', 'Oradea'],
            ['2', 'BELENYESI David', 'ORA', 0, 1, 1, 0, 0, 'field', 'Oradea'],
            ['3', 'NEGREAN Tiberiu (C)', 'ORA', 0, 0, 1, 2, 0, 'center', 'Oradea'],
            ['4', 'LUNCAN Darian', 'ORA', 0, 0, 0, 0, 0, 'field', 'Oradea'],
            ['5', 'OLTEAN Sebastian', 'ORA', 0, 0, 0, 0, 0, 'field', 'Oradea'],
            ['6', 'ILISIE Flavius Nichita', 'ORA', 1, 1, 0, 0, 0, 'field', 'Oradea'],
            ['7', 'GUSAROV Ivan', 'ORA', 0, 1, 0, 0, 0, 'field', 'Oradea'],
            ['8', 'GARDASEVIC Filip', 'ORA', 5, 1, 0, 2, 0, 'field', 'Oradea'],
            ['9', 'REMES Bogdan', 'ORA', 0, 0, 0, 0, 0, 'field', 'Oradea'],
            ['10', 'VANCSIK Levente', 'ORA', 2, 0, 1, 0, 0, 'field', 'Oradea'],
            ['11', 'CZENK Ferenc Istvan', 'ORA', 1, 1, 0, 0, 0, 'field', 'Oradea'],
            ['12', 'VELKIC Petar', 'ORA', 2, 0, 0, 0, 0, 'field', 'Oradea'],
            ['13', 'GAVRIS Raul Ionut', 'ORA', 0, 0, 0, 0, 0, 'goalkeeper', 'Oradea'],
            ['14', 'BINDEA Raul Alexandru', 'ORA', 0, 0, 1, 0, 0, 'field', 'Oradea'],
        ]

        # MATCH 4: Marseille vs Barceloneta - COMPLETE STATS (FIXED GOALKEEPER STATS)
        match4_players = [
            # MAR Players
            ['1', 'TESANOVIC Petar', 'MAR', 0, 0, 3, 4, 0, 'goalkeeper', 'Marseille'],  # FIXED: 3 steals, 4 blocks
            ['2', 'LARUMBE GONFAUS Marc', 'MAR', 1, 0, 0, 0, 0, 'field', 'Marseille'],
            ['3', 'ONDO METHOGO Leandre', 'MAR', 0, 0, 0, 0, 0, 'field', 'Marseille'],
            ['4', 'DE NARDI Andrea', 'MAR', 0, 0, 1, 0, 0, 'field', 'Marseille'],
            ['5', 'NAGY Adam', 'MAR', 0, 0, 3, 1, 0, 'field', 'Marseille'],
            ['6', 'VERNOUX Thomas', 'MAR', 2, 0, 1, 1, 0, 'field', 'Marseille'],
            ['7', 'DRASOVIC Radomir', 'MAR', 1, 0, 1, 0, 0, 'field', 'Marseille'],
            ['8', 'BOUET Alexandre', 'MAR', 4, 0, 1, 0, 0, 'field', 'Marseille'],
            ['9', 'MARION VERNOUX Romain', 'MAR', 1, 0, 0, 0, 0, 'field', 'Marseille'],
            ['10', 'SPAIC Vladan', 'MAR', 0, 0, 1, 0, 0, 'field', 'Marseille'],
            ['11', 'VANPEPERSTRAETE Pierre-Frederic', 'MAR', 0, 0, 1, 0, 0, 'field', 'Marseille'],
            ['12', 'KALOGEROPOULOS Efstathios', 'MAR', 2, 0, 0, 0, 0, 'field', 'Marseille'],
            ['13', 'MCKNIGHT Brody', 'MAR', 0, 0, 0, 0, 0, 'goalkeeper', 'Marseille'],
            ['14', 'GBADAMASSI Bilal', 'MAR', 0, 0, 1, 0, 0, 'field', 'Marseille'],
            # BAR Players
            ['1', 'AGUIRRE RUBIO Unai', 'BAR', 0, 0, 0, 0, 11, 'goalkeeper', 'Barceloneta'],  # FIXED: 11 saves
            ['2', 'MUNARRIZ EGANA Alberto', 'BAR', 0, 0, 0, 0, 0, 'field', 'Barceloneta'],
            ['3', 'VELOTTO Alessandro', 'BAR', 0, 0, 1, 0, 0, 'field', 'Barceloneta'],
            ['4', 'VALLS FERRER Marc', 'BAR', 1, 0, 0, 0, 0, 'field', 'Barceloneta'],
            ['5', 'SANAHUJA CARNE Bernat', 'BAR', 2, 0, 0, 0, 0, 'field', 'Barceloneta'],
            ['6', 'ECHENIQUE Gonzalo Oscar', 'BAR', 3, 0, 0, 0, 0, 'field', 'Barceloneta'],
            ['7', 'BUSTOS SANCHEZ Jose Javier', 'BAR', 0, 0, 2, 0, 0, 'field', 'Barceloneta'],
            ['8', 'BURIAN Gergely Zoltan', 'BAR', 1, 0, 1, 1, 0, 'field', 'Barceloneta'],
            ['9', 'TAHULL I COMPTE Roger', 'BAR', 0, 0, 2, 0, 0, 'field', 'Barceloneta'],
            ['10', 'VIGVARI Vince Pal', 'BAR', 3, 0, 1, 0, 0, 'field', 'Barceloneta'],
            ['11', 'BIEL LARA Unai', 'BAR', 2, 0, 0, 0, 0, 'field', 'Barceloneta'],
            ['12', 'BUSTOS SANCHEZ Alejandro', 'BAR', 0, 0, 1, 0, 0, 'field', 'Barceloneta'],
            ['13', 'DELMAS TORTORELLA Bruno', 'BAR', 0, 0, 0, 0, 0, 'goalkeeper', 'Barceloneta'],
            ['14', 'GOMILA FAIGES Biel', 'BAR', 0, 0, 2, 0, 0, 'field', 'Barceloneta'],
        ]

        # MATCH 5: Radnicki vs Mladost - COMPLETE STATS
        match5_players = [
            # RAD Players
            ['1', 'FILIPOVIC Radoslav', 'RAD', 0, 0, 0, 0, 6, 'goalkeeper', 'Radnicki'],
            ['2', 'RASOVIC Strahinja', 'RAD', 2, 1, 1, 2, 0, 'field', 'Radnicki'],
            ['3', 'DEDOVIC Nikola', 'RAD', 0, 0, 0, 0, 0, 'field', 'Radnicki'],
            ['4', 'RANDJELOVIC Sava', 'RAD', 0, 0, 0, 3, 0, 'field', 'Radnicki'],
            ['5', 'JAKSIC Petar', 'RAD', 0, 0, 1, 0, 0, 'field', 'Radnicki'],
            ['6', 'PIJETLOVIC Dusko', 'RAD', 1, 0, 1, 0, 0, 'field', 'Radnicki'],
            ['7', 'PRLAINOVIC Andrija', 'RAD', 5, 1, 0, 0, 0, 'field', 'Radnicki'],
            ['8', 'JAKSIC Nikola', 'RAD', 0, 0, 0, 0, 0, 'field', 'Radnicki'],
            ['9', 'MURISIC Nikola', 'RAD', 0, 0, 0, 0, 0, 'field', 'Radnicki'],
            ['10', 'VAPENSKI Boris', 'RAD', 2, 1, 0, 0, 0, 'field', 'Radnicki'],
            ['11', 'VLAHOPULOS Angelos', 'RAD', 4, 1, 1, 0, 0, 'field', 'Radnicki'],
            ['12', 'RASOVIC Viktor', 'RAD', 0, 0, 0, 0, 0, 'field', 'Radnicki'],
            ['13', 'TODOROVSKI Stefan', 'RAD', 0, 0, 0, 0, 0, 'goalkeeper', 'Radnicki'],
            ['14', 'DADVANI Valiko', 'RAD', 0, 0, 1, 0, 0, 'field', 'Radnicki'],
            # MLA Players
            ['1', 'MARCELIC Ivan', 'MLA', 0, 0, 0, 0, 5, 'goalkeeper', 'Mladost'],
            ['2', 'BASIC Andrija', 'MLA', 1, 1, 0, 0, 0, 'field', 'Mladost'],
            ['3', 'TONCINIC Viktor', 'MLA', 1, 0, 0, 0, 0, 'field', 'Mladost'],
            ['4', 'BULJUBASIC Ivan', 'MLA', 1, 1, 2, 1, 0, 'field', 'Mladost'],
            ['5', 'BABIC Karlo', 'MLA', 0, 0, 1, 1, 0, 'field', 'Mladost'],
            ['6', 'BILJAKA Matias', 'MLA', 1, 1, 1, 3, 0, 'field', 'Mladost'],
            ['7', 'BUKIC Luka', 'MLA', 1, 1, 1, 2, 0, 'field', 'Mladost'],
            ['8', 'LAZIC Franko', 'MLA', 2, 2, 0, 0, 0, 'field', 'Mladost'],
            ['9', 'NAGAEV Ivan', 'MLA', 1, 0, 0, 1, 0, 'field', 'Mladost'],
            ['10', 'VRLIC Josip', 'MLA', 0, 0, 0, 0, 0, 'field', 'Mladost'],
            ['11', 'VUKICEVIC Ante', 'MLA', 0, 0, 0, 2, 0, 'field', 'Mladost'],
            ['12', 'KHARKOV Konstantin', 'MLA', 2, 0, 1, 1, 0, 'field', 'Mladost'],
            ['13', 'CUBRANIC Mauro Ivan', 'MLA', 0, 0, 0, 0, 1, 'goalkeeper', 'Mladost'],
            ['14', 'LONCAR Luka', 'MLA', 1, 0, 1, 3, 0, 'field', 'Mladost'],
        ]

        # MATCH 6: Olympiacos vs Vasas - COMPLETE STATS
        match6_players = [
            # OLY Players
            ['1', 'TZORTZATOS Panagiotis', 'OLY', 0, 0, 0, 0, 3, 'goalkeeper', 'Olympiacos'],
            ['2', 'ANGYAL Daniel', 'OLY', 2, 1, 0, 0, 0, 'field', 'Olympiacos'],
            ['3', 'GKILLAS Nikolaos', 'OLY', 1, 0, 2, 0, 0, 'field', 'Olympiacos'],
            ['4', 'GENIDOUNIAS Konstantinos (C)', 'OLY', 2, 0, 1, 0, 0, 'center', 'Olympiacos'],
            ['5', 'FOUNTOULIS Ioannis', 'OLY', 1, 0, 2, 0, 0, 'field', 'Olympiacos'],
            ['6', 'GOUVIS Konstantinos', 'OLY', 0, 0, 1, 2, 0, 'field', 'Olympiacos'],
            ['7', 'ZALANKI Gergo', 'OLY', 3, 0, 1, 0, 0, 'field', 'Olympiacos'],
            ['8', 'DIMOU Dimitrios', 'OLY', 1, 0, 1, 0, 0, 'field', 'Olympiacos'],
            ['9', 'ALAFRAGKIS Ioannis', 'OLY', 0, 0, 1, 0, 0, 'field', 'Olympiacos'],
            ['10', 'KAKARIS Konstantinos', 'OLY', 4, 0, 2, 1, 0, 'field', 'Olympiacos'],
            ['11', 'NIKOLAIDIS Dimitrios', 'OLY', 3, 0, 1, 0, 0, 'field', 'Olympiacos'],
            ['12', 'PAPANASTASIOU Alexandros', 'OLY', 2, 1, 1, 1, 0, 'field', 'Olympiacos'],
            ['13', 'ZERDEVAS Emmanouil', 'OLY', 0, 0, 0, 0, 8, 'goalkeeper', 'Olympiacos'],
            ['14', 'POUROS Evangelos', 'OLY', 1, 0, 1, 2, 0, 'field', 'Olympiacos'],
            # VAS Players
            ['1', 'MIZSEI Marton Zoltan', 'VAS', 0, 0, 0, 0, 3, 'goalkeeper', 'Vasas'],
            ['2', 'LAKATOS Soma Benjamin', 'VAS', 0, 0, 1, 0, 0, 'field', 'Vasas'],
            ['3', 'CSORBA Tamas', 'VAS', 0, 0, 0, 0, 0, 'field', 'Vasas'],
            ['4', 'VARNAI Kristof', 'VAS', 0, 0, 1, 1, 0, 'field', 'Vasas'],
            ['5', 'GABOR Lorinc', 'VAS', 2, 0, 0, 0, 0, 'field', 'Vasas'],
            ['6', 'SELLEY-RAUSCHER Domonkos', 'VAS', 0, 0, 1, 0, 0, 'field', 'Vasas'],
            ['7', 'DALA Dome Mate', 'VAS', 1, 0, 0, 2, 0, 'field', 'Vasas'],
            ['8', 'DURDIC Bogdan', 'VAS', 2, 0, 1, 0, 0, 'field', 'Vasas'],
            ['9', 'FOSKOLOS Angelos', 'VAS', 1, 0, 1, 0, 0, 'field', 'Vasas'],
            ['10', 'BATORI Bence (C)', 'VAS', 1, 1, 0, 0, 0, 'center', 'Vasas'],
            ['11', 'GYARFAS Tamas Balazs', 'VAS', 0, 0, 1, 0, 0, 'field', 'Vasas'],
            ['12', 'SZALAI Peter Miklos', 'VAS', 1, 0, 1, 1, 0, 'field', 'Vasas'],
            ['13', 'COIMBRA SERRA FERNANDES Joao Pedro', 'VAS', 0, 0, 0, 0, 3, 'goalkeeper', 'Vasas'],
            ['14', 'RAGACS Benedek', 'VAS', 0, 0, 1, 0, 0, 'field', 'Vasas'],
        ]

        # MATCH 7: Jadran HN vs Pro Recco - COMPLETE STATS
        match7_players = [
            # JHN Players
            ['1', 'ANDRIC Lazar', 'JHN', 1, 1, 0, 0, 5, 'goalkeeper', 'Jadran HN'],
            ['2', 'KHOLOD Dmitrii', 'JHN', 1, 0, 1, 0, 0, 'field', 'Jadran HN'],
            ['3', 'STUPAR Danilo', 'JHN', 1, 0, 3, 2, 0, 'field', 'Jadran HN'],
            ['4', 'OBRADOVIC Dimitrije', 'JHN', 0, 0, 3, 0, 0, 'field', 'Jadran HN'],
            ['5', 'VUJOVIC Jovan', 'JHN', 2, 0, 1, 1, 0, 'field', 'Jadran HN'],
            ['6', 'VALERA CALATRAVA Francisco', 'JHN', 2, 0, 1, 1, 0, 'field', 'Jadran HN'],
            ['7', 'MERKULOV Daniil', 'JHN', 1, 1, 1, 1, 0, 'field', 'Jadran HN'],
            ['8', 'GOJKOVIC Strahinja', 'JHN', 1, 0, 0, 0, 0, 'field', 'Jadran HN'],
            ['9', 'LAZIC Dorde', 'JHN', 3, 1, 1, 0, 0, 'field', 'Jadran HN'],
            ['10', 'SLADOVIC Matija', 'JHN', 0, 0, 1, 0, 0, 'field', 'Jadran HN'],
            ['11', 'MATIJASEVIC Tadija', 'JHN', 0, 0, 3, 0, 0, 'field', 'Jadran HN'],
            ['12', 'RADOVIC Vasilije (C)', 'JHN', 0, 0, 2, 2, 0, 'center', 'Jadran HN'],
            ['13', 'RADOVIC Ilija', 'JHN', 0, 0, 0, 0, 4, 'goalkeeper', 'Jadran HN'],
            ['14', 'JANOVIC Srdan', 'JHN', 1, 1, 1, 0, 0, 'field', 'Jadran HN'],
            # REC Players
            ['1', 'NICOSIA Gianmarco', 'REC', 0, 0, 0, 0, 7, 'goalkeeper', 'Pro Recco'],
            ['2', 'DI FULVIO Francesco', 'REC', 1, 0, 1, 1, 0, 'field', 'Pro Recco'],
            ['3', 'GRANADOS ORTEGA Alvaro', 'REC', 1, 1, 1, 0, 0, 'field', 'Pro Recco'],
            ['4', 'CANNELLA Giacomo', 'REC', 4, 0, 2, 2, 0, 'field', 'Pro Recco'],
            ['5', 'PATCHALIEV Andrea', 'REC', 2, 1, 0, 1, 0, 'field', 'Pro Recco'],
            ['6', 'DURIK Lukas', 'REC', 2, 0, 1, 2, 0, 'field', 'Pro Recco'],
            ['7', 'PRESCIUTTI Nicholas', 'REC', 0, 0, 1, 0, 0, 'field', 'Pro Recco'],
            ['8', 'PAVILLARD Luke Anthony', 'REC', 0, 0, 1, 1, 0, 'field', 'Pro Recco'],
            ['9', 'IOCCHI GRATTA Matteo', 'REC', 3, 1, 1, 0, 0, 'field', 'Pro Recco'],
            ['10', 'BURIC Rino', 'REC', 1, 0, 0, 0, 0, 'field', 'Pro Recco'],
            ['11', 'CONDEMI Francesco', 'REC', 0, 0, 1, 0, 0, 'field', 'Pro Recco'],
            ['12', 'IRVING Maxwell Bruce', 'REC', 5, 4, 1, 1, 0, 'field', 'Pro Recco'],
            ['13', 'PERRONE Luca', 'REC', 0, 0, 0, 0, 2, 'goalkeeper', 'Pro Recco'],
            ['14', 'CASSIA Francesco', 'REC', 0, 0, 1, 0, 0, 'field', 'Pro Recco'],
        ]

        # MATCH 8: Sabadell vs Hannover - COMPLETE STATS
        match8_players = [
            # SAB Players
            ['1', 'LORRIO BEJAR Eduardo (C)', 'SAB', 0, 0, 1, 0, 7, 'goalkeeper', 'Sabadell'],
            ['2', 'FAMERA KOPENCOVA Martin', 'SAB', 2, 1, 4, 0, 0, 'field', 'Sabadell'],
            ['3', 'ASENSIO SURRIBAS Oscar', 'SAB', 1, 0, 1, 0, 0, 'field', 'Sabadell'],
            ['4', 'VALERA CALATRAVA Roberto', 'SAB', 0, 0, 0, 1, 0, 'field', 'Sabadell'],
            ['5', 'PANERAI Federico Neri', 'SAB', 0, 0, 1, 1, 0, 'field', 'Sabadell'],
            ['6', 'SOLER ROIZARENA Tomas', 'SAB', 0, 0, 0, 0, 0, 'field', 'Sabadell'],
            ['7', 'BARROSO MACARRO Alberto', 'SAB', 1, 0, 0, 0, 0, 'field', 'Sabadell'],
            ['8', 'CABANAS PEGADO Sergi', 'SAB', 2, 0, 3, 0, 0, 'field', 'Sabadell'],
            ['9', 'AVERKA Kanstantsin', 'SAB', 2, 1, 3, 1, 0, 'field', 'Sabadell'],
            ['10', 'PEREZ RODRIGUEZ Jan', 'SAB', 0, 0, 1, 1, 0, 'field', 'Sabadell'],
            ['11', 'SABOYA VERGARA REAL Rafael', 'SAB', 1, 0, 1, 2, 0, 'field', 'Sabadell'],
            ['12', 'LARSEN Jack Stewart', 'SAB', 0, 0, 2, 0, 0, 'field', 'Sabadell'],
            ['13', 'ROMEVA RIBA Noah', 'SAB', 0, 0, 0, 0, 0, 'goalkeeper', 'Sabadell'],
            ['14', 'CARRIO MANDOLINI Tiago', 'SAB', 0, 0, 1, 2, 0, 'field', 'Sabadell'],
            # HAN Players
            ['1', 'SPITTANK Max', 'HAN', 0, 0, 0, 0, 6, 'goalkeeper', 'Hannover'],
            ['2', 'MACAN Marko (C)', 'HAN', 0, 0, 3, 1, 0, 'center', 'Hannover'],
            ['3', 'SCHIPPER Niclas', 'HAN', 1, 0, 0, 0, 0, 'field', 'Hannover'],
            ['4', 'LANGIEWICZ Kacper Marek', 'HAN', 1, 0, 0, 1, 0, 'field', 'Hannover'],
            ['5', 'KUEPPERS Lukas', 'HAN', 1, 0, 1, 1, 0, 'field', 'Hannover'],
            ['6', 'STRELEZKIJ Denis', 'HAN', 1, 0, 1, 1, 0, 'field', 'Hannover'],
            ['7', 'LOZINA Luka', 'HAN', 0, 0, 2, 0, 0, 'field', 'Hannover'],
            ['8', 'JAESCHKE Luk', 'HAN', 0, 0, 0, 0, 0, 'field', 'Hannover'],
            ['9', 'BOZIC Zoran', 'HAN', 2, 1, 1, 0, 0, 'field', 'Hannover'],
            ['10', 'MILARDOVIC Nikola', 'HAN', 1, 0, 0, 0, 0, 'field', 'Hannover'],
            ['11', 'VAN DEN BURG Sam Henrike', 'HAN', 0, 0, 1, 3, 0, 'field', 'Hannover'],
            ['12', 'GANSEN Mark', 'HAN', 1, 0, 1, 1, 0, 'field', 'Hannover'],
            ['13', 'BENKE Felix', 'HAN', 0, 0, 0, 0, 0, 'goalkeeper', 'Hannover'],
            ['14', 'VUKICEVIC Lazar', 'HAN', 3, 1, 1, 2, 0, 'field', 'Hannover'],
        ]

        # Store ALL matches
        self.all_matches = {
            'nbg_jad': {
                'id': 'nbg_jad',
                'name': 'Novi Beograd vs Jadran',
                'date': '2025-12-02',
                'score': '15-10',
                'teams': ['Novi Beograd', 'Jadran Split'],
                'players': match1_players
            },
            'ftc_bre': {
                'id': 'ftc_bre',
                'name': 'FTC vs Brescia',
                'date': '2025-12-02',
                'score': '13-16',
                'teams': ['FTC Telekom', 'Brescia'],
                'players': match2_players
            },
            'pri_ora': {
                'id': 'pri_ora',
                'name': 'Primorac vs Oradea',
                'date': '2025-12-02',
                'score': '15-11',
                'teams': ['Primorac', 'Oradea'],
                'players': match3_players
            },
            'mar_bar': {
                'id': 'mar_bar',
                'name': 'Marseille vs Barceloneta',
                'date': '2025-12-02',
                'score': '11-12',
                'teams': ['Marseille', 'Barceloneta'],
                'players': match4_players
            },
            'rad_mla': {
                'id': 'rad_mla',
                'name': 'Radnicki vs Mladost',
                'date': '2025-12-02',
                'score': '14-11',
                'teams': ['Radnicki', 'Mladost'],
                'players': match5_players
            },
            'oly_vas': {
                'id': 'oly_vas',
                'name': 'Olympiacos vs Vasas',
                'date': '2025-12-02',
                'score': '20-8',
                'teams': ['Olympiacos', 'Vasas'],
                'players': match6_players
            },
            'jhn_rec': {
                'id': 'jhn_rec',
                'name': 'Jadran HN vs Pro Recco',
                'date': '2025-12-02',
                'score': '13-19',
                'teams': ['Jadran HN', 'Pro Recco'],
                'players': match7_players
            },
            'sab_han': {
                'id': 'sab_han',
                'name': 'Sabadell vs Hannover',
                'date': '2025-12-02',
                'score': '9-11',
                'teams': ['Sabadell', 'Hannover'],
                'players': match8_players
            }
        }

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

        return df

    def get_all_players_dataframe(self):
        """Get all players from all matches combined - SORTED GLOBALLY"""
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

        if all_dfs:
            combined_df = pd.concat(all_dfs, ignore_index=True)
            # Sort ALL players by fantasy points GLOBALLY
            combined_df = combined_df.sort_values(
                ['fantasy_points', 'goals', 'assists', 'steals', 'saves'],
                ascending=[False, False, False, False, False]
            ).reset_index(drop=True)
            return combined_df
        return pd.DataFrame()

    def get_player_pool(self):
        """Get combined player pool from all matches for team building"""
        return self.get_all_players_dataframe()

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