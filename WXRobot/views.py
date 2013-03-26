# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.template import RequestContext, Template
from django.views.decorators.csrf import csrf_exempt
from django.utils.encoding import smart_str, smart_unicode
from WXRobot.models import SimSimi

import xml.etree.ElementTree as ET
import urllib, urllib2, time, hashlib


TOKEN = "hugoye"


#def handleMsg(data):
#    simsimi = SimSimi()
#    return simsimi.chat(data)

#def testMsg(request):
#    simsimi = SimSimi()
#    if request.method == 'GET':
#        data = request.GET.get("data", 'hello')
#        reply = simsimi.chat(data)
        #reply = smart_unicode(reply)
        #print reply
#        return HttpResponse(reply, content_type = "text/plain; charset=UTF-8")
#    else:
#        return HttpResponse("Invalid Request")


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

