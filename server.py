import socket
import threading
import time
import traceback

import msgpack
import msgpack_numpy as m

import argparse
import numpy  # Make sure NumPy is loaded before it is used in the callback
import wave

from cryptography.fernet import Fernet

import requests

class Server:
    #server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    #Use 0.0.0.0 after you have port forwarded
    #host = "0.0.0.0" 
    host = "127.0.0.1"
    port = 5555
    privatekey = b'Hq9vW2opxUZ7ld51Inrz0rvnMhlHtukUnFKrIAyxyOE='
    publickey = b'4vF083_jOpvEdqbXqem8GP96wmawb0KKZLz3o43o-KU='
    pucryp = Fernet(publickey)
    prcryp = Fernet(privatekey)
    
    curclients = []

    version = "0.1"
    
    def __init__(self):
        server_config = (self.host, self.port)
        self.udp_server.bind(server_config)
        #self.server.bind(server_config)
        #self.server.listen(5)
        self.connections = []
        self.users = []
        self.loggedIN = []
        
        print(f"Server laucnhed {self.host}:{self.port}")
        
        try:
            # Use a get request for api.duckduckgo.com
            raw = requests.get('https://api.duckduckgo.com/?q=ip&format=json')
            # load the request as json, look for Answer.
            # split on spaces, find the 5th index ( as it starts at 0 ), which is the IP address
            answer = raw.json()["Answer"].split()[4]
        # if there are any connection issues, error out
        except Exception as e:
            print('Error: {0}'.format(e))
        # otherwise, return answer
        else:
            print(answer)
    
        self.acceptConnectionT = threading.Thread(target=self.acceptConnection)
        self.acceptConnectionT.daemon = True
        self.acceptConnectionT.start()

    def int_or_str(self, text):
        """Helper function for argument parsing."""
        try:
            return int(text)
        except ValueError:
            return text
        
    def acceptConnection(self):
        clients = dict()
        timeout = 5

        while True:
            try:
                #This doesnt quiet work yet but still fixing it
                d, a = self.udp_server.recvfrom(4096)
                clients[a] = time.time()

                for addr in clients.copy().keys():
                    if clients[addr] < (time.time() - timeout):
                        self.connections.remove(addr)
                        clients.pop(addr)
                        print("Removed!")

                if a not in self.connections:
                    if d == b"connection":
                        self.udp_server.sendto(d,a)
                        #self.cT = threading.Thread(target=self.handler,args=(d,a))
                        #self.cT.daemon = True
                        #self.cT.start()
                        self.connections.append(a)
                        print(self.connections)
                        print("Get connecting from ", a)

                else:
                    for c in self.connections:
                        if a != c:
                            self.udp_server.sendto(d, c)

            except Exception as ex:
                print(traceback.format_exc())
                print(self.connections)

                if a in self.connections:
                    self.connections.remove(a)
                    clients.pop(a)
                    #print(self.connections)
                    print(f"{a} has disconnected")
                    
                    
    def removeC(self, c):
        try:
            self.connections.remove(c)
            c.close()

        except Exception as ex:
            try:
                c.close()
            except Exception as ex:
                print(ex)
 
    def handler(self, data ,addr):
        try:
            #data = c.recv(4096)
            #if not data:
            #    self.removeC(c)
            #    print(f"{a} has disconnected")
            #    break
            #print(data)
            d, a = self.udp_server.recvfrom(4096)

            if a == addr:
                for c in self.connections:
                    if a != c:
                        self.udp_server.sendto(d, c)

            #data = msgpack.unpackb(data, object_hook=m.decode)
            #self.output_stream.write(data)
            #data = self.pucryp.decrypt(data).decode()
            #data = data.split()
            #for connection in self.connections:
            #    if connection != c:
            #        connection.send(data)
            ''' if data[0] == "Connection":
                print("Connection secured")
                if data[1] == "Audio":
                    print(data)
                    c.send(self.pucryp.encrypt(bytes("Audio recieved", 'utf-8'))) '''
        except Exception as ex:
            if a == addr:
                print(ex)
                self.connections.remove(addr)
                print(self.connections)
                print(f"{addr} has disconnected")
    
    def removeHandler(self,c,a,uuid):
        while True:
            counter = 0
            time.sleep(5)

            for i in self.loggedIN:
                if i[1] == uuid:
                    for x in self.users:
                        if self.users[x]["uuid"] == str(uuid):
                            counter += 1          
                    
            if counter == 0:
                c.send(self.pucryp.encrypt(bytes("invalid username or password", 'utf-8')))
                self.removeC(c)
                self.loggedIN.remove((a,uuid))
                break 

    def chat(self):
        while True:
            server_message = input()
            server_message = server_message.split()

            #  server_message = "\nserver:{}\n".format(server_message)
            #  server_message = self.pucryp.encrypt(bytes(server_message, 'utf-8'))
            #  for c in self.connections:
            #      c.send(self.pucryp.encrypt(bytes(server_message, 'utf-8')))
                
                

if __name__ == '__main__':
    Server_m = Server()
    Server_m.chat()