"""Assumes Python 3.6+
"""
import argparse
import time
import csv
import requests
import logging

# input: csv file showing how many users, how many minutes, one per line
# e.g., `10,120` = 10 users for 120 minutes

LOG = logging.getLogger("simulate_variable_usage")
csv_file=None

def argument_parser():
    parser = argparse.ArgumentParser(
        description="Run load test with variable amount of users specified by csv file of format (users, duration[min])",
    )
    parser.add_argument(
        "--host",
        default="dev.geoserver-ec.boundlessgeo.com",
    )
    parser.add_argument(
        "--csv-file",
        default="usage_load.csv",
    )
    return parser


def read_load_csv(csv_file): 
    return list(csv.reader(open(csv_file)))

def start_test(host,users):
    r=requests.post('http://'+host+'/swarm',data={'hatch_rate': 1, 'locust_count': users})
    print("Started test with ",users,":",r.status_code, r.reason)

def stop_test(host):
    r=requests.post('http://'+host+'/stop')
    print("Stopped test:",r.status_code, r.reason)


def run_test_static_users(host,users,duration_min):
    start_test(host,users)
    t_end=time.time()+60*float(duration_min)
    while True:
        if (time.time()>t_end):
            break
        time.sleep(1)
    stop_test(host)

def run_test_dynamic(host,usage_load_table):
    for r in range(len(usage_load_table[0])):
        users=usage_load_table[r][0]
        duration_min=usage_load_table[r][1]
        print("Running test with",users,"for",duration_min,"minutes")
        run_test_static_users(host,users,duration_min)


def main():
    parser = argument_parser()
    options = parser.parse_args()
    LOG.debug(f"options: {options}")
    usage_load_table=read_load_csv(options.csv_file)
    run_test_dynamic(options.host,usage_load_table)


main()