# FlatArc Version 2
A utility that automatically archives flat configuration files such as those found on network devices.

This utility runs as a service and is intended to periodically backup flat configuration files at an interval dictated by the user.  If you would like this software to have additional functionality please open an issue.  FlatArc uses SSH to backup network devices, SCP to backup flat files on servers, and GIT in order to track changes.

![alt tag](https://github.com/netdsg/FlatArc/blob/master/FlatArcFlow.png)

The administator uses flatarcManage.py to launch a CLI based management program.  In order for all the file permissions to be correct this progam must be invoked by the 'flatarc' user.  This program will allow the adminstrator to add, modify or remove devices to get backed up.  The backup interval is in hours.  This program also allows the administator to add, modify or remove 'authentication classes'.  'authentication classes' are username/password pairs that FlatArc will use to log into the network equpiment.  The passwords are encrypted with simple-crypt when writing them to disk.  The files refrenced in the above flow chart will be found in the /usr/local/flatarc directory.

The backup directories will be found in /usr/local/flatarc/backups/

Currently supported running configuration backups (Please open an issue if you'd like to see others):
- VyOS
- Cisco IOS
- JUNOS
- Flat files that can be retrieved via SCP.

Application Requirements:
- Python3
- GIT

Python3 Module Requirements:
- pexepct
- simple-crypt

## Installation instructions: ##

Unbuntu example:

As root do the following:

    apt-get install python3-pip
    apt-get install git

    pip3 install pexpect
    pip3 install simple-crypt

    useradd flatarc
    mkdir /usr/local/flatarc
    chown flatarc:flatarc /usr/local/flatarc

As user flatarc do the following:

    cp flatarc.py /usr/local/flatarc/.
    cp flatarcManage.py /usr/local/flatarc/.
    chmod +x flatarc*
    mkdir /usr/local/flatarc backups


