#!/usr/bin/python3

#import os, sys, pprint, getpass, json
import pexpect, time, sys, os, datetime, re, json, getpass
from simplecrypt import *

############################################
####  Password Managment 
############################################

### Change the EVar variable at installation time!
### This must also be changed and match in the flatarc.py file.
### These files should have permissions that do not allow others to view them.

EVar = 'thisvariablehashesthepasswords'

def cypherHash(authClassHash, option):
    for c in authClassHash:
        if option == 'encrypt':
            authClassHash[c]['pass'] = encrypt(EVar, authClassHash[c]['pass'])
        else:
            authClassHash[c]['pass'] = bytes.decode(decrypt(EVar, authClassHash[c]['pass']))

def writeAuthClassHash():
    for c in authClassHash:
        print('encrypting!')
        cipherPass = encrypt(EVar, authClassHash[c]['pass'])
        with open('/usr/local/flatarc/auth_class/auth_class_' + c + '.flatarc', 'wb') as output:
            output.write(cipherPass)
        ourHash = {}
        for i in authClassHash:
            ourHash[i] = {}
            ourHash[i]['user'] = authClassHash[i]['user']
    with open('/usr/local/flatarc/json/flatarcClass.json', 'w') as ourfile:
        json.dump(ourHash, ourfile)

def getAuthClassHash():
    with open('/usr/local/flatarc/json/flatarcClass.json') as ourFile:
        ourHash = json.load(ourFile)
        for c in ourHash:
            with open(('/usr/local/flatarc/auth_class/auth_class_' + c + '.flatarc'), 'rb') as inbound:
                cipherPass = inbound.read()
            print('decrypting!')
            ourHash[c]['pass'] = bytes.decode(decrypt(EVar, cipherPass))
    return ourHash

def DisplayData():
    if authClassHash != {}:
        for i in authClassHash:
            print()
            print('Account: ' + i)
            print('Username: ' + authClassHash[i]['user'])
            print('Password: ' + authClassHash[i]['pass'])
        print()
        input('press enter to continue.')
    else:
        print('No Authentication Class data was found.')
        print()
        input('Press enter to continue...')

def PassManage():
    print()
    print('1 - Display all Authenticaiton Classes')
    print('2 - Display a specific Authentication Class')
    print('3 - Add an Authentication class')
    print('4 - Remove an Authentication class')
    print('5 - Edit an Authentication class')
    print()
    Option = input('Please enter the option number: ')
    print()

    if Option == '1':
        DisplayData()
    if Option == '2':
        DisplayAccount()
    if Option == '3':
        AddAccount()
    if Option == '4':
        RmAccount()
    if Option == '5':
        EditAccount()


def DisplayAccount():
    print()
    Account = input('Enter Authentication Class name: ')
    if Account in authClassHash:
        print('Authentication Class: ' + Account)
        print('Username: ' + authClassHash[Account]['user'])
        print('Password: ' + authClassHash[Account]['pass'])
        print()
        input('Press enter to continue.')
    else:
        print('Class not found.')
        input('Press enter to continue.')

def AddAccount():
    Account = input('Enter Authentication Class name: ')
    if Account not in authClassHash:
        User = input('Enter username: ')
        PlainPassword = input('Enter Password: ')
        authClassHash[Account] = {}
        authClassHash[Account]['user'] = User
        authClassHash[Account]['pass'] = PlainPassword
        writeAuthClassHash()
        print()
        print(Account + ' Has been added.')
        input('Press enter to continue.')
    else:
        print('This class already exists.')
        input('press enter to continue.')

def RmAccount():
    Account = input('Enter Authentication Class name: ')
    if Account in authClassHash:
        print('Would you like to remove this Authentication Class?: ')
        print('Account: ' + Account)
        print('User: ' + authClassHash[Account]['user'])
        print()
        Delta = input('yes/no: ')
        if Delta == 'yes':
            del authClassHash[Account]
            os.remove('/usr/local/flatarc/auth_class/auth_class_' + Account + '.flatarc')
            writeAuthClassHash()
            print('This Authentication Class has been removed.')
            input('press enter to continue.')
        else:
            print('No action was taken')
            input('press enter to continue.')
    else:
        print(Account + ' was not found.')
        input('press enter to continue.')

