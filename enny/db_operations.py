import datetime
from sqlalchemy import (
    create_engine,
    func,
    MetaData,
    Column,
    Table,
    DateTime,
    Integer,
    sql,
)
from sqlalchemy_utils import database_exists, create_database
import pandas as pd


def get_connection_string(config, db_name):
    """This will be used by the SQLAlchemy engine"""
    return "postgresql://{}:{}@{}:{}/{}".format(
        config.db_user, config.db_password, config.db_host, config.db_port, db_name,
    )

def get_single_day(symbol, timestamp, config):
    """Takes a symbol and a ISO 8601 date, returns a single day of trading."""
    connection_string = get_connection_string(config, config.db_name)
    try:
        con = create_engine(connection_string)
        df = pd.read_sql(f'SELECT * FROM "{symbol}" WHERE index = to_timestamp(\'{timestamp}\', \'YYYY-MM-DD\')::timestamp without time zone;', con, index_col="index")
    except:
        raise
    finally:
        con.dispose()
    df["date"] = pd.to_datetime(df.index)
    return df.set_index("date")


def get_dataframe(symbol, config):
    """This function takes a symbol as input and returns a Pandas dataframe, indexed by date."""
    connection_string = get_connection_string(config, config.db_name)
    try:
        con = create_engine(connection_string)
        df = pd.read_sql(f'SELECT * FROM "{symbol}";', con, index_col="index")
    except:
        raise
    finally:
        con.dispose()
    df["date"] = pd.to_datetime(df.index)
    return df.set_index("date")


def store_data(df, symbol, instance):
    """Store the data in a SQL database. DB connection is configured through env variables.
        The columns are also renamed in this function."""
    config = instance.config
    df.rename(columns=lambda x: "".join([i for i in x if i.isalpha()]), inplace=True)
    try:
        con = create_engine(get_connection_string(config, config.db_name))
        if not database_exists(con.url):
            create_database(con.url)
        df.to_sql(symbol, con, if_exists="replace")
    except:
        raise
    finally:
        con.dispose()


def set_starting_time(config, **kwargs):
    """Set starting time and length in hours for the simulated timeline. If hours is omitted, it will
    default to the configuration variable. If that is non-existant, it's 6."""
    engine = create_engine(get_connection_string(config, "time_machine"))
    if not database_exists(engine.url):
        create_database(engine.url)
    meta = MetaData(engine)
    time_machine = Table(
        "time_machine",
        meta,
        Column("id", Integer, primary_key=True),
        Column("starting_time", DateTime),
        Column("hours_to_go", Integer),
    )
    if not engine.dialect.has_table(engine, "time_machine"):
        meta.create_all()
        operation = time_machine.insert().values(
            starting_time=func.current_timestamp(),
            hours_to_go=kwargs.get("hours", config.hours),
        )
    else:
        operation = (
            time_machine.update()
            .where(time_machine.c.id == 1)
            .values(
                starting_time=func.current_timestamp(),
                hours_to_go=kwargs.get("hours", config.hours),
            )
        )

    with engine.connect() as con:
        return con.execute(operation)


def get_starting_time(config):
    """Get starting time and length of the simulated timeline. Returns a tuple of a date and an integer.
    Starting time is always at ID 1."""
    engine = create_engine(get_connection_string(config, "time_machine"))
    with engine.connect() as con:
        query = sql.text(
            "SELECT starting_time, hours_to_go FROM time_machine WHERE id=1"
        )
        result = con.execute(query)
    return result.first()


def get_simulated_date(config):
    """Returns a datetime object."""
    starting_time, hours = get_starting_time(config)
    days_per_minute = (
        (starting_time.date() - datetime.date(2001, 1, 1)) / (hours * 60)
    ).days
    delta = (datetime.datetime.now() - starting_time).seconds / 60
    timedelta = datetime.timedelta(days=(delta * days_per_minute))
    return datetime.date(2001, 1, 1) + timedelta
