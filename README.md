# Bot for great financial gain.

![](https://melmagazine.com/wp-content/uploads/2019/07/Screen-Shot-2019-07-31-at-5.47.12-PM.png)


# Running enny

After cloning this project, get yourself a free API key from [Alpha Vantage](https://www.alphavantage.co/) and save it somewhere.

Then get [pipenv](https://github.com/pypa/pipenv) through your most preferred method. Build your virtualenv and run a shell in it:

    pipenv install
    pipenv shell

Then run the collector.py program in order to build a local database. You need to provide the API key as the environment variable ENNY_APIKEY.

```ENNY_APIKEY=$(cat apikey) python collector.py ```

This will take a while so make some coffee and watch Chinese Cooking Demystified on Youtube.

After your test DB has been built, run an instance of the Flask app on [localhost](http://localhost:5000).

