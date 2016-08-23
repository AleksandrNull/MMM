#!/bin/bash

compname=$(kubectl get pod -l k8s-app=master --namespace=minions -o=jsonpath='{.items[0].metadata.name}')

echo "Connecting to" $compname

kubectl port-forward $compname 8888:8888 --namespace=minions

