import logging
import logging.handlers
import time
import os
from flask import Flask
from app.data_ingestor import DataIngestor
from app.task_runner import ThreadPool

# Check if "results" directory exists, create it if not
if not os.path.exists("./results"):
    os.makedirs("./results")

logger = logging.getLogger(__name__)

if not os.path.exists("./logger"):
    os.makedirs("./logger")
else:
    os.system("rm -rf ./logger/*")

file_handler = logging.handlers.RotatingFileHandler(
    "./logger/webserver.log",
    mode = "a",
    maxBytes = 200000,
    backupCount = 5,
    encoding = "UTF-8")

formatter = logging.Formatter('%(levelname)s:%(asctime)s:%(message)s')

formatter.converter = time.gmtime
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)

logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

webserver = Flask(__name__)

webserver.logger = logger

webserver.tasks_runner = ThreadPool(webserver)

webserver.tasks_runner.start()

webserver.data_ingestor = DataIngestor("./nutrition_activity_obesity_usa_subset.csv")

webserver.job_counter = 0

webserver.json.sort_keys = False

from app import routes
