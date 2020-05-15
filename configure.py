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
            "api_version",
            "hours",
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
        os.getenv("ENNY_API_VERSION", "1.0"),
        os.getenv("ENNY_HOURS", 6),
        os.getenv("ENNY_DB_USER", "postgres"),
        os.getenv("ENNY_DB_PASSWORD", "LocalPassword"),
        os.getenv("ENNY_DB_HOST", "db"),
        os.getenv("ENNY_DB_PORT", 5432),
        os.getenv("ENNY_DB_NAME", "enny"),
    )
    return config
