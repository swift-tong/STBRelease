#!/usr/bin/env python
import sys
import logging
import datetime
import os
import intmapext


userInfoDict={
             ('S-010W-AV2S', 'cusx'): ('s010wav2s_cusx', '172.24.170.199'), 
             ('S-010W-AV2S', 'cuhi'): ('s010wav2s_cuhi', '172.24.170.156'), 
             ('S-010W-AV2S', 'cutj'): ('cutj_binwei', '172.24.170.199'), 
             ('S-010W-AV2S', 'cuha'): ('s010wav2s_cuha', '172.24.170.198'), 
             ('S-010W-AV2S', 'cuah'): ('s010wav2s_cuah', '172.24.170.156'), 
             ('S-010W-AV2S', 'cujl',"R2"): ('s010wav2s_jllt', '172.24.170.192'), 
             ('S-010W-AV2S', 'cujl'): ('s010wav2s_jllt', '172.24.170.192'), 
             ('NSB_RG020ETCA', 'ctgd'): ('kailiw_ctgd', '172.24.170.195'), 
             ('S-010W-AV2S', 'cufj'): ('cufj_yafei', '172.24.170.193'), 
             ('S-010W-AV2D', 'ctjc'): ('ctsh_lan', '172.24.170.191'), 
             ('S-010W-AV2A', 'ctjc'): ('liangchao_ctjc', '172.24.170.221'), 
             ('RG020ET-CA', 'cthq'): ('ctjc_s905lv3', '172.24.170.221'), 
             ('RG020ET-CA', 'ctossm'): ('singmeng_lan', '172.24.170.221'), 
             ('S-010W-AV2A', 'ctjc','R3'): ('gaoan_ctjc', '172.24.170.190'), 
             ('S-010W-AV2A-1', 'cmjc','R2'): ('jiaminr', '172.24.170.195'), 
             ('S-010W-AV2A-1', 'cmsh','R2'): ('jiaminr', '172.24.170.195'), 
             ('S-010W-AV2A-2', 'cmjc'): ('jiaminr', '172.24.170.195'), 
             ('S-010W-AV2A-2', 'cmsh'): ('jiaminr', '172.24.170.195'), 
             ('S-010W-A', 'ctln'): ('kailiw_ctln', '172.24.170.198'),
             ('G-120WT-P', 'cmhn'): ('kailiw_cmhn', '172.24.170.192'),
             ('G-120WT-P', 'ctjl'): ('g120wtp_ctjl', '172.24.170.156'),
             ('G-120WT-P', 'zsqd'): ('g-120wt-p_zsqd', '172.24.170.199'),
             ('G-120WT-P', 'ctgs'): ('ctgs_g120wtp', '172.24.170.199'),
             ('G-120WT-P', 'cusd'): ('g120wtp_cusd', '172.24.170.197'),
             ('RG020ET-CA', 'ctjl'): ('weiqing_ctjl', '172.24.170.191'),
             ('G-120WT-P', 'cmsc'): ('weiqingcmsc', '172.24.170.198'),
             ('G-120WT-P', 'ctlz'): ('ctlz_g120wtp', '172.24.170.156'),
             ('S-010W-AV2A', 'cujc'): ('cuhq_lan', '172.24.170.191'),
             ('G-120WT-P', 'cuhe'): ('kelly', '172.24.170.197'),
             ('G-120WT-P', 'ossm'): ('g120wtp_singmeng', '172.24.170.156'),
             ('G-120WT-P', 'cmha'): ('cmhagpon_liangchao', '172.24.170.193'),
             ('RG020ET-CA', 'ctln'): ('kailiw_ctln', '172.24.170.195'),
             ('G-120WT-Q', 'cusx'): ('g120wtq_cusx', '172.24.170.199'),
             ('G-120WT-P', 'cunm'): ('weiqing_cunm', '172.24.170.198'),
             ('G-120WT-P', 'ctsx'): ('ctsx_g120wt_pchao', '172.24.170.199'),
             ('S-010W-AV2S', 'cuhe'): ('jiaminr', '172.24.170.197'), 
             ('RG020ET-CA', 'cmha'): ('cmha_lan', '172.24.170.191'),
             ('RG020ET-CA', 'ossm'): ('singmeng_lan', '172.24.170.221'),
             ('G-120WT-P', 'cuah'): ('gpon_cuah', '172.24.170.192'),
             ('S-010W-A', 'ctnx'): ('mengxl', '172.24.170.197'),
             ('RG020ET-CA', 'ctjs'): ('ctjs_lan', '172.24.170.190'),
             ('S-010W-A', 'cusd'): ('xliu059', '172.24.170.197'),
             ('S-010W-A', 'cusd','R2'): ('congjinz', '172.24.170.198'),
             ('G-120WT-P', 'ctah'): ('kailiw_ctah', '172.24.170.192'),
             ('G-120WT-P', 'ctln'): ('youxianw_ctln', '172.24.170.198'),
             ('RG020ET-CA', 'cusd'): ('cusd_lan', '172.24.170.190'),
             ('RG020ET-CA', 'cujs'): ('cujs_lan', '172.24.170.221'),
             ('RG020ET-CA', 'cuqd'): ('cuqd_lan1', '172.24.170.221'),
             ('RG020ET-CA', 'cthn'): ('cthn_lan', '172.24.170.190'),
             ('RG020ET-CA', 'cthb'): ('cthb_lan', '172.24.170.190'),
             ('S-010W-A', 'cthn'): ('weiqing_cthn', '172.24.170.193'),
             ('G-120WT-P', 'cthn'): ('cthn_yafei', '172.24.170.199'),
             ('G-120WT-P', 'ctxj'): ('ctxj_yafei', '172.24.170.199'),
             ('RG020ET-CA', 'cusx'): ('cusx_lan', '172.24.170.191'),
             ('RG020ET-CA', 'ctah'): ('binwei_ctah', '172.24.170.191'),
             ('G-120WT-P', 'ctjs'): ('yafei_ctjs', '172.24.170.199'),
             ('S-010W-AV2B', 'cusd'): ('cusd_3228h', '172.24.170.193'),
             ('S-010W-AV2B', 'ossm'): ('singmeng_binwei', '172.24.170.199'),
             ('G-120WT-P', 'cusx'): ('cusx_2in1', '172.24.170.197'),
             ('S-010W-A', 'cusc'): ('standalone_cusc', '172.24.170.192'),
             ('S-010W-AV2C', 'cusc'): ('s010wav2b_cusc', '172.24.170.199'),
             ('S-010W-AV2C', 'cusd'): ('s010wav2c_cusd', '172.24.170.156'),
             ('S-010W-AV2S', 'cuhl'): ('congjinz', '172.24.170.197'),
             ('G-120WT-P', 'ctnx'): ('weiqingnx', '172.24.170.198'),
             ('RG020ET-CA', 'cuah'): ('liangchao_cuah', '172.24.170.191'),
             ('S-010W-AV2B', 'cujx'): ('cujx_liangchao', '172.24.170.199'),
             ('G-120WT-P', 'culn'): ('weiqingculn', '172.24.170.198'),
             ('S-010W-A', 'cuhn','R2'): ('wukaili', '172.24.170.198'),
             ('S-010W-AV2B', 'cuhn'): ('s010wav2_cuhn', '172.24.170.199'),
             ('S-010W-AV2', 'cuhn'): ('s010wav2_cuhn', '172.24.170.199'),
             ('RG020ET-CA', 'ctsx'): ('youxianw_ctsx', '172.24.170.191'),
             ('S-010W-A', 'cubj'): ('weiqing_cubj', '172.24.170.193'),
             ('S-010W-A', 'cubj',"R2"): ('s010wav2b_cubj', '172.24.170.156'),
             ('S-010W-AV2B', 'cubj'): ('weiqing_cubj', '172.24.170.193'),
             ('S-010W-AV2S', 'cunm','R2'): ('cunm_yafei', '172.24.170.199'),
             ('S-010W-AV2S', 'cunm'): ('cunm_liangchao', '172.24.170.192'),
             ('S-010W-AQD', 'cuqd'): ('cuqd_yafei', '172.24.170.193'),
             ('G-120WT-P', 'cuhl'): ('weiqinghl', '172.24.170.197'),
             ('G-120WT-P', 'ctzj'): ('youxianw_ctzj', '172.24.170.192'), 
             ('RG020ET-CA', 'cthe'): ('cthe_liangchao', '172.24.170.191'), 
             ('RG020ET-CA', 'cuhl'): ('kailiw_cuhl', '172.24.170.195'), 
             ('RG020ET-CA', 'ctgs'): ('ctgs_lan', '172.24.170.190'), 
             ('S-010W-A', 'cugd'): ('youxian_cugd', '172.24.170.198'), 
             ('S-010W-AV2B', 'cujs'): ('weiqingjs', '172.24.170.198'),
             ('RG020ET-CA', 'cmhn'): ('binwei_cmhn', '172.24.170.191'), 
             ('G-120WT-P', 'cmfj'): ('liangchao_cmfj', '172.24.170.192'),
             ('RG020ET-CA','ctgx'):('ctgx_lan','172.24.170.190'),
             ('G-120WT-P', 'ctgx'): ('ctgx_yafei', '172.24.170.199'),
             ('S-010W-A', 'cuxj'): ('dezhongl', '172.24.170.197'),
             ('G-120WT-P', 'ctnm'): ('weiqing_ctnm', '172.24.170.193'), 
             ('RG020ET-CA', 'ctgd'): ('ctgd_lan', '172.24.170.191'),
             ('S-010W-A', 'culn'): ('kailiw', '172.24.170.197')
          }

class GetUserInfo():
    def  __init__(self):
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

        self.userList=[]

    def getUserInfo(self):
        userInfoDict={}
        with open("./conf/IPSTB_Build_Owner.txt","r") as f:
            self.userList=f.readlines()
        for i,item in enumerate(self.userList):
            self.userList[i]=item.lower()

        for key in intmapext.IntToExtDict.keys():
            ukey=(key[0],key[4])
            if ukey not in userInfoDict.keys():
                for item in self.userList:
                    itemList=item.split(r"\t")[0].split("\t")
                    if key[0].lower() in itemList and key[4].lower() in itemList:
                        userInfoDict[ukey]=(itemList[1],itemList[2])
        self.logger.info(userInfoDict)



if __name__ == "__main__":
    gui=GetUserInfo()
    #gui.getUserInfo()
       


