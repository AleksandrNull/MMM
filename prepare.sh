#!/bin/bash
REGISTRY="127.0.0.1:5000/qa"
MY_PATH="`dirname \"$0\"`" 
MY_PATH="`( cd \"$MY_PATH\" && pwd )`"

for i in master minion mariadb; do
  docker build -t $REGISTRY/$i $MY_PATH/$i/
  docker push $REGISTRY/$i
done

