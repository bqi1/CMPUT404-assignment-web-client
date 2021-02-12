#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        try:
            return int(data.splitlines()[0].split(" ")[1])
        except ValueError:
            return 500

    def get_headers(self,data):
        return None

    def get_body(self, data):
        return data.split("\r\n\r\n")[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        code = 500
        body = ""
        split_values = urllib.parse.urlsplit(url)
        port = 80 if split_values.port == None else split_values.port
        hostname = split_values.hostname
        path = "/" if split_values[2] == "" else split_values[2]
        query = f"?{split_values[3]}" if split_values[3] != "" else ""
        try:
            self.connect(hostname,port)
            self.sendall(f"GET {path}{query} HTTP/1.1\r\nHost: {hostname}:{port}\r\nConnection: close\r\n\r\n")
            body = self.recvall(self.socket)
            print(body)
            self.close()
            code = self.get_code(body)
            body = self.get_body(body)
        except Exception as e:
            return HTTPResponse(code, body)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        split_values = urllib.parse.urlsplit(url)
        port = 80 if split_values.port == None else split_values.port
        hostname = split_values.hostname
        path = "/" if split_values[2] == "" else split_values[2]
        query = f"?{split_values[3]}" if split_values[3] != "" else ""
        processed_args = ""
        if args != None:
            processed_args = f"{self.process_args(args)}"
        content_length = len(processed_args)
        try:
            self.connect(hostname,port)
            self.sendall(f"POST {path}{query} HTTP/1.1\r\nHost: {hostname}:{port}\r\nContent-Type: application/x-www-form-urlencoded; charset=UTF-8\r\nContent-Length: {content_length}\r\nAccept: application/json\r\nConnection: close\r\n\r\n{processed_args}")
            body = self.recvall(self.socket)
            print(body) # ADD THIS ONE
            self.close()
            code = self.get_code(body)
            body = self.get_body(body)

        except Exception as e:
            return HTTPResponse(code, body)
        return HTTPResponse(code, body)
    def process_args(self,args): # Turn args(if any) into content for POST
        content = ""
        for key in args.keys():

            spaced_key = key.replace(" ","%20")
            spaced_value = args[key].replace(" ","%20")
            content+=f"{spaced_key}={spaced_value}&"
        return content[:-1]
    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
