import os
import sys


newReleaseRecordList=[]
selectSwVersionResultList=[]
with open("newReleaseRecord.txt","r") as f:
    newReleaseRecordList=f.readlines()

with open("selectSwVersionResult.txt","r") as f2:
    selectSwVersionResultList=f2.readlines()

for value in newReleaseRecordList:
    if value.split(",")[0]+"\n" not in selectSwVersionResultList:
        print value
