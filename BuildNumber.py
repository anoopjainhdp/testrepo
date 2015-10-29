import urllib2
import re
import sys
import smtplib
from email.mime.text import MIMEText
import os


OSBuildMap = {}

OSBuildMap['CENTOS6']="http://dev.hortonworks.com.s3.amazonaws.com/ambari/centos6/2.x"
OSBuildMap['CENTOS7']="http://dev.hortonworks.com.s3.amazonaws.com/ambari/centos7/2.x"
OSBuildMap['UBUNTU14']="http://dev.hortonworks.com.s3.amazonaws.com/ambari/ubuntu14/2.x"
OSBuildMap['SUSE11']="http://dev.hortonworks.com.s3.amazonaws.com/ambari/suse11/2.x"
OSBuildMap['DEBIAN7']="http://dev.hortonworks.com.s3.amazonaws.com/ambari/debian7/2.x"


buildNum = sys.argv[1]
diff4Alert = sys.argv[2]
toEmail = sys.argv[3]
msgText = ''
msgSubject = 'Build issues with '+buildNum + ' for '
alert = False
errMessage = ''

# Repeat the following steps for all the OS combinations
for operatingSystem,build in OSBuildMap.items():
    # Generate the QE and Dev Build Repo Url

    extn = '.repo'

    if(operatingSystem.startswith('UBUNTU') or operatingSystem.startswith('DEBIAN') ):
        extn = '.list'

    qeUrl = build+'/updates/'+buildNum+'/ambariqe'+extn
    bnUrl = build+'/latest/'+buildNum+'/ambaribn'+extn
    
    print qeUrl
    print bnUrl

    try:
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

        print "Operating System " , operatingSystem
        print "QE Build Number ",qeVersionNum.group(1)
        print "Compiled Build Number ",bnVersionNum.group(1)

        if(diff > int(diff4Alert)) :
            print '==============Alert===================='
            msgText += '=====================================\n'
            msgText += 'Operating System :'+operatingSystem+'\nQE Build Number :'+qeVersionNum.group(1)+'\nCompiled Build Number :'+bnVersionNum.group(1)
            msgText +='\n=====================================\n'
            if(alert):
                msgSubject += ' , '
                msgSubject += operatingSystem
                alert = True
    except:
        print "Exception for Operating System " , operatingSystem
        print sys.exc_info()[0]

if(alert):
        os.system('echo "'+msgText+'" | mail -s "'+msgSubject+'" '+toEmail)