from socket import *         
from datetime import *		 
import os					 
import time					 
import random				 
import threading			 # to handle requests coming to server
from urllib.parse import *	 	 # for parsing URL/URI
from _thread import *
import shutil				
import mimetypes			 # for getting extensions as well as content types
import csv				 # used in get and post method to insert the data into file
import base64				 # used for decoding autherization header in delete method
import sys					 
import logging				 # for logging
from config import *


serversocket = socket(AF_INET, SOCK_STREAM)
s = socket(AF_INET, SOCK_DGRAM)

#dictionary to convert extensions into content types
file_extension = {'.html':'text/html', '.txt':'text/plain', '.png':'image/png', '.gif': 'image/gif', '.jpg':'image/jpg', '.ico': 'image/x-icon', '.php':'application/x-www-form-urlencoded', '': 'text/plain', '.jpeg':'image/webp', '.pdf': 'application/pdf', '.js': 'application/javascript', '.css': 'text/css', '.mp3' : 'audio/mpeg'}


#LOG FILE
logging.basicConfig(filename = LOG, level = logging.INFO, format = '%(asctime)s:%(filename)s:%(message)s')


#dictionary to convert content types into extensions
#vice-versa of above
file_type = {'text/html': '.html','text/plain': '.txt', 'image/png': '.png', 'image/gif': '.gif', 'image/jpg': '.jpg','image/x-icon':'.ico', 'image/webp': '.jpeg', 'application/x-www-form-urlencoded':'.php', 'image/jpeg': '.jpeg', 'application/pdf': '.pdf', 'audio/mpeg': '.mp3', 'video/mp4': '.mp4'}

