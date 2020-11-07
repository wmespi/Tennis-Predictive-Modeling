import pandas as pd
from match_simulator import tennisPlayer, simulate_match
import math
import numpy as np
np.random.seed(5)

class tournament:

    def __init__(self, name, year,data):
        self.name = name
        self.year = year
        self.matches = self.get_matches(data)
        self.num_players = self.get_num_players(self.matches)
        self.empty_bracket,self.rounds = self.make_bracket(self.num_players,self.matches)
        self.results = self.get_results(self.matches,self.empty_bracket,self.rounds)
        self.players = self.get_players(self.matches)
        self.surface = self.matches['surface'].iloc[0]

    def get_matches(self, data):
        matches = data.copy()
        matches['year'] = matches['tourney_date'].astype(str).str[0:4]
        matches = matches[(matches['tourney_name'] == self.name) & (matches['year'] == str(self.year))]
        rounds =  list(matches['round'].unique())
        num_rounds = len(rounds)
        num_matches_per_round = [2**(i) for i in range(num_rounds)]
        num_matches_per_round = num_matches_per_round[::-1]

        ## check for enough matches
        for i,round in enumerate(rounds):
            test = len(matches[matches['round'] == round])
            check = num_matches_per_round[i]
            assert test == check, (round, 'from data source has an encoding error')
        return matches

    def get_num_players(self,matches):
        num_players = int(matches['draw_size'].max())
        return num_players

    def make_bracket(self,num_players,matches):
        bracket = {}
        rounds = list(matches['round'].unique())
        rounds.append('W')
        matches_p_round = int(num_players/2)

        for i in range(len(rounds)):
            round = rounds[i]
            bracket[round] = [[] for i in range(matches_p_round)]
            matches_p_round = int(matches_p_round/2)

        return bracket, rounds

    def get_results(self,matches,bracket,rounds):
        results = bracket.copy()

        for i, round in enumerate(rounds):
            round_matches = matches[matches['round'] == round]
            players = list(zip(round_matches.winner_name,round_matches.loser_name))
            results[round] = players

            if round == 'W':
                results[round] = results[rounds[i-1]][0][0]

        return results

    def get_players(self,matches):
        unique_winners = list(matches['winner_name'].unique())
        unique_losers = list(matches['loser_name'].unique())
        players = unique_winners + unique_losers
        players = list(set(players))
        return players


    # def get_first_round(self,matches):
    #     round_string = 'R'+str(self.num_players)
    #     first_round = matches[(matches['tourney_name'] == self.name) & (matches['round'] == round_string) & (matches['year'] == str(self.year))]
    #     return first_round

