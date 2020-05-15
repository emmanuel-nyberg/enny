# Bot for great financial gain.

![](https://melmagazine.com/wp-content/uploads/2019/07/Screen-Shot-2019-07-31-at-5.47.12-PM.png)


# Running enny

After cloning this project, get yourself a free API key from [Alpha Vantage](https://www.alphavantage.co/) and save it somewhere.

Open the repository in VSCode, which should auto-detect that there is a .devcontainer directory in the git. Choose "Open repository in container"
when prompted. Your environment should be created, [pipenv](https://github.com/pypa/pipenv) should be installed and the project requirements installed.

In order to run enny, you need to export the variable `ENNY_APIKEY` with your Alpha Vantage API key. Then run `python app.py` to start the app. It should
be reachable at `localhost:5000`. To seed the database with fresh stonks, point curl or your browser at `http://localhost:5000/api/v1.0/collector/collect_stocks`
and wait.
