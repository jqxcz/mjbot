import pygsheets
# import numpy as np
import datetime




class GSheetClient:
    def __init__(self):
        self.gc = pygsheets.authorize(service_file='client_secret.json')
        self.riichi_leaderboards = {}

    def refresh(self, hk_doc, hk_sheet, hk_players, riichi_doc, riichi_sheet, riichi_players, **kwargs):
        # Open spreadsheet and then worksheet
        self.hk_doc = self.gc.open_by_key(hk_doc)
        self.hk_form = self.hk_doc.worksheets('id', hk_sheet)[0]
        self.hk_players = self.hk_doc.worksheets('id', hk_players)[0]


        self.riichi_doc = self.gc.open_by_key(riichi_doc)
        self.riichi_form = self.riichi_doc.worksheets('id', riichi_sheet)[0]
        self.riichi_players = self.riichi_doc.worksheets('id', riichi_players)[0]

        self.refresh_leaderboards()
    

    def add_player(self, player):
        self.hk_players.client.sheet.values_append(
            self.hk_players.spreadsheet.id, [[player]], 'ROWS', 
            range=self.hk_players._get_range('A1', 'A'),
            insertDataOption='INSERT_ROWS'
        )
        self.hk_players.refresh(False)
        self.riichi_players.client.sheet.values_append(
            self.riichi_players.spreadsheet.id, [[player]], 'ROWS', 
            range=self.riichi_players._get_range('A1', 'A'),
            insertDataOption='INSERT_ROWS'
        )
        self.riichi_players.refresh(False)

    def refresh_leaderboards(self):
        self.riichi_leaderboards = dict(self.riichi_players.get_values('A', 'B')[1:])
        self.hk_leaderboards = dict(self.hk_players.get_values('A', 'B')[1:])
        self.players = sorted(self.riichi_leaderboards.keys() | self.hk_leaderboards.keys())

    def add_riichi_game(self, data):
        row = [
            datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            data['p1'],
            data['p2'],
            data['p3'],
            data['p4'],
            data['s1'],
            data['s2'],
            data['s3'],
            data['s4'],
            'Yes' if data['early'] else 'No',
            data['round']
        ]
        self.riichi_form.client.sheet.values_append(
            self.riichi_form.spreadsheet.id, [row], 'ROWS', 
            range=self.riichi_form._get_range('A1', 'K'),
            insertDataOption='INSERT_ROWS'
        )
        self.riichi_form.refresh(False)
        # self.riichi_form.append_table(row, start='A5', end='J')

    def add_hk_round(self, data):
        if data['winner'] != data['loser']:
            remaining = [
                p for p in ['p1', 'p2', 'p3', 'p4'] 
                if p not in {data['winner'], data['loser']}
            ]
            players = [
                data[data['winner']], 
                data[data['loser']],
                *map(data.get, remaining)
            ]
        else:
            remaining = [
                p for p in ['p1', 'p2', 'p3', 'p4'] 
                if p not in {data['winner'], data['loser']}
            ]
            players = [
                data[data['winner']], 
                *map(data.get, remaining)
            ]
        row = [
            datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'Feed off Player (1)' 
                if data['winner'] != data['loser'] 
                else 'Self Draw (2)',
            *players,
            ', '.join(data['shape']),
            data.get('special', ''),
            ', '.join(data.get('additional', []))
        ]
        self.hk_form.client.sheet.values_append(
            self.hk_form.spreadsheet.id, [row], 'ROWS', 
            range=self.hk_form._get_range('A1', 'I'),
            insertDataOption='INSERT_ROWS'
        )
        self.hk_form.refresh(False)

gs = GSheetClient()


# add_riichi_game(
#     {
#     'p1': "player 1",
#     'p2': "player 2",
#     'p3': 'player 3',
#     'p4': 'player 4',
#     's1': "25000",
#     's2': "25000",
#     's3': '25000',
#     's4': '25000',
#     'early': False,
#     }
# )

# add_hk_round({
#     'p1': "player 1",
#     'p2': "player 2",
#     'p3': 'player 3',
#     'p4': 'player 4',
#     'winner': 'p3',
#     'loser': 'p4',
#     'shape': ['All Pong (+3)', 'Half Flush (+3)'],
#     'additional': "Pong of Player's Own Wind (+1), Pong of Round Wind (+1), No Flower/Season (+1), Self-Draw (+1)".split(', ')
# })
# add_hk_round({
#     'p1': "player 1",
#     'p2': "player 2",
#     'p3': 'player 3',
#     'p4': 'player 4',
#     'winner': 'p3',
#     'loser': 'p3',
#     'shape': ['Special Hand'],
#     'special': 'Thirteen Orphans (13)'
# })
