"""WSC Earth is a flask app which renders a map of the current car positions."""

import logging
import os

from flask import Flask
from flask_caching import Cache
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
import flask_googlemaps

config = {
    "DEBUG": True,  # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300,
}
app = Flask(__name__)

app.config.from_mapping(config)
app.wsgi_app = ProxyFix(app.wsgi_app, x_prefix=1)
cache = Cache(app)
cors = CORS(app)

###########################
# Gather influx parameters.
###########################

app.config["INFLUX_URL"] = os.environ.get("INFLUX_URL", "https://us-east-1-1.aws.cloud2.influxdata.com")
app.config["INFLUX_ORG"] = os.environ.get("INFLUX_ORG", "Bridgestone World Solar Challenge")
app.config["INFLUX_TOKEN"] = os.environ.get("INFLUX_TOKEN", None)

app.config["INFLUX_BUCKET"] = os.environ.get("INFLUX_BUCKET", "test")

app.config["INFLUX_MEASUREMENT"] = os.environ.get("INFLUX_MEASUREMENT", "telemetry")

app.config["EXTERNAL_ONLY"] = bool(os.environ.get("EXTERNAL_ONLY", "True").lower() == "true")


if not app.config["INFLUX_TOKEN"]:
    raise ValueError("No InfluxDB token set using INFLUX_TOKEN environment variable")

###########################
# Set up Google Maps.
###########################
# Get the Gogole Maps API key
app.config["GOOGLEMAPS_KEY"] = os.environ.get("GOOGLEMAPS_KEY", None)
print(f"Got GoogleMaps Key: {os.environ.get('GOOGLEMAPS_KEY', None)}")

# See https://github.com/flask-extensions/Flask-GoogleMaps
# for details of the flask googlemaps extension.
flask_googlemaps.GoogleMaps(app)

import wscearth.views  # pylint: disable=wrong-import-position
import wscearth.earth  # pylint: disable=wrong-import-position
import wscearth.route  # pylint: disable=wrong-import-position

if __name__ == "__main__":
    LOG_FORMAT = "%(asctime)s - %(module)s - %(levelname)s - Thread_name: %(threadName)s - %(message)s"
    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
    app.run(debug=True, host="0.0.0.0", port=5000)