def simulate_tournament(tournament_name,year,file_path,iteration):
    ## need to make this data preprocessing and reading step outside of the main loop
    data = pd.read_csv(file_path)

    ## add serving stats
    data['w_2ndsvpt'] = data['w_svpt'] - data['w_1stIn']
    data['w_2ndIn'] = data['w_2ndsvpt'] - data['w_df']
    data['l_2ndsvpt'] = data['l_svpt'] - data['l_1stIn']
    data['l_2ndIn'] = data['l_2ndsvpt'] - data['l_df']

    ## need to calculate returning stats

    tourn = tournament(tournament_name,year,data)
    first_to = math.ceil(tourn.matches['best_of'].iloc[0]/2)
    surface = tourn.surface
    rounds = tourn.rounds

    ## limit data for calculating metrics to be before the current tournament
    tourn_index = list(tourn.matches.index.values.tolist())[0]
    history = data.copy()
    history = history.dropna()
    history = history.reset_index(drop=True)
    history = history[(history['surface'] == surface) & (history['tourney_name'] == tournament_name)]
    history = history.iloc[0:tourn_index]

    ## create simulated bracket
    sim_bracket = tourn.empty_bracket
    sim_bracket[tourn.rounds[0]] = tourn.results[tourn.rounds[0]]

    ## get metrics for every player
    competitors = pd.DataFrame([name for name in tourn.players],columns = ['Player'])
    competitors['total_1stIn'] = None
    competitors['total_1stWon'] = None
    competitors['total_2ndIn'] = None
    competitors['total_2ndWon'] = None
    competitors['total_1stRIn'] = None
    competitors['total_1stRWon'] = None
    competitors['total_2ndRIn'] = None
    competitors['total_2ndRWon'] = None
    for i, player in enumerate(tourn.players):
        # serving
        competitors['total_1stIn'].iloc[i] = history[history['winner_name'] == player].w_1stIn.sum() + history[history['loser_name'] == player].l_1stIn.sum()
        competitors['total_1stWon'].iloc[i] = history[history['winner_name'] == player].w_1stWon.sum() + history[history['loser_name'] == player].l_1stWon.sum()
        competitors['total_2ndIn'].iloc[i] = history[history['winner_name'] == player].w_2ndIn.sum() + history[history['loser_name'] == player].l_2ndIn.sum()
        competitors['total_2ndWon'].iloc[i] = history[history['winner_name'] == player].w_2ndWon.sum() + history[history['loser_name'] == player].l_2ndWon.sum()

        # returning
        competitors['total_1stRIn'].iloc[i] = history[history['winner_name'] == player].l_1stIn.sum() + history[history['loser_name'] == player].w_1stIn.sum()
        competitors['total_1stRWon'].iloc[i] = history[history['winner_name'] == player].l_1stIn.sum() - history[history['winner_name'] == player].l_1stWon.sum() + history[history['loser_name'] == player].w_1stIn.sum() - history[history['loser_name'] == player].w_1stWon.sum()
        competitors['total_2ndRIn'].iloc[i] = history[history['winner_name'] == player].l_2ndIn.sum() + history[history['loser_name'] == player].w_2ndIn.sum()
        competitors['total_2ndRWon'].iloc[i] = history[history['winner_name'] == player].l_2ndIn.sum() - history[history['winner_name'] == player].l_2ndWon.sum() + history[history['loser_name'] == player].w_2ndIn.sum() - history[history['loser_name'] == player].w_2ndWon.sum()

    afswp = competitors['total_1stWon'].sum() / competitors['total_1stIn'].sum()
    asswp = competitors['total_2ndWon'].sum() / competitors['total_2ndIn'].sum()
    afsrwp = competitors['total_1stRWon'].sum() / competitors['total_1stRIn'].sum()
    assrwp = competitors['total_2ndRWon'].sum() / competitors['total_2ndRIn'].sum()

    ## create player objects for everyone in the tournament
    players = {}
    pwins = {}
    plosses = {}
    for name in tourn.players:
        fsp, fswp, ssp, sswp, fsrwp, ssrwp = get_metrics(name,history)
        players[name] = tennisPlayer(name,fsp, fswp, ssp, sswp, fsrwp, ssrwp, afswp, asswp, afsrwp, assrwp)
        ## basic demographic characteristics)
        pwins[name] = 0
        plosses[name] = 0

    players_per_round = []
    for round_name in rounds:
        num_players = len(tourn.matches[tourn.matches['round'] == round_name])*2
        players_per_round.append(num_players)

    ## initiate first round match simulation
    print(tourn.name,'Iteration:',iteration)
    for i,round_name in enumerate(rounds):
        if round_name == rounds[0]:
            round = tourn.results[round_name]
            winners, losers = simulate_round(round,round_name, players, first_to)
            sim_bracket = update_bracket(winners, tourn.results,rounds,i)
        elif round_name == rounds[len(tourn.rounds)-1]:
            t_winner = winners[0]
            sim_bracket[round_name] = t_winner
            # print('Tournament Final:',sim_bracket[rounds[i-1]])
            # print('Tournament Winner:',sim_bracket[round_name])
            break
        else:
            round = sim_bracket[round_name]
            winners, losers = simulate_round(round,round_name, players, first_to)
            assert len(winners) == len(losers), 'Unequal number of winners and losers'
            assert len(winners) == int(players_per_round[i]/2), 'The number of winners is not equal to what it should be for this round'
            sim_bracket = update_bracket(winners, sim_bracket,rounds,i)

        for winner in winners:
            pwins[winner] += 1
        for loser in losers:
            plosses[loser] += 1

    return sim_bracket,players,t_winner,pwins,plosses


def update_bracket(winners,bracket,rounds,i):
    num_winners = len(winners)
    num_matches = int(num_winners/2)
    next_round = rounds[i+1]

    for match in range(num_matches):
        bracket[next_round][match] = (winners[2*match], winners[2*match+1])
        print(bracket[next_round][match])

    return bracket


def simulate_round(round,round_name,players,first_to):
    winners = []
    losers = []
    for match in round:
        player1 = players[match[0]]
        player2 = players[match[1]]
        if player1 == player2:
            print(round)
            print(round_name)
        match_winner,match_loser = simulate_match(player1,player2,first_to)
        winners.append(match_winner)
        losers.append(match_loser)
    #     if match_winner == player1.name:
    #         count.append(1)
    #     else:
    #         count.append(0)
    # print(sum(count)/len(count))

    winners = list(set(winners))
    losers = list(set(losers))

    return winners,losers


