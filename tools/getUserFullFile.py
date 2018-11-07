import paramiko
import os
import sys
import getUserInfo
import datetime
import logging
import stat

class GetUserFullFile():
    def __init__(self):
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
		
    def paramiko_command(self,_host,_user,_command):
        plog=self.logger.info
        host=_host
        user=_user
        command=_command
        ssh=paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=host, port=22, username=user, password="123456")
        stdin,stdout,stderr = ssh.exec_command(command)
        out = stdout.read().decode()
        err = stderr.read()
        ssh.close()
        #plog("out={}".format(out))
        #plog("err={}".format(err))

        return out
	
    def checkFullDir(self,_host,_user):
        plog=self.logger.info
        fullDir=""
        retTup=()
        buildType=""
        host=_host
        user=_user
        retStr=self.paramiko_command(host,user,"pwd")
        homeDir=retStr[:-1]
        plog("Home Ptah = {}".format(homeDir))
		
        retStr2=self.paramiko_command(host,user,"find build/property -name 'full'")
        if retStr2:
            fullDir=homeDir+"/"+retStr2[:-1]
            plog("fullDir rk={}".format(fullDir))
        else:
            retStr3=self.paramiko_command(host,user,"find property -name 'full'")
            if retStr3:
                fullDir=homeDir+"/"+retStr3[:-1]
                buildType="s905l"
                plog("fullDir aml={}".format(fullDir))
        if not fullDir:
            plog("user:{},host:{} no fullDir.".format(user,host))
        retTup=(fullDir,buildType)
        return retTup

    def get_all_files_in_remote_dir(self, _sftp, _remote_dir):
        plog=self.logger.info
        sftp=_sftp
        remote_dir=_remote_dir
        plog("remote_dir={}".format(remote_dir))
        all_files = list()
        if remote_dir[-1] == '/':
            remote_dir = remote_dir[0:-1]
        files = sftp.listdir_attr(remote_dir)
        plog("Files on {}:{}.".format(remote_dir,files))
        for x in files:
            filename = remote_dir + '/' + x.filename
            if stat.S_ISDIR(x.st_mode):
                all_files.extend(self.get_all_files_in_remote_dir(sftp, filename))
            else:
                all_files.append(filename)
        return all_files			

    def get_local_dir(self,_key,_retTup):
        key=_key
        retTup=_retTup
        if retTup[1]:
            child_dir1=retTup[1]
        else:
            if key[0] == "G-120WT-P" or (key[0] == "S-010W-A" and key[1] != "cubj"):
                child_dir1="rk3228b"
            else:
                child_dir1="rk3228h"
        child_dir2=key[0].lower()
        child_dir3=key[1].lower()
        return "/usr/local/stbrelease/data"+"/"+child_dir1+"/"+child_dir2+"/"+child_dir3+"/"+"full/"
	
			
    def transportFile(self,_host,_user,_key):
        plog=self.logger.info
        host=_host
        user=_user
        key=_key
        retTup=self.checkFullDir(host,user)
        plog("retTup={}".format(retTup))
        remoteFullDir=retTup[0]
        local_dir=self.get_local_dir(key,retTup)
        plog("local_dir={}".format(local_dir))

        transport = paramiko.Transport((host, 22))
        transport.connect(username=user, password="123456")
        sftp = paramiko.SFTPClient.from_transport(transport)

        if remoteFullDir:
            all_files = self.get_all_files_in_remote_dir(sftp, remoteFullDir)
            for x in all_files:
                filename = x.split('/')[-1]
                local_filename = os.path.join(local_dir, filename)
                plog(u'Get File%stransporting...'.format(filename))
                sftp.get(x, local_filename)
            transport.close()
		
    def getFullFile(self):
        plog=self.logger.info
        cwd=os.getcwd()
        tmp=cwd+"/tmp/"
        if not os.path.exists(tmp):
            os.mkdir(tmp)

        for key in self.userInfoDict.keys():
            plog("user={}".format(self.userInfoDict[key][0]))
            self.transportFile(self.userInfoDict[key][1],self.userInfoDict[key][0],key)
            plog("----------------------------------------------")			
		
		
if __name__ == "__main__":
    guff=GetUserFullFile()
    guff.getFullFile()
	
	
