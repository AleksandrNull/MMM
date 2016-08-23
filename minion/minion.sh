#!/bin/bash

time=$(date "+%s%N")
id=$(uuidgen)
curl "http://master:8888/register?minion_id=${id}&minion_time=${time}"
sleep 1000000
