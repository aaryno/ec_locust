"""Define a locust swarm for testing WMS on Geoserver EC.
"""

from locust import HttpLocust, task, events
from wms_behavior import WMSBehavior
from utils import load_bbox_data, check_content

def my_success_handler(request_type, name, response_time, response_length, **kw):
    print( request_type+","+name+","+str(response_time)+","+str(response_length))


events.request_success += my_success_handler

class WMSTester(WMSBehavior):
    """Exercise Geoserver EC WMS
    """

    
    # Load data at import time
    # wms_256_tiles.csv can be generated by mercantile_gen
    bbox_iterator = load_bbox_data("wms_256_tiles.csv")

    def on_start(self):
        """Startup method called by locust once for each new simulated user.
        """

    @task(0)
    def wms_get_capabilities(self):
        """Exercise WMS GetCapabilities
        """
        response = self.get_capabilities("/geoserver/ows")
        check_content(response, "text/xml")

    @task(1)
    def wms_png_bbox(self):
        response = self.wms_get_map("image/png")
        check_content(response, "image/png")

    # @task(1)
    def wms_png8_bbox(self):
        response = self.wms_get_map("image/png8")
        check_content(response, "image/png")

    # @task(1)
    def wms_jpeg_bbox(self):
        response = self.wms_get_map("image/jpeg")
        check_content(response, "image/jpeg")

    @task(0)
    def wms_tiff_bbox(self):
        response = self.wms_get_map("image/tiff")
        check_content(response, "image/tiff")

    def wms_get_map(self, image_format):
        """Exercise WMS GetMap with the specified format
        """
        line = next(self.bbox_iterator)
        bbox = [line[1], line[0], line[3], line[2]]
        bbox_string = ",".join(bbox)
        name = "WMS_{0}_BBOX".format(image_format.split("/")[-1])
        return self.get_map(
            uri="/geoserver/wms",
            layers="osm:osm",
            image_format=image_format,
            width=256,
            height=256,
            bbox=bbox_string,
            crs="EPSG:4326",
            name=name,
        )


class WMSUser(HttpLocust):
    """Specify how each simulated user will behave.
    """
    # Define the behavior of the user.
    task_set = WMSTester

    # Parameters for generating the random wait between tasks.
    min_wait = 0
    max_wait = 0
