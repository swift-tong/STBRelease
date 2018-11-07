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
import getUserInfo
import paramiko
import shutil

log = logging.getLogger("build check")
log.setLevel(logging.DEBUG)
hdlr = logging.StreamHandler()
formatter = logging.Formatter('%(message)s\n')
hdlr.setFormatter(formatter)
log.addHandler(hdlr)


class GetDiffFile(object):
    def __init__(self):
        super(GetDiffFile,self).__init__()
        self.userInfoDict=getUserInfo.userInfoDict
        self.dataFolder="/usr/local/stbrelease/data/"
        self.confFolder="/usr/local/stbrelease/scripts/conf/"
        self.rkType=["RK3228B","RK3228H"]
        self.amlType=["S905L"]
        self.retDict={}
        self.launcherList=[]
        self.folderList=[]
        self.diffFile=""
        self.province=""
        self.product=""
        self.imgName=""
        self.chipset=""
        self.user=""
        self.host=""
        self.password=""
        self.childFolder=""
        self.homeDir=""
        self.oldVersion=""
        self.newVersion=""
        self.fileList=[]

    def initUserInfo(self,_info):
        info=_info
        log.info("info="+info)
        self.imgName=eval(info)["swVersion"]
        self.chipset=eval(info)["chipset"]
		
        key_product=self.imgName.split("_SW")[0]
        self.product=key_product
        key_province=""
        p1=re.search("_(C[A-Z]+)_",self.imgName)
        p2=re.search("_(FAC)_",self.imgName)
        p3=re.search("_(CTOSSM)_",self.imgName)
        p4=re.search("_(ZSQD)_",self.imgName)
        p5=re.search("_(OSSM)_",self.imgName)
        check_list=[("S-010W-A","cusd"),("S-010W-AV2S","cunm")]

        if p1:
            key_province=p1.group(1)
        if p2:
            key_province=p2.group(1)
        if p3:
            key_province=p3.group(1)
        if p4:
            key_province=p4.group(1)
        if p5:
            key_province=p5.group(1)
            #key_province="OSOSSM"

        self.province=key_province
        if "R2" in self.imgName:
            userKey=(key_product,key_province.lower(),"R2")
        elif "R3" in self.imgName:
            userKey=(key_product,key_province.lower(),"R3")
        else:
            userKey=(key_product,key_province.lower())
        log.info("userKey is:{}".format(userKey))
        if userKey not in self.userInfoDict.keys():
            log.info("userKey {} can not make transition,check getUserInfo.py.".format(userKey))
            return False
        log.info("(self.product,self.province) is:({},{})".format(self.product,self.province))
        userValue=self.userInfoDict[userKey]
        self.user=userValue[0]
        self.host=userValue[1]
        self.password="123456"
        log.info("User is:{}".format(self.user))
        log.info("Host is:{}".format(self.host))
        self.childFolder=self.chipset.lower()+"/"+key_product.lower()+"/"+key_province.lower()+"/"+"ota/"
        self.full_dir="/usr/local/stbrelease/data/"+self.chipset.lower()+"/"+key_product.lower()+"/"+self.province.lower()+"/"+"full/"
        self.ota_dir="/usr/local/stbrelease/data/"+self.chipset.lower()+"/"+key_product.lower()+"/"+self.province.lower()+"/"+"ota/"
        command= "pwd"
        self.homeDir=self.ssh_command(command).split("\r\n")[1]
        return True

    def findLauncher(self):
        for item in self.fileList:
            p=re.search(".*{}_(\w+)_R.*".format(self.province.upper()),item)
            if p:
                if p.group() not in self.launcherList:
                    self.launcherList.append(p.group(1))
        log.info("self.launcherList={}".format(str(self.launcherList)))
		
    def getDiff(self):
        specialList=[]
        typeDict={}
        keyX="" 
        keyType=""		
        for fi in self.fileList:
            p=re.search(".*((R\d)\.(\d{2})).*",fi)
            if p:
                if int(p.group(3)) < 2:
                    keyX=p.group(2)+".(00,01)"
                    if keyX not in typeDict.keys():
                        typeDict[keyX]=[p.group()]
                    else:
                        typeDict[keyX].append(p.group())
                else:
                    keyX=p.group(1)
                    if p.group(1) not in typeDict.keys():
                        typeDict[keyX]=[p.group()]
                    else:
                        typeDict[keyX].append(p.group())
        log.info("typeDict:")
        for key in typeDict.keys():
            log.info("{}{}{}{}".format(key," "*(10-len(key)),":",typeDict[key]))
			
        log.info("\nInput Name:{}\n".format(self.imgName))
        pNew=re.search(r".*((R\d)\.(\d{2})).*",self.imgName)
        if pNew:
            if int(pNew.group(3)) < 2:
                keyType=pNew.group(2)+".(00,01)"
            else:
                keyType=pNew.group(1)			
		
        swIndex=typeDict[keyType].index(self.imgName+".txt")

        self.findLauncher()
        if len(self.launcherList) > 1 and len(typeDict.keys()) == 1:
            p2=re.search(".*{}_(\w+)_R.*".format(self.province.upper()),self.imgName)
            if p2:
                imgLauncher=p2.group(1)
            else:
                log.info("No launcher in img name,please re check.")
            for fi2 in self.fileList:
                p3=re.search(".*_{}_.*".format(imgLauncher.upper()),fi2)
                if p3:
                    specialList.append(p3.group())
            log.info("specialList:")
            log.info(str(specialList))
            swIndex=specialList.index(self.imgName+".txt")			

        if swIndex == 0:
            log.info("self.imgName:{} is the first version,copy it to ota dir {}.".format(self.imgName,self.ota_dir))
            fu_file=self.full_dir+self.imgName+".txt"
            ot_file=self.ota_dir+self.imgName+".txt"
            shutil.copyfile(fu_file,ot_file)
            return self.imgName+".txt"
        else:
            self.oldVersion=typeDict[keyType][swIndex-1][:-4]
            self.newVersion=self.imgName
            return typeDict[keyType][swIndex-1][:-4]+"_"+self.imgName+".txt"

    def ssh_command(self,_command):
        command=_command
        ssh_newkey = 'Are you sure you want to continue connecting'
        child = pexpect.spawn('ssh -l %s %s %s' % (self.user,self.host,command))
        i = child.expect([pexpect.TIMEOUT, ssh_newkey, 'password: '])
        if i == 0:
            log.error(""'ERROR!'
                              'SSH could not login. Here is what SSH said:'
                              'child.before, child.after')
            return False
        if i == 1:
            child.sendline('yes')
            child.expect('password: ')
            i = child.expect([pexpect.TIMEOUT, 'password: '])
            if i == 0:
                log.error(""'ERROR!'
                                  'SSH could not login. Here is what SSH said:'
                                  'child.before, child.after')
        child.sendline(self.password)
        child.expect(pexpect.EOF)
        retStr=child.before
        return retStr


    def firstSetDataFolder(self):
        for key in intmapext.IntToExtDict.keys():
            folderTup=(key[1][0],key[0],key[4])
            if folderTup not in self.folderList:
                self.folderList.append(folderTup)
        for item in self.folderList:
            path=self.dataFolder+item[0].lower()+"/"+item[1].lower()+"/"+item[2].lower()+"/"+"ota/"
            path2=self.dataFolder+item[0].lower()+"/"+item[1].lower()+"/"+item[2].lower()+"/"+"full/"
            if not os.path.exists(path):
                os.makedirs(path)
            if not os.path.exists(path2):
                os.makedirs(path2)

    def makeDataFolder(self):
        os.chdir("/usr/local/stbrelease/data/")
        path=self.chipset.lower()+"/"+self.product.lower()+"/"+self.province.lower()+"/"+"full/"
        path2=self.chipset.lower()+"/"+self.product.lower()+"/"+self.province.lower()+"/"+"ota/"
        log.info("path full = {}".format(path))
        if not os.path.exists(path):
            os.makedirs(path)
            log.info("Make path full {}".format(path))
        else:
            log.info("{} exists,do nothing.".format(path))
			
        log.info("path ota = {}".format(path2))
        if not os.path.exists(path2):
            os.makedirs(path2)
            log.info("Make path ota {}".format(path2))
        else:
            log.info("{} exists,do nothing.".format(path2))

    def checkDiffExist(self):
        diffPath=self.chipset.lower()+"/"+self.product.lower()+"/"+self.province.lower()+"/"+"ota/"
        check_file="/usr/local/stbrelease/data/"+diffPath+self.diffFile
        log.info("Check file = {}".format(check_file))
        return os.path.exists(check_file)

    def getDataFolderCount(self):
        count = 0
        for i in os.walk(self.dataFolder):
            count += 1
        log.info("dataFolder={}".format(count))
        return count

    def getRemoteFileList(self):
        retList=[]
        log.info("homeDir={}".format(self.homeDir))
        if self.chipset in self.rkType:
            command = "ls {}/build/property/full/*".format(self.homeDir)
        elif self.chipset in self.amlType:
            command = "ls {}/property/full/*".format(self.homeDir)
        log.info("command={}".format(command))
        retStr=self.ssh_command(command)
        log.info("retStr={}".format(retStr))
        retList_tmp=retStr.split("\r\n")
        del(retList_tmp[0])
        del(retList_tmp[-1])
        for i,item in enumerate(retList_tmp):
            retList_tmp[i]=item.split("/")[-1]
        for item in retList_tmp:
            if item.endswith(".txt"):
                retList.append(item)
        log.info("File on %s@%s:"%(self.user,self.host))	
        log.info(str(retList))
        return retList

    def getLocalFileList(self):
        retList=[]
        command= "ls {}*".format(self.full_dir)
        retStr=os.popen(command).read()
        log.info("retStr={}".format(retStr))	
		
        ret_full_list=retStr.split("\n")[:-1]
        retList_tmp=[fi.split("/")[-1] for fi in ret_full_list]
        for item in retList_tmp:
            if item.endswith(".txt"):
                retList.append(item)
        log.info("server retList={}".format(str(retList)))
        return retList

    def make_ota_from_server_new(self,_newVersion,_oldVersion):
        ota_diff_file=self.ota_dir+self.diffFile
        max_add_len=0
        max_modify_len=0
        max_delete_len=0
        newList=[]
        finalList=[]
        old_dict={}
        new_dict={}
        add_list_tmp=[]
        modify_list_tmp=[]
        delete_list_tmp=[]
        addList=["\nAdd:\n"]
        modifyList=["\nModify:\n"]
        deleteList=["\nDelete:\n"]
        oldVersion=_oldVersion
        newVersion=_newVersion
        pass_index_list=[]

        log.info(self.full_dir+"{}.json".format(newVersion))
        log.info(self.full_dir+"{}.json".format(oldVersion))
        with open(self.full_dir+"{}.json".format(newVersion),"r") as new_file:
            new_dict=json.loads(new_file.read())
        with open(self.full_dir+"{}.json".format(oldVersion),"r") as old_file:
            old_dict=json.loads(old_file.read())
        
        for key in old_dict.keys():
            if key in new_dict.keys():
                if old_dict[key] == new_dict[key]:
                    old_dict.pop(key)
                    new_dict.pop(key)
                else:
                    modify_list_tmp.append([old_dict[key],new_dict[key]])
                    old_dict.pop(key)
                    new_dict.pop(key)					
		
        for key in old_dict.keys():
            delete_list_tmp.append(old_dict[key])

        for key in new_dict.keys():
            add_list_tmp.append(new_dict[key])
			
        log.info("add_list_tmp={}".format(str(add_list_tmp)))
        log.info("modify_list_tmp={}".format(str(modify_list_tmp)))
        log.info("delete_list_tmp={}".format(str(delete_list_tmp)))
		
        for element in add_list_tmp:
            max_add_len=max_add_len if (max_add_len >= len(element[0])) else len(element[0])
        for element_list in modify_list_tmp:
            for element in element_list:
                max_modify_len=max_modify_len if (max_modify_len >= len(element[0])) else len(element[0])
        for element in delete_list_tmp:
            max_delete_len=max_delete_len if (max_delete_len >= len(element[0])) else len(element[0])
			
        for element in enumerate(add_list_tmp):
            addList.append("    "+element[1][0]+" "*(max_add_len-len(element[1][0]))+" : "+element[1][1]+"\n")
			
        for element_list in enumerate(modify_list_tmp):
            for element in element_list[1]:
                modifyList.append("    "+element[0]+" "*(max_modify_len-len(element[0]))+" : "+element[1]+"\n")
            modifyList.append("\n")
			
        for element in enumerate(delete_list_tmp):
            deleteList.append("    "+element[1][0]+" "*(max_delete_len-len(element[1][0]))+" : "+element[1][1]+"\n")
			
        log.info(str(addList))
        log.info((modifyList))	
        log.info((deleteList))		
        		
		
        if len(addList) == 1:
            addList[0] = addList[0][:-1]+"{}None\n".format(" "*10)
        if len(modifyList) == 1:
            modifyList[0] = modifyList[0][:-1]+"{}None\n".format(" "*10)
        if len(deleteList) == 1:
            deleteList[0] = deleteList[0][:-1]+"{}None\n".format(" "*10)
			
        finalList=addList+modifyList+deleteList
        finalList.append("\n")
        finalList.insert(0,"To:   {}\n".format(newVersion))
        finalList.insert(0,"From: {}\n".format(oldVersion))
        with open(ota_diff_file,"w") as f2:
            f2.writelines(finalList)
        return True		
		
    def make_ota_from_server(self):
        newList=[]
        finalList=[]
        addList=["\nAdd:\n"]
        modifyList=["\nModify:\n"]
        deleteList=["\nDelete:\n"]
        oldVersion=self.oldVersion
        newVersion=self.newVersion
        log.info("oldVersion on server ={}".format(oldVersion))
        log.info("newVersion on server ={}".format(newVersion))
        ota_diff_file=self.ota_dir+self.diffFile
        log.info("ota_diff_file on server ={}".format(ota_diff_file))
		
        old_json_file=self.full_dir+oldVersion+".json"
        if os.path.exists(old_json_file):
            self.make_ota_from_server_new(newVersion,oldVersion)
            log.info("make_ota_from_server_new Done.Will return.")
            return True

        os.popen("diff -b %s %s > %s"%(self.full_dir+oldVersion+".txt",self.full_dir+newVersion+".txt",ota_diff_file)).read()
        ret=os.path.exists(ota_diff_file)
        log.info("os.path.exists:{} {}".format(ota_diff_file,ret))
        if not ret:
            log.info("Make diff file on server failed Will  return false.")
            return False
        with open(ota_diff_file,"r") as f:
            diffList=f.readlines()
            for item in diffList:
                #p=re.match("\d+|\d+,\d+(\w)\d+|(\d+,\d+)",item)
                pTitle=re.match("\d.*\d",item)
                if pTitle:
                    p=re.search("\d(\w)\d",pTitle.group())
                    if p:
                        if p.group(1)=="a":
                            newList.append("\nAdd:\n")
                        elif p.group(1)=="c":
                            newList.append("\nModify:\n")
                        elif p.group(1)=="d":
                            newList.append("\nDelete:\n")
                else:
                    if item == "> \n" or item == "---\n" or item == " \n":
                        pass
                    elif (item[0] == ">" and len(item) > 10) or (item[0] == "<" and len(item) > 10):
                        newList.append(item[1:])
                    else:
                        pass
        #newList.append()
		
        for i,value in enumerate(newList):
            if value == "\nAdd:\n":
                tmpList=addList
            elif value == "\nModify:\n":
                tmpList=modifyList
            elif value == "\nDelete:\n":
                tmpList=deleteList
            else:
                tmpList.append(value)
         
        if len(addList) == 1:
            addList[0] = addList[0][:-1]+"{}None\n".format(" "*10)
        if len(modifyList) == 1:
            modifyList[0] = modifyList[0][:-1]+"{}None\n".format(" "*10)
        if len(deleteList) == 1:
            deleteList[0] = deleteList[0][:-1]+"{}None\n".format(" "*10)
			
        finalList=addList+modifyList+deleteList
        finalList.append("\n")
        finalList.insert(0,"To:   {}\n".format(newVersion))
        finalList.insert(0,"From: {}\n".format(oldVersion))
        with open(ota_diff_file,"w") as f2:
            f2.writelines(finalList) 
        return True			

    def checkRemoteFile(self,_check_file):
        retList=[]
        check_file=_check_file
        log.info("homeDir={}".format(self.homeDir))
        if self.chipset in self.rkType:
            command = "ls {}/build/property/full/*".format(self.homeDir)
        elif self.chipset in self.amlType:
            command = "ls {}/property/full/*".format(self.homeDir)
        log.info("command={}".format(command))
        retStr=self.ssh_command(command)
        log.info("retStr={}".format(retStr))
        retList=retStr.split("\r\n")
        del(retList[0])
        del(retList[-1])
        for i,item in enumerate(retList):
            retList[i]=item.split("/")[-1]
        if check_file in retList:      
            return True
        else:
            return False

    def checkRemoteFile_ota(self,_check_file):
        retList=[]
        check_file=_check_file
        log.info("homeDir={}".format(self.homeDir))
        if self.chipset in self.rkType:
            command = "ls {}/build/property/ota/*".format(self.homeDir)
        elif self.chipset in self.amlType:
            command = "ls {}/property/ota/*".format(self.homeDir)
        log.info("command={}".format(command))
        retStr=self.ssh_command(command)
        log.info("retStr={}".format(retStr))
        retList=retStr.split("\r\n")
        del(retList[0])
        del(retList[-1])
        for i,item in enumerate(retList):
            retList[i]=item.split("/")[-1]
        if check_file in retList:      
            return True
        else:
            return False
		
    def transportFile(self,_host,_user):
        host=_host
        user=_user
        transport = paramiko.Transport((host, 22))
        transport.connect(username=user, password="123456")
        sftp = paramiko.SFTPClient.from_transport(transport)

        local_filename = self.full_dir+self.imgName+".txt"
        local_json = self.full_dir+self.imgName+".json"
        if self.chipset in self.rkType:
            remote_filename = "{}/build/property/full/{}".format(self.homeDir,self.imgName+".txt")
            remote_json = "{}/build/property/full/{}".format(self.homeDir,self.imgName+".json")
        elif self.chipset in self.amlType:
            remote_filename = "{}/property/full/{}".format(self.homeDir,self.imgName+".txt")
            remote_json = "{}/property/full/{}".format(self.homeDir,self.imgName+".json")
        
        log.info("local_filename:{}".format(local_filename))
        log.info("remote_filename:{}".format(remote_filename))
        log.info("local_json:{}".format(local_json))
        log.info("remote_json:{}".format(remote_json))
		
        local_full_exists=os.path.exists(self.full_dir+self.imgName+".txt")
        local_json_exists=os.path.exists(self.full_dir+self.imgName+".json")		
		
        check_ret=self.checkRemoteFile(self.imgName+".txt")
        if check_ret and not local_full_exists:
            log.info(u'Get File%stransporting...'.format(self.imgName+".txt"))
            sftp.get(remote_filename, local_filename)

        check_ret2=self.checkRemoteFile(self.imgName+".json")
        if check_ret2 and not local_json_exists:
            log.info(u'Get File%stransporting...'.format(self.imgName+".json"))
            sftp.get(remote_json, local_json)
        transport.close()

    def getFileList(self):
        #get file list on server ,if full file on server.
        local_full_exists=os.path.exists(self.full_dir+self.imgName+".txt")
        local_json_exists=os.path.exists(self.full_dir+self.imgName+".json")
        if local_full_exists and local_json_exists:
            log.info("{} exists,will get file list from here.".format(self.full_dir+self.imgName+".txt"))
            self.fileList=self.getLocalFileList()
        else:
            self.transportFile(self.host,self.user)
            local_full_exists_2=os.path.exists(self.full_dir+self.imgName+".txt")
            if local_full_exists_2:
                log.info("{} get form judian success,will get file list from here.".format(self.full_dir+self.imgName+".txt"))
                self.fileList=self.getLocalFileList()
            else:
                log.info("{} get form judian failed,will get file list from judian.".format(self.full_dir+self.imgName+".txt"))
                log.info("{} not exists,will get from {}@{}".format(self.full_dir+self.imgName+".txt",self.user,self.host))		
                self.fileList=self.getRemoteFileList()
        
		
    def getPropertyDiff(self,_info):
        info=_info
        ret=self.getDataFolderCount()
        if ret < 2:
            self.firstSetDataFolder()
        else:
            log.info("data folder exists,do not make folder all.")
        retBool=self.initUserInfo(info)
        if not retBool:
            self.retDict={
                "result":"NOK",
                "reason":"No difference information for now.\nErrorCode:101.",
                "filename":[]
            }
            return False

        self.diffFile=None
        self.makeDataFolder()
        self.getFileList()
		
        if self.imgName+".txt" not in self.fileList:
            self.retDict={
                "result":"NOK",
                "reason":"No difference information for now.\nErrorCode:201.",
                "filename":[]
            }
            return False
        else:
            #get diff file
            self.diffFile=self.getDiff()
        log.info("self.diffFile={}".format(self.diffFile))
		
        #Return to web if diff file exists.
        isExists=self.checkDiffExist()
        if isExists:
            log.info("diff file {} is exists,will return.".format(self.childFolder+self.diffFile))
            self.retDict={
                "result":"OK",
                "reason":"",
                "filename":[self.childFolder+self.diffFile]
            }        
            return True
        #if diff file not on server ,make diff file on server.
        local_full_exists=os.path.exists(self.full_dir+self.imgName+".txt")
        local_json_exists=os.path.exists(self.full_dir+self.imgName+".json")
        if local_full_exists and local_json_exists:
            log.info("Will make diff file on server.")
            get_ota_ret=self.make_ota_from_server()
            if get_ota_ret:
                log.info("Make diff file on server success,Will return.")
                self.retDict={
                    "result":"OK",
                    "reason":"",
                    "filename":[self.childFolder+self.diffFile]
                } 			
                return True
        #if make diff file on server failed,make it on ju dian.		
        if self.chipset in self.rkType:
            command2="cat {}/build/property/ota/{}".format(self.homeDir,self.diffFile)
        elif self.chipset in self.amlType:
            command2="cat {}/property/ota/{}".format(self.homeDir,self.diffFile)
        log.info("command2={}".format(command2))			
        retStr=self.ssh_command(command2)
        if "cat:" in retStr:
            log.info("Will Return")
            self.retDict={
                "result":"NOK",
                "reason":"No difference information for now.\nErrorCode:202.",
                "filename":[]
            }
            return False			
        dataList=retStr.split("\r\n")
        for i,item in enumerate(dataList):
            dataList[i]=item+"\n"
        del(dataList[0])
		
		
        serverDiffFile=self.dataFolder+self.childFolder+self.diffFile
        with open(serverDiffFile,"w") as f:
            f.writelines(dataList)
			
        self.retDict={
            "result":"OK",
            "reason":"",
            "filename":[self.childFolder+self.diffFile]
        }
        return True
		

