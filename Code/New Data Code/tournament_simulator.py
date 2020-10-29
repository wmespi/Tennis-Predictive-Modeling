import pandas as pd

class tournament:

    def __init__(self, name, year,file_path):
        self.name = name
        self.year = year

        self.matches = self.get_matches(file_path)
        self.num_players = self.get_num_players(self.matches)

        self.bracket = self.make_bracket(self.num_players)

    def get_matches(self, file_path):
        matches = pd.read_csv(file_path)
        matches['year'] = matches['tourney_date'].astype(str).str[0:4]
        matches = matches[(matches['tourney_name'] == self.name)  & (matches['year'] == str(self.year))]
        return matches

    def get_num_players(self,matches):
        num_players = int(matches['draw_size'].max())
        return num_players

    def make_bracket(self,num_players):
        bracket = {}
        round = 1
        matches_p_round = int(num_players/2)
        while matches_p_round >= 1:
            round_string = 'Round ' + str(round)
            bracket[round_string] = [() for i in range(matches_p_round)]
            matches_p_round = int(matches_p_round/2)
            round += 1
        bracket['Winner'] = ()

        return bracket


    def get_first_round(self,matches):
        round_string = 'R'+str(self.num_players)
        first_round = matches[(matches['tourney_name'] == self.name) & (matches['round'] == round_string) & (matches['year'] == str(self.year))]
        return first_round




file_path = '/Users/William/Documents/Tennis-Predictive-Modeling/New Match Data/atp_matches_1990.csv'
tourn = tournament('Australian Open',1990,file_path)


# players_info = [
#     {'name':'R. Federer','age':38,'fsp':.65,'fswp':.91,'ssp':1,'sswp':.6},
#     {'name': 'R. Nadal', 'age': 34, 'fsp': .72, 'fswp': .85, 'ssp': 1, 'sswp': .635}
#     ]
#
# tennis_players = []
# for i in players_info:
#     name = i['name']
#     age = i['age']
#     fsp = i['fsp']
#     fswp = i['fswp']
#     ssp = i['ssp']
#     sswp = i['sswp']
#
#     player = tennisPlayer(name,age,fsp,fswp,ssp,sswp)
#     tennis_players.append(player)
#
# winner = simulate_match(tennis_players[0],tennis_players[1],3)
# print(winner)