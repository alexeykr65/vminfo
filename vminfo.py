#!/usr/bin/env python
import paramiko
import sys
import getopt
import re
from colorama import Fore, Style


host = '192.168.180.46'
user = 'root'
secret = ''
port = 22


def main(argv):
    # print 'Argument List:', str(sys.argv)
    try:
        opts, args = getopt.getopt(argv, "hlso:r:k:p:q:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print 'test.py -i <inputfile> -o <outputfile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-l':
            get_full_listvm()
            sys.exit()
        elif opt in ("-s",):
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname=host, username=user, password=secret, port=port)
            stdin, stdout, stderr = client.exec_command('esxcli vm process list')
            data = stdout.read()
            result_data = ''
            for sT in data.splitlines():
                print sT
            client.close()
            sys.exit()

        elif opt in ("-r"):
            argSt = arg
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname=host, username=user, password=secret, port=port)
            stdin, stdout, stderr = client.exec_command('vim-cmd vmsvc/getallvms | grep -i -E '+"\""+argSt+"\"\n")
            data = stdout.read()
            result_data = ''
            for sT in data.splitlines():
                # print sT
                for sF in sT.split():
                    # print sF
                    break
                sCom = 'vim-cmd vmsvc/power.on '+sF+"\n"
                print "======================================="
                print sCom
                stdin, stdout, stderr = client.exec_command(sCom)
                result_data = stdout.read() + stderr.read()
                print result_data
            client.close()
            sys.exit()
        elif opt in ("-p"):
            argSt = arg
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname=host, username=user, password=secret, port=port)
            for sF in argSt.split(','):
                print sF
                sCom = 'vim-cmd vmsvc/power.on '+sF+"\n"
                print "======================================="
                print sCom
                stdin, stdout, stderr = client.exec_command(sCom)
                result_data = stdout.read() + stderr.read()
                print result_data
            client.close()
            sys.exit()
        elif opt in ("-q"):
            argSt = arg
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname=host, username=user, password=secret, port=port)
            for sF in argSt.split(','):
                print sF
                sCom = 'vim-cmd vmsvc/power.off '+sF+"\n"
                print "======================================="
                print sCom
                stdin, stdout, stderr = client.exec_command(sCom)
                result_data = stdout.read() + stderr.read()
                print result_data
            client.close()
            sys.exit()

        elif opt in ("-k"):
            argSt = arg
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname=host, username=user, password=secret, port=port)
            stdin, stdout, stderr = client.exec_command('vim-cmd vmsvc/getallvms | grep -i -E '+"\""+argSt+"\"\n")
            data = stdout.read()
            result_data = ''
            for sT in data.splitlines():
                for sF in sT.split():
                    break
                sCom = 'vim-cmd vmsvc/power.off '+sF+"\n"
                print "======================================="
                print sCom
                stdin, stdout, stderr = client.exec_command(sCom)
                result_data = stdout.read() + stderr.read()
                print result_data
            client.close()

            sys.exit()

        elif opt in ("-o", "--ofile"):
            get_listvm(arg)
            sys.exit()


def get_full_listvm():
    #  t = Terminal()
    #  print(Fore.GREEN + 'Green text')
    #  print t.red('This is red.')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=user, password=secret, port=port)
    stdin, stdout, stderr = client.exec_command('vim-cmd vmsvc/getallvms ')
    data = stdout.read()
    result_data = ''
    for sT in data.splitlines():
        m = re.match(r"^(?P<snum>\d+)\s+(?P<sname>[^\[]+)\[(?P<sdisk>[^\]]+)\]\s+(?P<spath>(?:(?!vmx).)+vmx)([^\n]+)", sT)
        if m:
            sCom = 'vim-cmd vmsvc/power.getstate ' + m.group('snum') + "\n"
            stdin, stdout, stderr = client.exec_command(sCom)
            result_data = stdout.read() + stderr.read()
            if re.search(r"Powered on", result_data):
                sState = "ON"
                print (Fore.GREEN + Style.BRIGHT + "%5s    %20s     %20s    %5s" % (m.group('snum'), m.group('sname'), m.group('sdisk'), sState))
            else:
                sState = "OFF"
                print (Fore.WHITE + Style.BRIGHT + "%5s    %20s     %20s    %5s" % (m.group('snum'), m.group('sname'), m.group('sdisk'), sState))
    client.close()


def get_listvm(argSt):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=user, password=secret, port=port)
    stdin, stdout, stderr = client.exec_command('vim-cmd vmsvc/getallvms | grep -i -E '+"\""+argSt+"\"\n")
    data = stdout.read()
    for sT in data.splitlines():
        print sT
    client.close()

if __name__ == "__main__":
    main(sys.argv[1:])
