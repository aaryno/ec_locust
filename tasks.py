"""Task definitions used by a locust swarm.
"""
import random
from locust import HttpLocust, TaskSet, task
from wms import WMSBehavior


class Behavior(WMSBehavior):
    """Specify the set of tasks simulated users will perform.
    """

    # Define paths to use, etc.

    exception_format = "application/json"
    output_format = "application/json"

    def __init__(self, parent):
        super(Behavior, self).__init__(parent)

    def login(self):
        """
        """
        pass
        # response = self.client.post(
        #     "/something", json={
        #         "username": "basic@boundlessgeo.com",
        #         "password": "test_1234",
        #     },
        # )
        # response.json()

    def on_start(self):
        """Startup method automatically called by locust.
        """
        self.login()

    @task
    def test_get_capabilities(self):
        response = self.get_capabilities(path="wms", version="1.3.0")

        # Locust automatically marks fail if it's not a 200

        # This doesn't seem to support JSON output format anyway
        content_type = response.headers["Content-Type"]
        if content_type != 'text/xml;charset=UTF-8':
            response.failure("Unexpected content-type")

        if not response.content:
            response.failure("Empty response body")

    @task(0)
    def test_describe_layer(self):
        version = "1.1.1"
        # layers
        response = self.describe_layer(
            version, self.exception_format, self.output_format,
        )
        data = response.json()

    @task(0)
    def test_get_legend_graphic(self):
        response = self.get_legend_graphic()
        data = response.json()

    @task(0)
    def test_get_feature_info(self):
        response = self.get_feature_info()
        data = response.json()

    @task(0)
    def test_get_map(self):
        response = self.get_map()
        data = response.json()


class User(HttpLocust):
    """Specify how each simulated user will behave.
    """

    # task_set defines the tasks which each user will perform.
    task_set = Behavior

    # These are used to generate the random wait between task executions.
    min_wait = 1000
    max_wait = 15000
