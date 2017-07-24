"""Task definitions used by a locust swarm.
"""
import random
from locust import HttpLocust, TaskSet, task


class Behavior(TaskSet):
    """Specify the set of tasks simulated users will perform.
    """

    # Define paths to use, etc.

    def __init__(self, parent):
        super(Behavior, self).__init__(parent)

    def login(self):
        """
        """
        response = self.client.post(
            "/something", json={
                "username": "basic@boundlessgeo.com",
                "password": "test_1234",
            },
        )
        response.json()

    def on_start(self):
        """Startup method automatically called by locust.
        """
        self.login()

    @task
    def some_task(self):
        pass


class User(HttpLocust):
    """Specify how each simulated user will behave.
    """

    # task_set defines the tasks which each user will perform.
    task_set = Behavior

    # These are used to generate the random wait between task executions.
    min_wait = 1000
    max_wait = 15000
