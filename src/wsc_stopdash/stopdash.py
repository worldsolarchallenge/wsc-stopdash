# pylint: disable=duplicate-code
"""Basic app endpoints for wsc_stopdash"""

import logging
import math

import flask
import flask_cachecontrol
from influxdb_client_3 import InfluxDBClient3
import pandas as pd

# Circular import recommended here: https://flask.palletsprojects.com/en/3.0.x/patterns/packages/
from wsc_stopdash import app, cache  # pylint: disable=cyclic-import

logger = logging.getLogger(__name__)

config = app.config["WSC_CONFIG"]
client = InfluxDBClient3(
    host=config["target"]["host"],
    token=config["target"]["token"],
    org=config["target"]["org"],
    database=config["target"]["database"],
)


def get_timing_sheet():
    """Query Influx to get the timing sheet data."""
    query = """\
SELECT *
FROM "timingsheet"
WHERE
time >= -30d"""
    table = client.query(query=query, database=config["target"]["database"], language="influxql")
    df = table.to_pandas().sort_values(by="time")

    return df

def get_positions(measurement="telemetry", external_only=True):
    """Get the most recent position information from each car."""

    query = f"""\
SELECT LAST(latitude),latitude,longitude,*
FROM "{measurement}"
WHERE
class <> 'Other' AND
{"class <> 'Official Vehicles' AND " if external_only else ""}
time >= now() - 1d
GROUP BY shortname"""  # pylint: disable=duplicate-code

    table = client.query(query=query, language="influxql")

    # Convert to dataframe
    df = (table.to_pandas()
        .sort_values(by="time")
    )

    return df

def get_competing(external_only=True):
    """Get the competing table"""
    competing_query = f"""\
SELECT MIN(Competing)
FROM "timingsheet"
WHERE
class <> 'Other' AND
{"class <> 'Official Vehicles' AND " if external_only else ""}
time >= now() - 7d
GROUP BY shortname"""  # pylint: disable=duplicate-code
    competing_table = client.query(query=competing_query, language="influxql")

    # Convert to dataframe
    competing_df = pd.DataFrame()
    if len(competing_table) > 0:
        competing_df = (
            competing_table.to_pandas()
            .reset_index()
            .rename(columns={"min": "competing"})
            [["shortname","competing"]]
        )
        return competing_df

    return pd.DataFrame()


@app.route("/")
@flask_cachecontrol.cache_for(seconds=30)
def index():
    """An index document which serves as a reference."""
    return flask.render_template("index.html.j2", stops=config["controlstops"])

@app.route("/stops.html")
@flask_cachecontrol.cache_for(seconds=30)
def stops_index():
    """An index document which serves as a reference."""
    return flask.render_template("stops.html.j2", stops=config["controlstops"])

@app.route("/favicon.ico")
@cache.cached(timeout=10)
@flask_cachecontrol.cache_for(seconds=30)
def favicon():
    """Serve the favicon."""
    return flask.send_from_directory("static", "favicon.ico")

@app.route("/<stopname>/")
@cache.cached(timeout=10)
@flask_cachecontrol.cache_for(seconds=30)
def stopdash(stopname):
    """Render the control stop template"""

    timing_sheet = get_timing_sheet().sort_values(by=["control_stop.number"])
    positions = get_positions()
    competing = get_competing()

    timing_sheet["competing"] = False

    df = timing_sheet

    if not competing.empty:
        df = (df
            .drop(columns=["competing"])
            .merge(competing, on="shortname", how="left", suffixes=("_original",None))
        )
    else:
        logger.warning("No competing data found.")

    if not positions.empty:
        df = (df
            .merge(positions, on="shortname", how="left", suffixes=(None,"_positions"))
        )
    else:
        logger.warning("No positions data found.")

    print(df)

    print(config["controlstops"])
    stop = config["controlstops"][stopname]

    print(timing_sheet[["team", "control_stop.name"]])

    def _calculate_eta(row):
        if "speed" not in row or "distance" not in row:
            logger.warning("Row missing 'speed' or 'distance': %s", row)
            return "N/A"

        speed = row["speed"]
        if math.isnan(speed):
            return "N/A"
        if speed < 20.0:
            return "N/A"

        hours = (stop["km"] - row["distance"]) / speed

        print(f"{row['distance']=}")
        print(f"{row['speed']=}")
        print(hours)

        if hours < 0:
            return "now"
        if hours < 1.0:
            minutes = hours * 60.0
            return f"{round(minutes)} min"

        # FIXME: If the time is going beyond the EOD indicate "tomorrow", etc. # pylint: disable=fixme
        return f"{hours:.1f} hours"

    df["eta"] = df.apply(_calculate_eta, axis=1, result_type="reduce")

    print(df)
    print(df.columns)
    # Grab everything that has passed the previous control point
    entries = (
        df[
            (df["control_stop.number"] >= stop["number"] - 1)
            & (df["control_stop.number"] < stop["number"] + 1)
        ]
        .sort_values(by=["time"])
        .drop_duplicates(subset=["teamnum"], keep="last")
        .round({"distance": 0})
    ).sort_values(by=["competing", "control_stop.number", "time", "distance"], ascending=[False, False, True, False])

    #    print(f"Stop number: {stop['number']}")

    #    import pprint
    #    pprint.pprint(entries)

    #    for entry in timing_sheet.sort_values(by=:"time"):

    return flask.render_template("stopdash.html.j2", pd=pd, controlstop=stop, entries=entries)
