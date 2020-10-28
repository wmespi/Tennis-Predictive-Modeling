import numpy as np
import pandas as pd
from keras.models import Sequential
from keras.layers import Dense

def test_train_split(data,year):

    ## divide into training and testing data
    train = data[data['Year'] < year]
    test = data[data['Year'] >= year]

    ## pull out predictor variables and separate from predicted upset variable
    columns = list(data.columns)
    columns.remove('Upset')
    X_train = train[columns]
    X_test = test[columns]
    Y_train = train['Upset']
    Y_test = test['Upset']

    return X_train,X_test,Y_train,Y_test

def to_numpy(df1,df2,df3,df4):
    ## X arrays
    np1 = df1.to_numpy()
    np2 = df2.to_numpy()

    ## Y arrays
    np3 = df3.to_numpy()
    np3 = np3.reshape(np3.shape[0],-1)
    np4 = df4.to_numpy()
    np4 = np4.reshape(np4.shape[0], -1)

    return np1,np2,np3,np4

def define_model(data,num_layers,units):

    ## define model
    model = Sequential()

    ## get number of predictor variables
    num_vars = np.shape(data)[1]

    ## add layer 1
    model.add(Dense(units[0], input_dim=num_vars, activation='relu'))

    ## add middle layers
    for i in range(1,num_layers-1):
        model.add(Dense(units[i], activation='relu'))

    ## add final layer
    model.add(Dense(units[num_layers-1], activation='sigmoid'))

    return model

def main(infile,year=2018):

    ## read in data
    data = pd.read_csv(infile,index_col='Unnamed: 0')

    ## split the data
    X_train,X_test,Y_train,Y_test = test_train_split(data,year)
    X_train, X_test, Y_train, Y_test = to_numpy(X_train,X_test,Y_train,Y_test)

    ## build network
    units = [12,24,36,48,60,1]
    layers = len(units)
    model = define_model(X_train,layers,units)

    ## compile model
    model.compile(loss='binary_crossentropy',optimizer='adam',metrics=['accuracy'])

    ## fit model
    model.fit(X_train,Y_train,epochs=1000,batch_size=500)
    print('Model Fitted')

    # evaluate model
    _, accuracy = model.evaluate(X_test,Y_test)
    print('Accuracy: %.2f' % (accuracy * 100))

    return

first_data_set = '/Users/William/Documents/Tennis Neural Network Project/Cleaned Data/cleaned_match_data.csv'
second_data_set = '/Users/William/Documents/Tennis Neural Network Project/Cleaned Data/cleaned_match_data_v2.csv'
third_data_set = '/Users/William/Documents/Tennis Neural Network Project/Cleaned Data/cleaned_match_data_v3.csv'
main(third_data_set)
