# bybit Websocket App

For this project, I am using the websocket API of a bitcoin exchange (Bybit) to stream bitcoin prices to a database. Automatic orders can also be implemented into this script.
The necessary libraries for this project are: 
- psycopg2:       For the connection to a postgresql database
- websocket:      For building a websocket app
- json:           To load json messages
- threading:      To run the websocket app in a new thread
- pprint:         To pretty print json messages for easier debugging 
- datetime:       To convert timestamps
- configurations: Module with the database username, password, host, etc

## Prerequisites
The Database is run through docker. Install docker via this [link](https://www.docker.com/get-started)

Timescale DB can be installed to docker with this command in the command line (Please choose a password for your database):

```docker run -d --name timescaledb -p 5432:5432 -e POSTGRES_PASSWORD=[insert your password here] timescale/timescaledb:2.2.0-pg13```

Further information on installing timescale db in docker can be read [here](https://docs.timescale.com/latest/getting-started/installation/docker/installation-docker)

