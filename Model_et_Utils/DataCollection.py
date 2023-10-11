import pandas as pd

import yfinance as yf

from datetime import date



def FetchData():

    allCoin = [
        'ADA-USD',
      'AVAX-USD',
      'BNB-USD',
      'BTC-USD',
      'BCH-USD',
      'LINK-USD',
      'DOGE-USD',
      'ETH-USD',
      'ETC-USD',
      'HBAR-USD',
      'LTC-USD',
      'XMR-USD',
      'MATIC-USD',
      'SHIB-USD',
      'SOL-USD',
      'TRX-USD',
      'WBTC-USD',
      'XRP-USD'
    ]

    def remove(x): #  This function will strip the data column of the dataframe.

        x = str(x)

        res = x.split(" ")[0]

        return res



    all_coin_data = pd.DataFrame() # create an empty dataframe to hold all the coin data

    today = date.today().strftime('%Y-%m-%d')

    for coin in allCoin:

        ticker = yf.Ticker(coin)

        coin_data = ticker.history(start="2021-01-01", end=today) # fetch data for the coin after 2021

        coin_data.index = pd.to_datetime(coin_data.index)

        coin_data.index = coin_data.index.to_series().apply(lambda x: remove(x))

        coin_data['Symbol'] = coin.split('-')[0] # add a new column with the coin symbol

        all_coin_data = pd.concat([all_coin_data, coin_data])

    all_coin_data.to_csv('AllCoins.csv') # save the data to a csv file





    df = pd.read_csv('AllCoins.csv')

    df = df.drop(['Dividends', 'Stock Splits'], axis=1)

    df.set_index('Date', inplace=True)

    print('Null Values:',df.isnull().values.sum())

    print('NA values:',df.isnull().values.any())

    # If dataset had null values we use this code to drop all the null values present in the dataset

    df=df.dropna()

    datasetsize=df.shape

    df.to_csv('CryptoCurrency.csv')

    #Final shape of the dataset after dealing with null values

    return datasetsize





