# Writing a testing program

import requests
import sys
port = int(sys.argv[1])
url = 'http://127.0.0.1:' + str(port)

data = {'username':'sssss',
    'password':'1234'
}

data2 = "HI !!!"

s = requests.Session() 

getPath = '/home/user/HTTP-Web-Server-master/JioFi.txt'

try:
    print("GET request:")
    response = s.get(url + getPath)
    if not response:
        print("Something's Wrong!\nResponse Not Recieved.")
    print(f"text files opening succesfully\nstatus code: {response.status_code}\n")
except Exception as err:
    print(f'Other error occurred: {err}')


getPath = '/home/user/HTTP-Web-Server-master/song.mp3'
try:
    print("GET request:")
    response = s.get(url + getPath)
    if not response:
        print("Something's Wrong!\nResponse Not Recieved.")
    print(f"Media opening Succesfully\nstatus code: {response.status_code}\n")
except Exception as err:
    print(f'Other error occurred: {err}\n')


getPath = '/home/user/HTTP-Web-Server-master/audio.mp3'
try:
    print("\nGET request:")
    response = s.get(url + getPath)
    if not response:
        print("Something's Wrong!\nResponse Not Recieved")
    else:
    	print(f"Media opening Succesfully\nstatus code: {response.status_code}\n")
except Exception as err:
    print(f'Other error occurred: {err}\n')


getPath = '/home/user/HTTP-Web-Server-master/index.mp3'
try:
    print("\nGET request:")
    response = s.get(url + getPath)
    if not response:
        print("404 coming Succesfully.")
    print(f"status code: {response.status_code}\n")
except Exception as err:
    print(f'Other error occurred: {err}')


postPath = "/home/user/HTTP-Web-Server-master/action.csv"
try:
    print("\nsending POST request...")
    response = s.post( url+postPath, json=data)
    if not response:
        print("Something's Wrong!\nResponse Not Recieved.")
    print(f"Response recieved with status code: {response.status_code}")
except Exception as err:
    print(f'Other error occurred: {err}')

putPath = "/home/user/HTTP-Web-Server-master/action.csv"
try:
    print("\nsending PUT request...")
    response = s.put(url+putPath, data ={'key' : 'value'})
    if not response:
        print("Something's Wrong!\nResponse Not Recieved.")
    print(f"Response recieved with status code: {response.status_code}")
except Exception as err:
    print(f'Other error occurred: {err}')


delPath = "/home/user/HTTP-Web-Server-master/JioFi.txt"
try:
    print("\nsending DELETE request with Auth..")
    response = s.delete(url + delPath, auth = ('Sayali', 'S7721'))
    if not response:
        if response.status_code == 401:
            print("Unauthorized User")
    print(f"Deleted Succesfully\nstatus code: {response.status_code}")
except Exception as err:
    print(f'Other error occurred: {err}')


delPath = "/home/user/HTTP-Web-Server-master/song.mp3"
try:
    print("\nsending DELETE request without Auth...")
    response = s.delete(url + delPath)
    if not response:
        if response.status_code == 401:
            print("Unauthorized User")
    print(f"Response recieved with status code: {response.status_code}")
except Exception as err:
    print(f'Other error occurred: {err}')

headPath = "/home/user/HTTP-Web-Server-master/song.mp3"
try:
    print("\nsending HEAD request...")
    response = s.head(url + headPath)
    if not response:
        print("Something's Wrong!\nResponse Not Recieved.")
    print(f"Response recieved with status code: {response.status_code}")
except Exception as err:
    print(f'Other error occurred: {err}')

print("\nEverything Saved in log file succesfully.\nCheck server.log to check logs")
