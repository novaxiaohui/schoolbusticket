#import sae
#def app(environ, start_response):
#    status = '200 OK'
#    response_headers = [('Content-type', 'text/plain')]
#    start_response(status, response_headers)
#    return ['Hello, world!']
#application = sae.create_wsgi_app(app)

# -*- coding: utf-8 -*-

import os
import sys
import sae
import web
import xml.etree.ElementTree as ET
import sae.const
import MySQLdb
import urllib2
import json

app_root = os.path.dirname(__file__)
templates_root = os.path.join(app_root, 'templates')
sys.path.insert(0, os.path.join(app_root, 'qrcode-5.1')) 
sys.path.insert(0, os.path.join(app_root, 'six-1.9.0'))
render = web.template.render(templates_root)

import model
import qrcode
from weixinInterface import WeixinInterface
from customMenu import CreateMenu,DeleteMenu


 
urls = (

'/weixin','WeixinInterface',
'/create','CreateMenu',
'/delete','DeleteMenu',
'/ck','ckTicket',
'/ckre','ckRemain',
'/image','ticketImage'

)
class ticketImage:
	def GET(self):
		tmp="hello world"
		return render.QRcode(tmp)
class ckTicket:
	def GET(self):
		Ticketcontent = model.getTicketcontent()
		print Ticketcontent
		return render.checkTicket(Ticketcontent)

class ckRemain:
	def GET(self):
		Remaincontent=model.getRemain()
		return render.checkRemain(Remaincontent)
    
app = web.application(urls, globals()).wsgifunc()        
application = sae.create_wsgi_app(app)