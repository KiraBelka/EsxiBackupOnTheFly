####### VMWARE EXSi 4.x(5.x not tested) simple backup script #### 
from commands import *
import datetime
import string
import re
import os
import subprocess
import fnmatch
########### VARS ################################################
########### vms directory #######################################
vmdir='/vmfs/volumes/DataStore1/' 
################### exclude hosts directive #####################
###### example exclude_hosts=['name1','name2','name3']###########
exclude_hosts=['Backup', 'DHCP-Master', 'DNS-Resolver']
#################################################################
######## exclude files in backup ################################
##exclude_file
########### target folder if local copying enabled ##############
###### uncomment next 2strings for permit  ######################
#lfolder=
################### destination server ##########################
###################  nfs options  ###############################
#nfs_mount_point='/vmfs/volumes/nfsstore/'
#################################################################
#### execution errors check function ############################
def exec_with_err_check(command):
### """absolutely stupid and useless checker""" #################
	com_err_check=os.system(command)
	if com_err_check!=0:
		sys.exit()
		exit() 
################### scp/ssh options within autorized_keys #######
dest_host='xx.xx.xx.xx'        
#dest_login='root' uncomment and use your login #################                                                                                      
dest_folder='/vmfs/volumes/Datastore/'
ssh_key='/.ssh/id_rsa'
###########--- vm count :)--#####################################                      
vmlist = getoutput('vim-cmd vmsvc/getallvms')
com_err_check=0
vmid=[] 
folderid=[]
temp=[]     
vminfo=[]
tempff=[]
folderfiles=[]
k=vmlist.splitlines()
del k[0]
#### exclude vms action #########################################
for m in range(len(exclude_hosts)):
	   for g in range(len(k)):
			 if ' '+exclude_hosts[m]+' ' in k[g]:
								 del k[g]
								 break
#### selected host action #######################################

####backup action :) ---#########################################
for i in range(len(k)):                                  
       temp=k[i].split(' ')                              
       vmid=temp[0] 
       tempff[:]=[]
       folderfiles[:]=[]
       vminfo=getoutput('vim-cmd vmsvc/get.config '+vmid)
       vminform=vminfo.splitlines()
       startp=vminform[6].find(' "')
       lastp=vminform[6].find(',')
       folderid=vminform[6][startp+2:lastp-1]
       commanda1='vim-cmd vmsvc/snapshot.removeall '+vmid        
       commanda2='vim-cmd vmsvc/snapshot.get '+vmid              
       commanda3='vim-cmd vmsvc/snapshot.create '+vmid+' current'
       ## remove previous snapshots #############################  
       exec_with_err_check(commanda1)
	   ## making new snapshot ###################################
       exec_with_err_check(commanda3)
       #################################################################
       #### exclude files action #########################################
	     for file in os.listdir(vmdir+folderid):
		    	if fnmatch.fnmatch(file, '*delta*'):
		      		print 'found delta '+file
	    		else:
		      		folderfiles.append(file)
	    for b in range(len(folderfiles)):
		    	if 'vswp' in folderfiles[b]:
				      print 'pass vswp file'
		    	else:
		      		if 'napshot' in folderfiles[b]:
		  		    		print 'pass snapshot file'
			      	else:
			        		tempff.append(folderfiles[b])
	   ####backup action :) ---#########################################
	   ## local folder backup # uncomment next for permit #######
	   #os.system('cd lfolder')
	   #os.system('mkdir -r '+folderid)
       #os.system('cp '+vmdir+folderid+'/*.* '+ lfolder+folderid)
       ## network backup over ssh section #######################
       #os.system('dbclient -i ' + ssh_key + ' ' + dest_host + ' hostname')	
       exec_with_err_check('dbclient -i '+ ssh_key  + ' ' +  dest_host + ' mkdir -p ' +dest_folder+ '/'+folderid)
	   for j in range(len(tempff)):
			exec_with_err_check('scp -i '+ ssh_key + " '"+vmdir+folderid+"'"+'/'+tempff[j] + ' ' + dest_host+':'+dest_folder+"'"+folderid+"'")
       ## network backup over nfs section #######################
       ##os.system(nfs_mount_point)                                        
       ##os.system('mkdir -p '+"'"+nfs_mount_point+folderid+"'")           
       ##os.system('cp '+"'"+vmdir+folderid+"'"+'/*.* '+"'"+nfs_mount_point+folderid+"'")
       ## info about current snapshot############################
       exec_with_err_check(commanda2)
       ### remove new snapshot after transition #################
       exec_with_err_check(commanda1)
######### vm and storage capacity information ###################
os.system('du -h '+vmdir)
#os.system('du -h '+nfs_mount_point)
print 'Well done :)'
