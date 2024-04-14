import unittest
import sys
from threading import Event
from queue import Queue
sys.path.append("./app")
from data_ingestor import DataIngestor
from task_runner import ThreadPool, TaskRunner, Task
from deepdiff import DeepDiff

class TestWebserver(unittest.TestCase):

    def setUp(self):
        self.task_id = 1
        self.data_ingestor = DataIngestor("./new_nutrition_activity_obesity_usa_subset.csv")
        self.task_runner = TaskRunner(Queue(), [], Event(), None)

    def test_best5(self):
        """
        Test for the best5 method
        """
        data = {"question": "Percent of adults aged 18 years and older who have an overweight classification"}
        ref_result = {
            'Tennessee': 23.45,
            'Montana': 24.166666666666668,
            'Nevada': 25.8,
            'South Dakota': 25.9,
            'Wisconsin': 26.1
        }
        task = Task(self.task_id, 'running', data, '/api/best5',
                    self.data_ingestor, True)
        self.task_id += 1
        function_output = self.task_runner.calculate_best5(task)
        # Taken from the already provided checker
        d = DeepDiff(function_output, ref_result, math_epsilon=0.01)
        self.assertTrue(d == {}, str(d))

    def test_worst5(self):
        """
        Test for the worst5 method
        """
        data = {"question": "Percent of adults who engage in no leisure-time physical activity"}
        ref_result = {
            'Alabama': 53.6,
            'Nevada': 49.1,
            'Arizona': 47.1,
            'Wyoming': 45.05,
            'Connecticut': 44.5
        }
        task = Task(self.task_id, 'running', data, '/api/worst5',
                    self.data_ingestor, True)
        self.task_id += 1
        function_output = self.task_runner.calculate_worst5(task)
        # Taken from the already provided checker
        d = DeepDiff(function_output, ref_result, math_epsilon=0.01)
        self.assertTrue(d == {}, str(d))

    def test_global_mean(self):
        """
        Test for the global_mean method
        """
        data = {"question": "Percent of adults aged 18 years and older who have obesity"}
        ref_result = {"global_mean": 37.20789473684211}
        task = Task(self.task_id, 'running', data, '/api/global_mean',
                    self.data_ingestor, True)
        self.task_id += 1

        function_output = self.task_runner.calculate_global_mean(task)
        # Taken from the already provided checker
        d = DeepDiff(function_output, ref_result, math_epsilon=0.01)
        self.assertTrue(d == {}, str(d))

    def test_state_mean(self):
        """
        Test for the state_mean method
        """
        data = {"question": "Percent of adults who report consuming vegetables less than one time daily", "state": "New York"}
        ref_result = {"New York": 43.7}
        task = Task(self.task_id, 'running', data, '/api/state_mean',
                    self.data_ingestor, True)
        self.task_id += 1

        function_output = self.task_runner.calculate_state_mean(task)
        # Taken from the already provided checker
        d = DeepDiff(function_output, ref_result, math_epsilon=0.01)
        self.assertTrue(d == {}, str(d))

    def test_states_mean(self):
        """
        Test for the states_mean method
        """
        data = {"question": "Percent of adults who engage in muscle-strengthening activities on 2 or more days a week"}
        ref_result = {
            'Kentucky': 18.8,
            'Vermont': 19.7,
            'Utah': 21.4,
            'Maryland': 21.6,
            'Wisconsin': 24.8,
            'Oregon': 28.0,
            'Arkansas': 28.8,
            'Connecticut': 30.6,
            'Massachusetts': 45.1,
            'Michigan': 48.7,
            'Wyoming': 50.8,
            'Rhode Island': 53.5
        }
        task = Task(self.task_id, 'running', data, '/api/states_mean',
                    self.data_ingestor, True)
        self.task_id += 1

        function_output = self.task_runner.calculate_states_mean(task)
        # Taken from the already provided checker
        d = DeepDiff(function_output, ref_result, math_epsilon=0.01)
        self.assertTrue(d == {}, str(d))

    def test_diff_from_mean(self):
        """
        Test for the diff_from_mean method
        """
        data = {"question": "Percent of adults who achieve at least 150 minutes a week of moderate-intensity aerobic physical activity or 75 minutes a week of vigorous-intensity aerobic activity (or an equivalent combination)"}
        ref_result = {
            'Illinois': 5.966666666666669,
            'Connecticut': 3.2666666666666693,
            'Arizona': 3.06666666666667,
            'Arkansas': 2.9666666666666686,
            'Minnesota': 2.06666666666667, 
            'Maine': 0.9666666666666686,
            'Vermont': -1.7333333333333272,
            'Kansas': -2.733333333333327,
            'Virginia': -13.833333333333329
        }
        task = Task(self.task_id, 'running', data, '/api/diff_from_mean', self.data_ingestor, True)
        self.task_id += 1

        function_output = self.task_runner.calculate_diff_from_mean(task)
        # Taken from the already provided checker
        d = DeepDiff(function_output, ref_result, math_epsilon=0.01)
        self.assertTrue(d == {}, str(d))

    def test_state_diff_from_mean(self):
        """
        Test for the state_diff_from_mean method
        """
        data = {"question": "Percent of adults who achieve at least 300 minutes a week of moderate-intensity aerobic physical activity or 150 minutes a week of vigorous-intensity aerobic activity (or an equivalent combination)", "state": "Texas"}
        ref_result = {'Texas': 4.677777777777774}
        task = Task(self.task_id, 'running', data, '/api/state_diff_from_mean',
                    self.data_ingestor, True)
        self.task_id += 1

        function_output = self.task_runner.calculate_state_diff_from_mean(task)
        # Taken from the already provided checker
        d = DeepDiff(function_output, ref_result, math_epsilon=0.01)
        self.assertTrue(d == {}, str(d))

    def test_mean_by_category(self):
        """
        Test for the mean_by_category method
        """
        data = {"question": "Percent of adults aged 18 years and older who have an overweight classification"}
        ref_result = {
            "('Arkansas', 'Age (years)', '25 - 34')": 53.6,
            "('Arkansas', 'Age (years)', '65 or older')": 36.7,
            "('Colorado', 'Income', 'Data not reported')": 56.2,
            "('Colorado', 'Race/Ethnicity', 'Non-Hispanic Black')": 22.2,
            "('Georgia', 'Age (years)', '35 - 44')": 28.9,
            "('Georgia', 'Income', '$75,000 or greater')": 30.7,
            "('Hawaii', 'Income', '$15,000 - $24,999')": 31.5,
            "('Idaho', 'Race/Ethnicity', '2 or more races')": 44.2,
            "('Illinois', 'Education', 'Some college or technical school')": 54.8,
            "('Indiana', 'Education', 'Less than high school')": 33.9,
            "('Indiana', 'Gender', 'Female')": 33.4,
            "('Indiana', 'Income', 'Less than $15,000')": 51.0,
            "('Indiana', 'Race/Ethnicity', 'Non-Hispanic White')": 49.1,
            "('Kansas', 'Total', 'Total')": 45.0,
            "('Louisiana', 'Age (years)', '25 - 34')": 53.8,
            "('Massachusetts', 'Income', '$15,000 - $24,999')": 53.3,
            "('Massachusetts', 'Race/Ethnicity', 'Hispanic')": 21.7,
            "('Mississippi', 'Age (years)', '45 - 54')": 40.6,
            "('Mississippi', 'Income', 'Less than $15,000')": 36.4,
            "('Missouri', 'Age (years)', '25 - 34')": 26.3,
            "('Montana', 'Age (years)', '45 - 54')": 20.4,
            "('Montana', 'Gender', 'Female')": 28.7,
            "('Montana', 'Race/Ethnicity', 'Hispanic')": 23.4,
            "('Nebraska', 'Age (years)', '45 - 54')": 38.1,
            "('Nevada', 'Race/Ethnicity', 'Asian')": 25.8,
            "('New Hampshire', 'Income', '$50,000 - $74,999')": 38.8,
            "('New Mexico', 'Race/Ethnicity', 'Non-Hispanic White')": 27.7,
            "('North Dakota', 'Income', '$50,000 - $74,999')": 47.7,
            "('North Dakota', 'Income', '$75,000 or greater')": 40.9,
            "('Ohio', 'Income', 'Data not reported')": 40.5,
            "('Oregon', 'Total', 'Total')": 39.4,
            "('Rhode Island', 'Education', 'Less than high school')": 47.6,
            "('Rhode Island', 'Gender', 'Female')": 22.3,
            "('South Dakota', 'Age (years)', '45 - 54')": 25.9,
            "('Tennessee', 'Income', 'Less than $15,000')": 25.7,
            "('Tennessee', 'Race/Ethnicity', 'Non-Hispanic White')": 21.2,
            "('Utah', 'Education', 'College graduate')": 48.9,
            "('Utah', 'Education', 'High school graduate')": 38.4,
            "('Utah', 'Education', 'Less than high school')": 39.6,
            "('Utah', 'Income', '$25,000 - $34,999')": 40.0,
            "('Utah', 'Race/Ethnicity', 'Non-Hispanic White')": 40.6,
            "('Virginia', 'Income', 'Less than $15,000')": 27.5, 
            "('Virginia', 'Race/Ethnicity', 'Non-Hispanic Black')": 47.9,
            "('Virginia', 'Race/Ethnicity', 'Non-Hispanic White')": 21.4,
            "('Washington', 'Race/Ethnicity', 'Other')": 39.8,
            "('West Virginia', 'Age (years)', '25 - 34')": 54.4,
            "('West Virginia', 'Education', 'Less than high school')": 37.4,
            "('Wisconsin', 'Race/Ethnicity', '2 or more races')": 23.5,
            "('Wisconsin', 'Race/Ethnicity', 'Hispanic')": 28.7,
            "('Wyoming', 'Education', 'High school graduate')": 30.7}
        task = Task(self.task_id, 'running', data, '/api/mean_by_category',
                    self.data_ingestor, True)
        self.task_id += 1

        function_output = self.task_runner.calculate_mean_by_category(task)
        # Taken from the already provided checker
        d = DeepDiff(function_output, ref_result, math_epsilon=0.01)
        self.assertTrue(d == {}, str(d))

    def test_state_mean_by_category(self):
        """
        Test for the state_mean_by_category method
        """
        data = {"question": "Percent of adults who engage in muscle-strengthening activities on 2 or more days a week", "state": "Kentucky"}
        ref_result = {'Kentucky': {"('Age (years)', '65 or older')": 18.8}}

        task = Task(self.task_id, 'running', data, '/api/state_mean_by_category',
                    self.data_ingestor, True)
        self.task_id += 1
        function_output = self.task_runner.calculate_state_mean_by_category(task)
        # Taken from the already provided checker
        d = DeepDiff(function_output, ref_result, math_epsilon=0.01)
        self.assertTrue(d == {}, str(d))

if __name__ == "__main__":
    unittest.main()
