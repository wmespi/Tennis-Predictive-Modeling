import numpy as np

## tennisPlayer object
## includes various demographic information
## includes player statistics
class tennisPlayer:

    def __init__(self,name,fsp,fswp,ssp,sswp):
        ## basic demographic characteristics
        self.name = name
        # self.rank = rank
        # self.elo = elo
        # self.top10 = top10
        ## match statistics
        self.fsp = fsp
        self.fswp = fswp
        self.ssp = ssp
        self.sswp = sswp

## simulate the outcome of a point
## server: tennisPlayer object
## returner: tennisPlayer object
def simulate_point(server,returner):
    p_fs = server.fsp
    U1F = np.random.uniform()
    p_ss = server.ssp
    U1S = np.random.uniform()

    ## probability of making the first serve
    if U1F <= p_fs:
        p_wfs = server.fswp
        U2F = np.random.uniform()

        ## probability of winning the point on the first serve
        if U2F <= p_wfs:
            winner = server.name
        else:
            winner = returner.name
    ## probability of making second serve
    elif U1S <= p_ss:
        p_wss = server.sswp
        U2S = np.random.uniform()

        ## probability of winning point on second serve
        if U2S <= p_wss:
            winner = server.name
        else:
            winner = returner.name
    ## probability of double faulting
    else:
        winner = returner.name

    return winner

## simulate the outcome of a game
## server: tennisPlayer object
## returner: tennisPlayer object
def simulate_game(server,returner):
    s_name = server.name
    r_name = returner.name
    points = {s_name: 0, r_name: 0}
    score = {s_name: 0, r_name: 0}
    score_dict = {0:0,1:15,2:30,3:40,4:60}

    while points[s_name] != 'W' and points[r_name] != 'W':

        ## simulate a point
        point_winner = simulate_point(server, returner)
        points[point_winner] += 1

        ## gives the server the game
        if points[s_name] >= 4 and (points[s_name] - points[r_name]) >= 2:
            game_winner = s_name
            points[s_name] = 'W'
            continue

        ## gives the returner the break
        if points[r_name] >= 4 and (points[r_name] - points[s_name]) >= 2:
            game_winner = r_name
            points[r_name] = 'W'
            continue

        ## ends the loop if someone has won the game
        if points[s_name] == 'W' or points[r_name] == 'W':
            continue

        ## translates the point score to tennis score
        if points[s_name] >= 3 and points[r_name] >= 3:
            check = points[s_name] - points[r_name]
            if check == 0:
                score[s_name] = 40
                score[r_name] = 40
            if check == 1:
                score[s_name] = 'Adv'
                score[r_name] = 40
            if check == -1:
                score[s_name] = 40
                score[r_name] = 'Adv'
        else:
            score[s_name] = score_dict[points[s_name]]
            score[r_name] = score_dict[points[r_name]]

    return game_winner

def simulate_tiebreak(player1,player2):
    p1 = player1.name
    p2 = player2.name

    server = player1
    returner = player2

    points = {p1: 0, p2:0}

    while True:
        point_winner = simulate_point(server,returner)
        points[point_winner] += 1
        points_diff = points[p1] - points[p2]

        if points[p1] >= 7 and points_diff >= 2:
            tb_winner = p1
            break
        if points[p2] >= 7 and points_diff <= -2:
            tb_winner = p2
            break

        if server == player1:
            server = player2
            returner = player1
        else:
            server = player1
            returner = player2

    return tb_winner


def simulate_normal_set(player1,player2,server,returner):

    p1 = player1.name
    p2 = player2.name
    games = {p1: 0, p2: 0}

    while True:
        if games[p1] == 6 and games[p2] == 6:
            game_winner = simulate_tiebreak(server,returner)
        else:
            game_winner = simulate_game(server, returner)
        games[game_winner] += 1
        game_diff = games[p1] - games[p2]

        if games[p1] + games[p2] <= 12:

            if games[p1] >= 6 and game_diff >= 2:
                break
            if games[p2] >= 6 and game_diff <= -2:
                break
        else:
            break

        if server == player1:
            server = player2
            returner = player1
        else:
            server = player1
            returner = player2


    if game_diff > 0:
        set_winner = p1
    if game_diff < 0:
        set_winner = p2

    set_score = (games[p1],games[p2])
    return set_winner, set_score,server,returner

def simulate_match(player1,player2,sets_to_win):
    p1 = player1.name
    p2 = player2.name

    sets = {p1: 0, p2: 0}
    set_scores = []

    ## coin toss to see who serves first
    coin = np.random.uniform()
    if coin <= .5:
        server = player1
        returner = player2
    else:
        server = player2
        returner = player1

    while True:

        set_winner,set_score,server,returner = simulate_normal_set(player1,player2,server,returner)
        sets[set_winner] += 1
        set_scores.append(set_score)

        if sets[p1] >= sets_to_win:
            match_winner = p1
            match_loser = p2
            break
        if sets[p2] >= sets_to_win:
            match_winner = p2
            match_loser = p1
            break

        if server == player1:
            server = player2
            returner = player1
        else:
            server = player1
            returner = player2

    #print(match_winner,'won the match')
    return match_winner, match_loser



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
#     player = tennisPlayer(name,fsp,fswp,ssp,sswp)
#     tennis_players.append(player)
#
# winners = []
# for i in range(1000):
#     winner = simulate_match(tennis_players[0],tennis_players[1],3)
#     if winner == tennis_players[0].name:
#         winNum = 0
#     if winner == tennis_players[1].name:
#         winNum = 1
#     winners.append(winNum)
#
# pred = np.mean(winners)
# if pred <= .5:
#     print(pred)
#     print(tennis_players[0].name,'won the match')
# else:
#     print(pred)
#     print(tennis_players[1].name, 'won the match')


