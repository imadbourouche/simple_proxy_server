#!/usr/bin/env python

import argparse
from decouple import config,Csv
import signal
import socket
import sys
import threading
import logging
import colored_logging


# get arguments
argParser = argparse.ArgumentParser()
argParser.add_argument("-mc", "--max_conn", help="Define maximum connections", default=5, type=int)
argParser.add_argument("-bs", "--buf_size", help="Number of bytes to be reveived", default=8192, type=int)
args=argParser.parse_args()
max_connections = args.max_conn
buffer_size = args.buf_size


# get the configurations
PORT=config("PORT",default=8000,cast=int)
HOST=config("HOST",default="0.0.0.0")
CONNECTION_TIMEOUT=config("CONNECTION_TIMEOUT",default=15,cast=int)
BLACK_LIST=config("BLACK_LIST",default=[],cast=Csv())

# logging configuration
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setFormatter(colored_logging.CustomFormatter())
logger.addHandler(ch)






def start_server():
    try:
        # Create a TCP socket
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Re-use the socket
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # bind the socket to a public host, and a port   
        serverSocket.bind((HOST, PORT))
    
        serverSocket.listen(max_connections) # become a server socket

        logger.debug(f"Proxy running on http://{HOST}:{PORT}")

        while(True):
            (client_socket, client_address) = serverSocket.accept();
            # start a new thread to handle the connection
            d = threading.Thread(name=client_address, target = connection, args=(client_socket, client_address),daemon=True)
            d.start()
    except Exception as e:
        logging.error(f"Unable to start proxy server: {e}")
        


def connection(conn,addr):
    try:
        #getting the client data
        request= conn.recv(buffer_size)
        url = get_url(request)
        # check for black list domains
        if check_black_list(url):
            logging.warning(url.decode())
            error_response(conn)
        else:
            [port,webserver]=get_port_webserver(url)
            logging.info(request.decode())
            proxy(conn ,webserver ,port ,request,addr)

    except Exception as e:
        logging.error(e)
        error_response(conn)


def proxy(conn,webserver,port,request,addr):
    try:
        
        # set a new connection with the destination
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(CONNECTION_TIMEOUT)
        s.connect((webserver, port))
        s.send(request)
        while 1:
            # receive data from web server
            data = s.recv(buffer_size)
            if (len(data) > 0):
                conn.send(data) # send to client
                dar = float(len(data))
                dar = float(dar/1024)
                dar = "%.4s KB" % (str(dar))
                print("[*] Request Done: recevied %s" % str(dar))
            else:
                break
        s.close()
        conn.close()
    except ConnectionError as e:
        logging.error(e)
        error_response(conn)
    




# UTILITIES

def error_response(conn):
    response=b'HTTP/1.1 500\r\nServer: Python/3.10\r\nContent-Type: text/plain; charset=UTF-8\r\n\r\nConnection Error'
    conn.send(response)
    conn.close()


def check_black_list(url):
    for i in BLACK_LIST:
        if  bytes(i,'utf-8') in url:
            return True
    return False


def get_url(request):
    first_line = request.split(b'\n')[0]
    url = first_line.split(b' ')[1]
    return url

def get_port_webserver(url):
    http_pos = url.find(b"://") # find pos of ://
    if (http_pos==-1):
        temp = url
    else:
        temp = url[(http_pos+3):] # get the rest of url

    port_pos = temp.find(b":") # find the port pos (if any)

    # find end of web server
    webserver_pos = temp.find(b"/")
    if webserver_pos == -1:
        webserver_pos = len(temp)

    webserver = ""
    port = -1
    if (port_pos==-1 or webserver_pos < port_pos):
        # default port
        port = 80
        webserver = temp[:webserver_pos] 
    else: 
        # specific port 
        port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
        webserver = temp[:port_pos]

    return [port,webserver]




# Shutdown when CTRL+C
def handler(signum, frame):
    logging.debug("[*] Shutting down the proxy server")
    sys.exit(0)

signal.signal(signal.SIGINT, handler) 

if __name__=="__main__":
    start_server()