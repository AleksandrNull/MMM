MMM(MySQL/Master/Minions) testing suite
---------------------------------------

This is a pretty simple client/server set for testing speed of k8s/docker/
networking scheduling capabilies speed.

Architecture is pretty simple and consists of the following:
- mariadb/mysql service (replication controller with only one replica)
- master service, a simple python app based on flask with multiple threads
and producer/consumer queue for SQL inserts.
- minion replication controller is a simple bash script which registers minion
on master service.

Preparing environment
---------------------

This toolkit relies on your existing k8s infrastructure. It will use kubectl for
all k8s related operations so it also relies that kubectl will use its own
config file to access k8s cluster. Toolkit also relies on existing docker
registry or any other images storage which provides docker registry api. Little
to none network knowledge is required to be able to handle NAT to master service
from node where kubectl was ran. Toolkit also needs to have locally available
docker service to build images on.
Toolkit will create and use 'minions' namespace to work with. When testing is
considered done and/or you need to cleanup the environment you may just delete
the minions namespace.

To prepare and push images to the registry you need to first open prepare.sh file
and fix registry address. By default it's 127.0.0.1:31500. After that you could
run prepare.sh and wait till images got built. Remember you have to change
registry address in minions.yaml, mysql.yaml and master.yaml files also. Once
images are prepared master/mysql services set could be started by running
run-master.sh script.

When master is ready it should be accessible inside of k8s cloud but not outside
because usually dev clusters don't have proper external LB configured. The
easiest way to overcome that is to do port-forward of master-service port to any
node which you have kubectl on or manually. For the simple use-case there is a
proxy.sh script which will do local 127.0.0.1 8888 port mapping to master
service. After that you could expose this port to outside by using
ssh/tcppm/etc.

After everthing is prepared, it would be great to check that master is up and
running and that you have access to the DB. For that you could check URL
http://127.0.0.1:8888/stats
You should get something like:
Registered number of minions: 0 Overall time: 0 seconds

Congrats, you have master/db set deployed.

You have the following URLs to work with:
/stats - show curent statistics
/cleanup - delete all minion information from DB

After that minion-rc.yaml could be run for testing purposes. Before creating
replication controller with tons of minions consider changing the number of
minions to spawn by modifying minion-rc.yaml.

There is few more things to know before start such heavy load test:
- You'll put a lot of stress on k8s scheduler
- If you didn't preload the minion image on k8s worker nodes your docker
registry/repo/etc will be stressed a lot and will probably die. Do that only on
non-production cluster and/or consider preprovisioning minion images by pulling
them on all k8s workers hosts.

To run RC with minions execute the following command:
kubectl create -f minion-rc.yaml

Because of current implementation and python app/mysql settings it's close to
impossible to check stats online but don't worry, you could do that once all
minions will be spawned. Because k8s uses polling(as far as I understand) to
check pods/containers it will show then in ContainerSpawning state pretty long
time after they was actually spawned. Once you're able to see that all the
containers in Runned state you could check stats at master to see how long does
it take to actually boot up all the containers since first one is started.

To cleanup all this mess you may just delete minions namespace and repeat
everything from the beginning(excluding images build with prepare.sh)

TODO.
-----

- web ui to monitor/analize stats
- temp/inmemory tables in mysql
- tasks in app/minions
- many, many, many more things because it's just an example/poc ;)

