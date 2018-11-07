import os
import sys
import json


jsonObj={}


def sort_Province():
    with open("stbrelease.cfg.json","w") as f2:
        list_dict=jsonObj["Province"]
        list_str=[json.dumps(item) for item in list_dict]
        list_str.sort()
        for i in list_str:
            print i
        list_dict_new=[json.loads(item) for item in list_str]
        print list_dict_new
        jsonObj["Province"]=list_dict_new
        strObj=json.dumps(jsonObj,indent=4,ensure_ascii=False).encode("utf-8")
        print strObj
        print type(strObj)
        f2.write(strObj)


def sort_productClass():
    with open("stbrelease.cfg.json","w") as f2:
        list_str=jsonObj["productClass"]
        list_str.sort()
        for i in list_str:
            print i
        jsonObj["productClass"]=list_str
        strObj=json.dumps(jsonObj,indent=4,ensure_ascii=False).encode("utf-8")
        print strObj
        print type(strObj)
        f2.write(strObj)


if __name__ == "__main__":
    with open("stbrelease.cfg.json","r") as f:
        str=f.read()
        jsonObj=json.loads(str)
    sort_productClass()


