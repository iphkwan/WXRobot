# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.template import RequestContext, Template
from django.views.decorators.csrf import csrf_exempt
from django.utils.encoding import smart_str, smart_unicode

import xml.etree.ElementTree as ET
import urllib, urllib2, time, hashlib

TOKEN = "hugoye"

@csrf_exempt
def handleRequest(request):
    if request.method == 'GET':
        response = HttpResponse(checkSignature(request), content_type =
                "text/plain")
        return response
    elif request.method == 'POST':
        response = HttpResponse(responseMsg(request), content_type =
                "text/plain")
        return reponse
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
    print rawStr
    msg = paraseMsgXml(ET.fromstring(rawStr))
    print msg

    queryStr = msg.get('Content', 'input nothing')
    print queryStr

    replyContent = "Hello world!"
    return getReplyXml(msg, replyContent)

def paraseMsgXml(rootElem):
    msg = {}
    if rootElem.tag == 'xml':
        for child in rootElem:
            msg[child.tag] = smart_str(child.text)
    return msg

def getReplyXml(msg, replyContent):
    reply ="<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[%s]]></MsgType><Content><![CDATA[%s]]></Content><FuncFlag>0</FuncFlag></xml>";

    reply = reply % (msg['FromUserName'],msg['ToUserName'],str(int(time.time())),'text',replyContent)

    return reply
