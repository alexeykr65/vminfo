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
from colorama import Fore, Style

host = '192.168.180.46'
user = 'root'
secret = 'noncemale'
port = 22
description = "vminfo: Get and set information of VM from Vmware via ssh"
epilog = "Alexey Karpov "


def cmdArgsParser():
    parser = argparse.ArgumentParser(description=description, epilog=epilog)
    parser.add_argument('-k', '--killpid', help='Terminate vm with PIDs', action="store")
    parser.add_argument('-l', '--listvm', help='List vm', action="store_true")
    parser.add_argument('-p', '--procvm', help='Process list on vmware', action="store_true")  # List process -s
    parser.add_argument('-o', '--poweron', help='PowerON vm with PID', action="store")  # poweron -p
    parser.add_argument('-q', '--quitvmrx', dest='offvm', help='PowerOFF vm with Regex', action="store")  # poweron -p
    parser.add_argument('-r', '--runvm', help='PowerON vm with Regex', action="store")  # poweron -p
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
    vmCommand = 'vim-cmd vmsvc/getallvms '
    data = runCmdViaSSH(vmCommand)
    resultData = ''
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=user, password=secret, port=port)
    for i in data.splitlines():
        m = re.match(r"^(?P<snum>\d+)\s+(?P<sname>[^\[]+)\[(?P<sdisk>[^\]]+)\]\s+(?P<spath>(?:(?!vmx).)+vmx)([^\n]+)", i)
        if m:
            vmCommand = 'vim-cmd vmsvc/power.getstate ' + m.group('snum') + "\n"
            stdin, stdout, stderr = client.exec_command(vmCommand)
            resultData = stdout.read() + stderr.read()
            if re.search(r"Powered on", resultData):
                sState = "ON"
                print (Fore.GREEN + Style.BRIGHT + "%5s    %20s     %20s    %5s" % (m.group('snum'), m.group('sname'), m.group('sdisk'), sState))
            else:
                sState = "OFF"
                print (Fore.WHITE + Style.BRIGHT + "%5s    %20s     %20s    %5s" % (m.group('snum'), m.group('sname'), m.group('sdisk'), sState))
    client.close()


def main():
    args = cmdArgsParser()
    if(args.procvm):
        vmCommand = 'esxcli vm process list'
        data = runCmdViaSSH(vmCommand)
        for i in data.splitlines():
            print i
    # Kill vm with PIDs
    if(args.killpid):
        for i in args.killpid.split(','):
            vmCommand = 'vim-cmd vmsvc/power.off ' + i + "\n"
            data = runCmdViaSSH(vmCommand)
            print data
    # PowerON vm with PIDs
    if(args.poweron):
        for i in args.poweron.split(','):
            vmCommand = 'vim-cmd vmsvc/power.on ' + i + "\n"
            data = runCmdViaSSH(vmCommand)
            print data
    # PowerON vm with PIDs
    if(args.listvm):
        listVmOnVmware()

    sys.exit()

if __name__ == '__main__':
    sys.exit(main())
