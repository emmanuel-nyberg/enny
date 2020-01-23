from flask import Flask, render_template, request, abort
import db_operations as db
import pandas as pd
import pdb
import visualizer as grapher
import os

app = Flask(__name__)


@app.route("/api/v1.0/ticker/<symbol>", methods=["GET"])
def ticker(symbol):
    if len(symbol) == 0:
        abort(404)
    try:
        df = db.get_dataframe(symbol)
    except:
        abort(404)
    return df.to_json()


@app.route("/api/v1.0/graph/")
def graph():
    dfs = {}
    for symbol in request.args.getlist("field"):
        dfs[symbol.strip()] = db.get_dataframe(symbol.strip())
    return grapher.plot_to_html(dfs)


@app.route("/")
def root():
    return render_template(
        "index.html",
        data={"title": "Which stocks would you like to graph?", "fields": symbols,},
    )


if __name__ == "__main__":
    with open(os.getenv("ENNY_SYMBOLFILE", "./NDX"), "r") as f:
        symbols = f.readlines()
    app.run()
