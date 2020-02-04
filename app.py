import os
from datetime import date
from multiprocessing import Process
from flask import Flask, render_template, request, abort
import db_operations as db
import visualizer as grapher
import collector
import configure
import analyzer as meth

app = Flask(__name__)


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
    config = configure.parse_env()
    return {"conf": config}


@app.route("/api/v1.0/ticker/<symbol>", methods=["GET"])
def ticker(symbol,):
    """Get a dataframe as JSON"""
    config = configure.parse_env()
    if len(symbol) == 0:
        abort(404)
    try:
        df = db.get_dataframe(symbol, config)
    except:
        abort(404)
    return df.to_json()


@app.route("/api/v1.0/graph/")
def graph():
    """This method will return a graph as HTML. It takes all input from the Flask request object."""
    config = configure.parse_env()
    dfs = {}
    method = getattr(meth, request.args.get("method"))
    # For some reason, providing a default value to args.get didn't work as expected.
    if request.args.get("from"):
        chart_from = request.args.get("from")
    else:
        chart_from = "2000-01-01"
    if request.args.get("to"):
        chart_to = request.args.get("to")
    else:
        chart_to = date.today()
    for symbol in request.args.getlist("field"):
        dfs[symbol.strip()] = method(db.get_dataframe(symbol.strip(), config))
    return grapher.plot_to_html(dfs, chart_from=chart_from, chart_to=chart_to)


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
