#!/usr/bin/python3

import pexpect, time, sys, os, datetime, re, json, getpass, subprocess, pydoc
from simplecrypt import *

############################################
####  Password Managment 
############################################

### Change the EVar variable at installation time! - this is the variable that hashes the passwords
### This must also be changed and match in the flatarc.py file.
### These files should have permissions that do not allow others to view them.

EVar = 'thisvariablehashesthepasswords'

def writeAuthClassHash(Account, changePass):
    if authClassHash != {}:
        if changePass == 'yes' and authClassHash[Account]['method'] == 'password':
            print('encrypting ' + Account)
            cipherPass = encrypt(EVar, authClassHash[Account]['pass'])
            with open('/usr/local/flatarc/auth_class/auth_class_' + Account + '.flatarc', 'wb') as output:
                output.write(cipherPass)
        elif changePass == 'yes' and 'pre' in authClassHash[Account]['method']:
            cipherPreShare = encrypt(EVar, authClassHash[Account]['preshare'])
            with open('/usr/local/flatarc/auth_class/auth_class_preshared' + Account + '.flatarc', 'wb') as output:
                output.write(cipherPreShare)
        ourHash = {}
        for i in authClassHash:
            ourHash[i] = {}
            ourHash[i]['user'] = authClassHash[i]['user']
            ourHash[i]['method'] = authClassHash[i]['method']
    with open('/usr/local/flatarc/json/flatarcClass.json', 'w') as ourfile:
        json.dump(ourHash, ourfile)

def getAuthClassHash():
    with open('/usr/local/flatarc/json/flatarcClass.json') as ourFile:
        ourHash = json.load(ourFile)
        for c in ourHash:
            if ourHash[c]['method'] == 'password':
                with open(('/usr/local/flatarc/auth_class/auth_class_' + c + '.flatarc'), 'rb') as inbound:
                    cipherPass = inbound.read()
                print('decrypting ' + c)
                ourHash[c]['pass'] = bytes.decode(decrypt(EVar, cipherPass))
                ourHash[c]['preshare'] = 'null'
            if ourHash[c]['method'] == 'pre-shared':
                with open(('/usr/local/flatarc/auth_class/auth_class_preshared' + c + '.flatarc'), 'rb') as inbound:
                    cipherPreShare = inbound.read()
                print('decrypting ' + c)
                ourHash[c]['preshare'] = bytes.decode(decrypt(EVar, cipherPreShare))
                ourHash[c]['pass'] = 'null'
    return ourHash

def DisplayData():
    if authClassHash != {}:
        dText = ''
        for i in authClassHash:
            dText += ('\nAccount: ' + i)
            dText += ('\nUsername: ' + authClassHash[i]['user'])
            if authClassHash[i]['method'] == 'pre-shared':
                dText += ('\nMethod ssh key')
            else:
                dText += ('\nMethod: ' + authClassHash[i]['method'])
            dText += ('\nPassword: ' + authClassHash[i]['pass'] + '\n\n#######################\n')
        pydoc.pager(dText)
        print()
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
        print('Method: ' + authClassHash[Account]['method'])
        print('Password: ' + authClassHash[Account]['pass'])
        print()
        if 'pre' in authClassHash[Account]['method']:
            viewKey = input('Would you lke to veiw the private key (yes,no): ')
            if 'yes' in viewKey:
                print(authClassHash[Account]['preshare'])
        input('Press enter to continue.')
    else:
        print('Class not found.')
        input('Press enter to continue.')

def AddAccount():
    changePass = 'yes'
    Account = input('Enter Authentication Class name: ')
    if Account not in authClassHash:
        preSharedKey = ''
        PlainPassword = ''
        User = input('Enter username: ')
        method = input('Will this class use password or ssh key authentication (password, key): ')
        if 'key' in method:
            endOfInput = ''
            print('Enter the private key and press enter: ')
            for line in iter(input, endOfInput):
                preSharedKey += (line + '\n')
            method = 'pre-shared'
        else:
            PlainPassword = input('Enter Password: ')
        authClassHash[Account] = {}
        authClassHash[Account]['user'] = User
        authClassHash[Account]['pass'] = PlainPassword
        authClassHash[Account]['method'] = method
        authClassHash[Account]['preshare'] = preSharedKey
        writeAuthClassHash(Account, changePass)
        print()
        print(Account + ' Has been added.')
        input('Press enter to continue.')
    else:
        print('This class already exists.')
        input('press enter to continue.')

def RmAccount():
    ### check if changePass needs to be set!
    changePass = 'null'
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
            writeAuthClassHash(Account, changePass)
            print('This Authentication Class has been removed.')
            input('press enter to continue.')
        else:
            print('No action was taken')
            input('press enter to continue.')
    else:
        print(Account + ' was not found.')
        input('press enter to continue.')

