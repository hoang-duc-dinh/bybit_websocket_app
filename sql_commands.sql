CREATE DATABASE bybit;

CREATE TABLE btc_prices(
    time_request TIMESTAMP (6) WITH time zone not null primary key,
    price_close numeric not null,
	price_high numeric not null,
	price_low numeric not null,
	volume numeric not null,
	turnover numeric not null
);

set time ZONE "+2";

CREATE TABLE orders(
	id SERIAL PRIMARY KEY,
	order_time TIMESTAMP (6) WITH time ZONE not null,
	side TEXT not NULL,
	price NUMERIC NOT NULL,
	quantity NUMERIC NOT NULL,
	take_profit NUMERIC,
	stop_loss NUMERIC,
	order_type TEXT NOT NULL,
	constraint fk_order_time foreign key (order_time) references btc_prices (time_request)
);
