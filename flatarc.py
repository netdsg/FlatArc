#!/usr/bin/python3

import pexpect, time, sys, os, datetime, re, sched, json, getpass, subprocess
from multiprocessing import Process, Queue
from simplecrypt import *

### Change the EVar variable at installation time!
### This must also be changed and match in the flatarcManage.py file.
### These files should have permissions that do not allow others to view them.
EVar = 'thisvariablehashesthepasswords'

ClassList = None

def ReadTargets():
    try:
        #with open('/usr/local/flatarc/flatarcDeviceData.json') as ourfile:
        with open('/usr/local/flatarc/json/backupJobs.json') as ourfile:
            jobHash = json.load(ourfile)
    except:
        jobHash = {}
        pass
    return jobHash

def getAuthClassHash():
    with open('/usr/local/flatarc/json/flatarcClass.json') as ourFile:
        ourHash = json.load(ourFile)
        for c in ourHash:
            if ourHash[c]['method'] == 'password':
                with open(('/usr/local/flatarc/auth_class/auth_class_' + c + '.flatarc'), 'rb') as inbound:
                    cipherPass = inbound.read()
                #print('decrypting ' + c)
                ourHash[c]['pass'] = bytes.decode(decrypt(EVar, cipherPass))
                ourHash[c]['preshare'] = 'null'
            if ourHash[c]['method'] == 'pre-shared':
                with open(('/usr/local/flatarc/auth_class/auth_class_' + c + '_key.flatarc'), 'rb') as inbound:
                    cipherPreShare = inbound.read()
                print('decrypting ' + c)
                ourHash[c]['preshare'] = bytes.decode(decrypt(EVar, cipherPreShare))
                ourHash[c]['pass'] = 'null'
    return ourHash

def DisplayText(VAR, VAR2):
    bZ = (VAR + VAR2)
    Z = bytes.decode(bZ)
    A = Z.splitlines()
#    for i in A:
#        print(i)

def ScpSpawn(data, jobName):

    try:
        UserName = authHash[jobHash[jobName]['class']]['user']
        Password = authHash[jobHash[jobName]['class']]['pass']

        S = pexpect.spawn('bash')
        S.expect('\$')

        if 'pre' in authHash[jobHash[jobName]['class']]['method']:
            subprocess.run(['touch', ('/usr/local/flatarc/' + jobName + '.txt')])
            subprocess.run(['chmod', '600', ('/usr/local/flatarc/' + jobName + '.txt')])
            with open(('/usr/local/flatarc/' + jobName + '.txt'), 'a') as outFile:
                outFile.write(authHash[jobHash[jobName]['class']]['preshare'])
            outFile.close()
            S.sendline('scp -o StrictHostKeyChecking=no -r -i ' + ('/usr/local/flatarc/' + jobName + '.txt') + ' ' + UserName + '@' + jobHash[jobName]['ip'] + ':' + jobHash[jobName]['file'] + ' /usr/local/flatarc/backups/' + jobHash[jobName]['dir'] + '/' + jobHash[jobName]['file'].split('/')[-1] + '.' + jobName)
            S.expect('\$')
            DisplayText(S.before, S.after)

            os.remove('/usr/local/flatarc/' + jobName + '.txt')

        else:
            S.sendline('scp -o StrictHostKeyChecking=no -r ' + UserName + '@' + jobHash[jobName]['ip'] + ':' + jobHash[jobName]['file'] + ' /usr/local/flatarc/backups/' + jobHash[jobName]['dir'] + '/' + jobHash[jobName]['file'].split('/')[-1] + '.' + jobName)
            S.expect('word:')
            DisplayText(S.before, S.after)

            S.sendline(Password)
            S.expect('\$')
            DisplayText(S.before, S.after)

        EvalStatus = bytes.decode(S.before)
        if 'No such file or directory' in EvalStatus:
            Status = 'Failed'
        else:
            Status = 'Success'

        S.close()
        
        ReturnData = (jobName, Status)
        data.put(ReturnData)
    except:
        ourError = sys.exc_info()
        ReturnData = (jobName, ('Failed' + str(ourError)))
        data.put(ReturnData)
        S.close()
        pass

