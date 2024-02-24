"""
This is the entry point of the data pipeline. Run this file
to start the data ingestion, i.e get stock data from the mock api
and transform, clean and store this data to Postgresql table.


The storage table is ```market_data.stock_data```
"""

from datetime import timedelta, timezone
import calendar
import datetime
import os
import time

import requests
import pandas as pd
import psycopg2

from server import AVAILABLE_SYMBOLS


LAST_INSERTED_DATETIME_FILE = "last_inserted_month.csv"


# Make connection to postgres table
connection = psycopg2.connect(
    host="localhost",
    database=os.getenv("PG_DATABASE", "market_data"),
    user=os.getenv("PG_USERNAME", ""),
    password=os.getenv("PG_PASSWORD", "")
)
create_table_statement = (
    f"CREATE SCHEMA IF NOT EXISTS market_data;"
    f"CREATE TABLE IF NOT EXISTS market_data.stock_data "
    f"(stock_datetime TIMESTAMP WITHOUT TIME ZONE, open FLOAT, "
    f"high FLOAT, low FLOAT, close FLOAT, "
    f"volume FLOAT, symbol VARCHAR, "
    f"CONSTRAINT market_data_stock_data_unq UNIQUE (symbol, stock_datetime)"
    f") WITH (fillfactor=70);"
)
create_index_statement = (
    f"CREATE INDEX IF NOT EXISTS market_data_stock_data_stock_datetime_idx ON market_data.stock_data (stock_datetime);"
)


def create_insert_statement(data_dict: dict) -> str:
    """
    Create a postresql insert statement to push the
    data provided in that data_dict.
    """

    columns = data_dict.keys()
    columns_str = ", ".join(column for column in columns)
    column_values_str = ", ".join(f"%({column})s" for column in columns)
    stmt = (
        f"INSERT INTO market_data.stock_data ({columns_str}) "
        f"VALUES ({column_values_str}) ON CONFLICT ON CONSTRAINT market_data_stock_data_unq DO NOTHING"
    )
    return stmt


def create_month_range() -> list:
    months = []
    today = datetime.datetime.now(tz=timezone(-timedelta(hours=5)))
    start = datetime.datetime(year=2000, month=1, day=1, tzinfo=timezone(-timedelta(hours=5)))

    required_date = start
    while required_date <= today:
        required_month = required_date.date().strftime("%Y-%m")
        months.append(required_month)
        no_of_days = calendar.monthrange(required_date.year, required_date.month)[1]
        required_date = timedelta(days=no_of_days) + required_date

    return months


class YearMonth:
    def __init__(self, year_month: str) -> None:
        self.year_month = year_month
        self.year = year_month.split("-")[0]
        self.month = year_month.split("-")[1]

    def to_date(self) -> datetime.datetime:
        return datetime.datetime.strptime(f"{self.year}-{self.month}-01", "%Y-%m-%d")


def main():
    months = create_month_range()
    last_inserted_month = months[0]

    if os.path.exists(LAST_INSERTED_DATETIME_FILE):
        df = pd.read_csv(LAST_INSERTED_DATETIME_FILE)
        last_inserted_month = df.to_dict("records")[0]["month"]
    for month in months:
        custom_month = YearMonth(month).to_date()
        custom_last_inserted_month = YearMonth(last_inserted_month).to_date()

        # Skipping already ingested data
        if custom_month <= custom_last_inserted_month:
            continue

        # Get data from the mock api

        for symbol in AVAILABLE_SYMBOLS:
            res = requests.get(f"http://localhost:5000/alpha_vintage?month={month}&symbol={symbol}")
            stock_data = res.json()
            stock_data = stock_data["Time Series (1min)"]
            for date_time in stock_data:
                data_dict = {}
                data_dict["stock_datetime"] = date_time
                data_dict["open"] = stock_data[date_time]["1. open"]
                data_dict["high"] = stock_data[date_time]["2. high"]
                data_dict["low"] = stock_data[date_time]["3. low"]
                data_dict["close"] = stock_data[date_time]["4. close"]
                data_dict["volume"] = stock_data[date_time]["5. volume"]
                data_dict["symbol"] = symbol
                stmt = create_insert_statement(data_dict)
                cursor.execute(stmt, data_dict)
        connection.commit()
        df = pd.DataFrame([{"month": month}])
        df.to_csv(LAST_INSERTED_DATETIME_FILE, index=False)
        print(f"{month=}")




if __name__ == "__main__":
    cursor = connection.cursor()
    cursor.execute(create_table_statement)
    cursor.execute(create_index_statement)
    connection.commit()

    # Code to simulate real time data ingestion to the table
    main()
