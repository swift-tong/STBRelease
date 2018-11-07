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
import thread
import time
import multiprocessing
import getUserInfo
import paramiko
import getDiffFile
 
def isLinuxSystem():
    return 'Linux' in platform.system()

class CheckUserInput():
    def __init__(self,jsonData):
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
        self.userInfoDict=getUserInfo.userInfoDict
        self.homeDir=""
        self.jsonData=jsonData
        self.rkType=["rk3228b","rk3228h"]
        self.amlType=["s905l","s905lv2"]
        self.diff_mani=""
        self.host=""
        self.user=""
		
        dataDict = {}
        if isLinuxSystem():
            dataDict0 = json.loads(self.jsonData) #<type 'unicode'>
            dataDict = json.loads(dataDict0) #<type 'dict'>
        else:
            dataDict = json.loads(self.jsonData) #<type 'dict'>

        self.logger.info("Input dict = {}".format(dataDict))
        self.swVersion=dataDict["swVersion"]
        self.productClass=dataDict["productClass"]
        self.wifiType=dataDict["wifiType"]
        self.operator=dataDict["operator"]
        self.province=dataDict["province"]
        #if self.province == "jc":
        #    self.province="sh"
        if "R2" in self.swVersion:
            self.host=self.userInfoDict[(self.productClass,self.operator.lower()+self.province,"R2")][1]
            self.user=self.userInfoDict[(self.productClass,self.operator.lower()+self.province,"R2")][0]
        else:
            self.host=self.userInfoDict[(self.productClass,self.operator.lower()+self.province)][1]
            self.user=self.userInfoDict[(self.productClass,self.operator.lower()+self.province)][0]
        self.chipset=dataDict["chipset"]
        self.midware=dataDict["midware"]
		
        self.logger.info("chipset={}.".format(self.chipset))
        self.logger.info("Remot host={}.".format(self.host))
        self.logger.info("Remot user={}.".format(self.user))

    def getProductPropertyList(self):
        productList=[(key[0],key[1]) for key in tuple(intmapext.IntToExtDict.keys())]
        return productList

    def paramiko_command(self,_command):
        plog=self.logger.info
        command=_command
        ssh=paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=self.host, port=22, username=self.user, password="123456")
        stdin,stdout,stderr = ssh.exec_command(command)
        out = stdout.read().decode()
        err = stderr.read()
        ssh.close()
        #plog("out={}".format(out))
        #plog("err={}".format(err))

        return out

    def get_remote_full_dir(self):
        plog=self.logger.info
        fullDir=""
        retTup=()
        retStr=self.paramiko_command("pwd")
        self.homeDir=retStr[:-1]
        plog("Home Ptah = {}".format(self.homeDir))
		
        retStr2=self.paramiko_command("find build/property -name 'full'")
        if retStr2:
            fullDir=self.homeDir+"/"+retStr2[:-1]
            plog("fullDir rk={}".format(fullDir))
        else:
            retStr3=self.paramiko_command("find property -name 'full'")
            if retStr3:
                fullDir=self.homeDir+"/"+retStr3[:-1]
                plog("fullDir aml={}".format(fullDir))
        if not fullDir:
            plog("user:{},host:{} no fullDir.".format(self.user,self.host))
        return fullDir

    def checkRemoteFile(self,_check_file):
        retList=[]
        check_file=_check_file
        self.logger.info("self.homeDir={}".format(self.homeDir))
        if self.chipset.lower() in self.rkType:
            command = "ls {}/build/property/full/*".format(self.homeDir)
        elif self.chipset.lower() in self.amlType:
            command = "ls {}/property/full/*".format(self.homeDir)
        self.logger.info("command={}".format(command))
        retStr=self.paramiko_command(command)
        self.logger.info("retStr={}".format(retStr))
        retList=retStr.split("\n")
        del(retList[0])
        del(retList[-1])
        for i,item in enumerate(retList):
            retList[i]=item.split("/")[-1]
        if check_file in retList:      
            return True
        else:
            return False

    def checkRemoteMani(self):
        retList=[]
        self.logger.info("self.homeDir={}".format(self.homeDir))
        if self.chipset.lower() in self.rkType:
            command = "ls {}/build/property/ota/*".format(self.homeDir)
        elif self.chipset.lower() in self.amlType:
            command = "ls {}/property/ota/*".format(self.homeDir)
        self.logger.info("command={}".format(command))
        retStr=self.paramiko_command(command)
        self.logger.info("retStr={}".format(retStr))
        retList=retStr.split("\n")
        self.logger.info("retList={}".format(retList))
        for item in retList:
            if item:
                check_str=item.split("/")[-1]
                self.logger.info("check_str={}".format(check_str))
            else:
                check_str=""
                self.logger.info("check_str={}".format(check_str))
            if self.diff_mani == check_str:
                self.logger.info("self.diffmani find.")			
                return True
        self.logger.info("self.diffmani not find.")	
        return False			
		
    def transport_file(self,_local_full_dir,_remot_full_dir):
        plog=self.logger.info       
        local_full_dir=_local_full_dir
        remot_full_dir=_remot_full_dir
        full_file=self.swVersion+".txt"
        json_file=self.swVersion+".json"
        transport = paramiko.Transport((self.host, 22))
        transport.connect(username=self.user, password="123456")
        sftp = paramiko.SFTPClient.from_transport(transport)

        plog(u'Get File%stransporting...'.format(full_file))
        local_filename = os.path.join(local_full_dir, full_file)
        remote_filename = os.path.join(remot_full_dir, full_file)
        local_json_file= os.path.join(local_full_dir, json_file)
        remote_json_file = os.path.join(remot_full_dir, json_file)
        plog("local_filename={}".format(local_filename))
        plog("remote_filename={}".format(remote_filename))
        plog("local_json_file={}".format(local_json_file))
        plog("remote_json_file={}".format(remote_json_file))

        local_full_exists=os.path.exists(local_full_dir+self.swVersion+".txt")
        local_json_exists=os.path.exists(local_full_dir+self.swVersion+".json")		
		
        check_ret=self.checkRemoteFile(self.swVersion+".txt")
        if check_ret and not local_full_exists:
            sftp_ret=sftp.get(remote_filename, local_filename)
            plog("sftp_ret={}".format(sftp_ret))
            plog("Transport {} Done.".format(local_filename))
        check_ret2=self.checkRemoteFile(self.swVersion+".json")
        if check_ret2 and not local_json_exists:
            sftp_ret2=sftp.get(remote_json_file, local_json_file)
            plog("sftp_ret2={}".format(sftp_ret2))
            plog("Transport {} Done.".format(local_json_file))
        transport.close()


    def transport_mani_file(self,_local_mani_dir,_remot_mani_dir,):
        plog=self.logger.info       
        local_mani_dir=_local_mani_dir
        remot_mani_dir=_remot_mani_dir
        transport = paramiko.Transport((self.host, 22))
        transport.connect(username=self.user, password="123456")
        sftp = paramiko.SFTPClient.from_transport(transport)		
		
        info={"chipset":self.chipset,"swVersion":self.swVersion}
        gdf=getDiffFile.GetDiffFile()
        retBool=gdf.initUserInfo(str(info))
        if not retBool:
            plog("initUserInfo error!!")
        gdf.getFileList()
        if self.swVersion+".txt" not in gdf.fileList:
            plog("There are no {}".format(self.swVersion +"_manifest.txt"))
            return
        else:
            #get diff file
            diffFile=gdf.getDiff()
            self.diff_mani=diffFile[:-4]+"_manifest.txt"
            plog("diffFile={}".format(self.diff_mani))

        plog(u'Get File%stransporting...'.format(self.diff_mani))
        local_mani = os.path.join(local_mani_dir, self.diff_mani)
        remote_mani = os.path.join(remot_mani_dir, self.diff_mani)
        plog("local_mani={}".format(local_mani))
        plog("remote_mani={}".format(remote_mani))

        local_mani_exists=os.path.exists(local_mani)
			
        check_ret=self.checkRemoteMani()
        if check_ret and not local_mani_exists:
            sftp_ret=sftp.get(remote_mani,local_mani)
            #plog("sftp_ret={}".format(sftp_ret))
            plog("Transport {} Done.".format(local_mani))
        transport.close()		
	
    def getRemoteFile(self):
        plog=self.logger.info
        local_full_dir="/usr/local/stbrelease/data/"+self.chipset.lower()+"/"+self.productClass.lower()+"/"+self.operator.lower()+self.province.lower()+"/"+"full/"
        local_full_file=local_full_dir+self.swVersion+".txt"
        remot_full_dir=self.get_remote_full_dir()
        remote_full_file=remot_full_dir+self.swVersion+".txt"
        if not os.path.exists(local_full_dir):
            os.makedirs(local_full_dir)
        else:
            if not os.path.exists(local_full_file):
                retStr=self.transport_file(local_full_dir,remot_full_dir)
            else:
                plog("{} exists ,do nothing.".format(local_full_file))
				
        local_mani_dir="/usr/local/stbrelease/data/"+self.chipset.lower()+"/"+self.productClass.lower()+"/"+self.operator.lower()+self.province.lower()+"/"+"ota/"
        local_mani_file=local_mani_dir+self.swVersion+"_manifest.txt"
        remot_mani_dir=self.get_remote_full_dir()[:-4]+"ota/"
        remote_mani_file=remot_mani_dir+self.swVersion+"_manifest.txt"
        plog("remote_mani_file={}".format(remote_mani_file))
        if not os.path.exists(local_mani_dir):
            os.makedirs(local_mani_dir)
        else:
            if not os.path.exists(local_mani_file):
                retStr=self.transport_mani_file(local_mani_dir,remot_mani_dir)
            else:
                plog("{} exists ,do nothing.".format(local_mani_file))
        
		
		
    def checkInput(self):
        plog=self.logger.info
        reasonStr=""
        endStr=""
        searchPattern=""
        retJson=None       
                
        productPropertyList=self.getProductPropertyList()
        self.logger.info("productPropertyList={}".format(productPropertyList))

        if self.operator.upper()+self.province.upper() == "GCGC":
            searchPattern="_FAC_"
        else:
            searchPattern="_"+self.operator.upper()+self.province.upper()

        self.logger.info("searchPattern={}".format(searchPattern))
        self.logger.info("self.swVersion={}".format(self.swVersion))
        if searchPattern=="_CMJC":
            searchPattern="_CMSH"
        p1=re.search(searchPattern,self.swVersion)
        if not p1:
            reasonStr=reasonStr+"operator or province, "

        p2=re.match(self.productClass+'_',self.swVersion)
        if not p2:
            reasonStr=reasonStr+"productClass, "
                
        if "_" in self.swVersion:
            a_tup=(self.swVersion.split("_SW")[0],(self.chipset,self.wifiType))
            self.logger.info("a_tup={}".format(a_tup))
            if a_tup not in productPropertyList:
                reasonStr=reasonStr+"chipset or wifiType, "
        else:
            reasonStr=reasonStr+"chipset or wifiType, "

        self.logger.info("reasonStr={}".format(reasonStr))

        if self.swVersion.endswith(".img"):
            endStr=endStr+"Software version can not end with '.img'."
            self.logger.info("endStr={}".format(endStr))
        
        if reasonStr:
            reasonStr=reasonStr+"is(are) not correct."
        if reasonStr or endStr:
            retDict={
                      "result":"NOK", 
                      "reason":reasonStr+endStr
                    }
        else:
            retDict={
                   "result":"OK",
                   "reason":""
                } 
        if retDict["result"] == "OK":
            try:
                p = multiprocessing.Process(target = self.getRemoteFile, args = ())
                p.start()
            except:
                plog("Error: unable to start Process.")

        retJson=json.dumps(retDict)
        return retJson

			
# To adapt jsonstring from java api
def makeJson(jsonStr):
    str1 = re.sub(r"(\w+):", r"'\1':", jsonStr)
    str2 = re.sub(r":(\S)", r":'\1", str1)
    str3 = re.sub(r"(\S),", r"\1',", str2)
    str4 = re.sub(r"(})", r"'\1", str3)
    return str4
    
if __name__ == "__main__":
    
    DEBUG=0
    
    json_str=""
    if DEBUG:
        data={
            "swVersion":"S-010W-A_SW_ZY_CULN_R1.01.03",
            "productClass":"S-010W-A",
            "wifiType":"RTL8189ETV",
            "operator":"CU",
            "province":"ln",
            "chipset":"RK3228B",
            "midware":"suying"
        }
        json_str = json.dumps(data)
    else:
        input_json = sys.argv[1]
        if isLinuxSystem():
            json_str = json.dumps(input_json)
        else:
            newjson = makeJson(input_json)
            dictJson = eval(newjson)
            json_str = json.dumps(dictJson)
   
    #print 'json_str='+json_str
    
    cui=CheckUserInput(json_str)
    ret=cui.checkInput()
    print ret


#test:
