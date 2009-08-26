import httplib, mimetypes, urlparse, urllib, base64, os, sys, simplexmlapi
#import nirvanixutils

# Set Debug = True to display the Response from nirvanix.
debug = False

class Connection:
	def __init__(self, base_url):
		self.base_url = base_url
		self.url = urlparse.urlparse(base_url)

	def request_get(self, resource, args = None):
		return self.request(resource, "GET", args)

	def request_post(self, resource, args = None):
		return self.request(resource, "POST", args)

	def request(self, path, method = "GET", args = None):
		headers = {}
		webservice = None
		args = args + '\r\n'
		if (self.url.port == 443):
			webservice = httplib.HTTPS(self.url.netloc)
		else:
			webservice = httplib.HTTP(self.url.netloc)
		
		webservice.putrequest(method, path)
		webservice.putheader("User-Agent", "Nirvanix Python API")
		webservice.putheader("Content-length", "%d" % len(args))
		webservice.putheader("Content-Type", "application/x-www-form-urlencoded")
		webservice.putheader("Host", self.url.netloc)
		webservice.endheaders()
		webservice.send(args)

		# get the response
		statuscode, statusmessage, header = webservice.getreply()
		res = webservice.getfile().read()
		if debug:
			print "Response: ", statuscode, statusmessage
			print "headers: ", header
			print res
		return res
		   
	def post_multipart(self, host, selector, fields, files, start, end, length):
		"""
		Post fields and files to an http host as multipart/form-data.
		fields is a sequence of (name, value) elements for regular form fields.
		files is a sequence of (name, filename, value) elements for data to be uploaded as files
		Return the server response.
		"""
		
		content_type, body = self.encode_multipart_formdata(fields, files, start, end, length)
		
		h = httplib.HTTPConnection(host)  
		headers = {
		 	'Content-Length': str(len(body)),
			'User-Agent': 'Nirvanix Python SDK',
			'Content-Type': content_type
		}
		h.request('POST', selector, body, headers)
		res = h.getresponse()
		if debug:
			print "Err Code: " + str(res.status)
			print "Err Msg: " + str(res.reason)
		return simplexmlapi.loads(res.read())    

	def encode_multipart_formdata(self, fields, files, start, end, length, boundary = None, buf = None):
		"""
		fields is a sequence of (name, value) elements for regular form fields.
		files is a sequence of (name, filename, value) elements for data to be uploaded as files
		start is the start of the file part used for partial file uploads
		end is the end of the file part used for partial file uploads
		length is the total length of the file
		boundary can be set if you want to specify your own boundry
		buf should only be set if you need to pre-pend some data to the stream be aware of encoding issues
		Return (content_type, body) ready for httplib.HTTP instance
		"""
		if boundary is None:
			boundary = '----------NvxBOUNDNvxBOUNDNvxBOUND'
		# Set the buffer to an empty unicode string
		if buf is None:
			buf = u''
		#loop through each pair creating a content-disposition for each one
		for(key, value) in fields:
			buf += '--%s\r\n' % boundary
			buf += 'Content-Disposition: form-data; name="%s"' % key
			buf += '\r\n\r\n' + value + '\r\n'
		# loop through all files / file parts doing the upload.  Realistically this should be called
		# one at a time but (should) support multiples.
		for(key, filename, value) in files:
			buf += '--%s\r\n' % boundary
			buf += 'Content-Disposition: form-data; name="%s"; filename="%s"\r\n' % (key, filename)
			buf += 'Content-Type: %s\r\n' % self.get_content_type(filename)
			buf += 'Content-Range: %s-%s/%s\r\n\r\n' % (start, end, length)
			# be aware that we have to make sure we convert the buf to a buffer type
			# so the encoding will not be applied.
			if (value != None):
				buf = buffer(buf.encode('utf-8')) + buffer(value) 
		# append the following boundry after the last file.
		buf += '\r\n--%s--\r\n' % boundary
		content_type = 'multipart/form-data; boundary=%s' % boundary
		return content_type, str(buf)

	def get_footer(self, boundary = None):
		"""
		Used to generate a boundry and finish off the file.
		"""
		if boundary is None:
			boundary = '----------NvxBOUNDNvxBOUNDNvxBOUND'
		CRLF = '\r\n'
		L = []
		L.append('')
		L.append('--' + boundary + '--')
		L.append('')
		return CRLF.join(L)

	def get_content_type(self, filename):
		# Uses the mimetypes lib to get the content type.
		return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

	#--- Upload file ---#

	def uploadfile(self, uploadHost, uploadToken, localFilename, destFolderPath, destFilename):
		"""
		uploadHost is the host that will do the upload for you
		"""
		url = "/upload.ashx"
		params = [('uploadtoken', uploadToken), ('destFolderPath', destFolderPath)]
		
		f = file(localFilename, "rb")
		# 1 Mb is fairly efficient but may need to be changed based on memory or network speed.
		buffersize = 1024*1024*1 
		start = f.tell()
		data = f.read(buffersize)
		filelen = os.path.getsize(localFilename)
		while data:
			datalen = len(data) - 1
			end = start + datalen 
			result = self.post_multipart(uploadHost, url, params, [('FILE1',destFilename,data)],
				start, end, filelen)
			start = f.tell()
			data = f.read(buffersize)
		f.close()
		return result