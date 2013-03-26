# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.template import RequestContext, Template
from django.views.decorators.csrf import csrf_exempt
from django.utils.encoding import smart_str, smart_unicode

import xml.etree.ElementTree as ET
import urllib, urllib2, time, hashlib

import requests
import random

TOKEN = "hugoye"

try:
    from settings import SIMSIMI_KEY
except:
    SIMSIMI_KEY = ''


class SimSimi:

    def __init__(self):

        self.session = requests.Session()

        self.chat_url = 'http://www.simsimi.com/func/req?lc=ch&msg=%s'
        self.api_url = 'http://api.simsimi.com/request.p?key=%s&lc=ch&ft=1.0&text=%s'

        if not SIMSIMI_KEY:
            self.initSimSimiCookie()

    def initSimSimiCookie(self):
        self.session.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:18.0) Gecko/20100101 Firefox/18.0'})
        self.session.get('http://www.simsimi.com/talk.htm')
        self.session.headers.update({'Referer': 'http://www.simsimi.com/talk.htm'})
        self.session.get('http://www.simsimi.com/talk.htm?lc=ch')
        self.session.headers.update({'Referer': 'http://www.simsimi.com/talk.htm?lc=ch'})

    def getSimSimiResult(self, message, method='normal'):
        if method == 'normal':
            r = self.session.get(self.chat_url % message)
        else:
            url = self.api_url % (SIMSIMI_KEY, message)
            r = requests.get(url)
        return r

    def chat(self, message=''):
        if message:
            r = self.getSimSimiResult(message, 'normal' if not SIMSIMI_KEY else 'api')
            try:
                answer = r.json()['response'].encode('utf-8')
                return answer

            except:
                return random.choice(['Hehe', '...', '= =', '=. ='])
        else:
            return 'What?'


def handleMsg(data):
    simsimi = SimSimi()
    return simsimi.chat(data)

def testMsg(request):
    simsimi = SimSimi()
    if request.method == 'GET':
        data = request.GET.get("data", 'hello')
        reply = simsimi.chat(data)
        #reply = smart_unicode(reply)
        #print reply
        return HttpResponse(reply, content_type = "text/plain; charset=UTF-8")
    else:
        return HttpResponse("Invalid Request")


@csrf_exempt
def handleRequest(request):
    if request.method == 'GET':
        response = HttpResponse(checkSignature(request), content_type =
                "text/plain")
        return response
    elif request.method == 'POST':
        response = HttpResponse(responseMsg(request), content_type =
                "application/xml")
        return response
    else:
        return HttpResponse("Invalid Request")

def checkSignature(request):
    global TOKEN
    signature = request.GET.get("signature", None)
    timestamp = request.GET.get("timestamp", None)
    nonce = request.GET.get("nonce", None)
    echostr = request.GET.get("echostr", None)

    token = TOKEN
    tmplist = [token, timestamp, nonce]
    tmplist.sort()
    tmpstr = "%s%s%s" % tuple(tmplist)
    tmpstr = hashlib.sha1(tmpstr).hexdigest()
    if tmpstr == signature:
        return echostr
    else:
        return "Hehe!"

def responseMsg(request):
    rawStr = smart_str(request.raw_post_data)
    msg = paraseMsgXml(ET.fromstring(rawStr))

    queryStr = msg.get('Content', 'input nothing')
    print queryStr

    replyContent = "Hello world!"
    #replyContent = handleMsg(queryStr)
    print replyContent

    return getReplyXml(msg, replyContent)

def paraseMsgXml(rootElem):
    msg = {}
    if rootElem.tag == 'xml':
        for child in rootElem:
            msg[child.tag] = smart_str(child.text)
    return msg

def getReplyXml(msg, replyContent):
    extTpl = "<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[%s]]></MsgType><Content><![CDATA[%s]]></Content><FuncFlag>0</FuncFlag></xml>";
    extTpl = extTpl % (msg['FromUserName'],msg['ToUserName'],str(int(time.time())),'text',replyContent)
    return extTpl