def CiscoSpawn(data, jobName):
    try:
        UserName = authHash[jobHash[jobName]['class']]['user']
        Password = authHash[jobHash[jobName]['class']]['pass']
        prompt = '#'

        if 'pre' in authHash[jobHash[jobName]['class']]['method']:
            subprocess.run(['touch', ('/usr/local/flatarc/' + jobName + '.txt')])
            subprocess.run(['chmod', '600', ('usr/local/flatarc/' + jobName + '.txt')])
            with open(('/usr/local/flatarc/' + jobName + '.txt'), 'a') as outFile:
                outFile.write(authHash[jobHash[jobName]['class']]['preshare'])
            outFile.close()
            S = pexpect.spawn('ssh -o StrictHostKeyChecking=no -i ' + ('/usr/local/flatarc/' + jobName + '.txt') + ' ' + UserName + '@' + jobHash[jobName]['ip'])
            S.expect(prompt)
            DisplayText(S.before, S.after)

            os.remove('/usr/local/flatarc/' + jobName + '.txt')

        else:
            S = pexpect.spawn('ssh -o StrictHostKeyChecking=no ' + UserName + '@' + jobHash[i]['ip']) 
            S.expect('word:')
            DisplayText(S.before, S.after)

            S.sendline(Password)
            S.expect(prompt)
            DisplayText(S.before, S.after)

        S.sendline('term len 0')
        S.expect(prompt)
        DisplayText(S.before, S.after)

        S.sendline('show run')
        S.expect(prompt)
        Result = S.before
        DisplayText(S.before, S.after)

        S.sendline('exit')
        S.close()
        WriteFile(Result, jobName)
        ReturnData = (jobName, 'Success')
        data.put(ReturnData)
    except:
        ourError = sys.exc_info()
        ReturnData = (jobName, ('Failed' + str(ourError)))
        data.put(ReturnData)
        S.close()
        pass

def JunosSpawn(data, jobName):
    try:
        UserName = authHash[jobHash[jobName]['class']]['user']
        Password = authHash[jobHash[jobName]['class']]['pass']

        prompt = (UserName + '>')

        if 'pre' in authHash[jobHash[jobName]['class']]['method']:
            subprocess.run(['touch', ('/usr/local/flatarc/' + jobName + '.txt')])
            subprocess.run(['chmod', '600', ('/usr/local/flatarc/' + jobName + '.txt')])
            with open(('/usr/local/flatarc/' + jobName + '.txt'), 'a') as outFile:
                outFile.write(authHash[jobHash[jobName]['class']]['preshare'])
            outFile.close()
            S = pexpect.spawn('ssh -o StrictHostKeyChecking=no -i ' + ('/usr/local/flatarc/' + jobName + '.txt') + ' ' + UserName + '@' + jobHash[jobName]['ip'])
            S.expect(prompt)
            DisplayText(S.before, S.after)

            os.remove('/usr/local/flatarc/' + jobName + '.txt')

        else:
            S = pexpect.spawn('ssh -o StrictHostKeyChecking=no ' + UserName + '@' + jobHash[jobName]['ip'])
            S.expect('word:')
            DisplayText(S.before, S.after)

            S.sendline(Password)
            S.expect(prompt)
            DisplayText(S.before, S.after)

        S.sendline('show configuration | display set | no-more')
        S.expect(prompt)
        Result = S.before
        DisplayText(S.before, S.after)

        S.sendline('exit')
        S.close()
        WriteFile(Result, jobName)
        ReturnData = (jobName, 'Success')
        data.put(ReturnData)
    except:
        ourError = sys.exc_info()
        ReturnData = (jobName, ('Failed' + str(ourError)))
        data.put(ReturnData)
        S.close()
        pass

