import os
import sys

if sys.argv[-1] =="-h" or sys.argv[-1] =="-help" :
        print("Usage:")
        print("\t# python3 master.py port_number")
        print("Description:")
        print("\tSimple HTTP Server will process and answer incoming Requests !")
        print("\tport for the server can be passed as parameters to master.py:\n")
        sys.exit(1)

while True:
    # TO run the server with port number
    print("Press 'Ctrl+C' to get menu.")
    print("************************************************\n************************************************\n")
    
    print("Starting the server ...\n")
    
    os.system(f'python3 Server.py {sys.argv[1]}')
    while True:
        print("q for quit\nr for restart.")
        key = input()
        if key=='q':
            exit()
        elif key=='r':
            print("restarting the server ...")
            break
        else:
            print("invalid input\n")
            continue
exit()
