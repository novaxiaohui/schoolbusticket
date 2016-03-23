# -*- coding: utf-8 -*-

import hashlib
import web
import lxml
import time
import datetime
import os
import urllib2,json
import pylibmc
from lxml import etree
import web.db
import sae.const

import qrcode

db = web.database(
	dbn='mysql',
	host=sae.const.MYSQL_HOST,
	port=int(sae.const.MYSQL_PORT),
	user=sae.const.MYSQL_USER,
	passwd=sae.const.MYSQL_PASS,
	db=sae.const.MYSQL_DB
)

def Simi(ask):
	ask = ask.encode('UTF-8')
	key="7023cf3b6beb45f2f55ce485dbf7f4fb"
	enask = urllib2.quote(ask)
	baseurl = "http://www.tuling123.com/openapi/api?key=7023cf3b6beb45f2f55ce485dbf7f4fb"
	url = baseurl+ '&info=' + enask
	resp = urllib2.urlopen(url)
 	reson = json.loads(resp.read())
	#text = reson['text']
	return reson

def Timetable():
	replyText=u'''时刻表：
周一至五：
	雁栖湖至玉泉路 早7:20
     玉泉路至雁栖湖 晚3:00
周六、日：
	雁栖湖至玉泉路 早7:20
     玉泉路至雁栖湖 晚6:00'''
	return replyText

def orderInfo(uuid):
	uName=db.query("SELECT Name from User WHERE UserID = $userID",vars={'userID':uuid})[0]['Name']
	ordered=db.query("SELECT * FROM User_Ticket WHERE UserID = $userID ", vars={'userID':uuid})
	ordercount=db.query("SELECT COUNT(*) AS C FROM User_Ticket WHERE UserID = $userID ", vars={'userID':uuid})[0]
	replayText=uName+'-'+uuid+u'已订：\n'
	replyText=replayText
	if ordercount['C']==0:
		replyText=replayText
	else:
		for i in range(ordercount['C']):
			#tic=ordered[i]['TicketID']
					
			tic=db.query("SELECT * FROM Ticket WHERE TicketID = $ticketID ", vars={'ticketID':ordered[i]['TicketID']})[0]
			tic_tid=tic['TicketID']
			tic_date=tic['Date']
			tic_direction=tic['Direction']
			#replayText=tic_direction
			if tic_direction==1:
				string=u'雁栖湖至玉泉路'
			elif tic_direction==0:
				string=u'玉泉路至雁栖湖'
			date_time = datetime.datetime.strptime(tic_date,'%Y-%m-%d')
			today_time=datetime.datetime.today()
			if date_time+ datetime.timedelta(days=1) >= today_time :  ##当天订票显示
				replayText=replayText+tic_tid+':'+tic_date+'-- '+string+'\n'
		replyText=replayText
	return replyText


def validateStudent(uuid,passwd):
	res=db.query("SELECT COUNT(*) AS C FROM User WHERE userID = $id AND Password = $password",vars={'id':uuid,'password':passwd})[0]
	ifvalid=res['C']
	return ifvalid

last_lock=0

