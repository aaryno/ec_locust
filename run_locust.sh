#!/bin/bash
if [ -z "$URL" ]; then
    URL="$1"
fi
echo "URL='$URL'"
if [ -z "$URL" ]; then
    echo "please specify a URL"
    exit 1
fi

# if it's already on path, guess we should use that
if [ -n "$(command -v locust)" ]; then
    LOCUST=locust

# otherwise look for ./locust_env
elif [ -d locust_env ] && [ -x "locust_env/bin/locust" ]; then
    LOCUST=locust_env/bin/locust

else
    echo "Can't find a locust to use"
    exit 1
fi

# build data file if it is not present
if [ ! -f "wms_256_tiles.csv" ]; then
    ./mercantile_gen.py
fi

LOGLEVEL=CRITICAL
$LOCUST -f ./wms_tester.py --loglevel="$LOGLEVEL" --host="$URL"
