
from tkinter import *
from tkinter import ttk
import threading
import time
import socket
import json
import sys

import glob
lst = []

class ClientThread(threading.Thread):
    def __init__(self,conn,addr,closeconn):
        threading.Thread.__init__(self)
        self.conn=conn
        self.close_conn=closeconn
        self.addr=addr
    def run(self):
        while True:
            data=self.conn.recv(1024)
            if data.decode()=="CLOSE":
                self.conn.close()
                self.close_conn.send("CLOSE".encode())
                print("close "+str(self.addr))
                return
            self.func(data)
    def func(self, command):
        print(command.decode() + ' from ' + str(self.addr))
        if command.decode() == 'HELO':
            self.conn.send('HELO'.encode())
        elif command.decode() == 'CLOSE':
            self.conn.close()
        elif command.decode().find('AUTH') == 0:
            parts = command.decode().split()
            username = parts[1]
            password = parts[2]
            valid, errorcode = self.AuthCheck(username, password)

            if valid:
                self.conn.send("AUTH OK".encode())
            elif errorcode==1 or errorcode==2:
                self.conn.send('AUTH INVALID'.encode())
            else:
                self.conn.send('AUTH FAILED'.encode())
        elif command.decode().find('REG') == 0:
            parts = command.decode().split()
            username = parts[1]
            password = parts[2]
            valid, errorcode = self.RegCheck(username, password)

            if valid:
                self.conn.send("REG OK".encode())
            else:
                self.conn.send("REG OCCUPIED".encode())
        elif command.decode().find('SEARCH') == 0:
            parts = command.decode().split()
            by = parts[1]
            query = parts[2]
            print(by, query)
            with open ('data.json', 'r') as file:
                data = json.load(file)
                print(data)
                if by == 'ID':
                    try:
                        send = [data[query]]
                        print(send)
                        self.conn.send(bytes(str(len(send)),"utf8"))
                        self.conn.send(json.dumps(send).encode())
                        print('sent')
                    except Exception:
                        self.conn.send(bytes(str(len("NOT FOUND")),"utf8"))
                        self.conn.send("NOT FOUND".encode())
                else:
                    d = []
                    for i in data:
                        if data[i][by] == query:
                            d.append(data[i])
                    self.conn.send(bytes(str(len(d)),"utf8"))
                    self.conn.send(json.dumps(d).encode())
                    print('sent')
        elif command.decode().find('READ') == 0:
            parts=command.decode().split()
            id=str(parts[1])
            with open("data\\"+id+".txt","r") as file:
                data=file.read()
                #print(data)
                self.conn.send(bytes(str(len(data)),"utf8"))
                self.conn.sendall(bytes(data,"utf8"))

        
        
        pass
    def AuthCheck(self, username, password):
        with open('auth.json', "r") as file:
            active_acc = json.load(file)
            try:
                if active_acc[username] == password:
                    return True, 0
                else:
                    return False, 1
            except IndexError:
                return False, 2
            except:
                return False, 3

    def RegCheck(self, username, password):
        with open('auth.json', 'r') as file:
            active_acc = json.load(file)
            if username in active_acc:
                return False, 1
            active_acc[username] = password
        with open('auth.json', 'w') as file:
            json.dump(active_acc, file)
        return True, 0
class Server(object):
    def run(self):
        #Root
        self.root = Tk()
        self.root.title('Server')
        self.root.geometry('640x360')
        #Mainframe
        self.mainframe = ttk.Frame(self.root, padding="10 10 25 25")
        self.mainframe.grid(column=0, row=0)
        self.root.resizable(FALSE, FALSE)

        #TODO: Multi-connection
        
        self.openButton = ttk.Button(self.root, text='Open', command=self.connectThread)
        self.openButton.place(x=80, y=160, height=40, width=480)

        self.conn = None
        self.close_it = False
        self.root.mainloop()
    def connectThread(self):
        thr = threading.Thread(target=self.openServer, daemon=True)
        thr.start()
    def closeThread(self):
        thr = threading.Thread(target=self.Close, daemon=True)
        thr.start()
    def run_func(self,conn,addr):
        while True:
            data=conn.recv(1024)
            self.func(data)
    def openServer(self):
        global s 
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        
       
        self.openButton['command'] = self.closeThread
        self.openButton['text'] = 'Close (Current address: ' \
            + socket.gethostbyname(socket.gethostname()) + ', port: 1025)'
        s.bind(("", 1025))
        
        while True:
            s.listen()
            self.conn, self.addr = s.accept()
            s.listen()
            closeconn,closeaddr=s.accept()
            lst.append(closeconn)
            newthread=ClientThread(self.conn,self.addr,closeconn)
            newthread.start()


    def Close(self):
        for sockets in lst:
            try:
                sockets.send("CLOSE".encode())
                sockets.close()
            except:
                pass
        self.root.destroy()

se = Server()
thr = threading.Thread(target=se.run)
thr.start()