from queue import Queue
from threading import Thread, Event, Semaphore
import time
import os
import multiprocessing
from collections import defaultdict

class Task:
    def __init__(self, task_id, status, question, url, data_value):
        self.task_id = task_id
        self.status = status
        self.question = question
        self.url = url
        self.data_value = data_value

class ThreadPool:
    def __init__(self):
        # You must implement a ThreadPool of TaskRunners
        # Your ThreadPool should check if an environment variable TP_NUM_OF_THREADS is defined
        # If the env var is defined, that is the number of threads to be used by the thread pool
        # Otherwise, you are to use what the hardware concurrency allows
        # You are free to write your implementation as you see fit, but
        # You must NOT:
        #   * create more threads than the hardware concurrency allows
        #   * recreate threads for each task
        self.tsk_queue = Queue()
        self.thr_list = []
        self.jobs = {}

        self.num_threads_env = os.getenv('TP_NUM_OF_THREADS')
        if not self.num_threads_env:
            self.num_threads_env = multiprocessing.cpu_count()

        self.semaphore = Semaphore(self.num_threads_env)

    def submit_task(self, task):
        # Enqueue the task into the task queue
        self.tsk_queue.put(task)
        self.jobs[task.task_id] = task.status

    def start(self):
        for _ in range(self.num_threads_env):
            thread = TaskRunner(self.tsk_queue, self.semaphore, self.jobs)
            thread.start()
            self.thr_list.append(thread)

    def shutdown(self):
        # Signal TaskRunner threads to gracefully shutdown
        for thread in self.thr_list:
            thread.shutdown()

        # Wait for all threads to finish
        for thread in self.thr_list:
            thread.join()

class TaskRunner(Thread):
    def __init__(self, tsk_queue, semaphore, jobs):
        # TODO: init necessary data structures
        Thread.__init__(self)
        self.tsk_queue = tsk_queue
        self.semaphore = semaphore
        self.jobs = jobs

    def run(self):
        while True:
            # TODO
            # Get pending job
            # Execute the job and save the result to disk
            # Repeat until graceful_shutdown
            # Get a task from the task queue
            if self.tsk_queue.qsize() != 0:
                task = self.tsk_queue.get()

                # Execute the task
                self.execute_task(task)

    def execute_task(self, task):
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
        

    def calculate_global_mean(self, task):
        # Calculate the global mean based on the data
        val = task.data_value
        s = 0
        count = 0
        for line in val:
            if line['Question'] == task.question['question']:
                s += float(line['Data_Value'])
                count += 1
        
        if task.url == '/api/global_mean':
            self.jobs[task.task_id] = {'status': 'done', 'data': {"global_mean": s / count}}
        else:
            return s / count
    
    def calculate_worst5(self, task):
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

        for state, data in finished_data.items():
            finished_data[state] = data['total_value'] / data['count']

        # Sort states based on average values
        if task.question in task.data_value.questions_best_is_max:
            sorted_avg = {state: avg for state, avg in sorted(finished_data.items(), key=lambda x: x[1])}
        else:
            sorted_avg = {state: avg for state, avg in sorted(finished_data.items(), key=lambda x: x[1], reverse=True)}


        # Get the worst 5 states
        worst5 = dict(list(sorted_avg.items())[:5])

        # Store result in jobs dictionary
        self.jobs[task.task_id] = {'status': 'done', 'data': worst5}

    def calculate_best5(self, task):
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


        for state, data in finished_data.items():
            finished_data[state] = data['total_value'] / data['count']

        # Sort states based on average values
        if task.question in task.data_value.questions_best_is_min:
            sorted_avg = {state: avg for state, avg in sorted(finished_data.items(), key=lambda x: x[1])}
        else:
            sorted_avg = {state: avg for state, avg in sorted(finished_data.items(), key=lambda x: x[1], reverse=True)}


        # Get the worst 5 states
        best5 = dict(list(sorted_avg.items())[:5])

        # Store result in jobs dictionary
        self.jobs[task.task_id] = {'status': 'done', 'data': best5}
    
    def calculate_states_mean(self, task):
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
        sorted_avg = {state: avg for state, avg in sorted(finished_data.items(), key=lambda x: x[1])}

        if task.url == '/api/states_mean':
            # Store result in jobs dictionary
            self.jobs[task.task_id] = {'status': 'done', 'data': sorted_avg}

        return sorted_avg
    
    def calculate_state_mean(self, task):
        val = task.data_value
        state = task.question['state']
        s = 0
        count = 0
        for line in val:
            if line['Question'] == task.question['question'] and line['LocationDesc'] == state:
                s += float(line['Data_Value'])
                count += 1
        
        if task.url == '/api/state_mean':
            self.jobs[task.task_id] = {'status': 'done', 'data': {state: s / count}}
        else: 
            return s / count

    def calculate_diff_from_mean(self, task):
        # Calculate states mean
        data = self.calculate_states_mean(task)

        # Calculate global mean
        task.data_value = task.data_value.data
        glb_mean = self.calculate_global_mean(task)

        # Calculate difference from global mean for each state
        for state in data:
            data[state] = glb_mean - data[state]

        sorted_avg = {state: avg for state, avg in sorted(data.items(), key=lambda x: x[1], reverse=True)}

        # Store result in jobs dictionary
        self.jobs[task.task_id] = {'status': 'done', 'data': sorted_avg}

    def calculate_state_diff_from_mean(self, task):
        state = task.question['state']
        glb_mean = self.calculate_global_mean(task)
        st_mean = self.calculate_state_mean(task)
        avg = glb_mean - st_mean

        self.jobs[task.task_id] = {'status': 'done', 'data': {state: avg}}

    def calculate_mean_by_category(self, task):
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
        sorted_avg = {state: avg for state, avg in sorted(finished_data.items(), key=lambda x: (x[0], -x[1]))}
                    
        self.jobs[task.task_id] = {'status': 'done', 'data': sorted_avg}

    def calculate_state_mean_by_category(self, task):
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

        sorted_avg = {state: avg for state, avg in sorted(finished_data.items(), key=lambda x: (x[0], -x[1]))}

        self.jobs[task.task_id] = {'status': 'done', 'data': {state: sorted_avg}}
