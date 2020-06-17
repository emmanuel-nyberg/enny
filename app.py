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
API_VERSION = f"/api/v{config.api_version}"


@app.before_first_request
def set_timeline(request=None):
    """This guy is run when app is started. Returns the number of rows affected."""
    if request and request.args.get("hours"):
        result = db.set_starting_time(config, hours=request.args.get("hours"))
    else:
        result = db.set_starting_time(config)
    return result.rowcount


@app.route(f"{API_VERSION}/collector/collect_all")
def collect_all():
    """This will only work for all symbols if enny is hosted outside of Lambda
    as the container will kill itself before completion."""
    collector_process = Process(target=collector.main, args=())
    collector_process.start()
    return "Collecting."


@app.route(f"{API_VERSION}/collector/collect/<symbol>", methods=["GET"])
def collect(symbol):
    """Get a stock from AV."""
    return collector.collect(symbol)


@app.route(f"{API_VERSION}/conf")
def show_conf():
    """This endpoint is solely for admin purposes. Should be protected."""
    return {"conf": config}


@app.route(f"{API_VERSION}/timeline/help")
def timeline_help():
    return render_template(
        "help.html",
        text='POST will set the start of the timeline to "now", GET will get the "current time"',
    )


@app.route(f"{API_VERSION}/timeline", methods=["GET", "POST"])
def timeline():
    """POST will set the start of the timeline to "now", GET will get the "current time"."""
    if request.method == "POST":
        result = set_timeline(request=request)
        if result == 1:
            return {"msg": "Updated starting time or hours til now"}
        else:
            return {"msg": "Didn't update anything"}
    if request.method == "GET":
        return {"date": str(db.get_simulated_date(config))}


@app.route(f"{API_VERSION}/ticker/<symbol>", methods=["GET"])
def ticker(symbol,):
    """Get a dataframe as JSON. Note that datetime objects will be converted to UNIX timestamps and 
    NaN and None values will be null."""
    if len(symbol) == 0:
        abort(404)
    try:
        df = db.get_dataframe(symbol, config)
    except:
        abort(404)
    return df[pd.to_datetime(db.get_simulated_date(config)) :: -1].to_json()


@app.route(f"{API_VERSION}/ticker/<symbol>/today", methods=["GET"])
def today(symbol,):
    """Get a dataframe as JSON. Note that datetime objects will be converted to UNIX timestamps and 
    NaN and None values will be null."""
    if len(symbol) == 0:
        abort(404)
    try:
        df = db.get_single_day(symbol, db.get_simulated_date(config), config)
    except:
        abort(404)
    return df.to_json()


@app.route(f"{API_VERSION}/analysis/<method>/<symbol>")
def analyze(method, symbol):
    """Transform time series in some manner. If no chart_to argument is provided, simulated "now" will be used."""
    # For some reason, providing a default value to args.get didn't work as expected. Kakaself.
    if request.args.get("from"):
        chart_from = pd.to_datetime(request.args.get("from"))
    else:
        chart_from = pd.to_datetime(date(2000, 1, 1))
    if request.args.get("to"):
        chart_to = pd.to_datetime(request.args.get("to"))
    else:
        chart_to = pd.to_datetime(db.get_simulated_date(config))
    return method(db.get_dataframe(symbol.strip(), config))[
        chart_from:chart_to:-1
    ].to_json()


@app.route(f"{API_VERSION}/graph/")
def graph():
    """This method will return a graph as HTML. It takes all input from the Flask request object."""
    dfs = {}
    method = getattr(meth, request.args.get("method"))
    # For some reason, providing a default value to args.get didn't work as expected.
    for symbol in request.args.getlist("field"):
        dfs[symbol.strip()] = analyze(method, symbol.strip())
    return grapher.plot_to_html(dfs)


@app.route("/health")
def health_check():
    """Return a 200 OK."""
    return "OK"


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
