# -*- coding: cp936 -*-
from ProductPageHelper import *
from OrderPageHelper import *
import urllib, urllib2
import cookielib


if __name__=="__main__":

        userName = ''
        password = ''
        productAddress = ''
        size = repr('')
        color = repr('')
 	
	#Login        
        args = {
                'TPL_username':userName,
                'TPL_password':password,
                'TPL_checkcode':'',
                'need_check_code':'',
                '_tb_token_':'3ae3d5fe1558',
                'action':'Authenticator',
                'event_submit_do_login':'anything',
                'TPL_redirect_url':'',
                'from':'tb',
                'fc':'2',
                'style':'default',
                'css_style':'',
                'tid':'XOR_1_000000000000000000000000000000_6A583326340B7D790D7C017F',
                'support':'000001',
                'CtrlVersion':'1%2C0%2C0%2C7',
                'loginType':'3',
                'minititle':'',
                'minipara':'',
                'umto':'Tc3d70457869e730a9a1c0256c50b5d0e%2C200',
                'pstrong':'2',
                'llnick':'',
                'sign':'',
                'need_sign':'',
                'isIgnore':'',
                'full_redirect':'',
                'popid':'',
                'callback':'',
                'guf':'',
                'not_duplite_str':'',
                'need_user_id':'',
                'poy':'',
                'gvfdcname':'10',
                'gvfdcre':'',
                'from_encoding':''}
        encoded_args = urllib.urlencode(args)
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        opener.addheaders = [('User-agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.861.0 Safari/535.2')]
        urllib2.install_opener(opener)

        request = urllib2.Request("https://login.taobao.com/member/login.jhtml", encoded_args)

        request.add_header('User-agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.861.0 Safari/535.2')
        request.add_header('Host', 'login.taobao.com')
        request.add_header('Referer', 'https://login.taobao.com/member/login.jhtml')
        request.add_header("Cache-Control", "max-age=0")
        request.add_header("Origin", "https://login.taobao.com")
           
        response = urllib2.urlopen(request, encoded_args)

        #Start auction.
        #Get auction page source code.
        req = urllib2.Request(productAddress)
        r = urllib2.urlopen(req)
        productPage = r.read()        
        
        pageParser = PageParser()
        pageParser.feed(productPage)
        #Get orderAddress
        orderAddress = pageParser.getProductActionAddress()

        #TODO Skuid/questionAnswer
        
        #Get productFormContent productProperties productSkuMap && productSkuInfomation
        productFormContent = pageParser.getProductFormContent()
        # Use these two info to fill the blank in product input messages.
        productProperties = pageParser.getProductProperties()
        specItemList = GetProSpecItemList(productPage)

        #TODO Get the specific skuid and skuinfo by size, color and ...
        #Guess what, I find that skuinfo will never be used. What the hell!

        #Set product post data
        print  productProperties[color]
        postData = GeneratePostData(productFormContent, specItemList, productProperties[size], productProperties[color])
        
        #Get order page source code.
        reqBuy = urllib2.Request(orderAddress)
        
        reqBuy.add_header('User-agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.861.0 Safari/535.2')
        reqBuy.add_header('Host', 'buy.taobao.com')
        reqBuy.add_header('Referer', productAddress)
        reqBuy.add_header("Cache-Control", "max-age=0")
        reqBuy.add_header("Origin", "item.taobao.com")
        reqBuy.add_header("Connection", "keep-alive")
        respBuy = urllib2.urlopen(reqBuy, postData)
        orderPage = respBuy.read()

        #Submit final order
        orderPageParser = OrderPageParser()
        orderPageParser.feed(orderPage)
        submitAddress = orderPageParser.getOrderActionAddress()

	#Set order post data
        postData = orderPageParser.getOrderPostData()

        reqOrder = urllib2.Request("http://buy.taobao.com" + submitAddress)
        reqOrder.add_header('User-agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.861.0 Safari/535.2')
        reqOrder.add_header('Host', 'buy.taobao.com')
        reqOrder.add_header('Referer', "http://buy.taobao.com/auction/buy_now.jhtml")
        reqOrder.add_header("Cache-Control", "max-age=0")
        reqOrder.add_header("Origin", "buy.taobao.com")
        reqOrder.add_header("Connection", "keep-alive")

        respOrder = urllib2.urlopen(reqOrder, postData)
        finalPage = respOrder.read()
        
