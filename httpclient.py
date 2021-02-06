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


# Copyright 2021 Qianxi Li

#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at

#        http://www.apache.org/licenses/LICENSE-2.0

#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.


import sys
import socket
import re
import ssl
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
        split_response = data.split("\n")
        return int(split_response[0].split(' ')[1])

    def get_headers(self,data):
        return data.split("\n")[0]

    def get_body(self, data):
        body_divide_line = data.find("\n\r") + 1
        body = data[body_divide_line:]
        return body
    
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
        port = 80
        
        if url:
            #first, parse the url to get the host and port
            parsed_url = urllib.parse.urlparse(url)
            if parsed_url.port:
                port = parsed_url.port
            host = parsed_url.hostname
            # second, build connection

            self.connect(host, port)
            # then, send data
            
            path = parsed_url.path
            if (path == "" or path==None) and (host != "" or host != None):
                path = "/"
            if (parsed_url.query != ''):
                path += "?" + parsed_url.query

            all_command = ("GET {p1} HTTP/1.1\r\n"
                          + "Host: {p2}\r\n"
                          + "Accept: */*\r\n\r\n")

            command = all_command.format(p1=path, p2=host)

            self.sendall(command)

            # then, receive data
            recv_data = self.recvall(self.socket)
            print("===")
            print(recv_data)
            print("===")
            split_response = recv_data.split("\n")

            code = self.get_code(recv_data)
            body = self.get_body(recv_data)

            # close the connection
            self.close()


        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        port = 80
        if url:
            #first, parse the url to get the host and port
            parsed_url = urllib.parse.urlparse(url)
            if parsed_url.port:
                port = parsed_url.port
            host = parsed_url.hostname
            # second, build connection

            self.connect(host, port)

            # encode request and send it.
            args_string = ""
            body_length = 0

            if args:
                for k,v in zip(args.keys(), args.values()):
                    args_string += "{a}={b}&".format(a=k,b=v)
                # remove extra &
                args_string = args_string[:len(args_string)-1]
                body_length = len(args_string.encode('utf-8'))

            path = parsed_url.path
            if (path == "" or path==None) and 
               (user_agent != "" or user_agent != None):
                path = "/"
            if (parsed_url.query != ''):
                path += "?" + parsed_url.query

            all_commands = ("POST {file} HTTP/1.1\r\n" 
                           + "Host: {host}\r\n"
                           + "Content-Length: {length2}\r\n"
                           + "Content-Type: {content_type}; charset=UTF-8\r\n"
                           + "Connection: close\r\n\r\n")

            command = (all_commands).format(file = path,
                           content_type = "application/x-www-form-urlencoded",
                           length2 = body_length,
                           host = host)
           
            self.sendall(command)
 
            # then, receive data
            recv_data = self.recvall(self.socket)
            print("===")
            print(recv_data)
            print("===")

            code = self.get_code(recv_data)
            body = self.get_body(recv_data)

            # close the connection
            self.close()

        return HTTPResponse(code, body)

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
