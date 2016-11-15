# FlatArc
A utility that automatically archives flat configuration files such as those found on network devices.

This utility is intended to periodically backup flat configuration files at an interval dictated by the user.  If you would like this software to have additional functionality (or have questions or suggestions) please reach out to gatlin007 at gmail dot com.  FlatArc uses SSH to backup network devices, SCP to backup flat files on servers, and GIT in order to track changes in the files it is backing up.

![alt tag](https://github.com/netdsg/FlatArc/blob/master/FlatArcFlow.png)

The administator uses flatarcManage.py to launch a CLI based management program.  In order for all the file permissions to be correct this progam must be invoked by the 'flatarc' user.  This program will allow the adminstrator to add, modify or remove devices to get backed up.  The backup interval hour is in hours.  This program also allows the administator to add, modify or remove 'classes'.  'Classes' are username/password pairs that FlatArc will use to log into the network equpiment.  The passwords are encrypted with simple-crypt when writing them to disk.  The files refrenced in the above flow chart will be found in the /usr/local/flatarc directory.

Currently supported backups (others can be added; just ask):
- Cisco IOS
- JUNOS
- Flat files that can be retrieved via SCP.

Application Requirements:
- Python3
- GIT

Python3 Module Requirements:
- pexepct
- simple-crypt

#################################################

Installation instructions:

Unbuntu example:

As root do the following:

    apt-get install python3-pip
    apt-get install git

    pip3 install pexpect
    pip3 install simple-crypt

    useradd flatarc
    mkdir /usr/local/flatarc
    chown flatarc:flatarc /usr/local/flatarc

    cp flatarcd /etc/init.d/.
    chmod +x /etc/init.d/flatarcd

As user flatarc do the following:

    cp flatarc.py /usr/local/flatarc/.
    cp flatarcManage.py /usr/local/flatarc/.
    chmod +x flatarc*
    mkdir /usr/local/flatarc backups

As root start the service:

    /etc/init.d/flatarcd start

##################################################

Use flatarcManage.py to add/remove devices or config files.  This program must be run as the flatarc user to ensure the 
directories and files it creates have the proper permissions.  A class refers to a username/password pair.

The backup directories will be found in /usr/local/flatarc/backups


