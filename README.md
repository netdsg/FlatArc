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
### Install FlatArc Scripts ###
Unbuntu/Debian example:

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

### Make flatarc systemd service ####
As root do the following:

    cp flatarc.service /ect/systemd/system/.
    systemctl enable flatarc
    systemctl start flatarc
## Usage Example ##
	flatarc@deb-vm2:/usr/local/flatarc$ ./flatarcManage.py

	Flat Configuration Archiver - FlatArc

	Welcome to FlatArc!

	This is the FlatArc Managment tool.

	1 - Authentication Class management

	2 - Add backup job.
	3 - Edit/Delete backup job
	4 - View backup jobs

	99 - Exit

	Please enter your selection: 1


	1 - Display all Authenticaiton Classes
	2 - Display a specific Authentication Class
	3 - Add an Authentication class
	4 - Remove an Authentication class
	5 - Edit an Authentication class

	Please enter the option number: 3

	Enter Authentication Class name: hero
	Enter username: hero
	Enter Password: hero
	encrypting!

	hero Has been added.
	Press enter to continue.

	1 - Authentication Class management

	2 - Add backup job.
	3 - Edit/Delete backup job
	4 - View backup jobs

	99 - Exit


	1 - Authentication Class management

	2 - Add backup job.
	3 - Edit/Delete backup job
	4 - View backup jobs

	99 - Exit

	Please enter your selection: 2


	Backup Job Name - This name is only used to manage backup jobs.
	Job Name: r1
	Enter the IP Address or DNS name of the backup target: 10.10.1.1
	Enter the access protocol (ssh, scp): ssh
	Enter the device syntax (cisco, junos, vyos): cisco
	Enter the backup interval in hours: 12
	Enter the backup directory: lab
	Enter the Authentication Class name: hero
	Enter the device status (up, down): up
	Initialized empty Git repository in /usr/local/flatarc/backups/lab/.git/

	Backup job r1 has been added.

	Press enter to continue.

	1 - Authentication Class management

	2 - Add backup job.
	3 - Edit/Delete backup job
	4 - View backup jobs

	99 - Exit

	Please enter your selection: 99
## What To Look For ##
Look for job success/failures in /usr/local/flatarc/flatarc_log.txt

Look for the backup job files in /usr/local/flatarc/backups/\<backup dir\>
	
Use git commands to see what's changed.

	flatarc@flatarc:/usr/local/flatarc/backups/lab$ git log R1
	commit 5b0ee9f2c5a44fcc0231a30db6d6ba6032f0ea28
	Author: flatarc <flatarc@local.local>
	Date:   Thu Jun 13 17:04:41 2019 +0900

    		courtesy of flatarc!

	commit daa3c47e93e8d52575311956248a889d3213a9b7
	Author: flatarc <flatarc@local.local>
	Date:   Wed Jun 12 14:08:07 2019 +0900

    		courtesy of flatarc!

	commit 63b2362a3180c0ed057a211a278ce48e85dd8bdd
	Author: flatarc <flatarc@local.local>
	Date:   Wed Jun 12 11:07:23 2019 +0900

    		courtesy of flatarc!


	flatarc@flatarc:/usr/local/flatarc/backups/lab$ git diff daa3c47e93e8d52575311956248a889d3213a9b7 			5b0ee9f2c5a44fcc0231a30db6d6ba6032f0ea28
	diff --git a/R1 b/R1
	index b43ec75..5c4418b 100644
	--- a/R1
	+++ b/R1
	@@ -1,9 +1,9 @@
 	show run
 	Building configuration...
 
	-Current configuration : 8926 bytes
	+Current configuration : 8936 bytes
 	!
	-! Last configuration change at 04:32:50 UTC Wed Jun 12 2019 by hero
	+! Last configuration change at 07:36:21 UTC Thu Jun 13 2019 by hero
 	!
 	version 12.2
 	service timestamps debug datetime msec
	@@ -159,6 +159,7 @@ interface FastEthernet1/1
  	ip address 10.1.14.1 255.255.255.0
  	ip nat inside
  	ip flow ingress
	+ shutdown
  	speed auto
  	duplex auto
 	!

