"""Assumes Python 3.6+
"""
import argparse
import statistics
import time
import logging
from textwrap import indent, dedent
from urllib.parse import urlencode
import asyncio
import aiohttp
from async_timeout import timeout


LOG = logging.getLogger("")


def argument_parser():
    parser = argparse.ArgumentParser(
        description="Test some latency thing",
    )
    parser.add_argument(
        dest="node_names",
        nargs="+",
    )
    parser.add_argument(
        "--database-host",
        default="osm-test-chesapeake.cs5ahh3rwygg.us-east-1.rds.amazonaws.com",
    )
    parser.add_argument(
        "--database-port",
        default="5432",
    )
    parser.add_argument(
        "--database-name",
        default="osm",
    )
    parser.add_argument(
        "--database-user",
        default="geoserver",
    )
    parser.add_argument(
        "--database-password",
        default="geoserver",
    )
    return parser


class RequestResult:
    """Store data on one request.
    """
    def __init__(self):
        self.status = None
        self.body = None
        self.start = None
        self.end = None

    @property
    def success(self):
        return (200 <= self.status <= 299) if self.status else False

    @property
    def duration(self):
        if self.end is None or self.start is None:
            return None
        return self.end - self.start


class NodeResult:
    """Store data on one node test.
    """
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.workspace_results = None
        self.datastore_results = None
        self.featuretype_results = None
        self.get_results = None

    @property
    def get_result(self):
        return self.get_results[-1] if self.get_results else None

    @property
    def workspace_result(self):
        return self.workspace_results[-1] if self.workspace_results else None

    @property
    def datastore_result(self):
        return self.datastore_results[-1] if self.datastore_results else None

    @property
    def featuretype_result(self):
        return self.featuretype_results[-1] if self.featuretype_results else None

    @property
    def get_duration(self):
        return self.get_result.duration if self.get_result else None

    @property
    def workspace_duration(self):
        return self.workspace_result.duration if self.workspace_result else None

    @property
    def datastore_duration(self):
        return self.datastore_result.duration if self.datastore_result else None

    @property
    def featuretype_duration(self):
        return self.featuretype_result.duration if self.featuretype_result else None

    @property
    def get_end(self):
        return self.get_result.end if self.get_result else None

    @property
    def post_end(self):
        return (
            self.featuretype_result.end
            if self.featuretype_result
            else None
        )

    @property
    def latency(self):
        if not self.get_results:
            return None

        get_result = self.get_results[-1]
        get_end = get_result.end

        get_end, post_end = self.get_end, self.post_end
        if get_end is None or post_end is None:
            return None
        return self.get_end - self.post_end


async def retry(label, async_function, args=None, kwargs=None, max_fails=1):
    args = args or []
    kwargs = kwargs or {}

    results = []

    for fails in range(0, max_fails):
        LOG.debug(f"{label} Attempt #{fails + 1}")

        result = RequestResult()
        results.append(result)
        result.start = time.monotonic()

        # e.g. "async with session.post(url) as response:"
        async with async_function(*args, **kwargs) as response:
            LOG.debug(f"Response: {response}")
            result.status = response.status

            # Madness: 500 to mean resource already exists...
            # e.g. body = b":Workspace named 'osm' already exists."
            if result.status == 500:
                body = await response.read()
                result.length = len(body)
                result.type = response.headers.get("content-type")
                if (
                    result.type.startswith("text/plain")
                    and b"already exists" in body
                ):
                    LOG.info(f"Magic 500 Body: {body!r}")
                    # pretend everything is okay, go back to sleep
                    result.status = 200
                    result.end = time.monotonic()
                    break

            # If it looks okay so far, let's read it and check it
            if result.success:
                body = await response.read()

                result.end = time.monotonic()
                LOG.debug(f"Response Body: {body}")

                # geoserver doesn't seem to be giving up content-length,
                # so we'll just keep it all in RAM here, whatever
                result.length = len(body)
                result.type = response.headers.get("content-type")

                # Looks good, let's stop retrying
                break

            LOG.error(f"looks unsuccessful: {result.status}")

            # Stop the timer without bothering to read
            result.end = time.monotonic()

            # wait a bit to avoid being rude with very high request volume
            await asyncio.sleep(1)

    return results