def EditAccount():
    print()
    Account = input('Enter Authentication Class name: ' )
    if Account in authClassHash:
        print()
        print('AuthenticationClass: ' + Account)
        print('Username: ' + authClassHash[Account]['user'])
        print('Password: ' + authClassHash[Account]['pass'])
        print()
        print('1 - Change authentication class name')
        print('2 - Change username')
        print('3 - Change password')
        print()
        Option = input('Enter option: ')
        if Option == '1':
            NewAccount = input('Enter new class name: ')
            authClassHash[NewAccount] = authClassHash[Account]
            del authClassHash[Account]
            os.remove('/usr/local/flatarc/auth_class/auth_class_' + Account + '.flatarc')
            Account = NewAccount
        if Option == '2':
            NewUser = input('Enter new username: ')
            authClassHash[Account]['user'] = NewUser
        if Option == '3':
            NewPass = input('Enter new password: ')
            authClassHash[Account]['pass'] = NewPass
        writeAuthClassHash()
        print()
        print('New class Data:')
        print('Class: ' + Account)
        print('Username: ' + authClassHash[Account]['user'])
        print('Password: ' + authClassHash[Account]['pass'])
        input('Press enter to continue.')
    else:
        print('Account not found.')

#################################################
### Run Job Functions
#################################################

def runBackupJob():
    jobName = input('Enter backup job name: ')
    for j in masterJobHash:
        if jobName not in masterJobHash:
            print('Job not found.')
            print()
            #input('Press enter to continue')
            break
        else:
            if masterJobHash[jobName]['protocol'] == 'scp':
                ScpSpawn(jobName)
                break
            elif masterJobHash[jobName]['protocol'] == 'ssh':
                if masterJobHash[jobName]['syntax'] == 'cisco':
                    CiscoSpawn(jobName)
                    break
                elif masterJobHash[jobName]['syntax'] == 'vyos':
                    vyosSpawn(jobName)
                    break
                elif masterJobHash[jobName]['syntax'] == 'junos':
                    JunosSpawn(jobName)
                    break
    input('\nPress Enter to continue...')
        
def DisplayText(VAR, VAR2):
    bZ = (VAR + VAR2)
    Z = bytes.decode(bZ)
    A = Z.splitlines()
    for i in A:
        if 'Could not create directory' not in i and 'Failed to add the host to the list of known hosts' not in i:
            print(i)

def ScpSpawn(jobName):
    try:
        UserName = authClassHash[masterJobHash[jobName]['class']]['user']
        Password = authClassHash[masterJobHash[jobName]['class']]['pass']

        S = pexpect.spawn('bash')
        S.expect('\$')

        S.sendline('scp -o StrictHostKeyChecking=no -r ' + UserName + '@' + masterJobHash[jobName]['ip'] + ':' + masterJobHash[jobName]['file'] + ' /usr/local/flatarc/backups/' + masterJobHash[jobName]['dir'] + '/' + masterJobHash[jobName]['file'].split('/')[-1] + '.' + jobName)
        S.expect('word:')
        DisplayText(S.before, S.after)

        S.sendline(Password)
        S.expect('\$')
        DisplayText(S.before, S.after)

        EvalStatus = bytes.decode(S.before)
        if 'No such file or directory' in EvalStatus:
            print('Job failed - File could not be found.')
        else:
            Status = 'Success'
            print()
            print('Job was successful - find file at /usr/local/flatarc/backups/' + masterJobHash[jobName]['dir'] + '/' + masterJobHash[jobName]['file'].split('/')[-1] + '.' + jobName)

        S.close()
        
        
    except:
        ourError = sys.exc_info()
        print(str(ourError))
        print()
        print('Job Failed - check error message above')
        S.close()
        pass

def CiscoSpawn(jobName):
    try:
        UserName = authClassHash[masterJobHash[jobName]['class']]['user']
        Password = authClassHash[masterJobHash[jobName]['class']]['pass']
        prompt = '#'
        S = pexpect.spawn('ssh -o StrictHostKeyChecking=no ' + UserName + '@' + masterJobHash[jobName]['ip']) 
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
        print()
        print('Job was successful! - find the file at /usr/local/flatar/backups/' +  masterJobHash[jobName]['dir'] +'/' + jobName)
    except:
        ourError = sys.exc_info()
        print(str(ourError))
        print()
        print('Job Failed - check error message above')
        S.close()
        pass

