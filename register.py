from tkinter import *
from tkinter import ttk
import socket
import threading
import time

class Register(threading.Thread):
    def __init__(self, root, conn):
        threading.Thread().__init__()

        self.RegRoot = Tk(root)
        self.RegRoot.title("Register")

        self.mainframe = ttk.Frame(self.AuthRoot, padding="10 10 25 25")
        self.mainframe.grid(column=0, row=0)
        self.RegRoot.resizable(FALSE, FALSE)
        self.RegRoot.rowconfigure(0, weight=1)
        self.RegRoot.columnconfigure(0, weight=1)
        
        