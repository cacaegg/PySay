#!/usr/bin/env python
import os
import pickle
import traceback
import sys
import socket
import vm

"""
Translate engine will look up variable name of #VARNAME#
"""
CENTRAL_SERVER = "#SERVERIP#"
# PRODUCT = "#PRODUCT#"
PRODUCT = "DDI"

VERSION = "0.0.1" # ProjectYear.Feature.Modfied
DEBUG = True
PORT = 5566
HOME_DICT = {"DDI" : "/filestores/pfmnc"}
HOME = HOME_DICT[PRODUCT]


def init():
    global UUID
    print "Initializing UUID...",
    try:
        f_uuid = open("uuid.pkl", "rb")
        UUID = pickle.load(f_uuid)
        if len(UUID) == 0:
            raise IOError()
        print UUID
    except IOError as e:
        import uuid
        UUID = uuid.uuid1()
        f_uuid = open("uuid.pkl", "wb")
        pickle.dump(UUID, f_uuid)
        f_uuid.close()
        print UUID
    except:
        traceback.print_exc()

def runserver():
    """
    This will open a local socket server, and handle the request
    """    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("", PORT))
    if DEBUG:
        print "Listening on %s:%d..." % ("0.0.0.0", PORT)
    s.listen(1)
    while 1:
        try:
            # Program stall here wait for connection
            clientsock, clientaddr = s.accept()
        except KeyboardInterrupt:
            raise
        except:
            traceback.print_exc()
            continue
        # Got a connection, continue to processing
        inbuf = ''
        try:
            if DEBUG:
                print "Got connection from", clientsock.getpeername()
            vm.init_env()
            while 1:
                data = clientsock.recv(4096)
                if not len(data):
                    break
                inbuf += data

                # If client commit to go, then move buf to data and clean it. 
                # Otherwise, continue wait for client data
                if inbuf.strip()[-4:] == "#eos":
                    data = inbuf[:-5]
                    inbuf = ""
                else: 
                    continue

                # Start to parse client command buf
                if DEBUG:
                    print "Receive data..."
                    print data
                try:
                    ret = vm.start_exec(data.decode("base64"))
                    clientsock.sendall(str(ret).encode("base64")+"#eos")
                except:
                    clientsock.sendall(traceback.format_exc()+"#eos")
                # clientsock.sendall("\n> ")
        except KeyboardInterrupt, SystemExit:
            raise
        except:
            traceback.print_exc()

        # Close the connection    
        try:
            clientsock.close()
        except KeyboardInterrupt:
            raise
        except:
            traceback.print_exc()

def runvip():
    vm.init_env()
    code = ""
    print "Welcome to pysay-vm. : )"
    try:
        while 1:
            data = raw_input("> ")
            if data == "bye":
                print "bye!"
                break
            code += data

            # If client commit to go, then move buf to data and clean it. 
            # Otherwise, continue wait for client data
            if code.strip()[-4:] == "#eos":
                code = code[:-4]
            else: 
                continue

            print vm.start_exec(code)
            code = ""
    except EOFError:
        print "See you!"

def runweb():
    import sys
    import traceback
    sys.stderr = sys.stdout
    vm.init_env()
    code = ""
    while 1:
        try:
            data = sys.stdin.readline()
            if data == "bye":
                print "bye!"
                break
            code += data

            # If client commit to go, then move buf to data and clean it. 
            # Otherwise, continue wait for client data
            if code.strip()[-4:] == "#eos":
                code = code[:-4]
            else: 
                continue

            print vm.start_exec(code)
            sys.stdout.flush()
            code = ""
        except EOFError:
            pass
        except Exception as e:
            traceback.print_exc()
            sys.stdout.flush()
            code = ""

if __name__ == '__main__':
    sys.setrecursionlimit(8192)

    if DEBUG:
        print 'PySay-VM '+ VERSION
    if len(sys.argv) == 2 and sys.argv[1] == "vip":
        runvip()
    elif len(sys.argv) == 2 and sys.argv[1] == "web":
        runweb()
    else:
        runserver()
