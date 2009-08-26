import urllib, urllib2, httplib, simplexmlapi
from jinwright.api.utils.restutils import Connection
from xml.dom.minidom import Document
from xml.dom import minidom


class jinwrightXML:
    def __init__(self,xml_string,iter_tags=None,non_tags=None):
        self.xml_obj = minidom.parseString(xml_string)
        #self.xml_obj = minidom.parse('/Users/brianjinwright/workspace/ipoots/static/xml/test.xml')
        self.iter_tags = iter_tags
        self.non_tags = non_tags
    class jinObj:
        pass
    def staticTags(self):
        jobj = self.jinObj()
        for tags in self.non_tags:
            tag = self.xml_obj.getElementsByTagName(tags)[0].childNodes[0].data
            setattr(jobj, tags, tag)
        return jobj
    def iterableTags(self):
        tag_list = list()
        for tags in self.iter_tags:
            tag = self.xml_obj.getElementsByTagName(tags)
            #tag_list.append(tag)
            for node in tag:
                if node.nodeType == node.ELEMENT_NODE and node.nodeName != None:
                    jobj = self.jinObj()
                    setattr(jobj, 'jType', node.nodeName)
                    child_nodes = node.childNodes
                    for cn in child_nodes:
                        if cn.nodeType == cn.ELEMENT_NODE:
                            if len(node.getElementsByTagName(cn.nodeName)[0].childNodes) != 0:
                                if hasattr(node.getElementsByTagName(cn.nodeName)[0].childNodes[0], 'data'):
                                    setattr(jobj, cn.nodeName, node.getElementsByTagName(cn.nodeName)[0].childNodes[0].data)
                    tag_list.append(jobj)
                            
                        
        return tag_list
    def all(self):
        jobj = self.jinObj()
        setattr(jobj, 'iterable', self.iterableTags())
        setattr(jobj, 'static', self.staticTags())
        return jobj

            
class RestExcept(Exception):
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)


        
        
        
def restRequest(url,values,type=None,jXML=False,jXMLIter=None,jXMLNon=None,path=None,port=443,**kwargs):
    """
    REST request handler.
    URL - (GET) Entire URL (POST) Base URL, example: http://www.google.com
    Values - Query or form varialbes
    Type - Either GET or POST
    Path - (POST Only) Folder and file, example: /webservice/test.html
    """
    encodedValues = urllib.urlencode(values)
    if type == None:
        req = urllib2.Request(url,encodedValues)
        data = urllib2.urlopen(req).read()
        if jXML == False:
            return simplexmlapi.loads(data)
        if jXML == True and isinstance(jXMLIter, list):
            if isinstance(jXMLNon, list):
                jin = jinwrightXML(data,iter_tags=jXMLIter,non_tags=jXMLNon)
                return jin.all()
            else:
                jin = jinwrightXML(data,iter_tags=jXMLIter)
                return jin.iterableTags()
    else:
        if path != None: 
            headers = {}
            if hasattr(kwargs, 'headers'):
                headers = kwargs['headers']
            conn = httplib.HTTPConnection(url)
            conn.request(type, path, encodedValues, headers)
            response = conn.getresponse()
            data = response.read()
            conn.close()
            return data
        else:
            raise RestExcept("Path not defined.")