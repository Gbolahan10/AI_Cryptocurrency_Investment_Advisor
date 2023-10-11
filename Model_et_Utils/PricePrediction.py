# First we will import the necessary Library

import os

import pandas as pd

import numpy as np

import math

import datetime as dt

from numpy import array

import matplotlib.pyplot as plt



# For Evalution we will use these library

from sklearn.metrics import mean_squared_error, mean_absolute_error, explained_variance_score, r2_score

from sklearn.preprocessing import MinMaxScaler



# For model building we will use these library

import tensorflow as tf

from tensorflow.keras.models import Sequential

from tensorflow.keras.layers import Dense, Dropout

from tensorflow.keras.layers import LSTM



import random





def predict_price(df,prediction_days,CoinName):

    random.seed(42)

    np.random.seed(42)

    tf.random.set_seed(42)



    global results_df

    maindf=df.copy()



    # Let's First Take all the Close Price

    closedf = maindf[['Date','Close']]

    # Now we will Take data of 2021 up to now

    #closedf = closedf[closedf['Date'] > '2021-02-19']

    # deleting date column

    del closedf['Date']





    #Normalizing using MinMax Scaler

    scaler=MinMaxScaler(feature_range=(0,1))

    closedf=scaler.fit_transform(np.array(closedf).reshape(-1,1))





    # we keep the training set as 60% and 40% testing set

    training_size=int(len(closedf)*0.70)

    test_size=len(closedf)-training_size

    train_data,test_data=closedf[0:training_size,:],closedf[training_size:len(closedf),:1]





    # convert an array of values into a dataset matrix

    def create_dataset(dataset, time_step=1):

        dataX, dataY = [], []

        for i in range(len(dataset)-time_step-1):

            a = dataset[i:(i+time_step), 0]

            dataX.append(a)

            dataY.append(dataset[i + time_step, 0])

        return np.array(dataX), np.array(dataY)



    time_step = 15

    X_train, y_train = create_dataset(train_data, time_step)

    X_test, y_test = create_dataset(test_data, time_step)

    # reshape input to be [samples, time steps, features] which is required for LSTM

    X_train =X_train.reshape(X_train.shape[0],X_train.shape[1] , 1)

    X_test = X_test.reshape(X_test.shape[0],X_test.shape[1] , 1)







    #LSTM MODEL

    model=Sequential()

    model.add(LSTM(16,input_shape=(None,1),activation="relu"))

    model.add(Dense(1))

    model.compile(loss="mean_squared_error",optimizer="adam")

    history = model.fit(X_train,y_train,validation_data=(X_test,y_test),epochs=200,batch_size=32,verbose=1)



    # Model Evaluation

    # Lets Do the prediction and check performance metrics

    train_predict=model.predict(X_train)

    test_predict=model.predict(X_test)



    # Transform back to original form

    train_predict = scaler.inverse_transform(train_predict)

    test_predict = scaler.inverse_transform(test_predict)

    original_ytrain = scaler.inverse_transform(y_train.reshape(-1,1))

    original_ytest = scaler.inverse_transform(y_test.reshape(-1,1))



    # Evaluation metrices R2

    Train_R2_score = r2_score(original_ytrain, train_predict)

    Test_R2_score = r2_score(original_ytest, test_predict)

    # Model Evaluation

    Train_MAE = mean_absolute_error(original_ytrain, train_predict)

    Test_MAE = mean_absolute_error(original_ytest, test_predict)





    # Predicting next n days

    x_input=test_data[len(test_data)-time_step:].reshape(1,-1)

    temp_input=list(x_input)

    temp_input=temp_input[0].tolist()





    lst_output=[]

    n_steps=time_step

    i=0

    pred_days = prediction_days

    while(i<pred_days):

        if(len(temp_input)>time_step):

            x_input=np.array(temp_input[1:])

            #print("{} day input {}".format(i,x_input))

            x_input = x_input.reshape(1,-1)

            x_input = x_input.reshape((1, n_steps, 1))



            yhat = model.predict(x_input, verbose=0)

            #print("{} day output {}".format(i,yhat))

            temp_input.extend(yhat[0].tolist())

            temp_input=temp_input[1:]

            #print(temp_input)



            lst_output.extend(yhat.tolist())

            i=i+1

        else:

            x_input = x_input.reshape((1, n_steps,1))

            yhat = model.predict(x_input, verbose=0)

            temp_input.extend(yhat[0].tolist())

            lst_output.extend(yhat.tolist())

            i=i+1



    # Convert the predicted prices to their original scale

    predicted_prices = scaler.inverse_transform(lst_output)



    #creat Loss/Profit and Moving AVG columns

    last_price = maindf['Close'].iloc[-1]

    # Create a new row for day 0 with the last price

    day_zero_row = {'Coin Name': CoinName, 'Day': 0, 'Price': last_price, 'Loss_Profit': 0}

    results_df = pd.DataFrame(day_zero_row, index=[0])

    # Loop through the predicted prices

    for i in range(pred_days):

        # Get the predicted price for the current day

        predicted_price = predicted_prices[i][0]

        # Create a new row with the coin name (Bitcoin), day, and price

        new_row = {'Coin Name': CoinName, 'Day': i+1, 'Price': predicted_price, 'Loss_Profit':predicted_price-last_price}

        # Append the new row to the results DataFrame

        results_df = pd.concat([results_df, pd.DataFrame(new_row, index=[0])], ignore_index=True)

    # Create a column to calculate Moving Average and Exclude day 0 from the calculation

    results_df['Moving Average'] = results_df['Price'].rolling(window=2, min_periods=1).mean().shift()



    return results_df,Test_R2_score,Test_MAE





