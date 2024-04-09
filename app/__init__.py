from flask import Flask
from app.data_ingestor import DataIngestor
from app.task_runner import ThreadPool, Task

webserver = Flask(__name__)
webserver.tasks_runner = ThreadPool()

webserver.tasks_runner.start()

webserver.data_ingestor = DataIngestor("./nutrition_activity_obesity_usa_subset.csv")

webserver.job_counter = 0

webserver.json.sort_keys = False

from app import routes