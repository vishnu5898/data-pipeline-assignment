import requests
import psycopg2


connection = psycopg2.connect(
    host="localhost",
    database="market_data",
    user="test_user",
    password="test_password"
)

create_table_statement = (
    f"CREATE TABLE IF NOT EXISTS market_data.stock_data "
    f"(date_of_stock DATE, percentage_deliverable FLOAT, "
    f"close FLOAT, deliverable_volume INTEGER, high FLOAT, "
    f"last FLOAT, low FLOAT, open FLOAT, previous_close FLOAT, "
    f"series VARCHAR, symbol VARCHAR, trades INTEGER, "
    f"turnover BIGINT, volume_weighted_average_price FLOAT, "
    f"volume INTEGER"
    f") WITH (fillfactor=70);"
)

create_index_statement = (
    f"CREATE INDEX IF NOT EXISTS market_data_stock_data_date_idx ON market_data.stock_data (date_of_stock)"
)

api_to_column_mapping = {
    "%Deliverble": "percentage_deliverable",
    "Close": "close",
    "Date": "date_of_stock",
    "Deliverable Volume": "deliverable_volume",
    "High": "high",
    "Last": "last",
    "Low": "low",
    "Open": "open",
    "Prev Close": "previous_close",
    "Series": "series",
    "Symbol": "symbol",
    "Trades": "trades",
    "Turnover": "turnover",
    "VWAP": "volume_weighted_average_price",
    "Volume": "volume",
}


def create_insert_statement(data_dict: dict) -> str:
    columns = data_dict.keys()
    columns_str = ", ".join(column for column in columns)
    column_values_str = ", ".join(f"%({column})s" for column in columns)
    stmt = (
        f"INSERT INTO market_data.stock_data ({columns_str}) "
        f"VALUES ({column_values_str})"
    )
    return stmt



def main():
    data = True
    page_no = 1
    while data:
        res = requests.get(f"http://127.0.0.1:5000/data?page_no={page_no}")
        data = res.json()["data"]
        for api_data in data:
            data_dict = {}
            for key in api_data:
                data_dict[api_to_column_mapping[key]] = api_data[key]
            stmt = create_insert_statement(data_dict)
            cursor.execute(stmt, data_dict)
        connection.commit()
        page_no += 1


if __name__ == "__main__":
    cursor = connection.cursor()
    cursor.execute(create_table_statement)
    cursor.execute(create_index_statement)
    connection.commit()
    while True:
        main()
