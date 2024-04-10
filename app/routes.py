import os
import json
from flask import request, jsonify
from app import webserver
from app.task_runner import Task

# Example endpoint definition
@webserver.route('/api/post_endpoint', methods=['POST'])
def post_endpoint():
    if request.method == 'POST':
        # Assuming the request contains JSON data
        data = request.json
        print(f"got data in post {data}")

        # Process the received data
        # For demonstration purposes, just echoing back the received data
        response = {"message": "Received data successfully", "data": data}

        # Sending back a JSON response
        return jsonify(response)
    else:
        # Method Not Allowed
        return jsonify({"error": "Method not allowed"}), 405

@webserver.route('/api/get_results/<job_id>', methods=['GET'])
def get_response(job_id):
    # Check if job_id is valid
    if int(job_id) > webserver.job_counter:
        return jsonify({'status': 'error', 'reason': 'Invalid job_id'})

    # Check if job_id is done and return the result
    if webserver.tasks_runner.jobs[int(job_id)] != "running":
        with open(f"./results/job_id_{int(job_id)}.json", encoding="utf-8") as file:
            return jsonify(json.load(file))
    else:
        return jsonify({'status': 'running'}), 200

@webserver.route('/api/states_mean', methods=['POST'])
def states_mean_request():
    """
        Function used for the states_mean request
    """
    # Get request data
    data = request.json
    # Increment the global job counter
    webserver.job_counter += 1
    job_id = webserver.job_counter

    # Register job. Don't wait for task to finish
    task = Task(job_id, 'running', data, '/api/states_mean', webserver.data_ingestor)
    webserver.tasks_runner.submit_task(task)

    # Return associated job_id
    return jsonify({'job_id': job_id}), 200

@webserver.route('/api/state_mean', methods=['POST'])
def state_mean_request():
    """
        Function used for the state_mean request
    """
    # Get request data
    data = request.json
    # Increment the global job counter
    webserver.job_counter += 1
    job_id = webserver.job_counter

    # Register job. Don't wait for task to finish
    task = Task(job_id, 'running', data, '/api/state_mean', webserver.data_ingestor.data)
    webserver.tasks_runner.submit_task(task)

    # Return associated job_id
    return jsonify({'job_id': job_id}), 200

@webserver.route('/api/best5', methods=['POST'])
def best5_request():
    """
        Function used for the best5 request
    """
    # Get request data
    data = request.json
    # Increment the global job counter
    webserver.job_counter += 1
    job_id = webserver.job_counter

    # Register job. Don't wait for task to finish
    task = Task(job_id, 'running', data['question'], '/api/best5', webserver.data_ingestor)
    webserver.tasks_runner.submit_task(task)

    # Return associated job_id
    return jsonify({'job_id': job_id}), 200

@webserver.route('/api/worst5', methods=['POST'])
def worst5_request():
    """
        Function used for the worst5 request
    """
    # Get request data
    data = request.json
    # Increment the global job counter
    webserver.job_counter += 1
    job_id = webserver.job_counter

    # Register job. Don't wait for task to finish
    task = Task(job_id, 'running', data['question'], '/api/worst5', webserver.data_ingestor)
    webserver.tasks_runner.submit_task(task)

    # Return associated job_id
    return jsonify({'job_id': job_id}), 200

@webserver.route('/api/global_mean', methods=['POST'])
def global_mean_request():
    """
        Function used for the global_mean request
    """
    # Get request data
    data = request.json
    # Increment the global job counter
    webserver.job_counter += 1
    job_id = webserver.job_counter

    # Register job. Don't wait for task to finish
    task = Task(job_id, 'running', data, '/api/global_mean', webserver.data_ingestor.data)
    webserver.tasks_runner.submit_task(task)

    # Return associated job_id
    return jsonify({'job_id': job_id}), 200

@webserver.route('/api/diff_from_mean', methods=['POST'])
def diff_from_mean_request():
    """
    Function used for the diff_from_mean request
    """
    # Get request data
    data = request.json
    # Increment the global job counter
    webserver.job_counter += 1
    job_id = webserver.job_counter

    # Register job. Don't wait for task to finish
    task = Task(job_id, 'running', data, '/api/diff_from_mean', webserver.data_ingestor)
    webserver.tasks_runner.submit_task(task)

    # Return associated job_id
    return jsonify({'job_id': job_id}), 200

@webserver.route('/api/state_diff_from_mean', methods=['POST'])
def state_diff_from_mean_request():
    """
        Function used for the state_diff_from_mean request
    """
    # Get request data
    data = request.json
    # Increment the global job counter
    webserver.job_counter += 1
    job_id = webserver.job_counter

    # Register job. Don't wait for task to finish
    task = Task(job_id, 'running', data, '/api/state_diff_from_mean',
        webserver.data_ingestor.data)
    webserver.tasks_runner.submit_task(task)

    # Return associated job_id
    return jsonify({'job_id': job_id}), 200

@webserver.route('/api/mean_by_category', methods=['POST'])
def mean_by_category_request():
    """
        Function used for the mean_by_category request
    """
    # Get request data
    data = request.json
    # Increment the global job counter
    webserver.job_counter += 1
    job_id = webserver.job_counter

    # Register job. Don't wait for task to finish
    task = Task(job_id, 'running', data['question'], '/api/mean_by_category',
        webserver.data_ingestor.data)
    webserver.tasks_runner.submit_task(task)

    # Return associated job_id
    return jsonify({'job_id': job_id}), 200

@webserver.route('/api/state_mean_by_category', methods=['POST'])
def state_mean_by_category_request():
    """
        Function used for the state_mean_by_category request
    """
    # Get request data
    data = request.json
    # Increment the global job counter
    webserver.job_counter += 1
    job_id = webserver.job_counter
    # Register job. Don't wait for task to finish
    task = Task(job_id, 'running', data, '/api/state_mean_by_category',
        webserver.data_ingestor.data)
    webserver.tasks_runner.submit_task(task)
    # Return associated job_id
    return jsonify({'job_id': job_id}), 200

@webserver.route('/api/graceful_shutdown', methods=['GET'])
def shutdown_request():
    """
        Gracefully shutting the server.
    """
    webserver.tasks_runner.shutdown_flag.set()

    for thread in webserver.tasks_runner.thr_list:
        thread.join()

    return jsonify({'status': 'shutting down'}), 200

# You can check localhost in your browser to see what this displays
@webserver.route('/')
@webserver.route('/index')
def index():
    routes = get_defined_routes()
    msg = f"Hello, World!\n Interact with the webserver using one of the defined routes:\n"
    # Display each route as a separate HTML <p> tag
    paragraphs = ""
    for route in routes:
        paragraphs += f"<p>{route}</p>"
    msg += paragraphs
    return msg

def get_defined_routes():
    routes = []
    for rule in webserver.url_map.iter_rules():
        methods = ', '.join(rule.methods)
        routes.append(f"Endpoint: \"{rule}\" Methods: \"{methods}\"")
    return routes

states_mean_request
