import urllib2
import re
import sys
import smtplib
from email.mime.text import MIMEText


OSBuildMap = {}

OSBuildMap['CENTOS6']="http://dev.hortonworks.com.s3.amazonaws.com/ambari/centos6/2.x"


buildNum = sys.argv[1]
diff4Alert = sys.argv[2]
msgText = ''
msgSubject = ''
alert = False

# Repeat the following steps for all the OS combinations
for os,build in OSBuildMap.items():
    # Generate the QE and Dev Build Repo Url
    qeUrl = build+'/updates/'+buildNum+'/ambariqe.repo' 
    bnUrl = build+'/latest/'+buildNum+'/ambaribn.repo'
    print qeUrl
    print bnUrl
 
    req = urllib2.Request(qeUrl)
    res = urllib2.urlopen(req)
    response = res.read()
    qeVersionNum = re.search('VERSION_NUMBER=.*-([0-9]*)',response)
    
    req = urllib2.Request(bnUrl)
    res = urllib2.urlopen(req)
    response = res.read()
    bnVersionNum = re.search('VERSION_NUMBER=.*-([0-9]*)',response)

    # Get the build difference between the Dev and QE Repos
    diff = int(bnVersionNum.group(1)) - int(qeVersionNum.group(1))    
    
    print "Operating System " , os
    print "QE Build Number ",qeVersionNum.group(1)
    print "Dev Build Number ",bnVersionNum.group(1)

    if(diff > int(diff4Alert)) :
		print '==============Alert===================='
		msgText += '=====================================\n'
		msgText += 'Operating System :'+os+'\nQE Build Number :'+qeVersionNum.group(1)+'\nBN Build Number :'+bnVersionNum.group(1) 
		msgText +='\n=====================================\n'
		msgSubject += os + ' '
		alert = True
	
if(alert):
	sys.exit(1);
	