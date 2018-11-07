#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import re
import os
import sys
import datetime
import logging
import intmapext
import platform
import pexpect
 
def isLinuxSystem():
    return 'Linux' in platform.system()


class ConversionOldRelease():
    def __init__(self):
        logYear=str(datetime.datetime.now().year)
        logMonth=str(datetime.datetime.now().month) if datetime.datetime.now().month >10 else "0"+str(datetime.datetime.now().month)
        logDay=str(datetime.datetime.now().day) if datetime.datetime.now().day >10 else "0"+str(datetime.datetime.now().day)
        #logFile=logYear+logMonth+logDay+"_STBRelease.log"
        #logdir=os.getcwd()+"/%s"%logFile

        self.logger = logging.getLogger("STBRelease2 log")
        self.logger.setLevel(logging.INFO)
        #self.fh = logging.FileHandler(logdir)
        self.ch = logging.StreamHandler()
        formatter = logging.Formatter('%(message)s')
        #self.fh.setFormatter(formatter)
        self.ch.setFormatter(formatter)
        #self.logger.addHandler(self.fh)
        self.logger.addHandler(self.ch)

        self.oldRawDataFile=os.getcwd()+"/releaseNote/releaseRecord.txt"
        self.newRawDataFile=os.getcwd()+"/releaseNote/newReleaseRecord.txt"
        self.wifiTypeDict={
            ("RK3228B","S-010W-A") : "RTL8189ETV",
            ("RK3228B","G-120WT-P") : "MTK7526FU",
            ("S905L","RG020ET-CA") : "RTL8676",
            ("S905L","S-010W-AV2T") : "NOWIFI",
            ("RK3228H","S-010W-AV2S") : "NOWIFI",
            ("RK3228H","S-010W-A") : "8189FTV",
            ("RK3228H","S-010W-AQD") : "8189FTV",
            ("RK3228H","S-010W-AV2B") : "8189FTV",
            ("RK3228H","S-010W-AV2") : "RTL8822BS",
        }
		
        for key in intmapext.IntToExtDict:
            if (key[1][0],key[0]) not in self.wifiTypeDict.keys():
                self.wifiTypeDict[(key[1][0],key[0])]=key[1][1]
        self.logger.info("wifiTypeDict=")
        self.logger.info(self.wifiTypeDict)

    def getNewElement(self,_eleList):
        eList=_eleList
        swVersion=""
        productClass=""
        wifiType=""
        operator=""
        province=""
        chipset=""
        chipsetDate=""
        midware=""
        midwareDate=""
        author=""
        firmwareDate=""
        noteAddr=""
        firmwareAddr=""

        swVersion=eList[6]
        productClass=eList[0]
        if (eList[3].split("_")[0],eList[0]) in self.wifiTypeDict.keys():
            wifiType=self.wifiTypeDict[(eList[3].split("_")[0],eList[0])]
        else:
            wifiType=""

        operator=eList[2]
        province=eList[1]
        chipset=eList[3].split("_")[0]
        if len(eList[3].split("_")) == 2:
            chipsetDate=eList[3].split("_")[1]
        else:
            chipsetDate=""

        midware=eList[4].split("_")[0]
        if len(eList[4].split("_")) == 2:
            midwareDate=eList[4].split("_")[1]
        else:
            midwareDate=""

        author=eList[7]
        firmwareDate=eList[8]
        noteAddr=eList[9]
        firmwareAddr=eList[10]
        firmwareDate=re.sub(r'-','',firmwareDate)
        return swVersion+","+productClass+","+wifiType+","+operator+","+province+","+chipset+","+chipsetDate+","+midware+","+midwareDate+","+author+","+firmwareDate+","+noteAddr+","+firmwareAddr

    def makeNewRawData(self):
        newRawDataList=[]
        with open(self.oldRawDataFile) as f:
            lineList=f.readlines()
            for element in lineList:
                eleList=element.split(";")
                if len(eleList) != 11:
                    self.logger.info(element)
                    continue
                newElement=self.getNewElement(eleList)
                newRawDataList.append(newElement)

        with open(self.newRawDataFile,"w") as f1:
            f1.writelines(newRawDataList)

			
# To adapt jsonstring from java api
def makeJson(jsonStr):
    str1 = re.sub(r"(\w+):", r"'\1':", jsonStr)
    str2 = re.sub(r":(\S)", r":'\1", str1)
    str3 = re.sub(r"(\S),", r"\1',", str2)
    str4 = re.sub(r"(})", r"'\1", str3)
    return str4
    
if __name__ == "__main__":
    cor=ConversionOldRelease()
    cor.makeNewRawData()

#test:
