#!/usr/bin/python3

# This script comes with no warranty.

# for support contact gatlin007 at gmail dot com

import os, sys, shelve, csv, pprint, getpass
from simplecrypt import *

############################################
#### Begin Password Managment 
############################################
### Change the EVar variable at installation time!
### This must also be changed and match in the flatarc.py file.
### These files should have permissions that do not allow others to view them.
EVar = 'thisvariablehashesthepasswords'

def WriteClassData():
    ClassFile = shelve.open('FlatArcData')
    ClassFile['ClassList'] = ClassList
    ClassFile.close()

def GetClassData():
    global ClassList
    ClassFile = shelve.open('FlatArcData')
    ClassList = ClassFile['ClassList']
    ClassFile.close()

def DisplayData():
    try:
        GetClassData()
    except:
        print('No user data was found.')
    for i in ClassList:
        print()
        print('Account: ' + i[0])
        print('Username: ' + i[1])
        print('Password: ' + bytes.decode(decrypt(EVar, i[2])))
    print()
    input('press enter to continue.')

def PassManage():
    print()
    print('1 - Display all class data')
    print('2 - Display a specific class')
    print('3 - Add a class')
    print('4 - Remove an class')
    print('5 - Edit an class')
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
    FoundVar = 0
    print()
    Account = input('Enter account: ')
    for i in ClassList:
        if Account == i[0]:
            FoundVar = 1
            print('Class: ' + i[0])
            print('Username: ' + i[1])
            print('Password: ' + bytes.decode(decrypt(EVar, i[2])))
            print()
            input('Press enter to continue.')
            break
    if FoundVar == 0:
        print('Class not found.')
        input('Press enter to continue.')

def AddAccount():
    global ClassList
    Account = input('Enter Class name: ')
    ExistVar = 0
    for i in ClassList:
        if Account == i[0]:
            ExistVar = 1
            print('This class already exists.')
            input('press enter to continue.')
            break
    if ExistVar == 0:
        User = input('Enter username: ')
        PlainPassword = input('Enter Password: ')
        Password = encrypt(EVar, PlainPassword)
        ClassList.append([Account, User, Password])
        WriteClassData()
        print()
        print(Account + ' Has been added.')
        input('Press enter to continue.')

def RmAccount():
    global ClassList
    FoundVar = 0
    Account = input('Enter class name: ')
    for i in ClassList:
        if Account == i[0]:
            FoundVar = 1
            print('Would you like to remove this class: ')
            print('Account: ' + i[0])
            print('User: ' + i[0])
            print()
            Delta = input('yes/no: ')
            if Delta == 'yes':
                ClassList.remove(i)
                WriteClassData()
                print('This class has been removed.')
                input('press enter to continue.')
                break
            else:
                print('No action was taken')
                input('press enter to continue.')
                break
    if FoundVar == 0:
        print(Account + ' was not found.')
        input('press enter to continue.')

def EditAccount():
    FoundVar = 0
    print()
    Account = input('Enter class name:' )
    E = -1
    for i in ClassList: 
        E = E + 1
        if Account == i[0]:
            FoundVar = 1
            print()
            print('Class: ' + i[0])
            print('Username: ' + i[1])
            print('Password: ' + bytes.decode(decrypt(EVar, i[2])))
            print()
            print('1 - Change class name')
            print('2 - Change username')
            print('3 - Change password')
            print()
            Option = input('Enter option: ')
            if Option == '1':
                NewAccount = input('Enter new class name: ')
            else:
                NewAccount = None
            if Option == '2':
                NewUser = input('Enter new username: ')
            else:
                NewUser = None
            if Option == '3':
                NewPass = input('Enter new password: ')
            else:
                NewPass = None
            if NewAccount:
                ClassList[E][0] = NewAccount
            if NewUser:
                ClassList[E][1] = NewUser
            if NewPass:
                ClassList[E][2] = encrypt(EVar, NewPass)
            WriteClassData()
            print()
            print('New class Data:')
            print('Class: ' + ClassList[E][0])
            print('Username: ' + ClassList[E][1])
            print('Password: ' + bytes.decode(decrypt(EVar, ClassList[E][2])))
            input('Press enter to continue.')
    if FoundVar == 0:
        print('Account not found.')
#################################################
### End password managemnet
#################################################

#################################################
### Begin Device List Mangement
#################################################

def WriteDeviceData():
    DeviceDataFile = open('flatarcDeviceData.csv', 'w', newline='')
    W = csv.writer(DeviceDataFile)
    for i in DeviceList:
        W.writerow(i)
    DeviceDataFile.close()
        