async def test_node(session, node_name):
    # this coro contains the whole flow for one node
    # it returns report information on that node at the end

    max_post_fails = 2
    max_get_fails = 10

    base_url = f"http://{node_name}/geoserver"
    query_string = urlencode({
        "SERVICE": "WMS",
        "VERSION": "1.3.0",
        "REQUEST": "GetMap",
        "FORMAT": "image/png",
        "TRANSPARENT": "true",
        "LAYERS": "osm:osm",
        "TILED": "true",
        "WIDTH": "512",
        "HEIGHT": "512",
        "CRS": "EPSG:3857",
        "STYLES": "",
        "FORMAT_OPTIONS": "dpi:180",
    })
    url = f"{base_url}/wms?{query_string}"
    bbox = "-8575011.581144214,4709743.934819421,-8574400.084917933,4710355.431045703"
    url += f"&BBOX={bbox}"

    result = NodeResult(node_name, url)

    # mystery parameters
    workspace = "osm"
    datastore = "openstreetmap"
    layer_name = "ft0001"

    # Make sure we have an osm workspace I guess
    workspace_args = [
        f"{base_url}/rest/workspaces",
    ]
    workspace_kwargs = {
        "headers": {
            "Content-Type": "text/xml",
        },
        "data": f"<workspace><name>{workspace}</name></workspace>",
    }
    workspace_results = await retry(
        "POST",
        session.post,
        args=workspace_args,
        kwargs=workspace_kwargs,
        max_fails=max_post_fails,
    )
    result.workspace_results = workspace_results

    if not workspace_results or not workspace_results[-1].success:
        return result

    datastore_args = [
        f"{base_url}/rest/workspaces/{workspace}/datastores",
    ]
    datastore_kwargs = {
        "headers": {
            "Content-Type": "text/xml",
        },
        # magic parameters
        "data": """
            <dataStore>
            <name>openstreetmap</name>
            <connectionParameters>
                <host>
                osm-test-chesapeake.cs5ahh3rwygg.us-east-1.rds.amazonaws.com
                </host>
                <port>5432</port>
                <database>osm</database>
                <user>geoserver</user>
                <passwd>geoserver</passwd>
                <dbtype>postgis</dbtype>
            </connectionParameters>
            </dataStore>
        """.strip(),
    }
    datastore_results = await retry(
        "POST",
        session.post,
        args=datastore_args,
        kwargs=datastore_kwargs,
        max_fails=max_post_fails,
    )
    result.datastore_results = datastore_results

    if not datastore_results or not datastore_results[-1].success:
        return result

    featuretype_args = [
        (
            f"{base_url}/workspaces/{workspace}"
            f"/datastores/{datastore}"
            f"/featuretypes?recalculate=nativebbox,latlonbbox"
        ),
    ]
    featuretype_kwargs = {
        "headers": {
            "Content-Type": "text/xml",
        },
        "data": f"<featureType><name>{layer_name}</name></featureType>",
    }
    featuretype_results = await retry(
        "POST",
        session.post,
        args=featuretype_args,
        kwargs=featuretype_kwargs,
        max_fails=max_post_fails,
    )
    result.featuretype_results = featuretype_results

    if not featuretype_results or not featuretype_results[-1].success:
        return result

    # post_results = await retry(
    #     "POST",
    #     session.post,
    #     args=workspace_args,
    #     kwargs=workspace_kwargs,
    #     max_fails=max_post_fails,
    # )
    # result.post_results = post_results

    # if not post_results or not post_results[-1].success:
    #     LOG.error(f"No successful POST, skipping GETs: {post_results!r}")
    #     return result

    get_results = await retry(
        "GET",
        session.get,
        args=[url],
        kwargs={},
        max_fails=max_get_fails,
    )
    result.get_results = get_results

    return result


async def test_nodes(node_names):

    # this coro runs test_node once for each node
    # it aggregates their report information

    results = []
    start = time.monotonic()

    username = "admin"  # ??
    password = "geoserver"
    auth = aiohttp.BasicAuth(username, password)
    async with aiohttp.ClientSession(auth=auth) as session:

        futures = [test_node(session, node_name) for node_name in node_names]
        logging.debug(f"futures: {futures}")

        # results = await asyncio.gather(*futures, return_exceptions=True)
        results = await asyncio.gather(*futures)

    end = time.monotonic()
    duration = round(end - start, 4)
    LOG.debug(f"Finished in {duration}s.\n")
    return results


def summary_text(values):
    # drop None values to avoid mucking up the statistics
    values = [value for value in values if value is not None]
    if not values:
        return "no data to report"
    text = dedent(f"""
        values: {values}
        count : {len(values)}
        min   : {min(values)}
        mean  : {statistics.mean(values)}
        median: {statistics.median(values)}
        max   : {max(values)}
    """).strip()
    return text


def report(results):
    for result in results:
        if isinstance(result, Exception):
            logging.exception(result)

    results = [
        result for result in results
        if not isinstance(result, Exception)
    ]

    for index, result in enumerate(results, 1):
        paragraph = dedent(f"""
            Node #{index}: {result.name}
                url {result.url}
                latency {result.latency}
        """).strip()
        print(paragraph)

    workspace_durations = [result.workspace_duration for result in results]
    datastore_durations = [result.datastore_duration for result in results]
    featuretype_durations = [result.featuretype_duration for result in results]
    get_durations = [result.get_duration for result in results]
    latencies = [result.latency for result in results]

    for label, variable in [
        ("Workspace POST durations", workspace_durations),
        ("Datastore POST durations", datastore_durations),
        ("FeatureType POST durations", featuretype_durations),
        ("GET durations", get_durations),
        ("Latencies", latencies),
    ]:
        if not variable:
            print("no data to report")
        else:
            print(f"\n{label}")
            print(indent(summary_text(variable), "  "))


def run(async_function, *args, **kwargs):
    return asyncio.get_event_loop().run_until_complete(
        async_function(*args, **kwargs)
    )


def main():
    logging.basicConfig(level=logging.DEBUG)
    parser = argument_parser()
    options = parser.parse_args()
    LOG.debug(f"options: {options}")
    results = run(test_nodes, options.node_names)
    report(results)


main()

