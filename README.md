# HOMEWORK 1 ASC - # Le Stats Sportif

Vaideanu Renata - Georgia - 332 CD
Server for Request Handling
The aim of this project is to effectively apply synchronization elements to develop a concurrent client-server application in Python. The primary aim is to establish a Python server capable of handling requests derived from a dataset in CSV format, delivering statistical insights derived from the CSV data.

## Files
api_server.py
app/
    app/routes.py
    app/task_runner.py
    app/data_ingestor.py
    app/\_\_init\_\_.py
    README
    unittests/
    unittests/TestWebserver.py
    git-log


## ./app/task_runner.py contains:

- **Task class**: represents an individual task that can be submitted to a task queue for processing. It encapsulates all the necessary information required to execute the task effectively. I added a variable is_unittesting for the unittest case, that field is unused in any other case, being replaced with False
- **ThreadPool class**: manages a pool of threads for executing tasks concurrently.
->\_\_init\_\_: initializes several attributes
  - tsk_queue: A queue to hold tasks waiting to be processed;
  - thr_list: A list to keep track of the threads created for task execution;
  - jobs: A dictionary to maintain the status of each task.
  - shutdown_flag: A flag to indicate whether the thread pool is being shut down.

  -> *submit_task*: adds the new task to the task queue and updates the jobs dictionary to track the status of the submitted task.
  -> *start*: starts multiple threads based on the specified number of threads in the          environment. Each thread is an instance of the TaskRunner class, which is responsible for fetching tasks from the queue and executing them.
  -> *graceful_shutdown*: signals all TaskRunner threads to gracefully shut down. It iterates through the list of threads and invokes a shutdown method on each thread. Then, it waits for all threads to finish their execution by calling the join method on each thread.
 
- **TaskRunner class**: manages the tasks that would be used in the process 
    (In the code there is a docscript for each and every one of the request functions)
 ->\_\_init\_\_: initializes several attributes
  - tsk_queue: A queue to hold tasks waiting to be processed;
  - jobs - A dictionary for the tasks' statuses, running if it's execusion is not done yet or done if it's finished
  - shutdown_flag: the flag for shutdown that is used for the /api/graceful_shutdown  calling

  -> run:  function that runs through all the tasks and executes them 
  -> execute_task: function that goes through all the urls and based on that, tests the allocated test
  -> write_in_file: function designed to append data to the file located at `./results/job_id_{task_id}.json`. Additionally, it logs the output in the logger file to maintain a record of the operation.
  -> calculate_{request}: the 9 functions for each request:

	>-  `/api/global_mean`: calculates the global mean based on a specified question
	>-  `/api/worst5`: retrieves the worst5 states (sorted by mean) based on a specified question
	>-  `/api/best5`: retrieves the best 5 states (sorted by mean) based on a specified question
	>-  `/api/state_mean`: calculates the mean value for a specific state
	>- ` /api/states_mean`: calculates the mean for all the states
	>-  `/api/diff_from_mean`:calculates the difference between the global mean for each state
	>-  `/api/state_diff_from_mean`: calculates the difference from the global mean for a specific state
	>- `/api/state_mean_by_category`: calculates the mean values for each category within a specific state
   >-  `/api/mean_by_category`: calculates the mean values for each category within states

## ./app/routes.py contains:

- **get_response**: The endpoint `/api/get_results/<job_id>` retrieves the result of a previously submitted job identified by `job_id`. It checks if the job ID is valid and if the job is done, it returns the result stored in a JSON file corresponding to the job ID.
    
- **handle_request**: The function `handle_request()` is a common utility function used to handle requests for various endpoints. It increments the global job counter, logs the request details, creates a new task for the registered job, and returns the associated job ID.
    
- **Post {request}_request**: The 9 route definitions provided for different statistical analysis requests such as calculating means, finding top/bottom entries, etc. Each route invokes the `handle_request()` function with the corresponding endpoint.
    
- **shutdown_request**: The `/api/graceful_shutdown` endpoint initiates a graceful shutdown of the server by invoking the `graceful_shutdown()` method of the task runner.

## Logging
I created a "webserver.log" file to track inputs and outputs of the routes. The file uses a RotatingFileHandler to manage size and keep historical copies. The provided code sets up a RotatingFileHandler named file_handler, appending logs to "webserver.log", limiting file size, retaining historical copies, and using UTF-8 encoding. The log formatter includes log level, timestamp, and message. Finally, the file handler's log level is set to INFO, and is added to the logger.

## Unittesting

`./unittests/TestWebserver.py` contains unit tests for a web server application. It imports the necessary modules and sets up test cases for various server functionalities. Each test method simulates a specific request to the server and compares the actual output with expected results using the DeepDiff library. The setUp method initializes common test parameters, and each test method performs a specific test case.
