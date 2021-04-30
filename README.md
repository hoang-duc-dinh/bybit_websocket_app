# bybit_websocket_app

For this project, I am using the websocket API of a bitcoin exchange (Bybit) to stream bitcoin prices to a database. Automatic orders can also be implemented into this script.
The necessary libraries for this project are: 
- psycopg2:       For the connection to a postgresql database
- websocket:      For building a websocket app
- json:           To load json messages
- threading:      To run the websocket app in a new thread
- pprint:         To pretty print json messages for easier debugging 
- datetime:       To convert timestamps
- configurations: Module with the database username, password, host, etc

To build a websocket app in its simplest form, we need to define what happens 
- on opening the websocket connection
- on closing the connection
- when an error occurs
- on incoming messages

We want to subscribe to the bitcoin price candlestick stream, so we send a json file to the websocket on opening of the connection.
When we receive a message, we want to print the price and then query an sql insertion with the price data.
