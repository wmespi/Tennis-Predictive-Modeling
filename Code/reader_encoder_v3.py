import pandas as pd
import os

def collect_files(folder):

    ## pull specific columns from dataset and initialize dataframe
    cols = ['Tournament', 'Day','Month', 'Year', 'Court', 'Winner',
            'Loser', 'Surface', 'Round', 'Best of', 'WRank',
            'LRank']
    data = pd.DataFrame(columns = cols)

    ## open each file in directory and extract annual match data
    for filename in sorted(os.listdir(folder)):

        ## restrict file type
        if filename.endswith('xls') or filename.endswith('xlsx'):

            file_path = os.path.join(folder, filename)
            year_data = pd.read_excel(file_path)

            ## insert year and month fields
            year_data['Day'] = pd.DatetimeIndex(year_data['Date']).day
            year_data['Month'] = pd.DatetimeIndex(year_data['Date']).month
            year_data['Year'] = pd.DatetimeIndex(year_data['Date']).year
            year_data = year_data[cols]

            ## drop any matches with unranked players and remove duplicate matches
            year_data = year_data.dropna(subset=['WRank','LRank','Winner','Loser'])
            year_data = year_data.drop_duplicates()

            ## add new rows to master data set
            data = pd.concat([data,year_data],join='inner',ignore_index=True)

    return data


