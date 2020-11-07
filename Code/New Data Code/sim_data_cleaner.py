import pandas as pd
import os

def collect_files(folder,outfile):

    ## pull specific columns from dataset and initialize dataframe
    cols = [
        'tourney_id', 'tourney_name', 'surface', 'draw_size', 'tourney_level',
        'tourney_date', 'match_num',
        'winner_name','winner_age','winner_rank','winner_rank_points','w_ace','w_df','w_svpt','w_1stIn','w_1stWon','w_2ndWon','w_SvGms','w_bpSaved','w_bpFaced',
        'loser_name', 'loser_age','loser_rank','loser_rank_points','l_ace','l_df','l_svpt','l_1stIn','l_1stWon','l_2ndWon','l_SvGms','l_bpSaved','l_bpFaced',
        'best_of','round','minutes',
    ]

    data = pd.DataFrame(columns=cols)

    ## open each file in directory and extract annual match data
    i = 1968
    for filename in sorted(os.listdir(folder)):

        ## restrict file type
        if filename.endswith('csv'):

            file_path = os.path.join(folder, filename)
            year_data = pd.read_csv(file_path)

            ##remove duplicate matches
            year_data = year_data[cols]
            print(i)
            year_data = year_data.drop_duplicates()
            i+=1

            ## add new rows to master data set
            data = pd.concat([data,year_data],join='inner',ignore_index=True)

    #data = data.dropna()
    data = data.reset_index(drop=True)
    data.to_csv(outfile)

    return

path = '/Users/William/Documents/Tennis-Predictive-Modeling/New Match Data'
outfile = '/Users/William/Documents/Tennis-Predictive-Modeling/Cleaned Data/New Match Data Cleaned.csv'
collect_files(path,outfile)

#'/Users/William/Desktop/check.csv'