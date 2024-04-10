from queue import Queue
from threading import Thread, Event, Lock
import time
import os
import multiprocessing
from collections import defaultdict
import json

class Task:
    def __init__(self, task_id, status, question, url, data_value):
        """
        Implements the new task that will be added to the task queue.
        """
        self.task_id = task_id
        self.status = status
        self.question = question
        self.url = url
        self.data_value = data_value

class ThreadPool:
    def __init__(self):
        self.tsk_queue = Queue()
        self.thr_list = []
        self.jobs = {}
        self.shutdown_flag = Event()

        self.num_threads_env = os.getenv('TP_NUM_OF_THREADS')
        if not self.num_threads_env:
            self.num_threads_env = multiprocessing.cpu_count()

    def submit_task(self, task):
        """ 
        Enqueue the task into the task queue
        """
        if not self.shutdown_flag.is_set():
            self.tsk_queue.put(task)
            self.jobs[task.task_id] = task.status

    def start(self):
        """
        Starts multiple threads based on the specified number of threads in the environment.
        """
        for _ in range(self.num_threads_env):
            thread = TaskRunner(self.tsk_queue, self.jobs, self.shutdown_flag)
            thread.start()
            self.thr_list.append(thread)

class TaskRunner(Thread):
    def __init__(self, tsk_queue, jobs, shutdown_flag):
        Thread.__init__(self)
        self.tsk_queue = tsk_queue
        self.jobs = jobs
        self.shutdown_flag = shutdown_flag

    def run(self):
        while True:
            if self.shutdown_flag.is_set() and self.tsk_queue.qsize() == 0:
                break
            if self.tsk_queue.qsize() != 0:
                task = self.tsk_queue.get()
                # Execute the task
                self.execute_task(task)

    def execute_task(self, task):
        """
            Function used for testing each of the requests
        """
        if task.url == '/api/global_mean':
            self.calculate_global_mean(task)
        elif task.url == '/api/worst5':
            self.calculate_worst5(task)
        elif task.url == '/api/best5':
            self.calculate_best5(task)
        elif task.url == '/api/diff_from_mean':
            self.calculate_diff_from_mean(task)
        elif task.url == '/api/state_diff_from_mean':
            self.calculate_state_diff_from_mean(task)
        elif task.url == '/api/mean_by_category':
            self.calculate_mean_by_category(task)
        elif task.url == '/api/state_mean':
            self.calculate_state_mean(task)
        elif task.url == '/api/states_mean':
            self.calculate_states_mean(task)
        elif task.url == '/api/state_mean_by_category':
            self.calculate_state_mean_by_category(task)

    def write_in_file(self, data, task_id):
        """
        Function used for writing in the ./results/job_id_{task_id}.json so that we don't
        rewrite the same 3 lines
        """
        with open(f"./results/job_id_{task_id}.json", 'w') as file:
            json.dump(data, file)
        self.jobs[task_id] = "done"

    def calculate_global_mean(self, task):
        """ 
        Function used for the global_mean request that calculates the global mean based on the data
        The function iterates through the data values in the provided task, accumulating
        the sum and count of values associated with the specified question.
        If the task's URL is '/api/global_mean', the mean is written into a file along
        with a status indication; otherwise, the calculated global mean is returned (used for 
        calculate_diff_from_mean and calculate_state_diff_from_mean functions)
        """
        val = task.data_value
        s = 0
        count = 0
        for line in val:
            if line['Question'] == task.question['question']:
                s += float(line['Data_Value'])
                count += 1

        if task.url == '/api/global_mean':
            # Write result in the designed file
            self.write_in_file({'status': 'done', 'data': {"global_mean": s / count}},
                task.task_id)
        else:
            return s / count

    def calculate_worst5(self, task):
        """
        Function used for the worst_5 request that calculates the worst 5 states based on the data.
        Function accumulates data for each state, calculates the average value, sorts the states 
        based on the averages, and then selects the worst 5 states. The result is stored in the 
        task's file with a status indication.
        If the question is in the questions_best_is_max than the final dict is going to be reversed
        """
        val = task.data_value.data
        finished_data = {}

        # Accumulate data for each state
        for line in val:
            if line['Question'] == task.question:
                state = line['LocationDesc']
                data_val = float(line['Data_Value'])
                if state not in finished_data:
                    finished_data[state] = {'total_value': data_val, 'count': 1}
                else:
                    finished_data[state]['total_value'] += data_val
                    finished_data[state]['count'] += 1

        # Calculate the average for each state
        for state, data in finished_data.items():
            finished_data[state] = data['total_value'] / data['count']

        # Sort states based on average values
        if task.question in task.data_value.questions_best_is_max:
            sorted_avg = dict(sorted(finished_data.items(), key=lambda x: x[1]))
        else:
            sorted_avg = dict(sorted(finished_data.items(), key=lambda x: x[1], reverse=True))

        # Get the worst 5 states
        worst5 = dict(list(sorted_avg.items())[:5])

        # Write result in the designed file
        self.write_in_file ({'status': 'done', 'data': worst5}, task.task_id)

    def calculate_best5(self, task):
        """
        Function used for the best_5 request that calculates the best 5 states based on the data.
        Function accumulates data for each state, calculates the average value, sorts the states 
        based on the averages, and then selects the best 5 states. The result is stored in the 
        task's file with a status indication.
        If the question is in the questions_best_is_min than the final dict is going to be reversed
        """
        val = task.data_value.data
        finished_data = {}

        # Accumulate data for each state
        for line in val:
            if line['Question'] == task.question:
                state = line['LocationDesc']
                data_val = float(line['Data_Value'])
                if state not in finished_data:
                    finished_data[state] = {'total_value': data_val, 'count': 1}
                else:
                    finished_data[state]['total_value'] += data_val
                    finished_data[state]['count'] += 1

        # Calculate the average for each state
        for state, data in finished_data.items():
            finished_data[state] = data['total_value'] / data['count']

        # Sort states based on average values
        if task.question in task.data_value.questions_best_is_min:
            sorted_avg = dict(sorted(finished_data.items(), key=lambda x: x[1]))
        else:
            sorted_avg = dict(sorted(finished_data.items(), key=lambda x: x[1], reverse=True))

        # Get the best 5 states
        best5 = dict(list(sorted_avg.items())[:5])

        # Write result in the designed file
        self.write_in_file ({'status': 'done', 'data': best5}, task.task_id)

    def calculate_states_mean(self, task):
        """
        Function used for the states_mean request that calculates the mean for all the states
        based on the data.
        This function accumulates data for each state based on the provided task's data,
        calculates the mean value for each state. If the task's URL is '/api/states_mean', the
        result is stored in a file with a status indication, otherwise the sorted dict is returned
        (used for the calculate_diff_from_mean function.
        """
        val = task.data_value.data
        finished_data = {}
        # Accumulate data for each state
        for line in val:
            if line['Question'] == task.question['question']:
                state = line['LocationDesc']
                data_val = float(line['Data_Value'])
                if state not in finished_data:
                    finished_data[state] = {'total_value': data_val, 'count': 1}
                else:
                    finished_data[state]['total_value'] += data_val
                    finished_data[state]['count'] += 1

        for state, data in finished_data.items():
            finished_data[state] = data['total_value'] / data['count']

        # Sort states based on average values
        sorted_avg = dict(sorted(finished_data.items(), key=lambda x: x[1]))

        if task.url == '/api/states_mean':
            # Write result in the designed file
            self.write_in_file({'status': 'done', 'data': sorted_avg}, task.task_id)

        return sorted_avg

    def calculate_state_mean(self, task):
        """
        Function used for the state_mean request that calculates the mean value
        for a specific state based on the provided task data.
        The function iterates through the data values, accumulating the sum and count
        of values associated with the specified state and question. If the task's
        URL is '/api/state_mean', the mean is stored in a file with a status indication.
        Otherwise, the calculated mean value for the state is returned (used for 
        calculate_state_diff_from_mean function).
        """
        val = task.data_value
        state = task.question['state']
        s = 0
        count = 0

        for line in val:
            if line['Question'] == task.question['question'] and line['LocationDesc'] == state:
                s += float(line['Data_Value'])
                count += 1

        if task.url == '/api/state_mean':
            # Write result in the designed file
            self.write_in_file({'status': 'done', 'data': {state: s / count}}, task.task_id)
        else:
            return s / count

    def calculate_diff_from_mean(self, task):
        """
        Function used for the diff_from_mean request that calculates the difference 
        between the global mean for each state based on the provided task data.
        The function calculates the mean values for each state using the `calculate_states_mean` 
        method. Then, it calculates the global mean using the `calculate_global_mean` method. 
        Next, it subtracts the state mean from the global mean for each state to obtain the 
        difference. The results are sorted in descending order based on the difference and 
        written to a file with a status indication.
        """
        # Calculate states mean
        data = self.calculate_states_mean(task)

        # Calculate global mean
        task.data_value = task.data_value.data
        glb_mean = self.calculate_global_mean(task)

        # Calculate difference from global mean for each state
        for state in data:
            data[state] = glb_mean - data[state]
        sorted_avg = dict(sorted(data.items(), key=lambda x: x[1], reverse=True))

        # Write result in the designed file
        self.write_in_file({'status': 'done', 'data': sorted_avg}, task.task_id)

    def calculate_state_diff_from_mean(self, task):
        """
        Function used for the state_diff_from_mean request that calculates the difference from 
        the global mean for a specific state based on the provided task data.
        The function calculates the global mean using the `calculate_global_mean` method and
        the mean value for the specified state using the `calculate_state_mean` method. Then, it
        obtains the difference from the two values. The result is written in the designed file.
        """
        state = task.question['state']
        glb_mean = self.calculate_global_mean(task)
        st_mean = self.calculate_state_mean(task)
        avg = glb_mean - st_mean
        # Write result in the designed file
        self.write_in_file({'status': 'done', 'data': {state: avg}}, task.task_id)

    def calculate_mean_by_category(self, task):
        """
        Function used for the mean_by_category request that calculates the mean values for each
        category within states based on the provided task data.
        This function accumulates data for each state and category, calculates the mean value for
        each category, and returns a dictionary containing tuples of state, category, and
        subcategory mapped to their respective mean values. The results are sorted by state in
        ascending order and by average in descending order. The results are stored in the designed
        file.
        """
        val = task.data_value
        finished_data = {}
        # Accumulate data for each state
        for line in val:
            if line['Question'] == task.question:
                state = line['LocationDesc']
                category = line['StratificationCategory1']
                subcat = line['Stratification1']
                if category and subcat:
                    key_val = f"('{state}', '{category}', '{subcat}')"
                    data_val = float(line['Data_Value'])
                    if key_val not in finished_data:
                        finished_data[key_val] = {'total_value': data_val, 'count': 1}
                    else:
                        finished_data[key_val]['total_value'] += data_val
                        finished_data[key_val]['count'] += 1

        # Calculate average for each category
        for key_val, data in finished_data.items():
            finished_data[key_val] = data['total_value'] / data['count']
        # Create a dictionary sorted by state in ascending order and average in descending order
        sorted_avg =  dict(sorted(finished_data.items(), key=lambda x: (x[0], -x[1])))
        # Write result in the designed file
        self.write_in_file({'status': 'done', 'data': sorted_avg}, task.task_id)

    def calculate_state_mean_by_category(self, task):
        """
        Function used for the state_mean_by_category request that calculates the mean values
        for each category within a specific state based on the provided task data.
        This extracts the state from the task, then iterates through the data values, 
        accumulating the sum and count of values associated with each category within the
        specified state. The mean value for each category is calculated, and the results are 
        stored in a dictionary with the state as the key and a dictionary of category-subcategory
        pairs mapped to their respective mean values as the value. The results are then sorted
        by category in ascending order and by average in descending order. The results are stored
        in the designed file.
        """
        state = task.question['state']
        val = task.data_value
        finished_data = {}

        # Accumulate data for each state
        for line in val:
            if line['Question'] == task.question['question'] and line['LocationDesc'] == state:
                category = line['StratificationCategory1']
                subcat = line['Stratification1']
                key_val = f"('{category}', '{subcat}')"
                data_val = float(line['Data_Value'])
                if key_val not in finished_data:
                    finished_data[key_val] = {'total_value': data_val, 'count': 1}
                else:
                    finished_data[key_val]['total_value'] += data_val
                    finished_data[key_val]['count'] += 1

        # Calculate average for each category
        for key_val, data in finished_data.items():
            finished_data[key_val] = data['total_value'] / data['count']
        sorted_avg = dict(sorted(finished_data.items(), key=lambda x: (x[0], -x[1])))
        # Write result in the designed file
        self.write_in_file({'status': 'done', 'data': {state: sorted_avg}}, task.task_id)