#dictionary to convert month to its decimal
month = { 'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12 }

c_get = False    			 # to check the conditional get method
conn = True				 # to receive requests continuously in client's thread
list_thread = []			 # list to maintain threads
ip = '0.0.0.0'								
st_code = 0				 # status code
C_ID = 0				 # cookie id


#header : last modified date of the resource 
def last_modified(element):
	l = time.ctime(os.path.getmtime(element)).split(' ')
	for i in l:
		if len(i) == 0:
			l.remove(i)
	l[0] = l[0] + ','
	s = (' ').join(l)
	s = 'Last-Modified: ' + s
	s += " GMT"
	return s
	
#Header : date
def date():
    d = datetime.now()
    date = d.strftime('%A,%d %B %Y %H:%M:%S ')
    date += "GMT"
    response = 'Date: ' + date
    #print(response)
    return response

#function to check if the resource has been modified or not since the date in HTTP request 
def if_modify(state, element):
	global c_get
	day = state.split(' ')
	if len(day) == 5:
		global month
		m = month[day[1]]
		date = int(day[2])
		t = day[3].split(':')
		t[0], t[1], t[2] = int(t[0]), int(t[1]), int(t[2])
		y = int(day[4])
		ti = datetime(y, m, date, t[0], t[1], t[2])
		hsec = int(time.mktime(ti.timetuple()))
		fsec = int(os.path.getmtime(element))
		if hsec == fsec:
			c_get = True
		elif hsec < fsec:
			c_get = False



#function to give response and status code
def statuscode(connectionsocket, code):
	global ip, list_thread, st_code
	st_code = code
	msg = []
	if code == 200:
		msg.append('HTTP/1.1 200 Ok')
	elif code == 204:
		msg.append('HTTP/1.1 204 No Content')
	elif code == 301:
		msg.append('HTTP/1.1 301 Moved Permanently')	
	elif code == 403:
		msg.append('HTTP/1.1 403 Forbidden')
	elif code == 404:
		msg.append('HTTP/1.1 404 Not Found')
	elif code == 414:
		msg.append('HTTP/1.1 414 Request-URI Too Long')
	elif code == 415:
		msg.append('HTTP/1.1 415 Unsupported Media Type')
	elif code == 500:
		msg.append('HTTP/1.1 500 Internal Server Error')
	elif code == 503:
		msg.append('HTTP/1.1 503 Server Unavailable')
	elif code == 505:
		msg.append('HTTP/1.1 505 HTTP Version Not Supported')

	msg.append('Server: ' + ip)
	msg.append(date())
	msg.append('\r\n')
	if code == 505:
		msg.append('Supported Version - HTTP/1.1 \n Rest Unsupported')
	encoded = '\r\n'.join(msg).encode()
	connectionsocket.send(encoded)
	logging.info('	{}	{}\n'.format(connectionsocket, st_code))
	try:
		list_thread.remove(connectionsocket)
		connectionsocket.close()
	except:
		pass
	server()

#function for conditional get implementation
def status_code_304(connectionsocket, element):
	global ip
	st_code = 304
	msg = []
	msg.append('HTTP/1.1 304 Not Modified')
	msg.append(date())
	msg.append(last_modified(element))
	msg.append('Server: ' + ip)
	msg.append('\r\n')
	encoded = '\r\n'.join(msg).encode()
	connectionsocket.send(encoded)

#function to resolve url in request message
def resolve(element):
	u = urlparse(element)
	element = unquote(u.path)
	if element == '/':
		element = os.getcwd()
	query = parse_qs(u.query)
	return (element, query)
	
	
#function to implement trace method
def method_trace(request, connectionsocket, jump_to):
	global st_code
	st_code = 200
	msg = []
	msg.append('HTTP/1.1 200 OK')
	msg.append('Content-Type: message/http')
	msg.append('via: HTTP/1.1 ' + ip + ':' + str(serverport))
	msg.append('\r\n')
	msg.append(request)
	encoded = '\r\n'.join(msg).encode()
	connectionsocket.send(encoded)


#function to implement connect method 
def method_connect(connectionsocket,jump_to):
	global ip, st_code
	st_code = 204
	msg = []
	msg.append('HTTP/1.1 204 No Content')
	msg.append('Server: ' + ip)
	msg.append('Connection: keep-alive')
	msg.append(date())
	msg.append('\r\n')
	encoded = '\r\n'.join(msg).encode()
	connectionsocket.send(encoded)

#function to implement delete method
def method_delete(element, connectionsocket, ent_body, jump_to):
	global ip, st_code
	msg = []
	option_list = element.split('/')
	isfile = os.path.isfile(element)
	isdir = os.path.isdir(element)
	if 'Authorization' in jump_to.keys():
		string = jump_to['Authorization']
		string = string.split(' ')
		string = base64.decodebytes(string[1].encode()).decode()
		string = string.split(':')
		if string[0] == USERNAME and string[1] == PASSWORD:
			pass
		else:
			st_code = 401
			msg.append('HTTP/1.1 401 Unauthorized')
			msg.append('WWW-Authenticate: Basic')
			msg.append('\r\n')
			encoded = '\r\n'.join(msg).encode()
			connectionsocket.send(encoded)
			return
	else:
		st_code = 401
		msg.append('HTTP/1.1 401 Unauthorized')
		msg.append('WWW-Authenticate: Basic')
		msg.append('\r\n')
		encoded = '\r\n'.join(msg).encode()
		connectionsocket.send(encoded)
		return
	if len(ent_body) > 1 or 'delete' in option_list or isdir:
		st_code = 405
		msg.append('HTTP/1.1 405 Method Not Allowed')
		msg.append('Allow: GET, HEAD, POST, PUT')
	elif isfile:
		st_code = 200
		msg.append('HTTP/1.1 200 OK')
		try:
			if (os.access(element, os.W_OK) and os.access(element, os.R_OK)):
				pass
			else:
				statuscode(connectionsocket, 403)
			shutil.move(element, DELETE)
		except shutil.Error:
			os.remove(element)
	else:
		st_code = 400
		msg.append('HTTP/1.1 400 Bad Request')
	msg.append('Server: ' + ip)
	msg.append('Connection: keep-alive')
	msg.append(date())
	msg.append('\r\n')
	encoded = '\r\n'.join(msg).encode()
	connectionsocket.send(encoded)




#function to implement put method
def method_put(connectionsocket, addr, ent_body, filedata, element, jump_to, f_flag):
	global ip,st_code
	msg = []
	
	try:
		length = int(jump_to['Content-Length'])
	except KeyError:
		statuscode(connectionsocket, 411)
	
	try:
		filedata = filedata + ent_body
	except TypeError:
		ent_body = ent_body.encode()
		filedata = filedata + ent_body
	i = len(ent_body)
	size = length - i
	while size > 0:
		ent_body = connectionsocket.recv(SIZE)
		try:
			filedata = filedata + ent_body
		except TypeError:
			ent_body = ent_body.encode()
			filedata = filedata + ent_body
		size = size - len(ent_body)
	move_p, mode_f, mode_cr = False, False, False
	isfile = os.path.isfile(element)
	isdir = os.path.isdir(element)

	l = len(element)
	limit = len(ROOT)
	if l >= limit:
		if isdir:
			if os.access(element, os.W_OK):
				pass
			else:
				statuscode(connectionsocket, 403)
			move_p = True
			loc = ROOT + '/' + str(addr[1])
			try:
				loc = loc + file_type[jump_to['Content-Type'].split(';')[0]]
			except:
				statuscode(connectionsocket, 403)
			if f_flag == 0:	
				f = open(loc, "w")
				f.write(filedata.decode())
			else:
				f = open(loc, "wb")
				f.write(filedata)
			f.close()
		elif isfile:
			if os.access(element, os.W_OK):
				pass
			else:
				statuscode(connectionsocket, 403)
			mode_f = True
			if f_flag == 0:	
				f = open(element, "w")
				f.write(filedata.decode())
			else:
				f = open(element, "wb")
				f.write(filedata)
			f.close()
		else:
			
			if ROOT in element:
				mode_cr = True
				element = ROOT + '/' + str(addr[1])
				try:
					element = element + file_type[jump_to['Content-Type'].split(';')[0]]
				except:
					statuscode(connectionsocket, 403)
				if f_flag == 0:	
					f = open(element, "w")
					f.write(filedata.decode())
				else:
					f = open(element, "wb")
					f.write(filedata)
				f.close()
			else:
				mode_f = False
	else:
		move_p = True
		loc = ROOT + '/' + str(addr[1])
		try:
			loc = loc + file_type[jump_to['Content-Type']]
		except:
			statuscode(connectionsocket, 403)
		if f_flag == 0:	
			f = open(loc, "w")
		else:
			f = open(loc, "wb")
		f.write(filedata)
		f.close()
	if move_p:
		st_code = 301
		msg.append('HTTP/1.1 301 Moved Permanently')
		msg.append(date())
		msg.append('Server: ' + ip)
		msg.append('Location: ' + loc)
	elif mode_f:
		st_code = 204
		msg.append('HTTP/1.1 204 No Content')
		msg.append(date())
		msg.append('Server: ' + ip)
		msg.append('Content-Location: ' + element)
	elif mode_cr:
		st_code = 201
		msg.append('HTTP/1.1 201 Created')
		msg.append(date())
		msg.append('Server: ' + ip )
		msg.append('Content-Location: ' + element)
	elif not mode_f:
		st_code = 501
		msg.append('HTTP/1.1 501 Not Implemented')
		msg.append(date())
		msg.append('Server: ' + ip)
	msg.append('Connection: keep-alive')
	msg.append('Content-Type: text/html')
	msg.append('\r\n')
	
	return msg




	
#function to implement post method 		
def method_post(ent_body, connectionsocket, jump_to):
	global ip, st_code
	msg = []
	query = parse_qs(ent_body)
	element = CSVFILE
	if os.access(element, os.W_OK):
		pass
	else:
		statuscode(connectionsocket, 403)
	fi = []
	row = []
	for d in query:
		fi.append(d)
		for i in query[d]:
			row.append(i)
	check = os.path.exists(element)
	if check:
		fi = open(element, "a")
		msg.append('HTTP/1.1 200 OK')
		st_code = 200
		csvwriter = csv.writer(fi)
		csvwriter.writerow(row)
	else:
		fi = open(element, "w")
		msg.append('HTTP/1.1 201 Created')
		st_code = 201
		msg.append('Location: ' + element)
		csvwriter = csv.writer(fi)
		csvwriter.writerow(fi)
		csvwriter.writerow(row)
	fi.close()
	msg.append('Server: ' + ip)
	msg.append(date())
	f = open(SHOWFILE, "rb")
	msg.append('Content-Language: en-US,en')
	size = os.path.getsize(SHOWFILE)
	string = 'Content-Length: ' + str(size)
	msg.append('Content-Type: text/html')
	msg.append(string)
	msg.append(last_modified(element))
	msg.append('\r\n')
	encoded = '\r\n'.join(msg).encode()
	connectionsocket.send(encoded)
	connectionsocket.sendfile(f)


#function to implement option method
def method_option(element, connectionsocket, jump_to):
	global ip, st_code
	isfile = os.path.isfile(element)
	isdir = os.path.isdir(element)
	msg = []
	
	st_code = 200
	msg.append('HTTP/1.1 200 OK')
	msg.append(date())
	msg.append('Server: ' + ip)
	
	
	option_list = element.split('/')
	if '*' in option_list and len(option_list) <= 2:
		msg.append('Allow:GET, HEAD, POST, PUT, TRACE, DELETE')
	elif isfile or isdir:
		if 'delete' in option_list:
			msg.append('Allow: OPTIONS')
		elif isfile:
			if (os.access(element, os.W_OK) and os.access(element, os.R_OK)):
				pass
			else:
				statuscode(connectionsocket, 403)
			msg.append('Allow: GET, HEAD, POST, DELETE')
		elif isdir:
			if (os.access(element, os.W_OK) and os.access(element, os.R_OK)):
				pass
			else:
				statuscode(connectionsocket, 403)
			msg.append('Allow: GET, HEAD, POST, PUT')
	else:
		msg.append('Allow: OPTIONS')
	msg.append('Content-Length: 0')
	msg.append('Connection: close')
	msg.append('Content-Type: text/plain')
	msg.append('\r\n')
	encoded = '\r\n'.join(msg).encode()
	connectionsocket.send(encoded)

#function to implement get and head method
def method_get_head(connectionsocket, element, jump_to, query, method):
	global serversocket, file_extension, c_get, conn, ip, st_code, C_ID
	isfile = os.path.isfile(element)
	isdir = os.path.isdir(element)
	msg = []
	if isfile:
		if (os.access(element, os.W_OK) and os.access(element, os.R_OK)):
			pass
		else:
			statuscode(connectionsocket, 403)
		msg.append('HTTP/1.1 200 OK')
		st_code = 200
		try:
			f = open(element, "rb")
			size = os.path.getsize(element)
			data = f.read(size)
		except:
			statuscode(connectionsocket, 500)
	elif isdir:
		if (os.access(element, os.W_OK) and os.access(element, os.R_OK)):
			pass
		else:
			statuscode(connectionsocket, 403)
		msg.append('HTTP/1.1 200 OK')
		st_code = 200
		dir_list = os.listdir(element)
		for i in dir_list:
			if i.startswith('.'):
				dir_list.remove(i)
	else:
		element = element.rstrip('/')
		isfile = os.path.isfile(element)
		isdir = os.path.isdir(element)
		if isfile:
			if (os.access(element, os.W_OK) and os.access(element, os.R_OK)):
				pass
			else:
				statuscode(connectionsocket, 403)
			msg.append('HTTP/1.1 200 OK')
			st_code = 200
			try:
				f = open(element, "rb")
				size = os.path.getsize(element)
				data = f.read(size)
			except:
				statuscode(connectionsocket, 500)
		elif isdir:
			if (os.access(element, os.W_OK) and os.access(element, os.R_OK)):
				pass
			else:
				statuscode(connectionsocket, 403)
			msg.append('HTTP/1.1 200 OK')
			st_code = 200
			dir_list = os.listdir(element)
			for i in dir_list:
				if i.startswith('.'):
					dir_list.remove(i)
		else:	
			statuscode(connectionsocket, 404)
	msg.append(COOKIE + str(C_ID) + MAXAGE)
	C_ID += 1
	for state in jump_to:
		if state == 'Host':
			pass
		elif state == 'User-Agent':
			if isfile:
				msg.append('Server: ' + ip)
				msg.append(date())
				msg.append(last_modified(element))
			elif isdir:
				msg.append('Server: ' + ip)
		elif state == 'Accept':
			if isdir:
				string = 'Content-Type: text/html'
				msg.append(string)
			elif isfile:
				try:
					file_ext = os.path.splitext(element)
					if file_ext[1] in file_extension.keys():
						string = file_extension[file_ext[1]]
					else:
						string = 'text/plain'
					string = 'Content-Type: '+ string
					msg.append(string)
				except:
					statuscode(connectionsocket, 415)
		elif state == 'Accept-Language':
			if isfile:
				string = 'Content-Language: ' + jump_to[state]
				msg.append(string)
			elif isdir:
				string = 'Content-Language: ' + jump_to[state]
				msg.append(string)
		elif state == 'Accept-Encoding':
			if isfile:
				string = 'Content-Length: ' + str(size)
				msg.append(string)
		elif state == 'Connection':
			if isfile:
				conn = 	True
				msg.append('Connection: keep-alive')
			elif isdir:
				conn = False
				msg.append('Connection: close')
		elif state == 'If-Modified-Since':
			if_modify(jump_to[state], element)
		elif state == 'Cookie':
			C_ID -= 1 
			msg.remove(COOKIE + str(C_ID) + MAXAGE)
		else:
			continue
	if isdir and method == 'GET':
		msg.append('\r\n')
		msg.append('<!DOCTYPE html>')
		msg.append('<html>\n<head>')
		msg.append('<title>Directory listing</title>')
		msg.append('<meta http-equiv="Content-type" content="text/html;charset=UTF-8" /></head>')
		msg.append('<body><h1>Directory listing..</h1><ul>')
		for line in dir_list:
			if element == '/':
				link = 'http://' + ip + ':' + str(serverport) + element + line
				l = '<li><a href ="'+link+'">'+line+'</a></li>'
				msg.append(l)
			else:
				link = 'http://' + ip + ':' + str(serverport) + element + '/'+ line
				l = '<li><a href ="'+link+'">'+line+'</a></li>'
				msg.append(l)
		msg.append('</ul></body></html>')
		encoded = '\r\n'.join(msg).encode()
		connectionsocket.send(encoded)
		connectionsocket.close()
	elif len(query) > 0 and not isdir and not isfile:
		msg = []
		element = CSVFILE
		fi = []
		row = []
		for d in query:
			fi.append(d)
			for i in query[d]:
				row.append(i)
		check = os.path.exists(element)
		if check:
			fi = open(element, "a")
			msg.append('HTTP/1.1 200 OK')
			st_code = 200
			csvwriter = csv.writer(fi)
			csvwriter.writerow(row)
		else:
			fi = open(element, "w")
			msg.append('HTTP/1.1 201 Created')
			st_code = 201
			msg.append('Location: ' + element)
			csvwriter = csv.writer(fi)
			csvwriter.writerow(fi)
			csvwriter.writerow(row)
		fi.close()
		msg.append('Server: ' + ip)
		msg.append(date())
		f = open(SHOWFILE, "rb")
		msg.append('Content-Language: en-US,en')
		size = os.path.getsize(SHOWFILE)
		string = 'Content-Length: ' + str(size)
		msg.append('Content-Type: text/html')
		msg.append(string)
		msg.append(last_modified(element))
		msg.append('\r\n')
		encoded = '\r\n'.join(msg).encode()
		connectionsocket.send(encoded)
		connectionsocket.sendfile(f)
	elif isfile:
		msg.append('\r\n')
		if c_get == False and method == 'GET':
			encoded = '\r\n'.join(msg).encode()
			connectionsocket.send(encoded)
			connectionsocket.sendfile(f)
		elif c_get == False and method == 'HEAD':
			encoded = '\r\n'.join(msg).encode()
			connectionsocket.send(encoded)
		elif c_get == True and (method == 'GET' or method == 'HEAD'):
			status_code_304(connectionsocket, element)
	else:
		statuscode(connectionsocket, 400)

#function which is bridge between response and requests
def clientfun(connectionsocket, addr, start):
	global serversocket, file_extension, conn, SIZE, list_thread, st_code,c_get
	
	f_flag = 0
	c_get = False
	filedata = b""
	conn = True
	
	while conn:
		if SIZE > 0 :
			pass
		else:
			break
		message = connectionsocket.recv(SIZE)
		try:
			message = message.decode('utf-8')
			req_list = message.split('\r\n\r\n')
			f_flag = 0
		except UnicodeDecodeError:
			req_list = message.split(b'\r\n\r\n')
			req_list[0] = req_list[0].decode(errors = 'ignore')
			f_flag = 1
		if len(req_list) > 1:
			pass
		else:
			break
		try:
			log.write(((addr[0]) + '\n' + req_list[0] + '\n\n'))
		except:
			pass
		display = []
		header_list = req_list[0].split('\r\n')
		header_len = len(header_list)
		ent_body = req_list[1]
		request_line = header_list[0].split(' ')
		method = request_line[0]
		element = request_line[1]
		if element == icon:
			element = ICON
		elif element == '/':
			element = os.getcwd()
		element, query = resolve(element)
		if (len(element) > MAX_URL):
			statuscode(connectionsocket, 414)
			break
		
		version = request_line[2]
		try:
			version_num = version.split('/')[1]
			if not (version_num == RUNNING_VERSION):
				statuscode(connectionsocket, 505)
		except IndexError:
			statuscode(connectionsocket, 505)
		jump_to = {}
		request_line = header_list.pop(0)
		for line in header_list :
			line_list = line.split(': ')
			jump_to[line_list[0]] = line_list[1]
		if method == 'GET' or method == 'HEAD':
			method_get_head(connectionsocket, element, jump_to, query, method)
		elif method == 'POST':
			method_post(ent_body, connectionsocket, jump_to)
		elif method == 'PUT':
			display = method_put(connectionsocket, addr, ent_body, filedata, element, jump_to, f_flag)
			encoded = '\r\n'.join(display).encode()
			connectionsocket.send(encoded)
		elif method == 'DELETE':
			method_delete(element, connectionsocket, ent_body, jump_to)
			conn = False
			connectionsocket.close()
		elif method == 'CONNECT':
			method_connect(connectionsocket,jump_to)
			conn = False
			connectionsocket.close()
		elif method == 'OPTIONS':
			method_option(element, connectionsocket, jump_to)
			conn = False
			connectionsocket.close()
		elif method == 'TRACE':
			method_trace(req_list[0], connectionsocket, jump_to)
			conn = False
			connectionsocket.close()
		else:
			method = ''
			break
		logging.info('	{}	{}	{}	{}	{}\n'.format(addr[0], addr[1], request_line, element, st_code))
	try:
		connectionsocket.close()
		list_thread.remove(connectionsocket)
	except:
		pass

#function handling multiple requests
def server():
	global list_thread
	while True:
		start = 0
		connectionsocket, addr = serversocket.accept()
		list_thread.append(connectionsocket)
		if(len(list_thread) < MAX_REQUESTS):
			start_new_thread(clientfun, (connectionsocket, addr, start))
		else:
			statuscode(connectionsocket, 503)
			connectionsocket.close()
	serversocket.close()
	

# function to find the server's ip address
def findip():
	try:
		s.connect(('8.8.8.8', 8000))
		IP = s.getsockname()[0]
	except:
		IP = '127.0.0.1'
	s.close()
	return IP



# function main
if __name__ == '__main__':
	ip = str(findip())
	try:
		serverport = int(sys.argv[1])
	except:
		print('Usage: python3 Server.py port_number(valid)')
		sys.exit()
	try:
		serversocket.bind(('', serverport))
	except:
		print('HTTPServer invalid arguements')
		print('Usage: python3 Server.py port_number(valid)')
		sys.exit()
	serversocket.listen(40)
	print('Serving HTTP on ' + ip + ' port ' + str(serverport) + ' (http://' + ip + ':' + str(serverport) +'/)')
	
	server()
	sys.exit()
#end to server implementation
