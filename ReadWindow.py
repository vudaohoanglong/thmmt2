from tkinter import *
from tkinter import ttk
import tkinter.scrolledtext as st
class ReadWindow(object):
    def __init__(self,root,data):
        self.root=root
        self.root.title("Reading")
        self.root.geometry('1000x600')
        self.mainframe = ttk.Frame(self.root, padding='10 10 25 25')
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.resizable(FALSE, FALSE)
        self.text_area=st.ScrolledText(self.root,width=900,height=500,font=("Times New Roman",15))
        self.text_area.grid(column=0,row=0,padx=10,pady=10)
        self.text_area.insert(INSERT,data)
    def startInstance(self):
        self.root.mainloop()