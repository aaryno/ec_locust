Locust Tests for Geoserver EC
=============================

Simple Locust config for functional and load testing of Geoserver EC.

Prerequisites: Python and pip should be installed using your package manager.

Run::

    ./install

To run tests that you can manually control with a web interface::

    ./run "https://example.com"

The web interface is then running at::

    http://127.0.0.1:8089/

This prompts you for how many users you want and away it goes, until you get
bored and hit the big red button. Then you can go download CSVs that aggregate
the results of the test. Pretty easy.

If you want to run this headless, see `locust --help`, but here's an example::

    env/bin/locust --no-web --clients=2 --hatch-rate=1

If you want to run distributed tests, see `locust --help` and the locust manual
