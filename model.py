# _*_ coding:utf-8 _*_
import web
import web.db
import sae.const
import time 
 
db = web.database(
	dbn='mysql',
	host=sae.const.MYSQL_HOST,
	port=int(sae.const.MYSQL_PORT),
	user=sae.const.MYSQL_USER,
	passwd=sae.const.MYSQL_PASS,
	db=sae.const.MYSQL_DB
)

    
def getTicketcontent():
	#return db.select('Ticket', order='Date')
	curDate = time.strftime('%Y-%m-%d',time.localtime())
	return db.query("SELECT * FROM Ticket WHERE Date = $date AND Direction = $direction", vars={'direction':1,'date':curDate})

def getremain():
	#return db.query("SELECT * FROM Ticket WHERE Date =  AND Direction = $direction", vars={'direction':1,'date':2015-06-10})
	return db.select('Ticket', order='Date')