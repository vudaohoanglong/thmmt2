from tkinter import *
from tkinter import messagebox,filedialog
from tkinter import ttk
import socket
import threading
import sys
import auth
import json
import ReadWindow
try:
    addr = sys.argv[1]
    port = int(sys.argv[2])
except:
    addr = '127.0.0.1'
    port = 1025

print(addr)

class Client(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        
        
        #Root
        self.root = Tk()
        self.root.title("Client")
        self.root.geometry('1000x600')
        #Mainframe
        self.mainframe = ttk.Frame(self.root, padding='10 10 25 25')
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.resizable(FALSE, FALSE)
        
        #Frame for searching methods
        ttk.Label(self.mainframe, text="Search for books:").grid(column=1, row=1)
        self.searchQuery = StringVar()
        self.searchQuery.set("")
        self.searchBar = ttk.Entry(self.mainframe, width=100, textvariable=self.searchQuery)
        self.searchBar.grid(column=1, row=2)

        ttk.Label(self.mainframe, text='Search by:').grid(column=2, row=1)
        self.searchBy = StringVar(value="ID")
        self.searchByEntry = ttk.Combobox(self.mainframe, textvariable=self.searchBy, width=10, values=('ID', 'Author', 'Title', 'Genre'))
        self.searchByEntry.state(['readonly'])
        self.searchByEntry.grid(column=2, row=2)

        self.searchButton = ttk.Button(self.mainframe, text='Search', command=self.sendSearchQuery)
        self.searchButton.grid(column=3, row=2)

        for child in self.mainframe.winfo_children(): 
            child.grid_configure(padx=5, pady=5)
        #Frame for displaying details of books
        self.treeframe = ttk.Frame(self.root, padding='10 10 25 25')
        self.treeframe.grid(column=0, row=1)


        self.tree = ttk.Treeview(self.treeframe, columns=['Title', 'Author', 'Year', 'Genre'])
        
        self.tree.grid(column=1, row=2)
        self.tree.column('Year', width=50)
        self.tree.heading('Year', text='Year')
        self.tree.column('Genre', width=150)
        self.tree.heading('Genre', text='Genre')
        self.tree.column('Title', width=350)
        self.tree.heading('Title', text='Title')
        self.tree.column('Author', width=250)
        self.tree.heading('Author', text='Author')
        self.tree.column('#0', width=50)
        self.tree.heading('#0', text='ID')

        self.tree.bind("<Double-1>", self.OnDoubleClick)
        #Item
        
        self.item=None
        #Read and Download
        
     

        self.result = ''        
        for child in self.treeframe.winfo_children():
            child.grid_configure(padx=10, pady=5)
        #Connection socket and connecting to server
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        try:
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn.connect((addr,port))
            self.Connect()
            self.closeThread()
        except:
            #Quits if it fails to connect to the server
            messagebox.showerror(title='Connect error', message='An error occurred while trying to connect to the server.')
            try:
                self.root.destroy()
            except:
                pass
        self.authroot=Toplevel(self.root)
        self.auth = auth.Auth(self.authroot,self.conn); self.auth.startInstance()
        self.username = self.auth.username.get()
    def on_closing(self):
        self.Send("CLOSE")
        self.authroot.destroy()
        self.root.destroy()
    def Connect(self):
        self.closeconn=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.closeconn.connect((addr,port))
        self.Send('HELO')
        data = self.conn.recv(1024).decode()
        if data == 'HELO':
            return
        raise ConnectionError
    #TODO
    #closingthread
    def Closerecv(self):
        data=self.closeconn.recv(1024).decode()
        if (data=="CLOSE"):
            self.closeconn.close()
            self.authroot.destroy()
            self.root.destroy()
            self.conn.close()
    def closeThread(self):
        thr = threading.Thread(target=self.Closerecv, daemon=True)
        thr.start()
    #closingthread
    def sendSearchQuery(self):
        if (self.authroot.winfo_exists()): 
            messagebox.showerror("FAIL","PLEASE LOGIN")
            return
        self.tree.delete()
        command = "SEARCH " + self.searchBy.get() + " " + self.searchQuery.get()
        if (self.searchQuery.get()==""):
            return
        self.result = ''
        self.Send(command)
        leng=int(self.conn.recv(1024).decode("utf8"))
        #self.Send("got it")
        old = self.tree.get_children()
        for o in old:
            self.tree.delete(o)
        if (leng==0):
            data=self.conn.recv(1024)
            return
        while leng>0:
            data = self.conn.recv(1024)
            leng-=len(data)
            self.result += data.decode()
        if (self.result=="NOT FOUND"):
            return
        self.result = json.loads(self.result)
        for r in self.result:
            self.tree.insert("", "end", text=r['ID'], values=(r['Title'], r['Author'], r['Year'], r['Genre']))
    
    def update_UI(self):
        self.ReadButton=ttk.Button(self.mainframe,text="Read",command=self.read)
        self.ReadButton.grid(row=3,column=1)

        self.DownloadButton=ttk.Button(self.mainframe,text="Download",command=self.download)
        self.DownloadButton.grid(row=3,column=2)

    def OnDoubleClick(self,event):
        try:
            self.item = self.tree.selection()[0]
            #id=self.tree.item(self.item,"text")
            #print(id)
            self.update_UI()
            print("you clicked on", self.tree.item(self.item,"text"))
        except:
            pass
    def read(self):
        id=self.tree.item(self.item,"text")
        print(id)
        command="READ "+str(id)
        self.Send(command)
        leng=int(self.conn.recv(1024).decode("utf8"))
        data_book=b""
        while leng>0:
            data=self.conn.recv(1024)
            leng-=len(data)
            data_book+=data
        data_book=data_book.decode("utf8")
        newReadWindowroot=Toplevel(self.root)
        newReadWindow=ReadWindow.ReadWindow(newReadWindowroot,data_book)
        newReadWindow.startInstance()
    def download(self):
        id=self.tree.item(self.item,"text")
        print(id)
        command="READ "+str(id)
        self.Send(command)
        leng=int(self.conn.recv(1024).decode("utf8"))
        data_book=b""
        while leng>0:
            data=self.conn.recv(1024)
            leng-=len(data)
            data_book+=data
        #data_book=data_book.decode("utf8")
        files=[('Text Documents','*.txt')]
        file= filedialog.asksaveasfile(
            mode="wb", filetypes=files, defaultextension=files, title="Save book")
        if file !=None:
            file.write(data_book)
            file.close()
    def Send(self, command:str):
        #self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.conn.connect((addr, port))
        self.conn.send(command.encode())

user=Client()