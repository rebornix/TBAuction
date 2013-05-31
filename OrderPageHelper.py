# -*- coding: cp936 -*-
"""
OrderPageParser inherits from SGMLParser
"""
from sgmllib import SGMLParser
import re

class InputControl:
    def __init__(self):
        self.control = ''
        self.type = ''
        self.name = ''
        self.value = ''

class CheckCode:
    def __init__(self):
        self.checkCodeUrl = ''
        self.isCheckCode = False
        self.encryterString = ''
        self.sid = ''
        self.gmtCreate = ''
        self.checkCodeIds = ''
        self.checkCode = ''
    
class OrderPageParser(SGMLParser):
    def reset(self):
        SGMLParser.reset(self)
        self.orderActionAddress = ''
        self.orderFormContent = {}
        self.orderFormFind = False
        self.inputControls = []
        self.findCheckUrl = False
        self.checkCode = CheckCode()
        self.findPromotionInitData = False
        self.orderInformationDomain = {}
        self.transport = {}
        self.price = 0
        self.actualFee = 0

    def start_form(self, attrs):                      
        if attrs[0][0] == 'id' and attrs[0][1] == 'J_Form':
            self.orderActionAddress = attrs[2][1]
            self.orderFormFind = True
                                               
    def end_form(self):
        self.orderFormFind = False

    def start_input(self, attrs):
        if self.orderFormFind:
            inputControl = InputControl()
            inputControl.control = 'input'
            for item in attrs:
                if item[0] == 'type':
                    inputControl.type = item[1]
                elif item[0] == 'name':
                    inputControl.name = item[1]
                elif item[0] == 'value':
                    inputControl.value = item[1]
                elif item[0] == 'id' and item[1] == "J_checkCodeUrl":
                    self.findCheckUrl = True
            if self.findCheckUrl:
                self.checkCode.checkCodeUrl = inputControl.value
            self.inputControls.append(inputControl)

            if inputControl.name == 'checkCodeIds':
                self.checkCode.checkCodeIds = inputControl.value
            elif inputControl.name == 'gmtCreate':
                self.checkCode.gmtCreate = inputControl.value
            elif inputControl.name == 'sid':
                self.checkCode.sid = inputControl.value
            elif inputControl.name == 'encryptString':
                self.checkCode.encryterString = inputControl.value
            elif inputControl.name == 'checkCode':
                self.checkCode.checkCode = inputControl.value
                

    def end_input(self):
        self.findCheckUrl = False

    def start_textarea(self, attrs):
        if self.orderFormFind:
            inputControl = InputControl()
            inputControl.control = 'textarea'
            for item in attrs:
                if item[0] == 'type':
                    inputControl.type = item[1]
                elif item[0] == 'name':
                    inputControl.name = item[1]
                elif item[0] == 'value':
                    inputControl.value = item[1]
            self.inputControls.append(inputControl)
        else:
            if attrs[0][0] == 'id' and attrs[0][1] == 'J_OrderInitData':
                self.findPromotionInitData = True

    def end_textarea(self):
        self.findPromotionInitData = False

    def start_select(self, attrs):
        if self.orderFormFind:
            inputControl = InputControl()
            inputControl.control = 'select'
            for item in attrs:
                if item[0] == 'type':
                    inputControl.type = item[1]
                elif item[0] == 'name':
                    inputControl.name = item[1]
                elif item[0] == 'value':
                    inputControl.value = item[1]
            self.inputControls.append(inputControl)

    def end_select(attrs):
        pass

    def handle_data(self, text):
        if self.findPromotionInitData:
            m = re.search("(?<=price\":\")[\d]*(?=\")", text)
            self.price = int(m.group(0))
            m = re.search("(?<=postages\":\[\{).*(?=\}\])", text)
            postagesMatch = m.group(0)      
            m = re.search("(?<=\"id\":\").*(?=\",\"fare)", postagesMatch)
            self.transport["id"] = m.group(0)
            m = re.search("(?<=\"fare\":\").*(?=\",\"level)", postagesMatch)
            self.transport["fare"] = m.group(0)
            m = re.search("(?<=\"level\":\").*(?=\",\"message)", postagesMatch)
            self.transport["level"] = m.group(0)
            m = re.search("(?<=\"message\":\").*(?=\",\"extra)", postagesMatch)
            self.transport["message"] = m.group(0)
            m = re.search("(?<=\"extra\":\").*(?=\",\"select)", postagesMatch)
            self.transport["extra"] = m.group(0)
            m = re.search("(?<=\"select\":)[\w]*(?=,)", postagesMatch)
            self.transport["select"] = m.group(0)
            m = re.search("(?<=\"cod\":)[\w]*(?=,)", postagesMatch)
            self.transport["cod"] = m.group(0)

    def getOrderActionAddress(self):
        return self.orderActionAddress

    def getOrderFormContent(self):
        pass

    def getOrderTransports(self):
        return self.transport

    def getDefaultTransport(self):
        self.acutalFee += int(self.transport["fare"])
        return self.transport["id"]

    def getOrderPostData(self):
        postData = ""
        defaultTransport = self.transport["id"]
        for inputControl in self.inputControls:
            if inputControl.control == "input":
                if inputControl.type == "text":
                    if inputControl.name.find("quantity") >= 0:
                        postData += inputControl.name + "=" + inputControl.value + "&"
                    elif inputControl.name.lower() == "checkcode":
                        if self.checkCode.isCheckCode:
                            postData += inputControl.name + "=" + self.checkCode.checkCode + "&"
                        else:
                            postData += inputControl.name + "=" + inputControl.value + "&"
                    else:
                        postData += inputControl.name + "=" + inputControl.value + "&"
                elif inputControl.type == "hidden":
                     postData += inputControl.name + "=" + inputControl.value + "&";
            elif inputControl.control == "select":
                    postData += inputControl.name + "=" + defaultTransport + "&";
        postData = postData[0:len(postData)-1]
        return postData
            
        
        