class WeixinInterface:
    
    
 
	def __init__(self):
		self.app_root = os.path.dirname(__file__)
        
		self.templates_root = os.path.join(self.app_root, 'templates')
		#sys.path.insert(0, os.path.join(app_root, 'qrcode-5.1')) 
		self.render = web.template.render(self.templates_root)
 
	def GET(self):
        #获取输入参数
		data = web.input()
		signature=data.signature
		timestamp=data.timestamp
		nonce=data.nonce
		echostr=data.echostr
        #自己的token
		token="schoolbusticket" #这里改写你在微信公众平台里输入的token
        #字典序排序
		list=[token,timestamp,nonce]
		list.sort()
		sha1=hashlib.sha1()
		map(sha1.update,list)
		hashcode=sha1.hexdigest()
        #sha1加密算法        
 
        #如果是来自微信的请求，则回复echostr
		if hashcode == signature:
			return echostr
        
        

    
    
	def POST(self):        
		str_xml = web.data() #获得post来的数据
		xml = etree.fromstring(str_xml)#进行XML解析
		#content=xml.find("Content").text#获得用户所输入的内容
		msgType=xml.find("MsgType").text
		fromUser=xml.find("FromUserName").text
		toUser=xml.find("ToUserName").text
		mc=pylibmc.Client() #初始化一个memcache实例保存用户操作
		today=datetime.date.today()
        
		if msgType == "event":
			mscontent = xml.find("Event").text
			if mscontent == "subscribe":
				replayText = u'欢迎关注我，我是国科大校车订票系统，很高兴为您服务，输入help查看操作指令'
				return self.render.reply_text(fromUser,toUser,int(time.time()),replayText)

        
		if msgType == 'text':
			today=datetime.date.today()
			content=xml.find("Content").text
			if content.lower() == 'help':
				replayText = u'''1.查询余票\n2.订校车票\n3.订单信息\n4.乘车时间\n5.退校车票\n
或者点击URL 登录网页版订票'''
				orderurl="schoolbusbookdemo.sinaapp.com"
				replayText=replayText+orderurl
				return self.render.reply_text(fromUser,toUser,int(time.time()),replayText)
            
			if content.lower() == 'bye':
				mc.delete(fromUser+'_simi')
				return self.render.reply_text(fromUser,toUser,int(time.time()),u'您已退出了和小黄鸡的交谈中，输入help来显示操作指令')
            
			if content.lower()=='simi':
				mc.set(fromUser+'_simi','simi')
				return self.render.reply_text(fromUser,toUser,int(time.time()),u'小黄鸡is ready，请尽情调戏吧！输入bye退出交谈')
                
            
			if content.startswith('4') or content== '时间':
				replayText=Timetable()
				return self.render.reply_text(fromUser,toUser,int(time.time()),replayText)
            
            
            
            
			if content.startswith('1') or content == '查询余票':
				#curDate = time.strftime('%Y-%m-%d',time.localtime())
				
				direction=1
				#replayText=today + datetime.timedelta(days=1)
				replayText=u'余票信息：\n雁栖湖至玉泉路:\n'+today.strftime("%Y-%m-%d")+u' 余 '\
                +str(db.query("SELECT * FROM Ticket WHERE Date = $date AND Direction = $direction", vars={'direction':1,'date':today.strftime("%Y-%m-%d")})[0].Remain)+'\n'\
				+(today + datetime.timedelta(days=1)).strftime("%Y-%m-%d")+u' 余 '\
				+str(db.query("SELECT * FROM Ticket WHERE Date = $date AND Direction = $direction", vars={'direction':1,'date':(today + datetime.timedelta(days=1)).strftime("%Y-%m-%d")})[0].Remain)+'\n'\
				+(today + datetime.timedelta(days=2)).strftime("%Y-%m-%d")+u' 余 '\
				+str(db.query("SELECT * FROM Ticket WHERE Date = $date AND Direction = $direction", vars={'direction':1,'date':(today + datetime.timedelta(days=2)).strftime("%Y-%m-%d")})[0].Remain)+'\n'\
                +u'玉泉路至雁栖湖：\n' +today.strftime("%Y-%m-%d")+u' 余 '\
                +str(db.query("SELECT * FROM Ticket WHERE Date = $date AND Direction = $direction", vars={'direction':0,'date':today.strftime("%Y-%m-%d")})[0].Remain)+'\n'\
				+(today + datetime.timedelta(days=1)).strftime("%Y-%m-%d")+u' 余 '\
				+str(db.query("SELECT * FROM Ticket WHERE Date = $date AND Direction = $direction", vars={'direction':0,'date':(today + datetime.timedelta(days=1)).strftime("%Y-%m-%d")})[0].Remain)+'\n'\
				+(today + datetime.timedelta(days=2)).strftime("%Y-%m-%d")+u' 余 '\
				+str(db.query("SELECT * FROM Ticket WHERE Date = $date AND Direction = $direction", vars={'direction':0,'date':(today + datetime.timedelta(days=2)).strftime("%Y-%m-%d")})[0].Remain)+'\n'
				return self.render.reply_text(fromUser,toUser,int(time.time()),replayText)
            
            
            
            
            
            
			if content.startswith('2')or content== '订校车票':

				replayText=u'''输入订票人信息：
格式“#学号#密码#手机号码”'''
				return self.render.reply_text(fromUser,toUser,int(time.time()),replayText)
			if content.startswith('#'):
				content_list=content.split('#')
				userID=content_list[1]
				pwd=content_list[2]
				phone=content_list[3]
				replayText=userID
				mc.set(fromUser+'_uID',userID)
				mc.set(fromUser+'_upwd',pwd)
				mc.set(fromUser+'uphone',phone)
                #def validateStudent(studentid,passwd):
				#res=db.query("SELECT COUNT(*) AS C FROM User WHERE userID = $id AND Password = $password",vars={'id':userID,'password':pwd})[0]
				ifvalid=validateStudent(userID,pwd)
				if(ifvalid<1):
					replayText=u'学号或密码输入错误'
				else:
					replayText=u'选择订票类型：\n雁栖湖至玉泉路:\n'\
					+u'D01. '+today.strftime("%Y-%m-%d")+'\n'\
					+u'D02. '+(today + datetime.timedelta(days=1)).strftime("%Y-%m-%d")+'\n'\
					+u'D03. '+(today + datetime.timedelta(days=2)).strftime("%Y-%m-%d")+'\n'\
					+u'玉泉路至雁栖湖：\n'\
					+u'D04. '+today.strftime("%Y-%m-%d")+'\n'\
					+u'D05. '+(today + datetime.timedelta(days=1)).strftime("%Y-%m-%d")+'\n'\
					+u'D06. '+(today + datetime.timedelta(days=2)).strftime("%Y-%m-%d")+'\n'\
					+u'''PS：输入时间前的编码订票
建议先输入“1”查看“余票”
只能订两天以内车票^ ^'''
				return self.render.reply_text(fromUser,toUser,int(time.time()),replayText)
    		#mcxhj = mc.get(fromUser+'_uID') 
			if content.startswith('D0'):
				tno=content.split('0')[1]
				uID=mc.get(fromUser+'_uID')
				#replayText=tno
				ordirection=1
				orderdate=today.strftime("%Y-%m-%d")
				if(tno=='1'):
					ordirection=1
  					orderdate=today.strftime("%Y-%m-%d")

				if(tno=='2'):
					ordirection=1
					orderdate=(today + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
				if(tno=='3'):
					ordirection=1
					orderdate=(today + datetime.timedelta(days=2)).strftime("%Y-%m-%d")				
				if(tno=='4'):
					ordirection=0
					orderdate=today.strftime("%Y-%m-%d")
				if( tno=='5'):
					ordirection=0
					orderdate=(today + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
				if(tno=='6'):
					ordirection=0
					orderdate=(today + datetime.timedelta(days=2)).strftime("%Y-%m-%d")
                    
				res=db.query("SELECT * FROM Ticket WHERE Date = $date AND Direction = $direction  FOR UPDATE ", vars={'direction':ordirection,'date':orderdate})[0]
				curremain=res.Remain
				tID=res.TicketID
				tip=u'''请选择其他日期或路线
输入“2”选择订票类型^ ^'''
                
				if(curremain <= 0):
					replayText=u'余票为0'+tip
                
                    
				else:
					ifordered=db.query("SELECT 	COUNT(*)AS C FROM User_Ticket WHERE UserID = $userID AND TicketID = $ticketID", vars={'userID':uID,'ticketID':tID})[0]
					if ifordered['C'] >0:
						replayText=u'您已经订过该时间该路线的车票'+tip
						#replayText=ifordered['C']
					else:
                        
						db.query("UPDATE  Ticket SET Remain= $remain -1 WHERE  Date = $date AND Direction = $direction", vars={'remain':curremain,'direction':ordirection,'date':orderdate})
						res=db.query("SELECT * FROM Ticket WHERE Date = $date AND Direction = $direction  FOR UPDATE ", vars={'direction':ordirection,'date':orderdate})[0]
						curremain=res.Remain
						if(curremain<0):
							db.query("UPDATE  Ticket SET Remain= $remain +1 WHERE  Date = $date AND Direction = $direction", vars={'remain':curremain,'direction':ordirection,'date':orderdate})
							replayText=u'余票为0'+tip
 						else:
							db.query("INSERT INTO  User_Ticket (UserID,TicketID) VALUES ($userID,$ticketID)",vars={'userID':uID,'ticketID':tID})
						replayText=u'订票成功，车票号为：'+tID +u'输入“detail”或“订单信息”查看订单'

						#qr = qrcode.QRCode(
						#version=2,
						#error_correction=qrcode.constants.ERROR_CORRECT_L,
						#box_size=10,
						#border=1
						#)
						#qr.add_data(uID+"::"+orderdate+"::"+string+"::"+tID)
						#qr.make(fit=True)
						#img = qr.make_image()
						#img.save("ticket_qrcode.png")
				#replayText='abc (toUser,fromUser,createTime,replayText,title,description,picurl,url)'
						title=u'订票成功，车票信息：'
						description=u'出示二维码乘车'
						ask=uID+'+'+orderdate+'+'+str(ordirection)+'+'+str(tID)
						ask = ask.encode('UTF-8')
						enask = urllib2.quote(ask)
						baseurl = "http://qrcoder.sinaapp.com?t="+enask+"&f=json"
						url = baseurl
						resp = urllib2.urlopen(url)
				#replayText=resp
 						reson = json.loads(resp.read())
						replayText=u'订票成功，车票号为：'+tID +u'\n输入“detail”或“订单信息”查看订单,车票二维码：'+reson['url']
				#api="http://qrcoder.sinaapp.com?t=hello world"
				#response = urllib2.urlopen(api)
				#html = response.read()
				#qrcodeinfo = json.loads(html)
				#picurl=qrcodeinfo['url']
				#text=qrcodeinfo['text']
				#url=picurl
				return self.render.reply_text(fromUser,toUser,int(time.time()),replayText)
				#return self.render.reply_article(fromUser,toUser,int(time.time()),title,description,picurl,url)
                
                
                
                
			if content.lower()=='detail':    ###当前用户全部订票信息
				uID=mc.get(fromUser+'_uID')

				replayText=orderInfo(uID)
				return self.render.reply_text(fromUser,toUser,int(time.time()),replayText)	
            
			if content.startswith('3'):
				replayText=u'''查看订单，请输入订票人信息：
格式“&学号”'''
				return self.render.reply_text(fromUser,toUser,int(time.time()),replayText)
			if content.startswith('&'):
				content_list=content.split('&')
				userID=content_list[1]
				replayText=orderInfo(userID)
				return self.render.reply_text(fromUser,toUser,int(time.time()),replayText)
            
            
            
            
			if content.startswith('5')or content== '退校车票':
				replayText=u'''退票操作，请输入订单信息：
格式“@学号@密码@车票号”
'''
				return self.render.reply_text(fromUser,toUser,int(time.time()),replayText)
			if content.startswith('@'):
				content_list=content.split('@')
				userID=content_list[1]
				pwd=content_list[2]
				tID=content_list[3]
				ifvalid=validateStudent(userID,pwd)
				if(ifvalid<1):
					replayText=u'学号或密码输入错误'
				else:
					ifordered=db.query("SELECT 	COUNT(*)AS C FROM User_Ticket WHERE UserID = $userID AND TicketID = $ticketID", vars={'userID':userID,'ticketID':tID})[0]
					if ifordered['C'] >0:
						db.query("DELETE FROM User_Ticket WHERE UserID = $userID AND TicketID = $ticketID", vars={'userID':userID,'ticketID':tID})
						db.query("UPDATE  Ticket SET Remain= Remain +1 WHERE   TicketID = $ticketID", vars={'ticketID':tID})
						replayText=u'退票成功，感谢您的通知'
					else:
						replayText=u'没有该订单，请确认后再退票'
				return self.render.reply_text(fromUser,toUser,int(time.time()),replayText)
            
                
            
			mcsimi = mc.get(fromUser+'_simi')
             
			if mcsimi =='simi':
				res = Simi(content)
				replytext = res['text']
                #reply_text = res['response']
                #if u'微信' in reply_text:
                #    reply_text = u"小黄鸡脑袋出问题了，请换个问题吧~" 
				return self.render.reply_text(fromUser,toUser,int(time.time()),replytext)  
            
            
			else:
				#replayText = u'输入help查看操作指令,正在开发中，敬请期待，您刚刚说'+content
				replayText = u'''输入help查看操作指令
输入simi调戏小黄鸡！'''
				return self.render.reply_text(fromUser,toUser,int(time.time()),replayText)
			logging.debug("debug log ")
            
	