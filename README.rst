BCS Locust Config
=================

This is a simple locust config for running functional tests or load tests
which exercise deployments of the BCS APIs.

Right now, this can be used for checking that a deployment works in a basic
way, e.g. that certain endpoints are working and return the expected HTTP
status in a reasonable amount of time. Like as a basic health or sanity check.

It would also be relatively easy to make Locust simulate realistic workloads
that mimic activity from production logs, do round-the-clock random fuzzing, or
use a cluster to pound a deployment until it falls over. Or test functionality
in more detail. Whatever.


Locust
------

`Locust <http://docs.locust.io/>`_ is a load testing tool which can be used
over HTTP. However, it is a bit different from tools like `ab` or JMeter.
Locust can generate swarms of simulated users with behavior specified in simple
Python. It's easy to use, it can easily handle thousands of simulated users
using coroutines, and it can easily be run in a distributed fashion. 


How to use
----------

To use this, you should have a version of Python that is not like 10 years old,
which means that Python versions 2.7 or preferably 3.2+ should do.

It would normally be wise to start by creating a virtualenv. Any method will
do, but I recommend using `vex` to make this simple, e.g.::

    vex -m loadtest

Then, from within your virtualenv, in the repo directory, install the
dependencies with::

    ./install

(This really just runs ``pip install -r requirements.txt``.)

This repo includes a Python file, `tasks.py`, defining what locust should do
with the BCS APIs.

To run locust with the specified config, you can use the included bash script
named `run`::

    ./run

Or equivalently use the same kind of command line to specify the host you want
to test, e.g.::

    locust -f tasks.py --host="https://api.dev.boundlessgeo.io"

In any case, this does not start the test immediately, but launches a web
interface accessible at::

    http://127.0.0.1:8089/

It prompts you for how many users you want and away it goes, until you get
bored and hit the big red button. Then you can go download CSVs that aggregate
the results of the test. Pretty easy.

You have to know a little Python to edit `tasks.py` but the HTTP API is based
on `requests` and it's all pretty simple.

If you want to run it headless, just read `locust --help` for a while and
you'll figure it out.

See the locust manual for details on how to run distributed tests, but the same
code should work as-is.

If you would prefer a Makefile or something, let me know.
