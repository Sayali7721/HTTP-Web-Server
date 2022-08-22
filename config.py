import os

# data size to receive from client
SIZE = 4096

'''this initiation helps server to identify current working directory'''
ROOT = os.getcwd()

#supported version by the server. 
RUNNING_VERSION = '1.1'


#Thread requests handled by the server at one time
MAX_REQUESTS = 100


#Maximum Url length supported by the server 
MAX_URL = 150


COOKIE = 'Set-Cookie: id='
MAXAGE = '; max-age=3600'



#this folder contains all the files which are being deleted 
DELETE = ROOT + '/delete'

#try to make delete folder 
try:
	os.mkdir(DELETE)
except:
	pass

#username and password for authentication of delete request method
USERNAME = 'Sayali'
PASSWORD = 'S7721'

#log file to maintain log info
LOG = ROOT + '/server.log'
w = open(LOG, "a")
w.close()


#gives response to the client once they use get or post method using query or entity data respectively

SHOWFILE = ROOT + '/file.html'

w = open(SHOWFILE, "w")
d = '<html><head><title>Thank for response</title></head><body><h1>Your Response as been Saved</h1></body></html>'
w.write(d)
w.close()


#csv file is the used to store the data entered by user
CSVFILE = ROOT + '/action.csv'
w = open(CSVFILE, "a")
w.close()



#browser demands icon.ico file to show the icon in the tab of its window 
icon = '/icon.ico'
ICON = ROOT + icon

