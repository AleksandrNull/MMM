#!/bin/bash
kubectl create -f minion-rc.yaml
echo "Start time: $(date "+%s%N")"

