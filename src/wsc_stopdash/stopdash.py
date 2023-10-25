# pylint: disable=duplicate-code
"""Basic app endpoints for wsc_stopdash"""

import logging

import flask
import flask_cachecontrol
from influxdb_client_3 import InfluxDBClient3
import pandas as pd

# Circular import recommended here: https://flask.palletsprojects.com/en/3.0.x/patterns/packages/
from wsc_stopdash import app, cache  # pylint: disable=cyclic-import

logger = logging.getLogger(__name__)

config=app.config["WSC_CONFIG"]
client = InfluxDBClient3(
    host=config["target"]["host"],
    token=config["target"]["token"],
    org=config["target"]["org"],
    database=config["target"]["database"],
)


def get_timing_sheet():
    query = f"""\
SELECT *
FROM "timingsheet"
WHERE
time >= -30d"""
    table = client.query(query=query, database=config["target"]["database"], language="influxql")
    df = table.to_pandas().sort_values(by="time")

    return df

@app.route("/")
def index():
    return "Hello, World!"

@app.route("/<stopname>/")
@cache.cached(timeout=30)
@flask_cachecontrol.cache_for(seconds=30)
def stopdash(stopname):
    """Render the control stop template"""

    timing_sheet = get_timing_sheet()




    return flask.render_template("stopdash.html.j2")