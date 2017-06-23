#!/usr/bin/env python
#
# Get and set information from Vmware
#
# alexeykr@gmail.com
#
import sys
import argparse
import paramiko
import re
import getpass
from colorama import Fore, Style

host = '192.168.180.46'
user = 'root'
secret = ""
port = 22
description = "vminfo: Get and set information of VM from Vmware via ssh"
epilog = "Alexey Karpov "
flagVmAll = 1


def cmdArgsParser():
    global flagVmAll
    parser = argparse.ArgumentParser(description=description, epilog=epilog)
    parser.add_argument('-k', '--killpid', help='Terminate VM with PIDs', action="store")
    parser.add_argument('-r', '--runvm', help='PowerON VM with PIDs', action="store")  
    parser.add_argument('-l', '--listvm', help='List vm', action="store_true")
    parser.add_argument('-p', '--procvm', help='VM running  on vmware', action="store_true") 
    parser.add_argument('-i', '--ip', help='IP Esxi Host', action="store",  dest="host", default=host)
    
    return parser.parse_args()


def runCmdViaSSH(vmCommand):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=user, password=secret, port=port)
    stdin, stdout, stderr = client.exec_command(vmCommand)
    data = stdout.read() + stderr.read()
    client.close()
    return data
    

def listVmOnVmware():
    
    vmCommand = 'esxcli vm process list'
    resultData = runCmdViaSSH(vmCommand)
    lstVmRunning = list()
    for sLine in resultData.split("\n"):
        if(re.match(r"^([\S]+.*)", sLine)):
            lstVmRunning.append(sLine.strip())
    
    vmCommand = 'vim-cmd vmsvc/getallvms '
    resultData = runCmdViaSSH(vmCommand)

    for i in resultData.splitlines():
        m = re.match(r"^(?P<snum>\d+)\s+(?P<sname>[^\[]+)\[(?P<sdisk>[^\]]+)\]\s+(?P<spath>(?:(?!vmx).)+vmx)([^\n]+)", i)
        if m:
            flagRun = 0
            sState = "OFF"
            for vmName in lstVmRunning:
                if m.group('sname').strip() == vmName:
                    flagRun = 1
                    sState = "ON"
              
            if flagRun:
                print (Fore.GREEN + Style.BRIGHT + "%5s    %20s     %20s    %5s" % (m.group('snum'), m.group('sname'), m.group('sdisk'), sState))
            elif flagVmAll:
                print (Fore.WHITE + Style.BRIGHT + "%5s    %20s     %20s    %5s" % (m.group('snum'), m.group('sname'), m.group('sdisk'), sState))


def main():
    global flagVmAll
    args = cmdArgsParser()
    
    if(args.procvm):
        flagVmAll = 0
        listVmOnVmware()
        
    # Kill vm with PIDs
    if(args.killpid):
        for i in args.killpid.split(','):
            vmCommand = 'vim-cmd vmsvc/power.off ' + i + "\n"
            data = runCmdViaSSH(vmCommand)
            print data
    # PowerON vm with PIDs
    if(args.runvm):
        for i in args.runvm.split(','):
            vmCommand = 'vim-cmd vmsvc/power.on ' + i + "\n"
            data = runCmdViaSSH(vmCommand)
            print data
    # PowerON vm with PIDs
    if(args.listvm):
        listVmOnVmware()

    sys.exit()

if __name__ == '__main__':
    
    if secret == "": secret = getpass.getpass('Password:')
    sys.exit(main())
