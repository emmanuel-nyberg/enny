from collections import namedtuple
import os

ALPHA_VANTAGE_API_URL = "https://www.alphavantage.co/query?"
DATEFORMAT = "%Y-%m-%d"
TIMEFORMAT = "%H:%M:%S"


def parse_env():
    """Parse config. Retuns a Config NamedTuple."""
    Config = namedtuple(
        "Config",
        [
            "url",
            "dateformat",
            "timeformat",
            "ts_key",
            "symbols",
            "apikey",
            "db_user",
            "db_password",
            "db_host",
            "db_port",
            "db_name",
        ],
    )
    config = Config(
        os.getenv("ENNY_API_URL", ALPHA_VANTAGE_API_URL),
        os.getenv("ENNY_DATEFORMAT", DATEFORMAT),
        os.getenv("ENNY_TIMEFORMAT", TIMEFORMAT),
        "Time Series (60min)" if os.getenv("ENNY_HOURLY") else "Time Series (Daily)",
        os.getenv("ENNY_SYMBOLFILE", "./NDX"),
        os.getenv("ENNY_APIKEY"),
        os.getenv("ENNY_DB_USER", "enny"),
        os.getenv("ENNY_DB_PASSWORD"),
        os.getenv("ENNY_DB_HOST"),
        os.getenv("ENNY_DB_PORT", 3306),
        os.getenv("ENNY_DB_NAME", "enny"),
    )
    return config
