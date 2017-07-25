from locust import TaskSet, task


class WMSBehavior(TaskSet):
    """Specify the set of tasks simulated users will perform.
    """

    exception_format = "application/json"
    output_format = "application/json"

    def __init__(self, parent):
        super(WMSBehavior, self).__init__(parent)

    def get_capabilities(self, path, version, namespace=None, fmt=None):
        """Get data about a WMS service
        """
        service = "WMS"
        request = "GetCapabilities"
        headers = {
            "Accept": "application/json",
        }
        parameters = {
            "service": service,
            "version": version,
            "request": request,
        }
        if namespace is not None:
            parameters["namespace"] = namespace
        if fmt is not None:
            parameters["format"] = fmt
        response = self.client.get(path, params=parameters, headers=headers)
        return response

    def describe_layer(self, path, service, version, request):
        """Get the WFS or WCS to retrieve additional info about a WMS layer.
        """
        service = "WMS"
        request = "DescribeLayer"
        exception_format = self.exception_format
        output_format = self.output_format
        parameters = {
            "service": service,
            "version": version,
            "request": request,
            "layers": "whee",
            "exceptions": exception_format,
            "output_format": output_format,
        }
        response = self.client.get(path, params=parameters)
        return response

    def get_legend_graphic(self):
        """Get a generated legend for a WMS map.
        """
        request = "GetLegendGraphic"
        version = "1.0.0"
        fmt = "image/png"
        width = 20
        height = 20
        layer = "topp:states"
        parameters = {
            "VERSION": version,
            "REQUEST": request,
            "LAYER": layer,
            "FORMAT": fmt,
            "EXCEPTIONS": self.exception_format,
        }
        if width:
            parameters["WIDTH"] = width
        if height:
            parameters["HEIGHT"] = height

    def get_feature_info(self):
        """Get data for a pixel location on a WMS map
        """
        "GetFeatureInfo"

    @task
    def get_map(self):
        """Get a WMS map image
        """
        "GetMap"
