#Used to get Product infomation from page source
from sgmllib import SGMLParser
import re

"""
Use Regex to get infomation.
"""
class ProductSpecificItem:
        def __init__(self, proID):
                self.id = proID
                self.skuId = ''
                self.oversold = 'false'
                self.tagPrice = ''
                self.spPrice = ''
                self.price = ''
                self.stock = 0

def GetProSpecItemList(productPage):
        p = re.compile("\"skuMap\":[\s]*{", re.MULTILINE)
        match1 = p.search(productPage)
        p = re.compile("Hub.config.set\(\'async_sd")
        match2 = p.search(productPage)
        skuinfoall = productPage[match1.start():match2.start()]
        
        p = re.compile(";[\d]*:[\d]*;[\d]*:[\d]*;", re.MULTILINE)
        ids = p.findall(skuinfoall)
        p = re.compile("skuId\" : \"[\d]*\"", re.MULTILINE)
        skuIds = p.findall(skuinfoall)
        p = re.compile("\"oversold\":[\s]*\"[\w]*\"", re.MULTILINE)
        oversolds = p.findall(skuinfoall)
        p = re.compile("\"tagPrice\":[\s]*\"[\w.]*\"", re.MULTILINE)
        tagPrices = p.findall(skuinfoall)
        p = re.compile("\"spPrice\":[\s]*\"[\w.]*\"", re.MULTILINE)
        spPrices = p.findall(skuinfoall)
        p = re.compile("\"price\" : \"[\w.]*\"", re.MULTILINE)
        prices = p.findall(skuinfoall)
        p = re.compile("\"stock\" :[\s]*\"[\d]*\"", re.MULTILINE)
        stocks = p.findall(skuinfoall)

        specItemList = []
        count = len(ids)
        for i in range(count):
                prod = ProductSpecificItem(ids[i])
                #skuId
                p = re.compile("[0-9]")
                sku = p.search(skuIds[i])                
                prod.skuId = skuIds[i][sku.start():len(skuIds[i])-1] 
                #oversold
                if oversolds[i].find('false') != -1:
                        prod.oversold = 'false'
                elif oversolds[i].find('true') != -1:
                        prod.oversold = 'true'
                #tagPrice
                p = re.compile("\"tagPrice\":[\s]*\"")
                obj = p.match(tagPrices[i])
                prod.tagPrice = tagPrices[i][obj.end():len(tagPrices[i])-1]
                #spPrice
                p = re.compile("\"spPrice\":[\s]*\"")
                obj = p.match(spPrices[i])
                prod.spPrice = spPrices[i][obj.end():len(spPrices[i])-1]
                #Price
                p = re.compile("\"price\" : \"")
                obj = p.match(prices[i])
                prod.price = prices[i][obj.end():len(prices[i])-1]
                #stock
                p = re.compile("\"stock\" :[\s]*\"")
                obj = p.match(stocks[i])
                prod.stock = stocks[i][obj.end():len(stocks[i])-1]
                specItemList.append(prod)
        return specItemList
        #Damn too ugly!
      

"""
PageParser inherits from SGMLParser
"""
class PageParser(SGMLParser):
        def reset(self):
                SGMLParser.reset(self)
                self.BidAddress = ''
                self.Find = False
                self.formContent = {}
                self.dataProperty = False
                self.tempKey = ''
                self.catchData = False
                self.is_span = False
                self.propertyDic = {}

        def start_form(self, attrs):                      
                for item in attrs:
                        if item[0] == 'id' and item[1] != 'J_FrmBid':
                                break
                        self.Find = True
                        if item[0] == 'action':
                                self.BidAddress = item[1]
                                
        def end_form(self):
                self.Find = False
                pass

        def start_input(self, attrs):
                if self.Find is True:
                        name = ''
                        for item in attrs:
                                if item[0] == 'name':
                                        name = item[1]
                                elif item[0] == 'value':
                                        self.formContent[name] = item[1]
                else:
                        pass
                
        def end_input(self):
                pass

        def start_ul(self, attrs):
                if len(attrs) != 0  and attrs[0][0] == 'data-property':
                        self.dataProperty = True
                        
                        
        def end_ul(self):
                self.dataProperty = False


        """
        TODO add each li info to dictionary
        """
        def start_li(self, attrs):
                if self.dataProperty:
                        dataValue = attrs[0][1]
                        if len(attrs) < 2 or attrs[1][0] != 'title':
                                self.tempKey = dataValue
                                self.catchData = True
                        else:
                                self.propertyDic[attrs[1][1]] = dataValue

        def end_li(self):
                self.catchData = False

        def start_span(self, attrs):
                self.is_span = True

        def end_span(self):
                self.is_span = False
                
        def handle_data(self, text):
                if self.catchData and self.is_span:
                        self.propertyDic[text] = self.tempKey

        def getProductActionAddress(self):
                return self.BidAddress

        def getProductFormContent(self):
                #TODO Get the questions and answers
                return self.formContent

        def getProductProperties(self):
                return self.propertyDic



def GeneratePostData(productInputDict, specItemList, sizeID, colorID):
        postData = ''
        itemID = ';' + sizeID + ';' + colorID + ';'
        for item in specItemList:
                if item.id == itemID:
                        skuId = item.skuId
        for key in productInputDict.keys():
                value = productInputDict[key]
                if key != "":
                        if key == "skuId":
                                postData = postData + "skuId=" + skuId + "&"
                        elif key == "skuinfo":
                                postData += "skuinfo=" + "" + "&"
                        else:
                                postData += key + "=" + value + "&"

        postData = postData[0:len(postData)-1]
        return postData


