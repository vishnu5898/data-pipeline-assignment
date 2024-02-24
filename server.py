from argparse import ArgumentParser, Namespace, RawTextHelpFormatter
from datetime import timedelta, timezone
import calendar
import datetime
import random

from flask import Flask, request, jsonify
import numpy as np
import pandas as pd


DATAFRAME_DATA = pd.read_csv("AXISBANK.csv")
DATAFRAME_DATA = DATAFRAME_DATA.replace(np.nan, None)

AVAILABLE_SYMBOLS = ["AAPL", "IBM", "META", "GOOG"]


app = Flask(__name__)


@app.route("/alpha_vintage", methods=["GET"])
def get_alpha_vintage_data():

    symbol = request.args.get("symbol")

    if not symbol:
        return jsonify({"error": "symbol is not specified"})
    if symbol not in AVAILABLE_SYMBOLS:
        return jsonify({"error": f"Invalid symbol - {symbol}"})

    today = datetime.datetime.now(tz=timezone(-timedelta(hours=5)))

    month = request.args.get("month", today.strftime("%Y-%m"))
    year, month = month.split("-")
    required_date = datetime.datetime.strptime(f"{year}-{month}-01 -0500", "%Y-%m-%d %z")
    no_of_days = calendar.monthrange(required_date.year, required_date.month)[1]
    target_date = datetime.datetime.strptime(f"{year}-{month}-{no_of_days} -0500", "%Y-%m-%d %z")
    
    current_date = required_date

    stock_data = {}
    while current_date < target_date and current_date < today:
        date_string = current_date.strftime("%Y-%m-%d %H:%M:%S")
        stock_prices = [
            random.random()*100 + 100,
            random.random()*100 + 100,
            random.random()*100 + 100,
            random.random()*100 + 100,
            random.random()*100 + 100
        ]
        max_stock_price = max(stock_prices)
        min_stock_price = min(stock_prices)
        stock_data[date_string] = {
                "1. open": str(round(stock_prices[0], 4)),
                "2. high": str(round(max_stock_price, 4)),
                "3. low": str(round(min_stock_price, 4)),
                "4. close": str(round(stock_prices[-1], 4)),
                "5. volume": str(random.randrange(3568393, 3798656))
        }
        current_date = current_date + timedelta(days=1)

    

    sample = {
        "Meta Data": {
            "1. Information": "Intraday Prices (open, high, low, close) and Volumes",
            "2. Symbol": "IBM",
            "3. Last Refreshed": "2024-02-23",
            "4. Output Size": "Compact",
            "5. Time Zone": "US/Eastern"
        },
        "Time Series (1min)": stock_data
    }
    return jsonify(sample)


@app.route("/data", methods=["GET"])
def get_data():
    try:
        page_no = int(request.args.get("page_no", "1"))
    except ValueError:
        page_no = 1
    limit = 10
    start_index = (page_no - 1) * limit
    if start_index < 0:
        start_index = 0
    end_index = start_index + limit
    subset_data = DATAFRAME_DATA.iloc[start_index: end_index]
    api_data = subset_data.to_dict("records")
    if not api_data:
        return jsonify({"status": "FAILED", "error_message": "Data not available","data": api_data})
    return jsonify({"status": "SUCCESS", "error_message": "", "data": api_data})


def handle_sys_args() -> Namespace:
    arg_parser = ArgumentParser(formatter_class=RawTextHelpFormatter,
                                allow_abbrev=False)
    arg_parser.add_argument("-p",
                            "--port",
                            default="5000")
    return arg_parser.parse_args()


if __name__ == "__main__":
    args = handle_sys_args()
    app.run("0.0.0.0", port=int(args.port))
