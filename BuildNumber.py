import urllib2
import re
import sys
import smtplib
from email.mime.text import MIMEText
import os
import datetime


OSBuildMap = {}

OSBuildMap['CENTOS6']="http://dev.hortonworks.com.s3.amazonaws.com/ambari/centos6/2.x"
OSBuildMap['CENTOS7']="http://dev.hortonworks.com.s3.amazonaws.com/ambari/centos7/2.x"
OSBuildMap['UBUNTU14']="http://dev.hortonworks.com.s3.amazonaws.com/ambari/ubuntu14/2.x"
OSBuildMap['SUSE11']="http://dev.hortonworks.com.s3.amazonaws.com/ambari/suse11/2.x"
OSBuildMap['DEBIAN7']="http://dev.hortonworks.com.s3.amazonaws.com/ambari/debian7/2.x"


buildNumString = sys.argv[1]
diff4Alert = sys.argv[2]
toEmail = sys.argv[3]

finalAlert = False
alert ={}
msgText ={}
msgSubject={}
buildNumArray = buildNumString.split(',')

msgFinalText= ''
msgFinalSubject = ''

releaseOSBuildMap = {}

for buildNum in buildNumArray:
    alert[buildNum] = False
    msgSubject[buildNum] = 'Build Issue With Release '+buildNum+'('
    releaseOSBuildMap[buildNum] = {}
    
    print '\n-----------Release Number : '+buildNum+'--------------\n'
    # Repeat the following steps for all the OS combinations
    for operatingSystem,buildUrl in OSBuildMap.items():
        # Generate the QE and Dev Build Repo Url

        extn = '.repo'

        if(operatingSystem.startswith('UBUNTU') or operatingSystem.startswith('DEBIAN') ):
            extn = '.list'

        qeUrl = buildUrl+'/updates/'+buildNum+'/ambariqe'+extn
        bnUrl = buildUrl+'/latest/'+buildNum+'/ambaribn'+extn
    
        print qeUrl
        print bnUrl

        try:
            req = urllib2.Request(qeUrl)
            res = urllib2.urlopen(req)
            response = res.read()
            qeVersionNum = re.search('VERSION_NUMBER=.*-([0-9]*)',response)
            repoDate = res.info().getheader("Last-Modified")
            qeRepoUTime = datetime.strptime(repoDate,"%a, %d %b %Y %H:%M:%S GMT")
            print qeRepoUTime

            req = urllib2.Request(bnUrl)
            res = urllib2.urlopen(req)
            response = res.read()
            bnVersionNum = re.search('VERSION_NUMBER=.*-([0-9]*)',response)
            repoDate = res.info().getheader("Last-Modified")
            bnRepoUTime = datetime.strptime(repoDate,"%a, %d %b %Y %H:%M:%S GMT")
           
            # Get the build difference between the Dev and QE Repos
            diff = int(bnVersionNum.group(1)) - int(qeVersionNum.group(1))
            timeDiff = bnRepoUTime - qeRepoUTime

            print "Operating System " , operatingSystem
            print "QE Build Number ",qeVersionNum.group(1)
            print "Compiled Build Number ",bnVersionNum.group(1)
            print "Time Diff ",timediff
            
            releaseOSBuildMap[buildNum][operatingSystem] = qeVersionNum.group(1)

            if(diff > int(diff4Alert)) :
                print '==============Alert Generated For Release '+buildNum+'===================='
                if(not alert[buildNum]):
                    msgText[buildNum] = '\n-------------------Release '+buildNum+'------------------\n'
                    
                    
                msgText[buildNum] += '=====================================\n'
                msgText[buildNum] += 'Operating System :'+operatingSystem+'\nQE Build Number :'+qeVersionNum.group(1)+'\nCompiled Build Number :'+bnVersionNum.group(1)
                msgText[buildNum] +='\n=====================================\n'
                
                
                if(alert[buildNum]):
                    msgSubject[buildNum] += ' , '
                    
                msgSubject[buildNum] += operatingSystem
                
                alert[buildNum] = True
                finalAlert = True
        except:
            print "Exception for Operating System " , operatingSystem
            print sys.exc_info()[0]
            
    if(alert[buildNum]):
        msgSubject[buildNum] +=') '
    else:
        msgSubject[buildNum] = 'No Build Issue With Release '+buildNum


for buildNum,subject in msgSubject.items():
        msgFinalSubject += subject

for buildNum,text in msgText.items():
    msgFinalText += text

msgFooterText = ''

for buildNum,osBuildMap in releaseOSBuildMap.items():
    maxBuildNum = 0
    maxBuildOS = ''
    for operatingSystem,qeBuild in osBuildMap.items():
        if(int(qeBuild) > maxBuildNum):
            maxBuildNum = int(qeBuild)
            maxBuildOS = operatingSystem
        elif(int(qeBuild) == maxBuildNum):
            maxBuildOS += ','+operatingSystem
    
    msgFooterText += '\nSuggested Build For Release '+buildNum +' : '+ str(maxBuildNum)  +' on '+maxBuildOS
    
msgFinalText += '\n\n'+msgFooterText
    
if(finalAlert):
        os.system('echo "'+msgFinalText+'" | mail -s "'+msgFinalSubject+'" '+toEmail)
        print 'Mail Sent Successfully to '+toEmail