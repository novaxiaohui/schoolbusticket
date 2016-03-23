# -*- coding: utf8 -*-
  
import os
import json
import urllib2
  
  
class Chat(object):
	key = "7023cf3b6beb45f2f55ce485dbf7f4fb"    # tuling123网站
	apiurl = "http://www.tuling123.com/openapi/api?"
  
	def init(self):
		os.system("clear")
		replyText=u "尽情调教小黄鸡吧!"
		print "-------------------------------"
  
	def get(self):
		print "> ",
		info = raw_input()
		if info == ('q' or 'exit' or "quit"):
			print "- Goodbye"
			return
		self.send(info)
  
	def send(self, info):
		url = self.apiurl + 'key=' + self.key + '&' + 'info=' + info
		re = urllib2.urlopen(url).read()
		re_dict = json.loads(re)
		text = re_dict['text']
		print '- ', text
		self.get()
  
  
if __name__ == "__main__":
    chat = Chat()
    chat.init()
    chat.get()