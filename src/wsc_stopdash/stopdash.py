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
@cache.cached(timeout=1)
@flask_cachecontrol.cache_for(seconds=30)
def stopdash(stopname):
    """Render the control stop template"""

    config = app.config["WSC_CONFIG"]
    timing_sheet = get_timing_sheet().sort_values(by=["control_stop.number"])

    print(config["controlstops"])
    stop = config["controlstops"][stopname]

    before = {}
    after = {}

    print( timing_sheet[ ["team", "control_stop.name" ]] )

    # Grab everything that has passed the previous control point
    entries = (timing_sheet
                [(timing_sheet["control_stop.number"] >= stop["number"] - 1) &
                 (timing_sheet["control_stop.number"] < stop["number"] + 1) &
                 (timing_sheet["trailering"] == False)]
                 .sort_values(by=["time"])
                 .drop_duplicates(subset=['teamnum'], keep='last')
                 ).sort_values(by=["control_stop.number", "time"], ascending=[False, True]
            )


#    print(f"Stop number: {stop['number']}")

#    import pprint
#    pprint.pprint(entries)

#    for entry in timing_sheet.sort_values(by=:"time"):



    return flask.render_template("stopdash.html.j2", pd=pd, controlstop=stop, entries=entries)