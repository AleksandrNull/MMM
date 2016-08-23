#!/bin/bash

kubectl create namespace minions
kubectl create -f mysql.yaml

kub="kubectl --namespace=minions"

while ! $kub get pods|grep mysql|grep -i Running|cut -f1 -d" "|grep mysql;do
  sleep 5
done

cnt=`$kub get pods|grep mysql|grep -i Running|cut -f1 -d" "`

while ! $kub exec -ti $cnt -- test -f /tmp/mariadb_ok; do
  sleep 5
done

kubectl create -f master.yaml

echo "Done"