def clean_data(data):

    ## ensure numerical types are correct for appropriate variables
    data = data[pd.to_numeric(data['LRank'], errors='coerce').notnull()]
    data = data[pd.to_numeric(data['WRank'], errors='coerce').notnull()]
    cols = ['Day', 'Month', 'Year', 'Best of', 'WRank', 'LRank']
    data[cols] = data[cols].astype(float)

    ## initialize player 1 (better ranking)
    data.loc[data['WRank'] > data['LRank'], 'Player 1'] = data.loc[data['WRank'] > data['LRank'], 'Loser']
    data.loc[data['WRank'] < data['LRank'], 'Player 1'] = data.loc[data['WRank'] < data['LRank'], 'Winner']

    ## initialize player 1 ranking
    data.loc[data['WRank'] > data['LRank'], 'Player 1 Rank'] = data.loc[data['WRank'] > data['LRank'], 'LRank']
    data.loc[data['WRank'] < data['LRank'], 'Player 1 Rank'] = data.loc[data['WRank'] < data['LRank'], 'WRank']

    ## initialize player 2 (worse ranking)
    data.loc[data['WRank'] < data['LRank'], 'Player 2'] = data.loc[data['WRank'] < data['LRank'], 'Loser']
    data.loc[data['WRank'] > data['LRank'], 'Player 2'] = data.loc[data['WRank'] > data['LRank'], 'Winner']

    ## initialize player 2 ranking
    data.loc[data['WRank'] < data['LRank'], 'Player 2 Rank'] = data.loc[data['WRank'] < data['LRank'], 'LRank']
    data.loc[data['WRank'] > data['LRank'], 'Player 2 Rank'] = data.loc[data['WRank'] > data['LRank'], 'WRank']

    ## dictionaries for storing a players matches
    all_time_matches = {}
    data['Player 1 All-Time Matches'] = None
    data['Player 2 All-Time Matches'] = None

    ## function for updating match dictionaries
    def get_matches(player,player_dict):
        ## set initial values
        if player not in all_time_matches:
            player_dict[player] = 0
        else:
            player_dict[player] += 1

        result = player_dict[player]

        return result

    ## dictionaries for storing a players wins
    all_time_wins = {}
    data['Player 1 All-Time Wins'] = None
    data['Player 2 All-Time Wins'] = None

    ## dictionaries for storing a players losses
    all_time_losses = {}
    data['Player 1 All-Time Losses'] = None
    data['Player 2 All-Time Losses'] = None

    ## function for updating players win/loss dicts
    def get_results(player, winner, loser, win_dict, loss_dict):
        ## set initial values
        if player not in win_dict:
            win_dict[player] = 0
        if player not in loss_dict:
            loss_dict[player] = 0

        wins = win_dict[player]
        losses = loss_dict[player]

        if player == winner:
            win_dict[player] += 1
        if player == loser:
            loss_dict[player] += 1

        return wins, losses

    ## dictionaries for storing a players YTD matches
    years_matches = {}
    data['Player 1 YTD Matches'] = None
    data['Player 2 YTD Matches'] = None

    ## function for updating YTD dictionaries
    def get_YTD_matches(player, year_dict, year):
        ## create initial year dictionary
        if year not in year_dict:
            year_dict[year] = {}
        ## update year dictionary
        if player not in year_dict[year]:
            year_dict[year][player] = 0
        else:
            year_dict[year][player] += 1

        matches = year_dict[year][player]

        return matches

    ## dictionaries for storing a players YTD wins
    years_wins = {}
    data['Player 1 YTD Wins'] = None
    data['Player 2 YTD Wins'] = None

    ## dictionaries for storing a players YTD losses
    years_losses = {}
    data['Player 1 YTD Losses'] = None
    data['Player 2 YTD Losses'] = None

    ## function for updating YTD win/loss dictionaries
    def get_YTD_results(player,year,winner,loser,y_win_dict,y_loss_dict):
        ## create initial year dictionary
        if year not in y_win_dict:
            y_win_dict[year] = {}
        if year not in y_loss_dict:
            y_loss_dict[year] = {}

        ## create initial year wins/losses dictionaries
        if player not in y_win_dict[year]:
            y_win_dict[year][player] = 0
        if player not in y_loss_dict[year]:
            y_loss_dict[year][player] = 0

        wins = y_win_dict[year][player]
        losses = y_loss_dict[year][player]

        ## update dictionaries
        if player == winner:
            y_win_dict[year][player] += 1
        if player == loser:
            y_loss_dict[year][player] += 1

        return wins,losses

    ## dictionaries for storing h2h wins
    h2h_wins = {}
    data['Player 1 All-Time H2H Wins'] = None
    data['Player 2 All-Time H2H Wins'] = None

    ## function for updating h2h dictionary
    def get_h2h(player1,player2,h2h_dict,winner):
        ## create dictionary key for matchup
        if type(player1) != str:
            print(player1)
        if type(player2) != str:
            print(player2)
        key = str(player1) + ' d. ' + str(player2)

        ## create initial dictionary entry
        if key not in h2h_dict:
            h2h_dict[key] = 0
        wins = h2h_dict[key]

        ## update dictionary value
        if player1 == winner:
            h2h_dict[key] += 1

        return wins

    ## dictionaries for storing YTD h2h wins
    year_h2h = {}
    data['Player 1 YTD H2H Wins'] = None
    data['Player 2 YTD H2H Wins'] = None

    ## function for updating YTD h2h status
    def get_YTD_h2h(player1,player2,year,year_h2h_dict,winner):
        if year not in year_h2h_dict:
            year_h2h_dict[year] = {}
        key = str(player1) + ' d. ' + str(player2)
        if key not in year_h2h_dict[year]:
            year_h2h_dict[year][key] = 0

        wins_YTD = year_h2h_dict[year][key]

        if player1 == winner:
            year_h2h_dict[year][key] += 1

        return wins_YTD

    ## dictionary for previous match per player
    prev_matches = {}

    ## function for storing previous match
    def get_prev_matches(player,prev_match_dict,row,data):
        if player not in prev_match_dict:
            prev_match_dict[player] = []

        last_match = prev_match_dict[player]
        prev_match_dict[player] = row

        return last_match

    ## initialize elo win probability (probability of player 1 winning)
    data['Player 1 Elo Rating'] = None
    data['Player 2 Elo Rating'] = None
    data['Elo Probability'] = None
    elo_dict = {}

    ## Calculate probability of winning
    def calculate_win_prob(opponent_elo, player_elo):
        p_win = (1 + (10 ** ((opponent_elo - player_elo) / 400))) ** (-1)
        return p_win

    ## Calculate Elo rating
    def calculate_elo(elo_dict, last_match, player, K):

        if len(last_match) == 0:
            return 1500  ## baseline elo rating value for new players

        elo_prev = elo_dict[player]

        if last_match['Winner'] == player:
            outcome = 1
            opponent = last_match['Loser']
            opponent_elo = elo_dict[opponent]
        if last_match['Loser'] == player:
            outcome = 0
            opponent = last_match['Winner']
            opponent_elo = elo_dict[opponent]

        prev_p_win = calculate_win_prob(opponent_elo, elo_prev)

        elo_new = int(elo_prev + K * (outcome - prev_p_win))

        return elo_new

    # Elo constants
    c = 250
    o = 5
    s = .4

    ## initialize adjusted match dataframe
    final_match_data = pd.DataFrame(columns=list(data.columns))

    count = 0
    for i, row in data.iterrows():

        ## time variables
        year = row['Year']
        month = row['Month']
        day = row['Day']
        ##t = 365*(year - 2000) --> calculate a formula for t

        ## extract two competing players for a match
        p1 = row['Player 1']
        p2 = row['Player 2']

        ## extract winners and losers for a match
        winner = row['Winner']
        loser = row['Loser']

        ## create entry for number of matches played per player (all time)
        p1_matches = get_matches(p1,all_time_matches)
        row['Player 1 All-Time Matches'] = p1_matches
        p2_matches = get_matches(p2,all_time_matches)
        row['Player 2 All-Time Matches'] = p2_matches

        ## create entry for number of wins/losses per player (all time)
        p1_wins,p1_losses = get_results(p1,winner,loser,all_time_wins,all_time_losses)
        row['Player 1 All-Time Wins'] = p1_wins
        row['Player 1 All-Time Losses'] = p1_losses

        p2_wins, p2_losses = get_results(p2, winner, loser, all_time_wins, all_time_losses)
        row['Player 2 All-Time Wins'] = p2_wins
        row['Player 2 All-Time Losses'] = p2_losses

        ## quality check
        assert p1_wins + p1_losses == p1_matches
        assert p2_wins + p2_losses == p2_matches

        ## create entry for number of matches played per player (YTD)
        p1_matches_YTD = get_YTD_matches(p1,years_matches,year)
        row['Player 1 YTD Matches'] = p1_matches_YTD
        p2_matches_YTD = get_YTD_matches(p2,years_matches,year)
        row['Player 2 YTD Matches'] = p2_matches_YTD

        ## create entry for number of wins/losses per player (YTD)
        p1_wins_YTD, p1_losses_YTD = get_YTD_results(p1,year,winner, loser, years_wins, years_losses)
        row['Player 1 YTD Wins'] = p1_wins_YTD
        row['Player 1 YTD Losses'] = p1_losses_YTD

        p2_wins_YTD, p2_losses_YTD = get_YTD_results(p2,year,winner, loser, years_wins, years_losses)
        row['Player 2 YTD Wins'] = p2_wins_YTD
        row['Player 2 YTD Losses'] = p2_losses_YTD

        ## quality check
        assert p1_wins_YTD + p1_losses_YTD == p1_matches_YTD
        assert p2_wins_YTD + p2_losses_YTD == p2_matches_YTD

        ## create entry for h2h matchup
        p1_wins_h2h = get_h2h(p1,p2,h2h_wins,winner)
        row['Player 1 All-Time H2H Wins'] = p1_wins_h2h

        p2_wins_h2h = get_h2h(p2, p1, h2h_wins, winner)
        row['Player 2 All-Time H2H Wins'] = p2_wins_h2h

        ## create entry for YTD h2h matchup
        p1_wins_h2h_ytd = get_YTD_h2h(p1,p2,year,year_h2h,winner)
        row['Player 1 YTD H2H Wins'] = p1_wins_h2h_ytd

        p2_wins_h2h_ytd = get_YTD_h2h(p2,p1,year,year_h2h,winner)
        row['Player 2 YTD H2H Wins'] = p2_wins_h2h_ytd

        '''Calculate Elo Win Probability'''
        p1_last_match = get_prev_matches(p1,prev_matches,row,data)
        p2_last_match = get_prev_matches(p2, prev_matches, row,data)

        ## Calculate K Factor per player
        p1_K = c / (p1_matches + o) ** s
        p2_K = c / (p2_matches + o) ** s

        ## Calculate each players elo rating
        p1_elo_new = calculate_elo(elo_dict, p1_last_match, p1, p1_K)
        elo_dict[p1] = p1_elo_new
        row['Player 1 Elo Rating'] = p1_elo_new

        p2_elo_new = calculate_elo(elo_dict, p2_last_match, p2, p2_K)
        elo_dict[p2] = p2_elo_new
        row['Player 2 Elo Rating'] = p2_elo_new

        ## Calculate probability that player 1 wins the match
        row['Elo Probability'] = calculate_win_prob(p2_elo_new, p1_elo_new)

        ## add row to final match data
        final_match_data.loc[i] = row

        ## code progress report
        if count % 2500 == 0:
            print('Year:', year)
            print('Completed Row:', count)
            print('i:', i)
            print('Rows Left:', len(data) - count)
        count += 1

    return final_match_data

