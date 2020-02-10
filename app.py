import os
from datetime import date
from multiprocessing import Process
from flask import Flask, render_template, request, abort
import pandas as pd
import db_operations as db
import visualizer as grapher
import collector
import configure
import analyzer as meth

app = Flask(__name__)
config = configure.parse_env()


@app.route("/api/v1.0/collector/collect_all")
def collect_all():
    """This will only work for all symbols if enny is hosted outside of Lambda
    as the container will kill itself before completion."""
    collector_process = Process(target=collector.main, args=())
    collector_process.start()
    return "Collecting."


@app.route("/api/v1.0/collector/collect/<symbol>", methods=["GET"])
def collect(symbol):
    """Get a stock from AV."""
    return collector.collect(symbol)


@app.route("/api/v1.0/conf")
def show_conf():
    return {"conf": config}


@app.route("/api/v1.0/ticker/<symbol>", methods=["GET"])
def ticker(symbol,):
    """Get a dataframe as JSON"""
    if len(symbol) == 0:
        abort(404)
    try:
        df = db.get_dataframe(symbol, config)
    except:
        abort(404)
    return df.to_json()


@app.route("/api/v1.0/analysis/<method>/<symbol>")
def analyze(method, symbol):
    """Transform time series in some manner."""
    dfs = {}
    method = getattr(meth, method)
    # For some reason, providing a default value to args.get didn't work as expected.
    if request.args.get("from"):
        chart_from = pd.to_datetime(request.args.get("from"))
    else:
        chart_from = pd.to_datetime(date(2000, 1, 1))
    if request.args.get("to"):
        chart_to = pd.to_datetime(request.args.get("to"))
    else:
        chart_to = pd.to_datetime(date.today())
    return method(db.get_dataframe(symbol.strip(), config))[
        chart_from:chart_to:-1
    ].to_json()


@app.route("/api/v1.0/graph/")
def graph():
    """This method will return a graph as HTML. It takes all input from the Flask request object."""
    dfs = {}
    method = getattr(meth, request.args.get("method"))
    # For some reason, providing a default value to args.get didn't work as expected.
    for symbol in request.args.getlist("field"):
        dfs[symbol.strip()] = analyze(method, symbol.strip())
    return grapher.plot_to_html(dfs)


@app.route("/")
def root():
    """Render the index.html template and show the results."""
    with open(os.getenv("ENNY_SYMBOLFILE", "./NDX"), "r") as f:
        symbols = f.readlines()
    return render_template(
        "index.html",
        data={"title": "Which stocks would you like to graph?", "fields": symbols,},
    )


if __name__ == "__main__":
    """Supply data to the rest of the app. Configured through env variables."""
    app.run()
