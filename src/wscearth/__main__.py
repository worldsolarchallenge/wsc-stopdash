"""Main entry point for executing wscearth as a module via python3 -m wscearth"""
import argparse
import logging

import wscearth

LOG_FORMAT = "%(asctime)s - %(module)s - %(levelname)s - Thread_name: %(threadName)s - %(message)s"
logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument("--port", default=5000)
args = parser.parse_args()

wscearth.app.run(debug=True, host="0.0.0.0", port=args.port)