def run_prediction(df, allCoin):

    results_df = pd.DataFrame(columns=['Coin Name', 'Day', 'Price', 'Loss_Profit'])

    r2_scores = []  # Initialize the list for R2 scores

    mae_scores = []  # Initialize the list for MAE scores

    coin_r2_scores = {}  # Initialize a dictionary to store coin R2 scores

    coin_mae_scores = {}  # Initialize a dictionary to store coin MAE scores

    for coin in allCoin:

        filtered_df = df[df['Symbol'] == coin]

        if not filtered_df.empty:

            coin_results, Test_R2_score, Test_MAE = predict_price(filtered_df, 365, coin)

            results_df = pd.concat([results_df, coin_results], ignore_index=True)

            r2_scores.append(Test_R2_score)  # Append the R2 score to the list

            mae_scores.append(Test_MAE)  # Append the MAE score to the list

            coin_r2_scores[coin] = Test_R2_score  # Store the R2 score in the dictionary

            coin_mae_scores[coin] = Test_MAE  # Store the MAE score in the dictionary

            print(coin_results)

        else:

            print(f"No data found for {coin}.")



    overall_r2_score = np.mean(r2_scores)  # Calculate the average R2 score

    overall_mae_score = np.mean(mae_scores)  # Calculate the average MAE score



    results_df.to_csv('Predictedfile.csv', index=False)



    # Print the list of coins and their R2 scores and MAE scores

    print("R2 scores for each coin:")

    for coin, r2_score in coin_r2_scores.items():

        print(coin, "-", r2_score)



    print("MAE scores for each coin:")

    for coin, mae_score in coin_mae_scores.items():

        print(coin, "-", mae_score)



    return overall_r2_score, results_df


df = pd.read_csv('CryptoCurrency.csv')
df = df.interpolate()

allCoin = [
        'ADA',
      'AVAX',
      'BNB',
      'BTC',
      'BCH',
      'LINK',
      'DOGE',
      'ETH',
      'ETC',
      'HBAR',
      'LTC',
      'XMR',
      'MATIC',
      'SHIB',
      'SOL',
      'TRX',
      'WBTC',
      'XRP'
    ]

r2_score, PredictedResultDf = run_prediction(df, allCoin)
