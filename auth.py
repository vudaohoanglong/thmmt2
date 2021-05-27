from tkinter import *
from tkinter import ttk
import sys
import socket
from tkinter import messagebox

try:
    addr = sys.argv[1]
    port = int(sys.argv[2])
except:
    addr = '127.0.0.1'
    port = 1025

class Auth(object):
    def __init__(self, root, conn):
        
        self.conn=conn
        

        self.AuthRoot = root
        self.AuthRoot.title("Login")

        self.mainframe = ttk.Frame(self.AuthRoot, padding="10 10 25 25")
        self.mainframe.grid(column=0, row=0)
        self.AuthRoot.resizable(FALSE, FALSE)
        self.AuthRoot.rowconfigure(0, weight=1)
        self.AuthRoot.columnconfigure(0, weight=1)
        #Username input
        self.username = StringVar()
        self.username.set("")
        username_entry = ttk.Entry(self.mainframe, width=30, textvariable=self.username)
        ttk.Label(self.mainframe, text="Username\t").grid(column=1, row=1)
        username_entry.grid(column=2, row=1)
        #Password input
        self.password = StringVar()
        self.password.set("")
        password_entry = ttk.Entry(self.mainframe, show="*", width=30, textvariable=self.password)
        ttk.Label(self.mainframe, text="Password\t").grid(column=1, row=2)
        password_entry.grid(column=2, row=2)
        #Confirmation button
        subframe = ttk.Frame(self.AuthRoot, padding = "3 3 12 12")
        subframe.grid(column=0, row=1)
        confButton = ttk.Button(subframe, text="Log in", command=self.Authenticate)
        confButton.grid(column=1, row=1)
        #Register button
        regButton = ttk.Button(subframe, text='Register', command=self.Register)
        regButton.grid(column=2, row=1)
        self.AuthRoot.protocol("WM_DELETE_WINDOW", self.on_closing)
    def on_closing(self):
        return
    def startInstance(self):
        self.AuthRoot.mainloop()
    def Register(self):
        command = "REG " + self.username.get() + " " + self.password.get()
        if self.username.get()=="" or self.password.get()=="":
            messagebox.showerror("FAIL","FAIL")
            return
        self.Send(command)
        data = self.conn.recv(20).decode()
        if data != 'REG OK':
            messagebox.showerror(title="Register failed", message=f"The account accociated with the username {self.username.get()} has been registered.")
        else:
            messagebox.showinfo(title="Register successful", message=f"You have registered successfully. Welcome, {self.username.get()}.")
        
    def Authenticate(self):
        command = "AUTH " + self.username.get() + " " + self.password.get()
        if self.username.get()=="" or self.password.get()=="":
            messagebox.showerror("FAIL","FAIL")
            return
        self.Send(command)
        data = self.conn.recv(20).decode()
        if data == 'AUTH OK':
            self.AuthRoot.destroy()
        elif data == 'AUTH INVALID':
            messagebox.showerror(title='Invalid credentials', message='The username or password is incorrect.')
        elif data == 'AUTH FAILED':
            messagebox.showerror(title='Error', message='An unknown error occured during authentication.')
        
    def Send(self, command:str):
        self.conn.send(command.encode())
