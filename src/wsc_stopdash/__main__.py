"""Main entry point for executing wsc_stopdash as a module via python3 -m wsc_stopdash"""
import argparse
import logging

import wsc_stopdash

LOG_FORMAT = "%(asctime)s - %(module)s - %(levelname)s - Thread_name: %(threadName)s - %(message)s"
logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument("--port", default=5000)
parser.add_argument("--config", type=argparse.FileType("r"))

args = parser.parse_args()

wsc_stopdash.app.run(debug=True, host="0.0.0.0", port=args.port)
