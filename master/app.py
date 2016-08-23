from flask import Flask
from flask import request,make_response
import MySQLdb
import multiprocessing
import time

def trydb(db,query):
  try:
    db.query(query)
  except Exception as e:
    print ("Query: %s wasn't successfull with error: %s." % (query,e))
    pass

def prepare():
  db = MySQLdb.connect("mysql", "root", "swordfish")
  db.autocommit(True)
  trydb(db,"CREATE DATABASE `master` DEFAULT CHARSET=utf8")
  db = MySQLdb.connect("mysql", "root", "swordfish","master")
  trydb(db,"CREATE TABLE `minions` ( \
                  `id` bigint(20) NOT NULL, \
                  `minion_id` varchar(60) NOT NULL, \
                  `last_seen` bigint(20) DEFAULT NULL, \
                  `minion_time` bigint(20) DEFAULT NULL)")
  trydb(db,"CREATE TABLE `tasks` ( \
                  `id` int(11) NOT NULL, \
                  `task` mediumtext NOT NULL, \
                  `minion_id` varchar(60) NOT NULL, \
                  `token` varchar(60) NOT NULL)")
  trydb(db,"CREATE USER master IDENTIFIED BY 'master'")
  trydb(db,"GRANT USAGE ON *.* TO 'master'@'*'")
  trydb(db,"GRANT ALL PRIVILEGES ON `master`.* TO 'master'@'%' WITH GRANT OPTION")

class DBWorker(multiprocessing.Process):
    
    def __init__(self, task_queue, result_queue):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.db = MySQLdb.connect("mysql", "master", "master", "master")
        self.cursor = self.db.cursor()

    def run(self):
        proc_name = self.name
        while True:
            next_task = self.task_queue.get()
            if next_task is None:
                # Poison pill means shutdown
                print '%s: Exiting' % proc_name
                self.task_queue.task_done()
                break
            print '%s: %s' % (proc_name, next_task())
            self.cursor.execute(next_task())
            self.db.commit()
            self.task_queue.task_done()
        return

class Task(object):
    def __init__(self, minion_id,minion_time,last_seen):
        self.minion_id = minion_id
        self.minion_time = minion_time
        self.last_seen = last_seen
    def __call__(self):
        return "INSERT into minions (minion_id,minion_time,last_seen) values ('%s','%s','%s')" % (self.minion_id,self.minion_time,self.last_seen)

prepare()

# Establish communication queues
tasks = multiprocessing.JoinableQueue()
results = multiprocessing.Queue()
    
# Start consumers
num_consumers = multiprocessing.cpu_count() * 2
print 'Creating %d consumers' % num_consumers
consumers = [ DBWorker(tasks, results)
              for i in xrange(num_consumers) ]
for w in consumers:
    w.start()

app = Flask(__name__)

@app.route('/register')
def register():
    minion_id = request.args.get('minion_id')
    minion_time = request.args.get('minion_time')
    if (minion_id):
      tasks.put(Task(minion_id, minion_time, int(time.time()*1000000000)))
      resp = make_response('Minion queued.')
      resp.headers['Content-Type'] = "text/html"    
    else:
      resp = make_response('No UUID to register.')
      resp.headers['Content-Type'] = "text/html"
    return resp

@app.route('/stats')
def stats():
    db = MySQLdb.connect("mysql", "master", "master", "master")
    cursor = db.cursor()
    cursor.execute("SELECT count(*) FROM minions")
    minions = cursor.fetchone()[0]
    cursor.execute("SELECT (max(last_seen) - min(last_seen)) as value FROM `minions`")
    time_diff = cursor.fetchone()[0]
    if (time_diff):
      time=time_diff/1000000000
    else:
      time=0
    resp = make_response('Registered number of minions: %s \n Overall time: %s seconds'% (minions,time))
    resp.headers['Content-Type'] = "text/html"    
    return resp

@app.route('/cleanup')
def cleanup():
    db = MySQLdb.connect("mysql", "master", "master", "master")
    cursor = db.cursor()
    cursor.execute("DELETE FROM minions")
    db.commit()
    resp = make_response("All minions was deleted")
    resp.headers['Content-Type'] = "text/html"           
    return resp

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    resp = make_response('There is no such path: %s' % path)
    resp.headers['Content-Type'] = "text/html"    
    return resp

if __name__ == '__main__':
    app.run(threaded=True,host="0.0.0.0",port=8888)

