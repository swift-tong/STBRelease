#!/usr/bin/env python
# coding=utf-8 
import sys
import os
import intmapext
import json
import datetime
import logging

class WriteConfig():
    def __init__(self):
        self.confDict={}

        logYear=str(datetime.datetime.now().year)
        logMonth=str(datetime.datetime.now().month) if datetime.datetime.now().month >10 else "0"+str(datetime.datetime.now().month)
        logDay=str(datetime.datetime.now().day) if datetime.datetime.now().day >10 else "0"+str(datetime.datetime.now().day)
        #logFile=logYear+logMonth+logDay+"_STBRelease.log"
        #logdir=os.getcwd()+"/%s"%logFile

        self.logger = logging.getLogger("STBRelease log")
        self.logger.setLevel(logging.INFO)
        #self.fh = logging.FileHandler(logdir)
        self.ch = logging.StreamHandler()
        formatter = logging.Formatter('%(message)s')
        #self.fh.setFormatter(formatter)
        self.ch.setFormatter(formatter)
        #self.logger.addHandler(self.fh)
        self.logger.addHandler(self.ch)


    def writeConfig(self):
        plog=self.logger.info
        cfgpath = "/usr/local/stbrelease/scripts/stbrelease.cfg.json"
        with open(cfgpath) as f:
            fileStr=f.read()
            self.confDict=eval(fileStr)
        plog("self.confDict.keys():")
        plog(self.confDict.keys())
        
        for key in intmapext.IntToExtDict:
            if key[0] not in self.confDict["productClass"]:
                self.confDict["productClass"].append(key[0])
            
            if key[1][0] not in self.confDict["chipset"]:
                self.confDict["chipset"].append(key[1][0])

            if key[1][1] not in self.confDict["wifiType"]:
                self.confDict["wifiType"].append(key[1][1])

        plog(self.confDict["productClass"])
        plog(self.confDict["chipset"])
        plog(self.confDict["wifiType"])
           
        jsonStr=json.dumps(self.confDict,indent=4,ensure_ascii=False)
        #print jsonStr
        with open(cfgpath,"w") as f2:
            f2.write(jsonStr)
	
	
	
	
if __name__ == "__main__":
    wc=WriteConfig()
    ret=wc.writeConfig()
    json = {"result":"OK","reason":""}
    print json
