from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests, json, csv
import datetime
from GoogleNews import GoogleNews
from datetime import datetime, timedelta
from pytz import timezone

app = Flask(__name__)

app.static_folder = 'static'
app.template_folder = 'templates'

CORS(app)


@app.route('/')
def index():
    return render_template('homepage.html')

@app.route('/home')
def home():
    return render_template('test.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/predict', methods = ['POST'])
def predict():
    request_data = request.get_json()
    coins_traded = request_data['coins']
    target_profit = int(request_data['desiredPrice'])
    desiredDate = request_data['desiredDate']

    # Define two date strings
    date_str1 = desiredDate
    date_str2 = '2023-08-16'

    # Convert the date strings to datetime objects
    date1 = datetime.strptime(date_str1, '%Y-%m-%d')
    date2 = datetime.strptime(date_str2, '%Y-%m-%d')

    # Calculate the difference between the two dates
    date_difference = date1 - date2

    days = date_difference.days

    #def Invest_advice(days, target_profit):

    with open('Predictedfile.csv', 'r') as file:

        reader = csv.DictReader(file)

        filtered_coins = []

        coins_profit = {}

        # Filter coins based on the given number of days and non-negative loss_profit

        filtered_data = [row for row in reader if int(row['Day']) == days and float(row['Loss_Profit']) >= 0 and str(row['Coin Name']) in coins_traded]
        
        # Calculate profit for each coin and store it in a dictionary

        for row in filtered_data:

            coin = row['Coin Name']

            profit = float(row['Loss_Profit'])

            if coin not in coins_profit:

                coins_profit[coin] = profit

            else:

                coins_profit[coin] += profit

        # Sort coins based on profit

        sorted_coins = sorted(coins_profit.items(), key=lambda x: x[1], reverse=True)

        # Find coins that can reach the target profit

        total_profit = 0

        for coin, profit in sorted_coins:

            if total_profit >= target_profit:

                break

            total_profit += profit

            filtered_coins.append(coin)

        if total_profit < target_profit:

            return jsonify({'data':'None'})  # No combination of coins can reach the target profit

        return jsonify({'data':filtered_coins})
    

@app.route('/overview', methods = ['POST'])
def overview():
    request_data = request.get_json()
    symbol = request_data['symbol'].lower()

    with open('overview_dict.txt', 'r') as file:
        loaded_dict = json.load(file)

    result = {'data':loaded_dict[symbol]}
    return jsonify(result)


@app.route('/get-feeds')
def get_feeds():
    request_data = request.get_json()
    query = request_data['query']
    #GET A PERIOD OF TIME
    est = timezone('EST')
    today = datetime.now(est)
    yesterday = today - timedelta(days=1)

    #SET THE DATE RANGE
    googlenews=GoogleNews(start=yesterday.strftime("%m-%d-%Y"),end=today.strftime("%m-%d-%Y"))
    #SET THE LANGUAGE
    googlenews.set_lang('en')
    #SET THE TOPIC
    googlenews.search(query)
    #GET THE NEWS
    result=googlenews.result()
    
    return result

@app.route('/history', methods=['POST'])
def history():
    request_data = request.get_json()
    symbol = request_data['symbol']
    interval = request_data['interval']
    limit = 2000
    print("got to history")
    candlesticks = requests.get(f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}")
    print("got the history")
    new_candles = json.loads(candlesticks.text)
    processed_candlesticks = []

    for data in new_candles:
        candlestick = { 
            "time": data[0] / 1000, 
            "open": data[1],
            "high": data[2], 
            "low": data[3], 
            "close": data[4]
        }

        processed_candlesticks.append(candlestick)
    
    print("sent the history")
    return jsonify(processed_candlesticks)

if __name__ == '__main__':
    app.run(debug=True)