def vyosSpawn(data, jobName):
    try:
        UserName = authHash[jobHash[jobName]['class']]['user']
        Password = authHash[jobHash[jobName]['class']]['pass']

        prompt = (':~\$')

        if 'pre' in authHash[jobHash[jobName]['class']]['method']:
            subprocess.run(['touch', ('/usr/local/flatarc/' + jobName + '.txt')])
            subprocess.run(['chmod', '600', ('/usr/local/flatarc/' + jobName + '.txt')])
            with open(('/usr/local/flatarc/' + jobName + '.txt'), 'a') as outFile:
                outFile.write(authHash[jobHash[jobName]['class']]['preshare'])
            outFile.close()
            S = pexpect.spawn('ssh -o StrictHostKeyChecking=no -i ' + ('/usr/local/flatarc/' + jobName + '.txt') + ' ' + UserName + '@' + jobHash[jobName]['ip'])
            S.expect(prompt)
            DisplayText(S.before, S.after)

            os.remove('/usr/local/flatarc/' + jobName + '.txt')

        else:
            S = pexpect.spawn('ssh -o StrictHostKeyChecking=no ' + UserName + '@' + jobHash[jobName]['ip'])
            S.expect('word:')
            DisplayText(S.before, S.after)

            S.sendline(Password)
            S.expect(prompt)
            DisplayText(S.before, S.after)

        S.sendline('show configuration commands | no-more')
        S.expect(prompt)
        Result = S.before
        DisplayText(S.before, S.after)

        S.sendline('exit')
        S.close()
        WriteFile(Result, jobName)
        ReturnData = (jobName, 'Success')
        data.put(ReturnData)
    except:
        ourError = sys.exc_info()
        ReturnData = (jobName, ('Failed' + str(ourError)))
        data.put(ReturnData)
        S.close()
        pass

def WriteFile(Content, jobName):
    cList = bytes.decode(Content).splitlines()
    ConfigFile = open(('/usr/local/flatarc/backups/' + jobHash[jobName]['dir'] +'/' + jobName), 'w')
    for i in cList:
        ConfigFile.write(i + '\n')
    ConfigFile.close()

###################################
### Main Program 
###################################

CurUser = getpass.getuser()
if CurUser != 'flatarc':
    print()
    print('This program must only be utilized with the flatarc account.  If another user uses this account the directories and files it creates will not have the proper permissions for the flatarc daemon to utilize them.')
    print()
    print('Exiting...')
    sys.exit()

lastRunHour = 'null'
lastSeenHour = 'null'
currentHour = datetime.datetime.now().hour - 1
if currentHour == -1:
    currentHour = 23
while True:
    if lastSeenHour == datetime.datetime.now().hour:
        time.sleep(600)
    else:
        currentHour += 1
        jobHash = ReadTargets()
        log = open('/usr/local/flatarc/flatarc.log', 'a')
        try:
            authHash = getAuthClassHash()
        except:
            log.write(datetime.datetime.isoformat(datetime.datetime.now()) + ' No authentication credentials found; will try again in an hour\n')
            log.close()
            pass
        dirSet = set()
        proc = []
        cue = []
        for i in jobHash:
            if jobHash[i]['status'] != 'up':
                continue
            if currentHour % int(jobHash[i]['interval']) != 0 and lastSeenHour != 'null':
                continue
            dirSet.add(jobHash[i]['dir'])
            q = Queue()
            if jobHash[i]['protocol'] == 'ssh':
                if jobHash[i]['syntax']  == 'cisco':
                    p = Process(target=CiscoSpawn, args=(q, i))
                elif jobHash[i]['syntax'] == 'junos':
                    p = Process(target=JunosSpawn, args=(q, i))
                elif jobHash[i]['syntax'] == 'vyos':
                    p = Process(target=vyosSpawn, args=(q, i))
            if jobHash[i]['protocol'] == 'scp':
                p = Process(target=ScpSpawn, args=(q, i))
            p.start()
            proc.append(p)
            cue.append(q)
        for q in cue:
            data = q.get()
            #print(data)
            log.write(datetime.datetime.isoformat(datetime.datetime.now()) + ' ' + data[0] + ' - ' + data[1]  + '\n')
        for p in proc:
            p.join()
        log.close()

        time.sleep(2)
        S = pexpect.spawn('bash')
        S.expect('\$')

        for i in dirSet:
            S.sendline('cd /usr/local/flatarc/backups/' + i)
            S.expect('\$')
            DisplayText(S.before, S.after)

            S.sendline('git config user.name "flatarc"')
            S.expect('\$')

            S.sendline('git config user.email "flatarc@local.local"')
            S.expect('\$')

            S.sendline('git add *')
            S.expect('\$')

            S.sendline('git commit -a -m "courtesy of flatarc!"')
            S.expect('\$')
            DisplayText(S.before, S.after)

        S.sendline('exit')
        S.close()

        lastSeenHour = datetime.datetime.now().hour
