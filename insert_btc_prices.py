import configurations
import psycopg2
import psycopg2.extras
import websocket, json, threading, pprint, time
import numpy as np
from datetime import datetime

# A connection with timescale db will be created with the psycopg2 library. The configuration details are imported through the configuration file.
connection = psycopg2.connect(
    host = configurations.db_host,
    database = configurations.db_name,
    user = configurations.db_user,
    password = configurations.db_pass
)

cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

# We can test the connection by doing a simple sql query
cursor.execute("select 1")
cursor.fetchall()

# Declaring the constants. 
symbol = "BTCUSD" # We want to fetch the current BTC prices in USD. Our exchange market (bybit) uses the symbol "BTCUSD" for that. We can subscribe to a stream by sending a json file with the streaming channel as an argument.
interval = "1" # This is the time interval for the candlestick data
ws_url = "wss://stream.bybit.com/realtime" # The websocket url of bybit
candle = [f"klineV2.{interval}.{symbol}"] # Create the string for candlestick data with set interval and set symbol
sub = {"op":"subscribe", "args": candle} # Create the json-string to send to the websocket
gambling_amount = 10 # The maximum amount of cash for an order position
position = False # This script only allows one order position at the same time. If position is True, no more orders will be taken.
max_price = 0 # The global maximum price
min_price = 99999 # The global minimum price

def on_open(ws):
    print("Opened")
    ws.send(json.dumps(sub))
def on_close(ws):
    print("Closed")

def on_error(ws, error):
    #cursor.execute("abort;")
    print(error)

def on_message(ws, message):
    global min_price
    global max_price
    
    if "data" in json.loads(message):
        
        # print that message is received with the request time and the current btc price
        data_message = json.loads(message)["data"][0]
        print("Message Received at " + datetime.fromtimestamp(
            data_message["timestamp"]/1000000).strftime("%H:%M:%S")
            + " with price at: {}.".format(data_message["close"])
            )
        
        # query an sql-insertion 
        cursor.execute("""insert into btc_prices (time_request, price_close,
        price_high, price_low, volume, turnover) values (to_timestamp({}), {},
        {}, {}, {}, {});""".format(
            data_message["timestamp"]/1000000,
            data_message["close"],
            data_message["high"],
            data_message["low"],
            data_message["volume"],
            data_message["turnover"]
            )
        )
        
        # if position = true: normally, i check if there is already an order, 
        # for demonstration purposes, we skip that part
        
        # if the price is 10% higher than the last max price, sell!
        if data_message["close"] > max_price*1.1:
            
            # set a new max_price
            max_price = data_message["close"]

            cursor.execute(
            """insert into orders ( order_time, side, quantity,
            take_profit, stop_loss, order_type )
            values (to_timestamp({}),'sell', {},
            NULL, NULL,'Limit');""".format(
                data_message["timestamp"]/1000000,
                gambling_amount
                )
            )
            print("Sell order placed.")
        
        # if the price is 10% lower than the last min price, buy!
        if data_message["close"] < min_price*0.9:
            min_price = data_message["close"]

            cursor.execute(
            """insert into orders ( order_time, side, quantity,
            take_profit, stop_loss, order_type )
            values (to_timestamp({}),'buy', {},
            NULL, NULL,'Limit');""".format(
                data_message["timestamp"]/1000000,
                gambling_amount
                )
            )
            print("Buy order placed.")

# Set Up the Websocket App
ws = websocket.WebSocketApp(
        url=ws_url,
        on_message=on_message,
        on_close=on_close,
        on_open=on_open,
        on_error=on_error
        )

# Create a separate thread to run the Websocket App.
wst = threading.Thread(target=lambda: ws.run_forever())
wst.daemon = True
wst.start()


ws.close()
cursor.execute("commit;")
