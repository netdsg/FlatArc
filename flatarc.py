#!/usr/bin/python3

import pexpect, time, sys, os, csv, pprint, datetime, shelve, re, sched
from multiprocessing import Process, Queue
from simplecrypt import *

### Change the EVar variable at installation time!
### This must also be changed and match in the flatarcManage.py file.
### These files should have permissions that do not allow others to view them.
EVar = 'thisvariablehashesthepasswords'

CommentTerm = re.compile(r'^#')
ClassList = None

def ReadTargets():
    global DeviceList
    try:
        DeviceData = open('/usr/local/flatarc/flatarcDeviceData.csv')
        DeviceReader = csv.reader(DeviceData)
        dDeviceList = list(DeviceReader)
        DeviceData.close()
    except:
        dDeviceList = []
        pass

    try:
        FileData = open('/usr/local/flatarc/flatarcFileData.csv')
        FileReader = csv.reader(FileData)
        FileList = list(FileReader)
        FileData.close()
    except:
        FileList = []
        pass
    DeviceList = dDeviceList + FileList
    return DeviceList


def ReadClassData():
    try:
        GetClassData()
    except:
        #print(sys.exc_info())
        pass

    if ClassList:
        global PlainClassList
        PlainClassList = []
        for i in ClassList:
            Class = i[0]
            UserName = i[1]
            Pass = bytes.decode(decrypt(EVar, i[2]))
            PlainClassList.append([Class, UserName, Pass])

### Password Database
def GetClassData():
    global ClassList
    ClassFile = shelve.open('/usr/local/flatarc/FlatArcData')
    ClassList = ClassFile['ClassList']
    ClassFile.close()

def DisplayText(VAR, VAR2):
    bZ = (VAR + VAR2)
    Z = bytes.decode(bZ)
    A = Z.splitlines()
    #for i in A:
    #    print(i)

def ScpSpawn(data, DeviceData):
    try:
        for i in PlainClassList:
            if DeviceData[6] == i[0]:
                UserName = i[1]
                Password = i[2]
                break
        S = pexpect.spawn('bash')
        S.expect('\$')
        
        S.sendline('scp -o StrictHostKeyChecking=no ' + UserName + '@' + DeviceData[1] + ':' + DeviceData[2] + ' /usr/local/flatarc/backups/' + DeviceData[5] + '/.')
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
        
        ReturnData = (DeviceData[0], Status)
        data.put(ReturnData)
    except:
        ReturnData = (DeviceData[0], 'Failed')
        data.put(ReturnData)
        S.close()
        #print(sys.exc_info())
        pass

def CiscoSpawn(data, DeviceData):
    try:
        for i in PlainClassList:
            if DeviceData[6] == i[0]:
                UserName = i[1]
                Password = i[2]
                break
        prompt = (DeviceData[0] + '#')
        S = pexpect.spawn('ssh -o StrictHostKeyChecking=no ' + UserName + '@' + DeviceData[1]) 
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
        WriteFile(Result, DeviceData)
        ReturnData = (DeviceData[0], 'Success')
        data.put(ReturnData)
    except:
        ReturnData = (DeviceData[0], 'Failed')
        data.put(ReturnData)
        S.close()
        print(sys.exc_info())
        pass

def JunosSpawn(data, DeviceData):
    try:
        for i in PlainClassList:
            if DeviceData[6] == i[0]:
                UserName = i[1]
                Password = i[2]
                break
        prompt = (DeviceData[0] + '>')
        S = pexpect.spawn('ssh -o StrictHostKeyChecking=no ' + UserName + '@' + DeviceData[1])
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
        WriteFile(Result, DeviceData)
        ReturnData = (DeviceData[0], 'Success')
        data.put(ReturnData)
    except:
        ReturnData = (DeviceData[0], 'Failed')
        data.put(ReturnData)
        S.close()
        #print(sys.exc_info())
        pass

### fix this when we need to backup files local to the FlatArc server ###
def bashSpawn(data, DeviceData):
    try:
        S = pexpect.spawn('bash')
        S.expect('\$')

        S.sendline('cat ' + DeviceData[4])
        S.expect('/usr/local/flatarc\$')
        Result = S.before
        DisplayText(S.before, S.after) 
        
        S.sendline('exit')
        S.close()
        S = None
        WriteFile(Result, DeviceData)
        ReturnData = (DeviceData[0], 'Success')
        data.put(ReturnData)
    except:
        ReturnData = (DeviceData[0], 'Failed')
        data.put(ReturnData)
        S.close()
        pass

### add some file path error checking....
def WriteFile(Content, DeviceData):
    ConfTgt = DeviceData[0]
    cList = bytes.decode(Content).splitlines()
    ConfigFile = open(('/usr/local/flatarc/backups/' + DeviceData[5] +'/' + ConfTgt), 'w')
    for i in cList:
        ConfigFile.write(i + '\n')
    ConfigFile.close()

def Runner(Zulu):
    Zulu = Zulu + 1
    DeviceList = ReadTargets()
    ReadClassData()
    log = open('/usr/local/flatarc/flatarc_log.txt', 'a')

    proc = []
    cue = []
    for i in DeviceList:
        FindComment = CommentTerm.match(i[0])
        if FindComment:
            continue
        if i[7] != 'up':
            continue
        if Zulu % int(i[4]) != 0:
            #print(i[0] + ' - interval value - ' + i[4] + 'Zulu value = ' + str(Zulu))
            continue
        q = Queue()
        if i[3] == 'cisco':
            p = Process(target=CiscoSpawn, args=(q, i))
        if i[3] == 'junos':
            p = Process(target=JunosSpawn, args=(q, i))
        if i[3] == 'scp':
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

    DirList = []
    for i in DeviceList:
        DirList.append(i[5])
    DirList = list(set(DirList))
    time.sleep(2)
    S = pexpect.spawn('bash')
    S.expect('\$')

    for i in DirList:
        S.sendline('cd /usr/local/flatarc/backups/' + i)
        S.expect('\$')
        DisplayText(S.before, S.after)

        S.sendline('git config user.name "flatarc"')
        S.expect('\$')

        S.sendline('git config user.email "flatarc@local.net"')
        S.expect('\$')

        S.sendline('git add *')
        S.expect('\$')

        S.sendline('git commit -a -m "courtesy of flatarc!"')
        S.expect('\$')
        DisplayText(S.before, S.after)

    S.sendline('exit')
    #print('#################### Zulu = ' + str(Zulu) + ' ####################################')
    Timing.enter(3600, 1, Runner, (Zulu,))

### Main Program ########################################

Zulu = -1 
Timing = sched.scheduler(time.time, time.sleep)
Timing.enter(5, 1, Runner, (Zulu,))
Timing.run()