def EditAccount():
    ### need to allow shh key change here!
    print()
    Account = input('Enter Authentication Class name: ' )
    if Account in authClassHash:
        changePass = 'null'
        print()
        print('AuthenticationClass: ' + Account)
        print('Username: ' + authClassHash[Account]['user'])
        print('Password: ' + authClassHash[Account]['pass'])
        if authClassHash[Account]['method'] == 'pre-shared':
            print('Method: ssh key')
        else:
            print('Method: ' + authClassHash[Account]['method'])
        print()
        print('1 - Change authentication class name')
        print('2 - Change username')
        print('3 - Change password')
        print('4 - Change method')
        print('5 - Change ssh private key')
        print()
        Option = input('Enter option: ')
        if Option == '1':
            NewAccount = input('Enter new class name: ')
            authClassHash[NewAccount] = authClassHash[Account]
            del authClassHash[Account]
            try:
                os.remove('/usr/local/flatarc/auth_class/auth_class_' + Account + '.flatarc')
                os.remove('/usr/local/flatarc/auth_class/auth_class_' + Account + '_key.flatarc')
            except:
                pass
            Account = NewAccount
            changePass = 'yes'
        if Option == '2':
            NewUser = input('Enter new username: ')
            authClassHash[Account]['user'] = NewUser
        if Option == '3':
            NewPass = input('Enter new password: ')
            authClassHash[Account]['pass'] = NewPass
            changePass = 'yes'
        if Option == '4':
            methodOption = input('Enter new method (password, key): ')
            if 'key' in methodOption:
                authClassHash[Account]['method'] = 'pre-shared'
                print('Enter the private key and press enter: ')
                endOfInput = ''
                preSharedKey = ''
                for line in iter(input, endOfInput):
                    preSharedKey += (line + '\n')
                authClassHash[Account]['preshare'] = preSharedKey
            else:
                authClassHash[Account]['pass'] = input('Enter new password: ')
                authClassHash[Account]['method'] = 'password'
            changePass = 'yes'
        if Option == '5': 
            print('Enter the private key and press enter: ')
            endOfInput = ''
            preSharedKey = ''
            for line in iter(input, endOfInput):
                preSharedKey += (line + '\n')
            authClassHash[Account]['preshare'] = preSharedKey
            changePass = 'yes'
        writeAuthClassHash(Account, changePass)
        print()
        print('New class Data:')
        print('Class: ' + Account)
        print('Username: ' + authClassHash[Account]['user'])
        print('Password: ' + authClassHash[Account]['pass'])
        if authClassHash[Account]['method'] == 'pre-shared':
            print('Method: ssh key')
        else:
            print('Method: ' + authClassHash[Account]['method'])
        print()
        input('Press enter to continue.')
    else:
        print('Account not found.')

#################################################
### Run Job Functions
#################################################

def gitCommit(tgtDir):
    print()
    print('Running git commmit...')
    S = pexpect.spawn('bash')
    S.expect('\$')

    S.sendline('cd /usr/local/flatarc/backups/' + tgtDir)
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
        if 'Could not create directory' in i or 'Failed to add the host to the list of known hosts' in i:
            pass
        else:
            print(i)

