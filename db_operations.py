from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import pandas as pd


def get_connection_string(config):
    return "mysql+pymysql://{}:{}@{}:{}/{}".format(
        config.db_user,
        config.db_password,
        config.db_host,
        config.db_port,
        config.db_name,
    )


def get_dataframe(symbol, config):
    """This function takes a symbol as input and returns a Pandas dataframe, indexed by date."""
    connection_string = get_connection_string(config)
    try:
        con = create_engine(connection_string)
        df = pd.read_sql(f"SELECT * FROM {symbol};", con, index_col="index")
    except:
        raise
    df["date"] = pd.to_datetime(df.index)
    return df.set_index("date")


def store_data(df, symbol, instance):
    """Store the data in a SQL database. DB connection is configured through env variables.
        The columns are also renamed in this function."""
    config = instance.config
    df.rename(columns=lambda x: "".join([i for i in x if i.isalpha()]), inplace=True)
    try:
        con = create_engine(get_connection_string(config))
        if not database_exists(con.url):
            create_database(con.url)
        df.to_sql(symbol, con, if_exists="replace")
    except:
        raise
