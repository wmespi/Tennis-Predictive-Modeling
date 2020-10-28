import pandas as pd
import os
import xlrd

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
    cols = ['Day','Month', 'Year', 'Best of', 'WRank','LRank']
    data[cols] = data[cols].astype(int)

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

    ## initialize total matches played for each player
    data['Player 1 All-Time Matches'] = None
    data['Player 2 All-Time Matches'] = None

    ## initialize win-loss columns player 1
    data['Player 1 All-Time Wins'] = None
    data['Player 1 All-Time Losses'] = None
    data['Player 1 YTD Wins'] = None
    data['Player 1 YTD Losses'] = None
    data['Player 1 All-Time Titles'] = None

    ## initialize win-loss columns player 2
    data['Player 2 All-Time Wins'] = None
    data['Player 2 All-Time Losses'] = None
    data['Player 2 YTD Wins'] = None
    data['Player 2 YTD Losses'] = None
    data['Player 2 All-Time Titles'] = None

    ## initialize head to head stats
    data['Player 1 All-Time H2H Wins'] = None
    data['Player 2 All-Time H2H Wins'] = None
    data['Player 1 YTD H2H Wins'] = None
    data['Player 2 YTD H2H Wins'] = None

    ## initialize elo win probability (probability of player 1 winning)
    data['Player 1 Elo Rating'] = None
    data['Player 2 Elo Rating'] = None
    data['Elo Probability'] = None
    elo_dict = {}

    ## initialize adjusted match dataframe
    final_match_data = pd.DataFrame(columns=list(data.columns))

    ## player 1 and player 2 win-loss statistics
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

        ## reduce to matches that have been played in the past
        past_matches = data.loc[0:i-1]

        ''' All Time statistics for both players'''
        ## player 1 All-Time Matches played
        p1_past_matches = past_matches[(past_matches['Winner'] == p1) | (past_matches['Loser'] == p1)]
        row['Player 1 All-Time Matches'] = len(p1_past_matches)

        ## player 2 All-Time Matches played
        p2_past_matches = past_matches[(past_matches['Winner'] == p2) | (past_matches['Loser'] == p2)]
        row['Player 2 All-Time Matches'] = len(p2_past_matches)

        ## player 1 All-Time wins and losses
        p1_wins = p1_past_matches[(p1_past_matches['Winner'] == p1)]
        p1_losses = p1_past_matches[(p1_past_matches['Loser'] == p1)]
        row['Player 1 All-Time Wins'] = len(p1_wins)
        row['Player 1 All-Time Losses'] = len(p1_losses)

        ## player 2 All-Time wins and losses
        p2_wins = p2_past_matches[(p2_past_matches['Winner'] == p2)]
        p2_losses = p2_past_matches[(p2_past_matches['Loser'] == p2)]
        row['Player 2 All-Time Wins'] = len(p2_wins)
        row['Player 2 All-Time Losses'] = len(p2_losses)

        ## All-Time H2H Wins
        p1_wins_H2H = p1_wins[p1_wins['Loser'] == p2]
        p2_wins_H2H = p1_wins[p1_wins['Loser'] == p1]
        row['Player 1 All-Time H2H Wins'] = len(p1_wins_H2H)
        row['Player 2 All-Time H2H Wins'] = len(p2_wins_H2H)

        ## Player 1 All-Time titles
        p1_titles = len(p1_wins[(p1_wins['Round'] == 'The Final')])
        row['Player 1 All-Time Titles'] = p1_titles

        ## Player 2 All-Time titles
        p2_titles = len(p2_wins[(p2_wins['Round'] == 'The Final')])
        row['Player 2 All-Time Titles'] = p2_titles

        '''Year to Date statistics for both players'''
        ## player 1 YTD wins and losses
        p1_wins_YTD = p1_wins[p1_wins['Year'] == year]
        p1_losses_YTD = p1_losses[p1_losses['Year'] == year]
        row['Player 1 YTD Wins'] = len(p1_wins_YTD)
        row['Player 1 YTD Losses'] = len(p1_losses_YTD)

        ## player 2 YTD wins and losses
        p2_wins_YTD = p2_wins[p2_wins['Year'] == year]
        p2_losses_YTD = p2_losses[p2_losses['Year'] == year]
        row['Player 2 YTD Wins'] = len(p2_wins_YTD)
        row['Player 2 YTD Losses'] = len(p2_losses_YTD)

        ## YTD H2H Wins
        p1_wins_YTD_H2H = p1_wins_YTD[p1_wins_YTD['Loser'] == p2]
        p2_wins_YTD_H2H = p1_wins_YTD[p1_wins_YTD['Loser'] == p1]
        row['Player 1 YTD H2H Wins'] = len(p1_wins_YTD_H2H)
        row['Player 2 YTD H2H Wins'] = len(p2_wins_YTD_H2H)

        '''Calculate Elo Win Probability'''
        ## Calculate K Factor per player
        c = 250
        o = 5
        s = .4
        p1_M = len(p1_past_matches)
        p1_K = c/(p1_M + o)**s
        p2_M = len(p2_past_matches)
        p2_K = c /(p2_M + o) ** s

        ## Calculate probability of winning
        def calculate_win_prob(opponent_elo,player_elo):
            p_win = (1 + (10 ** ((opponent_elo - player_elo) / 400))) ** (-1)

            return p_win

        ## Calculate Elo rating
        def calculate_elo(elo_dict,player_past_matches,player,K):

            if len(player_past_matches) == 0:
                return 1500 ## baseline elo rating value for new players

            last_match = player_past_matches.iloc[len(player_past_matches)-1]
            elo_prev =  elo_dict[player]

            if last_match['Winner'] == player:
                outcome = 1
                opponent = last_match['Loser']
                opponent_elo = elo_dict[opponent]
            if last_match['Loser'] == player:
                outcome = 0
                opponent = last_match['Winner']
                opponent_elo = elo_dict[opponent]

            prev_p_win = calculate_win_prob(opponent_elo,elo_prev)

            elo_new = int(elo_prev + K*(outcome-prev_p_win))

            return elo_new

        ## Calculate each players elo rating
        p1_elo_new = calculate_elo(elo_dict,p1_past_matches,p1,p1_K)
        elo_dict[p1] = p1_elo_new
        row['Player 1 Elo Rating'] = p1_elo_new

        p2_elo_new = calculate_elo(elo_dict, p2_past_matches, p2, p2_K)
        elo_dict[p2] = p2_elo_new
        row['Player 2 Elo Rating'] = p2_elo_new

        ## Calculate probability that player 1 wins the match
        row['Elo Probability'] = calculate_win_prob(p2_elo_new,p1_elo_new)

        ## add row to final_match_data
        final_match_data.loc[i] = row

        ## add stats for number of titles, masters, and grand slams
        ## add stats for top 10/top 20 record (all time and YTD)
        ## stats for weeks in top 10? Might not be able to get exact numbers
        ## stats for years on tour?
        ## stats for wins (H2H, YTD, and overall) based on surface type!!!!
        ## stats for win streaks (H2H, YTD,  and overall)?
        ## stats for missing grand slams/masters (trying to be a proxy for injury)
        ## stats for retirements could also be used for injuries/fatigue problems

        ## code progress report
        if count%2500 == 0:
            print('Year:',year)
            print('Completed Row:',count)
            print('i:',i)
            print('Rows Left:',len(data)-count)
        count += 1

    return final_match_data


def encode_data(data):
    print(data.dtypes)
    cols = ['Player 1 Elo Rating','Player 1 Elo Rating','Elo Probability']
    print(data[cols])

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
    print(encoded_data)
    print('Data successfully preprocessed')




main(r'/Users/William/Documents/Tennis Neural Network Project/Match Data','/Users/William/Documents/Tennis Neural Network Project/Cleaned Data/cleaned_match_data_v3_check.csv')





## probably don't need
def player_test(player_test):
    player_file_test_path = '/Users/William/Documents/Tennis Neural Network Project/Cleaned Data/test/'
    if p1 == player_test or p2 == player_test:
        past_matches = final_match_data.loc[0:i]
        player_matches = past_matches[(past_matches['Winner'] == player_test) | (past_matches['Loser'] == player_test)]
        file = player_file_test_path + str(count) + '.csv'
        player_matches.to_csv(file)