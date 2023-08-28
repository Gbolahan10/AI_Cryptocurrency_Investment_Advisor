# This code was used to scrape data for the overview page
# The contents are saved in a text file so scraping is not done everytime the overview page is needed. 

import requests, time, json
from bs4 import BeautifulSoup
import pandas as pd

filtered_names = [
    'Aptos', 'Arbitrum', 'Avalanche', 'BNB', 'Bitcoin', 'Bitcoin-Cash', 'Cardano', 'Chainlink', 'Dogecoin', 'Ethereum', 'Ethereum-Classic', 'Hedera', 'Litecoin', 'Monero', 'Polygon', 'Shiba-Inu', 'Solana', 'TRON', 'Wrapped-Bitcoin', 'XRP'
]

diction = {}

for symbol in filtered_names:
    sym = symbol.lower()

    url = f'https://coinmarketcap.com/currencies/{sym}/'

    r = requests.get(url)

    time.sleep(7)

    soup = BeautifulSoup(r.text, 'html.parser')

    about =soup.find_all('div', {"class":"sc-30065ccd-0 keBwNL"})

    result = ""
    
    for i in about[:-1]:
        result += str(i)
    diction.update({
        sym: result 
    })


# Save the dictionary to a .txt file
with open('overview_dict.txt', 'w') as file:
    json.dump(diction, file)