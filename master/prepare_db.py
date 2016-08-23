from flask import Flask
from flaskext.mysql import MySQL

def trydb(cursor,query):
  try:
    cursor.execute(query)
    connection.commit()
  except Exception as e:
    print ("Query: %s wasn't successfull with error: %s." % (query,e))
    pass
 
def prepare():
  app = Flask(__name__)
  mysql_setup = MySQL()
  app.config['MYSQL_DATABASE_USER'] = 'root'
  app.config['MYSQL_DATABASE_PASSWORD'] = 'swordfish'
  app.config['MYSQL_DATABASE_HOST'] = 'mysql'
  app.config['MYSQL_DATABASE_DB'] = 'master'
  mysql_setup.init_app(app)
  connection=mysql_setup.connect()
  cursor = connection.cursor()
  trydb(cursor,"CREATE DATABASE `master` DEFAULT CHARSET=utf8;")
  trydb(cursor,"CREATE TABLE `minions` ( \
                  `id` bigint(20) NOT NULL, \
                  `minion_id` varchar(60) NOT NULL, \
                  `last_seen` bigint(20) DEFAULT NULL, \
                  `minion_time` bigint(20) DEFAULT NULL) ;")

  trydb(cursor,"CREATE TABLE `tasks` ( \
                  `id` int(11) NOT NULL, \
                  `task` mediumtext NOT NULL, \
                  `minion_id` varchar(60) NOT NULL, \
                  `token` varchar(60) NOT NULL)") 
  trydb(cursor,"CREATE USER master IDENTIFIED BY 'master';")
  cursor.execute("GRANT USAGE ON *.* TO 'master'@'*';")
  cursor.execute("GRANT ALL PRIVILEGES ON `master`.* TO 'master'@'%' WITH GRANT OPTION;")

if __name__ == '__main__':
    prepare()

