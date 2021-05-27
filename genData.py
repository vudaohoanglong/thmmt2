import json
import sys
with open("data.json","r") as file:
    data_book=json.load(file)
    data_book["2"]={"ID":"2","Title":"Hehe","Author":"Hoangnhoxx","Year":"2001","Genre":"Sci-fi"}
with open("data.json","w") as file:
    json.dump(data_book,file)