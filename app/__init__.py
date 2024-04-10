from flask import Flask
from app.data_ingestor import DataIngestor
from app.task_runner import ThreadPool, Task
import logging
import logging.handlers
import time

webserver = Flask(__name__)
webserver.tasks_runner = ThreadPool()

webserver.tasks_runner.start()

webserver.data_ingestor = DataIngestor("./nutrition_activity_obesity_usa_subset.csv")

webserver.job_counter = 0

webserver.json.sort_keys = False

persistent_logger = logging.getLogger(__name__)

formatter = logging.Formatter('%(levelname)s:%(asctime)s:%(message)s')
formatter.converter = time.gmtime

file_handler = logging.handlers.RotatingFileHandler("webserver.log",
                                                    "a",
                                                    200000,
                                                    10,
                                                    "UTF-8")
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)

persistent_logger.addHandler(file_handler)
persistent_logger.setLevel(logging.INFO)

webserver.persistent_logger = persistent_logger

from app import routes
