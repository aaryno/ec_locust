"""
Invoke with, e.g.::

    locust -f tasks.py --host="http://whatever"

Example hosts:

    "https://api.dev.boundlessgeo.io"
    "https://api.dev.boundlessgeo.com"
    "https://api.boundlessgeo.io"
    "https://api.boundlessgeo.com"

See the locust manual for how to run simulated requests from a cluster for
proper load testing.
"""
import random
from locust import HttpLocust, TaskSet, task


class Behavior(TaskSet):
    """Specify the set of tasks simulated users will perform.
    """

    # Path for the token service
    token_uri = "/v1/token/"

    # Paths for the routing service
    route_uris = {
        "mapbox": "/v1/route/mapbox/",
        "mapzen": "/v1/route/mapzen/",
        "graphhopper": "/v1/route/graphhopper/",
    }

    # Paths for the geocoding service
    geocode_uris = {
        "mapbox": "/v1/geocode/mapbox/address/",
        "mapzen": "/v1/geocode/mapzen/address/",
    }

    # Paths for the basemap service
    # TODO
    basemap_uris = {
    }

    addresses = [
        "50 Broad St #703, New York, NY 10004",
        "4240 Duncan Ave, St Louis, MO 63110",
        "1600 Pennsylvania Ave., Washington, DC",
        "625 Celeste St, New Orleans, LA 70130",
        "7500 GEOINT Drive, Springfield, Virginia 22150-7500",
    ]

    route_origin = "2311 Broadway Street, San Francisco, CA" 
    route_destination = "916 Kearny Street, San Francisco, CA"
    geocode_address = "1600 Pennsylvania Avenue, Washington, DC"

    def __init__(self, parent):
        self.token = None
        super(Behavior, self).__init__(parent)

    def login(self):
        """Get a token from the token service.
        """

        # e.g. "https://api.boundlessgeo.com/v1/token/"
        # This MUST have the trailing slash or it will mysteriously 403!
        response = self.client.post(
            self.token_uri, json={
                "username": "basic@boundlessgeo.com",
                "password": "test_1234",
            },
        )
        body_json = response.json()
        token = body_json.get("token")
        self.token = token

    def headers(self):
        return {
            "Authorization": "Bearer {0}".format(self.token),
        }
    
    def on_start(self):
        """Startup method automatically called by locust.
        """
        self.token = None
        self.login()

    def route(self, service_name, origin, destination):
        """Get a route from origin to destination using the BCS routing API.
        """
        uri = "{0}?waypoints={1}|{2}".format(
            self.route_uris[service_name], origin, destination,
        )
        response = self.client.get(uri, headers=self.headers())

    def geocode(self, service_name, address):
        """Get candidate geocodes for an address using the BCS geocoding API.
        """
        uri = "{0}/{1}".format(
            self.geocode_uris[service_name].rstrip("/"),
            address,
        )
        response = self.client.get(uri, headers=self.headers())

    @task
    def route_mapbox(self):
        self.route("mapbox", self.route_origin, self.route_destination)

    @task
    def route_mapzen(self):
        self.route("mapzen", self.route_origin, self.route_destination)

    @task
    def geocode_mapbox(self):
        self.geocode("mapbox", self.geocode_address)

    @task
    def geocode_mapzen(self):
        self.geocode("mapzen", self.geocode_address)

    @task(0)
    def basemap_tile(self):
        pass

    @task(0)
    def login_randomly(self):
        if random.uniform(0, 1) > 0.9:
            self.login()

    @task(0)
    def route_randomly(self):
        service_name = random.choice(self.route_uris.keys())
        origin = random.choice(self.addresses)
        destination = random.choice(self.addresses)
        self.route(service_name, origin, destination)

    @task(0)
    def geocode_randomly(self):
        service_name = random.choice(self.geocode_uris.keys())
        address = random.choice(self.addresses)
        self.geocode(service_name, address)

   
class User(HttpLocust):
    """Specify how each simulated user will behave.
    """

    # task_set defines the tasks which each user will perform.
    task_set = Behavior

    # These are used to generate the random wait between task executions.
    min_wait = 1000
    max_wait = 15000