def ScpSpawn(jobName):
    try:
        UserName = authClassHash[masterJobHash[jobName]['class']]['user']
        Password = authClassHash[masterJobHash[jobName]['class']]['pass']

        S = pexpect.spawn('bash')
        S.expect('\$')
        
        if 'pre' in authClassHash[masterJobHash[jobName]['class']]['method']:
            subprocess.run(['touch', (jobName + '.txt')])
            subprocess.run(['chmod', '600', (jobName + '.txt')])
            with open(('/usr/local/flatarc/' + jobName + '.txt'), 'a') as outFile:
                outFile.write(authClassHash[masterJobHash[jobName]['class']]['preshare'])
            outFile.close()
            S.sendline('scp -o StrictHostKeyChecking=no -r -i ' + ('/usr/local/flatarc/' + jobName + '.txt') + ' ' + UserName + '@' + masterJobHash[jobName]['ip'] + ':' + masterJobHash[jobName]['file'] + ' /usr/local/flatarc/backups/' + masterJobHash[jobName]['dir'] + '/' + masterJobHash[jobName]['file'].split('/')[-1] + '.' + jobName)
            S.expect('\$')
            DisplayText(S.before, S.after)

            os.remove('/usr/local/flatarc/' + jobName + '.txt')

        else:
            S.sendline('scp -o StrictHostKeyChecking=no -r ' + UserName + '@' + masterJobHash[jobName]['ip'] + ':' + masterJobHash[jobName]['file'] + ' /usr/local/flatarc/backups/' + masterJobHash[jobName]['dir'] + '/' + masterJobHash[jobName]['file'].split('/')[-1] + '.' + jobName)
            S.expect('word:')

            DisplayText(S.before, S.after)

            S.sendline(Password)
            S.expect('\$')
            DisplayText(S.before, S.after)

        EvalStatus = bytes.decode(S.before)
        print(EvalStatus)
        if 'No such file or directory' in EvalStatus:
            print('Job failed - File could not be found.')
        else:
            Status = 'Success'
            gitCommit(masterJobHash[jobName]['dir'])
            print()
            print('Job was successful - find file at /usr/local/flatarc/backups/' + masterJobHash[jobName]['dir'] + '/' + masterJobHash[jobName]['file'].split('/')[-1] + '.' + jobName)
        if 'pre' in authClassHash[masterJobHash[jobName]['class']]['method']:
            os.remove('/usr/local/flatarc/' + jobName + '.txt')

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

        if 'pre' in authClassHash[masterJobHash[jobName]['class']]['method']:
            subprocess.run(['touch', (jobName + '.txt')])
            subprocess.run(['chmod', '600', (jobName + '.txt')])
            with open(('/usr/local/flatarc/' + jobName + '.txt'), 'a') as outFile:
                outFile.write(authClassHash[masterJobHash[jobName]['class']]['preshare'])
            outFile.close()
            S = pexpect.spawn('ssh -o StrictHostKeyChecking=no -i ' + ('/usr/local/flatarc/' + jobName + '.txt') + ' ' + UserName + '@' + masterJobHash[jobName]['ip'])
            S.expect(prompt)
            DisplayText(S.before, S.after)

            os.remove('/usr/local/flatarc/' + jobName + '.txt')

        else:
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
        gitCommit(masterJobHash[jobName]['dir'])
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

        if 'pre' in authClassHash[masterJobHash[jobName]['class']]['method']:
            subprocess.run(['touch', (jobName + '.txt')])
            subprocess.run(['chmod', '600', (jobName + '.txt')])
            with open(('/usr/local/flatarc/' + jobName + '.txt'), 'a') as outFile:
                outFile.write(authClassHash[masterJobHash[jobName]['class']]['preshare'])
            outFile.close()
            S = pexpect.spawn('ssh -o StrictHostKeyChecking=no -i ' + ('/usr/local/flatarc/' + jobName + '.txt') + ' ' + UserName + '@' + masterJobHash[jobName]['ip'])
            S.expect(prompt)
            DisplayText(S.before, S.after)

            os.remove('/usr/local/flatarc/' + jobName + '.txt')
        
        else:
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
        gitCommit(masterJobHash[jobName]['dir'])
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
        if 'pre' in authClassHash[masterJobHash[jobName]['class']]['method']:
            subprocess.run(['touch', (jobName + '.txt')])
            subprocess.run(['chmod', '600', (jobName + '.txt')])
            with open(('/usr/local/flatarc/' + jobName + '.txt'), 'a') as outFile:
                outFile.write(authClassHash[masterJobHash[jobName]['class']]['preshare'])
            outFile.close()
            S = pexpect.spawn('ssh -o StrictHostKeyChecking=no -i ' + ('/usr/local/flatarc/' + jobName + '.txt') + ' ' + UserName + '@' + masterJobHash[jobName]['ip'])
            S.expect(prompt)
            DisplayText(S.before, S.after)

            os.remove('/usr/local/flatarc/' + jobName + '.txt')

        else:
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
        gitCommit(masterJobHash[jobName]['dir'])
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
    with open('/usr/local/flatarc/json/backupJobs.json', 'w') as outfile:
        json.dump(masterJobHash, outfile)
        
def GetDeviceData():
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
        dText = ''
        for j in masterJobHash:
            #printJobHash(j, masterJobHash[j])
            dText += ('Job Name: ' + j + '\n')
            dText += ('Authentication Class: ' + masterJobHash[j]['class'] + '\n')
            dText += ('Device Status: ' + masterJobHash[j]['status'] + '\n')
            dText += ('Backup Interval: ' + masterJobHash[j]['interval'] + '\n')
            dText += ('Access Protocol: ' + masterJobHash[j]['protocol'] + '\n')
            dText += ('Backup Directory: ' + masterJobHash[j]['dir'] + '\n')
            dText += ('IP Address: ' + masterJobHash[j]['ip'] + '\n')
            if 'syntax' in masterJobHash[j]:
                dText += ('Syntax: ' + masterJobHash[j]['syntax'] + '\n')
            if 'file' in masterJobHash[j]:
                dText += ('file: ' + masterJobHash[j]['file'] + '\n')
            dText += ('\n#############################\n\n')
        pydoc.pager(dText)
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

if not os.path.isdir('/usr/local/flatarc/json'):
    os.makedirs('/usr/local/flatarc/json')
if not os.path.isdir('/usr/local/flatarc/auth_class'):
    os.makedirs('/usr/local/flatarc/auth_class')

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
