import os
from datetime import date
from flask import Flask, render_template, request, abort
import db_operations as db
import visualizer as grapher

app = Flask(__name__)


@app.route("/api/v1.0/ticker/<symbol>", methods=["GET"])
def ticker(symbol):
    """Get a dataframe as JSON"""
    if len(symbol) == 0:
        abort(404)
    try:
        df = db.get_dataframe(symbol)
    except:
        abort(404)
    return df.to_json()


@app.route("/api/v1.0/graph/")
def graph():
    """This method will return a graph as HTML. It takes all input from the Flask request object."""
    dfs = {}
    if request.args.get("from"):
        chart_from = request.args.get("from")
    else:
        chart_from = "2000-01-01"
    if request.args.get("to"):
        chart_to = request.args.get("to")
    else:
        chart_to = date.today()
    for symbol in request.args.getlist("field"):
        dfs[symbol.strip()] = db.get_dataframe(symbol.strip())
    return grapher.plot_to_html(dfs, chart_from=chart_from, chart_to=chart_to)


@app.route("/")
def root():
    """Render the index.html template and show the results."""
    return render_template(
        "index.html",
        data={"title": "Which stocks would you like to graph?", "fields": symbols,},
    )


if __name__ == "__main__":
    """Supply data to the rest of the app. Configured through env variables."""
    with open(os.getenv("ENNY_SYMBOLFILE", "./NDX"), "r") as f:
        symbols = f.readlines()
    app.run()