def JunosSpawn(jobName):
    try:
        UserName = authClassHash[masterJobHash[jobName]['class']]['user']
        Password = authClassHash[masterJobHash[jobName]['class']]['pass']

        prompt = (UserName + '>')
        S = pexpect.spawn('ssh -o StrictHostKeyChecking=no ' + UserName + '@' + masterJobHash[jobName]['ip'])
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
        print()
        print('Job was successful! - find the file at /usr/local/flatar/backups/' +  masterJobHash[jobName]['dir'] +'/' + jobName)
    except:
        ourError = sys.exc_info()
        print(str(ourError))
        print()
        print('Job Failed - check error message above')
        S.close()
        pass

def vyosSpawn(jobName):
    try:
        UserName = authClassHash[masterJobHash[jobName]['class']]['user']
        Password = authClassHash[masterJobHash[jobName]['class']]['pass']

        prompt = (':~\$')
        S = pexpect.spawn('ssh -o StrictHostKeyChecking=no ' + UserName + '@' + masterJobHash[jobName]['ip'])
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
        print()
        print('Job was successful! - find the file at /usr/local/flatar/backups/' +  masterJobHash[jobName]['dir'] +'/' + jobName)
    except:
        ourError = sys.exc_info()
        print(str(ourError))
        print()
        print('Job Failed - check error message above')
        S.close()
        pass

def WriteFile(Content, jobName):
    cList = bytes.decode(Content).splitlines()
    ConfigFile = open(('/usr/local/flatarc/backups/' + masterJobHash[jobName]['dir'] +'/' + jobName), 'w')
    for i in cList:
        ConfigFile.write(i + '\n')
    ConfigFile.close()

#################################################
### Device Mangement
#################################################

def WriteDeviceData():
    #with open('/usr/local/flatarc/flatarcDeviceData.json', 'w') as outfile:
    with open('/usr/local/flatarc/json/backupJobs.json', 'w') as outfile:
        json.dump(masterJobHash, outfile)
        
def GetDeviceData():
    #with open('/usr/local/flatarc/flatarcDeviceData.json') as ourfile:
    with open('/usr/local/flatarc/json/backupJobs.json') as ourfile:
        masterJobHash = json.load(ourfile)
    return masterJobHash

def printJobHash(name, jobHash):
    print('Job Name: ' + name)
    for a in jobHash:
        if a == 'dir':
            print('Backups Directory: ' +  jobHash[a])
        elif a == 'class':
            print('Authentication Class: ' + jobHash[a] )
        elif a == 'status':
            print('Device Status: ' +  jobHash[a])
        elif a == 'interval':
            print('Backup Interval(hours): ' + jobHash[a] )
        elif a == 'protocol':
            print('Access Protocol: ' +  jobHash[a])
        else:
            print(a + ': ' +  jobHash[a])
    print()
    print('##############################')
    print()

def viewAll():
    print()
    if masterJobHash != {}:
        for j in masterJobHash:
            printJobHash(j, masterJobHash[j])
    else:
        print('There are currently no devices managed by flatarc.')
    print()
    input('Press enter to continue: ')


def CheckDir(ourDir):
    if not os.path.isdir('/usr/local/flatarc/backups/' + ourDir):
        os.makedirs('/usr/local/flatarc/backups/' + ourDir)
        os.chmod(('/usr/local/flatarc/backups/' + ourDir), 0o777)
        os.system('git init /usr/local/flatarc/backups/' + ourDir)

