from argparse import ArgumentParser, Namespace, RawTextHelpFormatter

from flask import Flask, request, jsonify
import numpy as np
import pandas as pd


DATAFRAME_DATA = pd.read_csv("AXISBANK.csv")
DATAFRAME_DATA = DATAFRAME_DATA.replace(np.nan, None)


app = Flask(__name__)


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


args = handle_sys_args()
app.run("0.0.0.0", port=int(args.port))
