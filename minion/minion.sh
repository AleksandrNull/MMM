#!/bin/bash

time=$(date "+%s%N")
id=$(uuidgen)
env=$(echo {$(export -p |grep MINION_|cut -f3 -d" "|awk -F "=" 'NR > 1 { printf(",") } { printf("\"%s\":%s", $1, $2) }')}|base64)
curl "http://master:8888/register?minion_id=${id}&minion_time=${time}&env=${env}"
sleep 1000000