def addJob():
    print()
    print('Backup Job Name - This name is only used to manage backup jobs.')
    jobName = input('Job Name: ')
    if jobName in masterJobHash or jobName == '':
        print()
        print('This job name is already taken.')
        print()
        input('Press enter to continue')
    else:
        deviceHash = {}
        deviceHash['ip'] = input('Enter the IP Address or DNS name of the backup target: ')
        deviceHash['protocol'] = input('Enter the access protocol (ssh, scp): ')
        if deviceHash['protocol'] == 'ssh':
            deviceHash['syntax'] = input('Enter the device syntax (cisco, junos, vyos): ')
        else:
            deviceHash['file'] = input('Enter full path to file to backup: ')
        deviceHash['interval'] = input('Enter the backup interval in hours: ')
        deviceHash['dir'] = input('Enter the backup directory: ')
        deviceHash['class'] = input('Enter the Authentication Class name: ')
        deviceHash['status'] = input('Enter the device status (up, down): ')
        masterJobHash[jobName] = deviceHash
        WriteDeviceData()
        CheckDir(deviceHash['dir'])
        print()
        print('Backup job ' + jobName + ' has been added.')
        print()
        input('Press enter to continue.')

def editJobs():
    print()
    tgt = input('Enter Job Name: ')
    print()
    if tgt in masterJobHash:
        printJobHash(tgt, masterJobHash[tgt])
        while True:
            print('1 - Modify this job')
            print('2 - Delete this job')
            print()
            print('3 - Return to main menu')
            print()
            Var = input('Enter Selection: ')
            if Var == '3':
                WriteDeviceData()
                break
            if Var == '1':
                print('Which attribute shall be modified?: ')
                print('1 - Job Name')
                print('2 - Ip Address')
                print('3 - Access Protocol')
                if 'file' in masterJobHash[tgt]:
                    print('4 - file')
                else:
                    print('4 - Syntax')
                print('5 - Backup Interval(hours)')
                print('6 - Backups Directory')
                print('7 - Authentication Class')
                print('8 - Status')
                print()
                att = input('Enter the attribute to be modified: ')
                attVal = input('Enter the new value: ')
                if att == '1':
                    masterJobHash[attVal] = masterJobHash[tgt]
                    del masterJobHash[tgt]
                    tgt = attVal
                elif att == '2':
                    masterJobHash[tgt]['ip'] = attVal
                elif att == '3':
                    masterJobHash[tgt]['protocol'] == attVal
                elif att == '4' and 'file' in masterJobHash[tgt]:
                    masterJobHash[tgt]['file'] = attVal
                elif att == '4':
                    masterJobHash[tgt]['syntax'] = attVal
                elif att == '5':
                    masterJobHash[tgt]['interval'] = attVal
                elif att == '6':
                    masterJobHash[tgt]['dir'] = attVal
                elif att == '7':
                    masterJobHash[tgt]['class'] = attVal
                elif att == '8':
                    masterJobHash[tgt]['status'] == attVal
                print()
                CheckDir(masterJobHash[tgt]['dir'])
                printJobHash(tgt, masterJobHash[tgt])
            if Var == '2':
                del masterJobHash[tgt]
                WriteDeviceData()
                print()
                print('The following job has been removed: ' + tgt)
                print()
                input('Press enter to continue')
                break
    else:
        print()
        print('Job not found.')
        print()
        input('Press enter to continue')

##################################################
############## Main program ######################
##################################################

CurUser = getpass.getuser()
if CurUser != 'flatarc':
    print()
    print('This program must only be utilized with the flatarc account.  If another user uses this account the directories and files it creates will not have the proper permissions for the flatarc daemon to utilize them.')
    print()
    print('Exiting...')
    sys.exit()

try:
    authClassHash = getAuthClassHash()
except:
    authClassHash = {}
    pass

try:
    masterJobHash = GetDeviceData()
except:
    masterJobHash = {}
    pass

print()
print('Flat Configuration Archiver - FlatArc')
print()
print('Welcome to FlatArc!')
print()
print('This is the FlatArc Managment tool.')
while True:
    print()
    print('1 - Authentication Class management')
    print()
    print('2 - Add backup job.')
    print('3 - Edit/Delete backup job')
    print('4 - View backup jobs')
    print('5 - Run a backup job')
    print()
    print('99 - Exit')
    print()
    Selection = input('Please enter your selection: ')
    print()
    if Selection == '1':
        PassManage()
    if Selection == '99':
        break
        sys.exit()
    if Selection == '2':
        addJob()
    if Selection == '3':
        editJobs()
    if Selection == '4':
        viewAll()
    if Selection == '5':
        runBackupJob()
