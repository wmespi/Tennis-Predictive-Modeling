import pandas as pd
import os
import xlrd

def collect_files(folder):

    ## pull specific columns from dataset and initialize dataframe
    cols = ['Tournament', 'Month', 'Year', 'Court','Winner',
            'Loser','Surface','Round', 'Best of', 'WRank',
            'LRank']
    data = pd.DataFrame(columns = cols)

    ## open each file in directory and extract annual match data
    for filename in sorted(os.listdir(folder)):

        ## restrict file type
        if filename.endswith('xls') or filename.endswith('xlsx'):

            file_path = os.path.join(folder, filename)
            year_data = pd.read_excel(file_path)

            ## insert year and month fields
            year_data['Month'] = pd.DatetimeIndex(year_data['Date']).month
            year_data['Year'] = pd.DatetimeIndex(year_data['Date']).year

            ## add new rows to master data set
            data = pd.concat([data,year_data],join='inner')

    return data

def encode_data(data):

    ## ensure numerical types are correct for appropriate variables
    data = data[pd.to_numeric(data['LRank'], errors='coerce').notnull()]
    data = data[pd.to_numeric(data['WRank'], errors='coerce').notnull()]
    cols = ['Month', 'Year', 'Best of', 'WRank','LRank']
    data[cols] = data[cols].astype(int)

    ## initialize lower ranked players rank
    data['LowRank'] = data[['LRank','WRank']].min(axis=1)
    data.loc[data['WRank'] > data['LRank'], 'LowPlayer'] = data.loc[data['WRank'] > data['LRank'], 'Winner']
    data.loc[data['WRank'] < data['LRank'], 'LowPlayer'] = data.loc[data['WRank'] < data['LRank'], 'Loser']

    ## initialize higher ranked players rank
    data['HighRank'] = data[['LRank','WRank']].max(axis=1)
    data.loc[data['WRank'] < data['LRank'], 'HighPlayer'] = data.loc[data['WRank'] < data['LRank'], 'Winner']
    data.loc[data['WRank'] > data['LRank'], 'HighPlayer'] = data.loc[data['WRank'] > data['LRank'], 'Loser']

    ## initialize upset predictor variable
    data.loc[data['WRank'] > data['LRank'],'Upset'] = 1
    data.loc[data['WRank'] < data['LRank'], 'Upset'] = 0
    data = data[pd.to_numeric(data['Upset'], errors='coerce').notnull()]
    data['Upset'] = data['Upset'].astype(int)

    ## encode categorical variables
    one_hot_cols = ['Tournament','Court','Surface','Round','HighPlayer','LowPlayer']
    data = pd.get_dummies(data,columns=one_hot_cols)

    ## drop unecessary columns
    drop_cols = ['WRank', 'LRank', 'Winner', 'Loser']
    data = data.drop(drop_cols, axis=1)

    ## ensure categorical variables are the correct type
    data = data.astype(int)

    return data

def main(infolder,outfile):

    ## extract match data
    match_data = collect_files(infolder)

    ## clean match data
    cleaned_match_data = encode_data(match_data)

    ## export final data for neural network
    cleaned_match_data.to_csv(outfile)

main(r'/Users/William/Documents/Tennis Neural Network Project/Match Data','/Users/William/Documents/Tennis Neural Network Project/Cleaned Data/cleaned_match_data.csv')