def GetDeviceData():
    global DeviceList 
    DeviceDataFile = open('flatarcDeviceData.csv')
    R = csv.reader(DeviceDataFile)
    DeviceList = list(R)
    DeviceDataFile.close()

def WriteFileData():
    DataFile = open('flatarcFileData.csv', 'w', newline='')
    W = csv.writer(DataFile)
    for i in ServerFiles:
        W.writerow(i)
    DataFile.close()

def GetFileData():
    global ServerFiles
    DataFile = open('flatarcFileData.csv')
    R = csv.reader(DataFile)
    ServerFiles = list(R)
    DataFile.close()

def PrintHost(i):
    Line = ''
    print('Hostname - Ip Address - Protocol - Syntax - Interval - Directory - Password Class - Status')
    for j in i:
        Line = (Line + j + ' - ')
    Line = Line[:-3]
    print(Line)
    print()

def ViewAll():
    print()
    if DeviceList:
        print('Hostname - Ip Address - Protocol - Syntax - Interval - Directory - Password Class - Status')
        for i in DeviceList:
            Line = ''
            for j in i:
                Line = (Line + j + ' - ')
            Line = Line[:-3]
            print(Line)
    else:
        print('There are currently no devices managed by flatarc.')
    print()
    input('Press enter to continue: ')


def CheckDir():
    for i in DeviceList:
        if not os.path.isdir('/usr/local/flatarc/backups/' + i[5]):
            os.makedirs('/usr/local/flatarc/backups/' + i[5])
            os.chmod(('/usr/local/flatarc/backups/' + i[5]), 0o777)
            os.system('git init /usr/local/flatarc/backups/' + i[5])

def AddDevice():
    global DeviceList
    DupVar = 0
    print()
    Host = input('Enter the device host name: ')
    if DeviceList:
        for i in DeviceList:
            if i[0] == Host:
                DupVar = 1
                break
    if DupVar == 1:
        print()
        print('This device is already registered')
        print()
        input('Press enter to continue')
    else:
        IpAdd = input('Enter the IP Address or DNS name: ')
        #Protocol = input('Enter the access protocol (ssh, telnet): ')
        Protocol = 'ssh'
        Syntax = input('Enter the device syntax (cisco, junos): ')
        Interval = input('Enter the backup interval in hours: ')
        Dir = input('Enter the backup directory: ')
        Class = input('Enter the username/password class: ')
        Status = input('Enter the device status (up, down): ')
        DeviceList.append([Host, IpAdd, Protocol, Syntax, Interval, Dir, Class, Status])
        WriteDeviceData()
        CheckDir()
        print()
        print(Host + ' has been added.')
        print()
        input('Press enter to continue.')

def EditDevices():
    E = -1
    Found = 0
    print()
    Tgt = input('Enter the hostname: ')
    print()
    for i in DeviceList:
        E = E + 1
        if i[0] == Tgt:
            Line = ''
            print('Hostname - Ip Address - Protocol - Syntax - Interval - Directory - Password Class - Status')
            for j in i:
                Line = (Line + j + ' - ')
            Line = Line[:-3]
            print(Line) 
            print()
            Found = 1
            break
    if Found == 1:
        while True:
            print('1 - Modify this device')
            print('2 - Delete this device')
            print()
            print('3 - Return to main menu')
            print()
            Var = input('Enter Selection: ')
            if Var == '3':
                WriteDeviceData()
                break
            if Var == '1':
                print('Which attribute shall be modified?: ')
                print('1 - Hostname')
                print('2 - Ip Address')
                print('3 - Protocol')
                print('4 - Syntax')
                print('5 - Interval')
                print('6 - Directory')
                print('7 - Password Class')
                print('8 - Status')
                print()
                Att = input('Enter the attribute to be modified: ')
                AttVal = input('Enter the new value: ')
                for zoot in range(7):
                    if int(Att) == zoot+1:
                        DeviceList[E][zoot] = AttVal
                PrintHost(DeviceList[E])
                CheckDir()
            if Var == '2':
                DeviceList.remove(i)
                WriteDeviceData()
                print()
                print('The following device has been removed:')
                PrintHost(i)
                print()
                input('Press enter to continue')
                break
    else:
        print()
        print('Device not found.')
        print()
        input('Press enter to continue')
#################################################
### begin server file management
#################################################

