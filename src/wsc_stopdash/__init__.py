"""WSC Control Stop Dashboard is a flask app displays a dashboard for control stops."""

import logging
import os

from flask import Flask
from flask_caching import Cache
from flask_cors import CORS
import mergedeep
from werkzeug.middleware.proxy_fix import ProxyFix
import yaml

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
# Gather config
###########################

config_defaults = {
    "cars": {},
    "controlstops": {},
    "target": {
        "database": None,
        "host": None,
        "measurement": "telemetry",
        "token": os.environ.get("INFLUX_TOKEN", None),
        "org": None,
    },
}

app.config["WSC_CONFIG_FILE_PATH"] = os.environ.get("WSC_CONFIG_FILE_PATH", "config.yaml")
with open(app.config["WSC_CONFIG_FILE_PATH"], encoding="utf-8") as f:
    app.config["WSC_CONFIG"] = mergedeep.merge(config_defaults, yaml.safe_load(f))

import wsc_stopdash.stopdash  # pylint: disable=wrong-import-position

if __name__ == "__main__":
    LOG_FORMAT = "%(asctime)s - %(module)s - %(levelname)s - Thread_name: %(threadName)s - %(message)s"
    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)

    app.run(debug=True, host="0.0.0.0", port=5000)