def encode_data(data):

    ## initialize upset predictor variable
    data.loc[data['WRank'] > data['LRank'],'Upset'] = 1
    data.loc[data['WRank'] < data['LRank'], 'Upset'] = 0
    data = data[pd.to_numeric(data['Upset'], errors='coerce').notnull()]
    data['Upset'] = data['Upset'].astype(int)

    ## encode categorical variables
    one_hot_cols = ['Tournament','Court','Surface','Round','Player 1','Player 2']
    data = pd.get_dummies(data,columns=one_hot_cols)

    ## drop unecessary columns
    drop_cols = ['WRank', 'LRank', 'Winner', 'Loser']#,'Player 1','Player 2']
    data = data.drop(drop_cols, axis=1)

    ## ensure categorical variables are the correct type
    data = data.astype(float)
    print(data.dtypes)

    return data


def main(infolder,outfile):

    ## extract match data
    match_data = collect_files(infolder)

    ## clean match data
    cleaned_match_data = clean_data(match_data)

    ## encoded data
    encoded_data = encode_data(cleaned_match_data)

    ## export final data for neural network
    encoded_data.to_csv(outfile)
    print('Data successfully preprocessed')

main(r'/Users/William/Documents/Tennis Neural Network Project/Match Data','/Users/William/Documents/Tennis Neural Network Project/Cleaned Data/cleaned_match_data_v4.csv')