def get_metrics(player,history):

    ## get matches player won
    player_history_w = history[(history['winner_name'] == player)]

    ## get serving metrics for matches won
    w_svpt = player_history_w['w_svpt'].sum()
    w_1stIn = player_history_w['w_1stIn'].sum()
    w_1stWon = player_history_w['w_1stWon'].sum()
    w_2ndsvpt = player_history_w['w_2ndsvpt'].sum()
    w_2ndIn = player_history_w['w_2ndIn'].sum()
    w_2ndWon = player_history_w['w_2ndWon'].sum()

    ## get returning metrics for matches won
    l_R1stIn = player_history_w['l_1stIn'].sum()
    l_R1stWon = player_history_w['l_1stWon'].sum()
    l_R2ndIn = player_history_w['l_2ndIn'].sum()
    l_R2ndWon = player_history_w['l_2ndWon'].sum()

    ## get matches lost
    player_history_l = history[(history['loser_name'] == player)]

    ## get serving metrics for matches player lost
    l_svpt = player_history_l['l_svpt'].sum()
    l_1stIn = player_history_l['l_1stIn'].sum()
    l_1stWon = player_history_l['l_1stWon'].sum()
    l_2ndsvpt = player_history_l['l_2ndsvpt'].sum()
    l_2ndIn = player_history_l['l_2ndIn'].sum()
    l_2ndWon = player_history_l['l_2ndWon'].sum()

    ## get returning metrics for matches player lost
    w_R1stIn = player_history_l['w_1stIn'].sum()
    w_R1stWon = player_history_l['w_1stWon'].sum()
    w_R2ndIn = player_history_l['w_2ndIn'].sum()
    w_R2ndWon = player_history_l['w_2ndWon'].sum()

    ## combined serving metrics
    total_svpt = w_svpt + l_svpt
    total_1stIn = w_1stIn + l_1stIn
    total_1stWon = w_1stWon + l_1stWon
    total_2ndsvpt = w_2ndsvpt + l_2ndsvpt
    total_2ndIn = w_2ndIn + l_2ndIn
    total_2ndWon = w_2ndWon + l_2ndWon

    ## combined returning metrics
    total_R1stIn = w_R1stIn + l_R1stIn
    total_R1stWon = w_R1stWon + l_R1stWon
    total_R2ndIn = w_R2ndIn + l_R2ndIn
    total_R2ndWon = w_R2ndWon + l_R2ndWon


    ## if there are no matches for a player
    ## establish baseline percentages
    if len(player_history_w) + len(player_history_l) == 0:
        print('new player alert')
        fsp = .6
        fswp = .7
        ssp = .9
        sswp = .5
    else:
        ## serve stats
        fsp = total_1stIn / total_svpt
        fswp = total_1stWon / total_1stIn
        ssp = total_2ndIn / total_2ndsvpt
        sswp = total_2ndWon / total_2ndIn

        ## return stats
        fsrwp = (total_R1stIn - total_R1stWon) / total_R1stIn
        ssrwp = (total_R2ndIn - total_R2ndWon) / total_R2ndIn

    return fsp, fswp, ssp, sswp, fsrwp, ssrwp


def main(tournament_name,year,file_path):
    p_titles = {}
    p_wins = {}
    n_runs = 100

    for i in range(0,n_runs):
        sim_bracket,players,t_winner,pwins,plosses = simulate_tournament(tournament_name,year,file_path,i)
        for player in players.keys():
            if i == 0:
                p_wins[player] = [pwins[player]]
                if player != t_winner:
                    p_titles[player] = [0]
                else:
                    p_titles[player] = [1]
            else:
                p_wins[player].append(pwins[player])
                if player != t_winner:
                    p_titles[player].append(0)
                else:
                    p_titles[player].append(1)
            if i == n_runs-1:
                p_wins[player] = np.mean(p_wins[player])
                p_titles[player] = np.mean(p_titles[player])
    print(tournament_name,year)
    print('Number of Tournament Simulations:', n_runs)
    print('Percentage of Titles Won:')
    for w in sorted(p_titles, key=p_titles.get, reverse=True):
        if p_titles[w] < .10:
            continue
        print(w, round(p_titles[w]*100,2))
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print('Average Number of Matches Won:')
    for w in sorted(p_wins, key=p_wins.get, reverse=True):
        if p_wins[w] < 3:
            continue
        print(w, p_wins[w])


tournament_name = 'Wimbledon'
year = 2016
file_path = '/Users/William/Documents/Tennis-Predictive-Modeling/Cleaned Data/New Match Data Cleaned.csv'
main(tournament_name,year,file_path)