def ViewAllFiles():
    print()
    if ServerFiles:
        print('Hostname - Ip Address - File Path - Copy Protocol - Interval - Directory - Password Class - Status')
        for i in ServerFiles:
            Line = ''
            for j in i:
                Line = (Line + j + ' - ')
            Line = Line[:-3]
            print(Line)
    else:
        print('There are currently no server files managed by flatarc.')
    print()
    input('Press enter to continue: ')


def AddFile():
    global ServerFiles
    DupVar = 0
    print()
    Host = input('Enter the server host name: ')
    File = input('Enter the full file path of the target file: ')
    if ServerFiles:
        for i in ServerFiles:
            if (i[0] == Host) and (i[2] == File):
                DupVar = 1
                break
    if DupVar == 1:
        print()
        print('This server and file pair is already registered')
        print()
        input('Press enter to continue')
    else:
        IpAdd = input('Enter the IP Address or DNS name: ')
        Syntax = 'scp'
        Interval = input('Enter the backup interval in hours: ')
        Dir = input('Enter the backup directory: ')
        Class = input('Enter the username/password class: ')
        Status = input('Enter the device status (up, down): ')
        ServerFiles.append([Host, IpAdd, File, Syntax, Interval, Dir, Class, Status])
        WriteFileData()
        print()
        print(File + ' at ' + Host + ' has been added.')
        print()
        input('Press enter to continue.')

def EditFiles():
    E = -1
    Found = 0
    print()
    hTgt = input('Enter the hostname: ')
    fTgt = input('Enter the file path: ')
    print()
    for i in ServerFiles:
        E = E + 1
        if (i[0] == hTgt) and (i[2] == fTgt):
            Line = ''
            print('Hostname - Ip Address - File Path - Copy Protocol - Interval - Directory - Password Class - Status')
            for j in i:
                Line = (Line + j + ' - ')
            Line = Line[:-3]
            print(Line) 
            print()
            Found = 1
            break
    if Found == 1:
        while True:
            print('1 - Modify this device')
            print('2 - Delete this device')
            print()
            print('3 - Return to main menu')
            print()
            Var = input('Enter Selection: ')
            if Var == '3':
                WriteFileData()
                break
            if Var == '1':
                print('Which attribute shall be modified?: ')
                print('1 - Hostname')
                print('2 - Ip Address')
                print('3 - File Path')
                print('4 - Copy Protocol')
                print('5 - Interval')
                print('6 - Directory')
                print('7 - Password Class')
                print('8 - Status')
                print()
                Att = input('Enter the attribute to be modified: ')
                AttVal = input('Enter the new value: ')
                for zoot in range(7):
                    if int(Att) == zoot+1:
                        ServerFiles[E][zoot] = AttVal
                PrintHost(ServerFiles[E])
            if Var == '2':
                ServerFiles.remove(i)
                WriteFileData()
                print()
                print('The following device has been removed:')
                PrintHost(i)
                print()
                input('Press enter to continue')
                break
    else:
        print()
        print('Device not found.')
        print()
        input('Press enter to continue')
############## Main program ######################

CurUser = getpass.getuser()
if CurUser != 'flatarc':
    print()
    print('This program must only be utilized with the flatarc account.  If another user uses this account the directories and files it creates will not have the proper permissions for the flatarc daemon to utilize them.')
    print()
    print('Exiting...')
    sys.exit()

ClassList = []
DeviceList = []
ServerFiles = []

try:
    GetClassData()
except:
    pass

try:
    GetDeviceData()
except:
    pass

try:
    GetFileData()
except:
    pass

print()
print('Flat Configuration Archiver - FlatArc')
print()
print('Welcome to FlatArc!')
print()
print('This is the FlatArc Managment tool.')
while True:
    print()
    print('1 - Add network devices.')
    print('2 - Edit or remove network devices')
    print('3 - View all provisioned network devices')
    print()
    print('4 - Add server configuration files')
    print('5 - Edit or remove server configuration files')
    print('6 - View all provisioned server configuration files')
    print()
    print('10 - Password management')
    print()
    print('99 - Exit')
    print()
    Selection = input('Please enter your selection: ')
    print()
    if Selection == '10':
        PassManage()
    if Selection == '99':
        break
        sys.exit()
    if Selection == '1':
        AddDevice()
    if Selection == '2':
        EditDevices()
    if Selection == '3':
        ViewAll()
    if Selection == '4':
        AddFile()
    if Selection == '5':
        EditFiles()
    if Selection == '6':
        ViewAllFiles()
