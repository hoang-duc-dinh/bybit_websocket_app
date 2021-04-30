import os
os.chdir("C:\\Users\\hoangduc.dinh\\Documents\\timescale database\\Bybit")
import configurations
import psycopg2
import psycopg2.extras
import websocket, json, threading, pprint, time
import numpy as np
from datetime import datetime
#import bybit
#import talib

connection = psycopg2.connect(
    host = configurations.db_host,
    database = configurations.db_name,
    user = configurations.db_user,
    password = configurations.db_pass
)

cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)


symbol = "BTCUSD"
interval = "1"
ws_url = "wss://stream.bybit.com/realtime"
candle = [f"klineV2.{interval}.{symbol}"]
sub = {"op":"subscribe", "args": candle}
gambling_amount = 10
data_storage_length = 60*60*3
position = False
max_price = 0
min_price = 99999

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
        data_message = json.loads(message)["data"][0]
        print("Message Received at " + datetime.fromtimestamp(
            data_message["timestamp"]/1000000).strftime("%H:%M:%S")
            + " with price at: {}.".format(data_message["close"])
            )
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

        if data_message["close"] > max_price*1.1:
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

        if json.loads(message)["data"][0]["close"] < min_price*0.9:
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

ws = websocket.WebSocketApp(
        url=ws_url,
        on_message=on_message,
        on_close=on_close,
        on_open=on_open,
        on_error=on_error
        )

wst = threading.Thread(target=lambda: ws.run_forever())
wst.daemon = True
wst.start()


ws.close()
cursor.execute("commit;")
