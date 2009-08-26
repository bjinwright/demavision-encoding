from jinwright.api.utils import restRequest
import datetime
from jinwright.api.utils.restutils import Connection
from xml.dom.minidom import Document, DocumentFragment
#Application Key
ENCODING_USERID = ''

#Master Account Username
ENCODING_USERKEY = ''

url = 'manage.encoding.com:80'
class EncodingError(Exception):
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value) 

class Encoding:
    """
    Encoding.com (www.encoding.com) Python API wrapper.
    Example:
    format_list = [[{'output':'flv'},{'video_codec':'vp6'},{'destination':'ftp://yourusername:yourpassword@yourdomain.com/path/to/video/%s' % file_name}],[{'output':'thumbnail'},{'width':'128'},{'time':'10'},{'destination':'ftp://youruser:yourpassword@yourdomain.com/path/to/thumbs/%s' % thumb_file_name}]]
    source_string = 'ftp://yourusername:yourpassword@yourdomain.com/path/to/raw/video/%s' % filename
    notify_string = 'http://yourdomain.com/your/notify/url/%s' % someidvariable
    enc = Encoding()
    query = enc.encodingReq("addMedia",sourceString=source_string,notifyString=notify_string,formatList=format_list)
    """
    def __init__(self,userid=None,userkey=None):
        """
        You can specify the userid and userkey here to override the variables at the top.
        """
        self.userid = userid
        self.userkey = userkey
    
    def encodingReq(self,actionString,sourceString=None,notifyString=None,formatList=None,logoList=None):
        doc = Document()
        query = doc.createElement("query")
        
        action = doc.createElement("action")
        query.appendChild(action)
        
        actionData = doc.createTextNode(str(actionString))
        action.appendChild(actionData)
        
        
        userid = doc.createElement("userid")
        if self.userid != None:
            userData = doc.createTextNode(self.userid)
        else:
            userData = doc.createTextNode(ENCODING_USERID)
        userid.appendChild(userData)
        
        userkey = doc.createElement("userkey")
        if self.userkey != None:
            userkeyData = doc.createTextNode(self.userkey)
        else:
            userkeyData = doc.createTextNode(ENCODING_USERKEY)
        userkey.appendChild(userkeyData) 
        
        doc.appendChild(query)
        query.appendChild(userid)
        query.appendChild(userkey)
        
        if sourceString:
            source = doc.createElement("source")
            doc.appendChild(source)
            sourceData = source.createTextNode(source)
            source.appendChild(sourceData)
        if notifyString:
            notify = doc.createElement("notify")
            doc.appendChild(notify)
            notifyData = source.createTextNode(notify)
            notify.appendChild(notifyData)
        
        if isinstance(formatList, list):
            format = doc.createElement("format")
            query.appendChild(format)
            for formatList in formatList:
                if isinstance(formatList, dict):
                    for k,v in formatList.iteritems():
                        ce = doc.createElement(k)
                        format.appendChild(ce)
                        ceData = doc.createTextNode(v)
                        ce.appendChild(ceData)
            if isinstance(logoList, list):
                logo = doc.createElement("logo")
                format.appendChild(logo)
                for logoList in logoList:
                    if isinstance(logoList, dict):
                        for k,v in logoList.iteritems():
                            ce = doc.createElement(k)
                            logo.appendChild(ce)
                            ceData = doc.createTextNode(v)
                            ce.appendChild(ceData)

        
        xmlString = doc.toxml()  
        values = {'xml': xmlString,}
        return restRequest(url, values,type='POST',path='')