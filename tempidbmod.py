# -*- coding: utf-8 -*-
from __future__ import print_function

import logging
import os
import os.path
import sys
import string
from datetime import datetime,date,timedelta
import time
import filestoragemod
#import hardwaremod

logger = logging.getLogger("raspbeery."+__name__)

# ///////////////// -- GLOBAL VARIABLES AND INIZIALIZATION --- //////////////////////////////////////////



global DATAFILENAME
DATAFILENAME="tempi.txt"
global DEFDATAFILENAME
DEFDATAFILENAME="default/deftempi.txt"
global filedata
filedata=[]

# read filedata -----
if not filestoragemod.readfiledata(DATAFILENAME,filedata): #read watering setting file
	#read from default file
	filestoragemod.readfiledata(DEFDATAFILENAME,filedata)
	filestoragemod.savefiledata(DATAFILENAME,filedata)

	
def savedata(filedata):
	filestoragemod.savefiledata(DATAFILENAME,filedata)

def readdata(filedata):
	filestoragemod.readfiledata(DATAFILENAME,filedata)



def getTimeCo2():
	recordkey="name"
	recordvalue="timesettings"
	keytosearch="timeCo2"
	dataitem=filestoragemod.searchdata(DATAFILENAME,recordkey,recordvalue,keytosearch)
	return dataitem

def getTimeCo2Sfiato():
	recordkey="name"
	recordvalue="timesettings"
	keytosearch="timeCo2Sfiato"
	dataitem=filestoragemod.searchdata(DATAFILENAME,recordkey,recordvalue,keytosearch)
	return dataitem

def getTimeBirraRiempimento():
	recordkey="name"
	recordvalue="timesettings"
	keytosearch="timeBirraRiempimento"
	dataitem=filestoragemod.searchdata(DATAFILENAME,recordkey,recordvalue,keytosearch)
	return dataitem

def getTimeBirraAttesa():
	recordkey="name"
	recordvalue="timesettings"
	keytosearch="timeBirraAttesa"
	dataitem=filestoragemod.searchdata(DATAFILENAME,recordkey,recordvalue,keytosearch)
	return dataitem

def getTimeSfiato():
	recordkey="name"
	recordvalue="timesettings"
	keytosearch="timeSfiato"
	dataitem=filestoragemod.searchdata(DATAFILENAME,recordkey,recordvalue,keytosearch)
	return dataitem

	
def getTimeVuoto():
	recordkey="name"
	recordvalue="timesettings"
	keytosearch="timeVuoto"
	dataitem=filestoragemod.searchdata(DATAFILENAME,recordkey,recordvalue,keytosearch)
	return dataitem

def getNumCicliPrepara():
	recordkey="name"
	recordvalue="timesettings"
	keytosearch="numCicliPrepara"
	dataitem=filestoragemod.searchdata(DATAFILENAME,recordkey,recordvalue,keytosearch)
	return dataitem

def getNumCicliPulizia():
	recordkey="name"
	recordvalue="timesettings"
	keytosearch="numCicliPulizia"
	dataitem=filestoragemod.searchdata(DATAFILENAME,recordkey,recordvalue,keytosearch)
	return dataitem
	
	
def changesavesetting(FTparameter,FTvalue):
	searchfield="name"
	searchvalue="timesettings"
	isok=filestoragemod.savechange(DATAFILENAME,searchfield,searchvalue,FTparameter,FTvalue)
	if not isok:
		print("problem saving parameters")
	return isok



	
def restoredefault():
	filestoragemod.deletefile(DATAFILENAME)
	filedata=[{"name": "timesettings", "numCicliPrepara": "2", "timeVuoto": "5", "timeCo2": "1", "timeCo2Sfiato": "1", "timeBirraRiempimento": "5", "timeBirraAttesa" : "3", "timeSfiato" : "5", "numCicliPulizia": "2"}]
	filestoragemod.savefiledata(DATAFILENAME,filedata)


	
#--end --------////////////////////////////////////////////////////////////////////////////////////		
	
	
if __name__ == '__main__':
	# comment
	address="hello@mail.com"
	password="haha"
	#changesavesetting("address",address)
	#changesavesetting("password",password)
	#print getaddress()
	#print getpassword()