class ParamikoInfo():
    def __init__(self,_host,_user,_password):
        self.host=_host
        self.user=_user
        self.password=_password

        self.transport = paramiko.Transport((self.host, 22))
        self.transport.connect(username=self.user, password=self.password)
        self.sftp = paramiko.SFTPClient.from_transport(self.transport)

        self.ssh=paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(hostname=self.host, port=22, username=self.user, password=self.password)

    def __del__(self):
        self.ssh.close()
        self.transport.close()


    def perform_command(self,_command):
        command = _command
        stdin,stdout,stderr = self.ssh.exec_command(command)
        out = stdout.read().decode()
        err = stderr.read()
        return (out,err)

    def paramiko_get(self,local_file,remote_file):
        log.info(u'Get File to {} transporting...'.format(remote_file))
        self.sftp.get(remote_file, local_file)

    def paramiko_put(self,local_file,remote_file):
        log.info(u'Put File to {} transporting...'.format(remote_file))
        self.sftp.put(local_file,remote_file)


class GetManifestDiff(GetDiffFile):
    def __init__(self):
        super(GetManifestDiff,self).__init__()
        self.mani_diff_file=""
        self.local_mani_file=""
        self.remote_mani_file=""

    def get_all_diff(self):
        ret=self.getPropertyDiff(sys.argv[1])
        if not ret:
            return self.retDict

        self.mani_diff_file=self.diffFile[:-4]+"_manifest.txt"
        log.warn("self.mani_diff_file={}".format(self.mani_diff_file))
        self.local_mani_file=self.ota_dir+self.mani_diff_file
        log.warn("self.local_mani_file={}".format(self.local_mani_file))
        if self.chipset in self.rkType:
            self.remote_mani_file = "{}/build/property/ota/{}".format(self.homeDir,self.mani_diff_file)
        elif self.chipset in self.amlType:
            self.remote_mani_file = "{}/property/ota/{}".format(self.homeDir,self.mani_diff_file)
        log.warn("self.remote_mani_file={}".format(self.remote_mani_file))

        pi=ParamikoInfo(self.host,self.user,self.password)		
        if os.path.exists(self.local_mani_file):
            log.info(self.local_mani_file+"on server ,will get it here.")
            self.retDict["filename"].append(self.childFolder + self.mani_diff_file)
            return self.retDict			
        else:
            check_ret=self.checkRemoteFile_ota(self.mani_diff_file)
            if not check_ret:
                log.info("Not found {} on {}@{},will return a blank file!!".format(self.mani_diff_file,self.user,self.host))
                with open(self.local_mani_file,"w") as f:
                    f.write("\n-------------------------------Workspace diff-----------------------------------\n    Not found manifest diff file\n")
                self.retDict["filename"].append(self.childFolder + self.mani_diff_file)
                return self.retDict
            else:
                log.info("Found {} on {}@{},will get it!!".format(self.mani_diff_file, self.user, self.host))
                pi.paramiko_get(self.local_mani_file,self.remote_mani_file)
                self.retDict["filename"].append(self.childFolder + self.mani_diff_file)
            return self.retDict
			
# To adapt jsonstring from java api
    
if __name__ == "__main__":
    
    #cui=CheckUserInput(json_str)
    #ret=cui.checkInput()

    gmd=GetManifestDiff()
    ret=gmd.get_all_diff()
    print ret

    #cor=ConversionOldRelease()
    #cor.makeNewRawData()
