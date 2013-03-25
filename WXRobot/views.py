# coding=utf-8
from django.http import HttpResponse
import hashlib, time, re
from xml.etree import ElementTree as ET
      
def weixin(request):
    token = "hugoye"
    params = request.GET
    args = [token, params['timestamp'], params['nonce']]
    args.sort()
    if hashlib.sha1("".join(args)).hexdigest() == params['signature']:
        if params.has_key('echostr'):
            return HttpResponse(params['echostr'])
        else:
            reply = """<xml>
				<ToUserName><![CDATA[%s]]></ToUserName>
			    <FromUserName><![CDATA[%s]]></FromUserName>
                <CreateTime>%s</CreateTime>
                <MsgType><![CDATA[text]]></MsgType>
                <Content><![CDATA[%s]]></Content>
                <FuncFlag>0</FuncFlag>
                </xml>"""
            if request.raw_post_data:
                xml = ET.fromstring(request.raw_post_data)
                content = xml.find("Content").text
                fromUserName = xml.find("ToUserName").text
                toUserName = xml.find("FromUserName").text
                postTime = str(int(time.time()))
                if not content:
                    return HttpResponse(reply % (toUserName, fromUserName,
                        postTime, "Please try to input some command!"))
                if content == "hello":
                    return HttpResponse(reply % (toUserName, fromUserName,
                        postTime, "Hello world!"))
                else:
                    return HttpResponse(reply % (toUserName, fromUserName,
                        postTime, "Please try to input some other command!")) 
            else:
                return HttpResponse("Invalid Request")
    else:
        return HttpResponse("Invalid Request")


