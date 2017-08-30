#! /usr/bin/env python2

"""
    Welcome to auto_ssh.py
    ======================

    This is a simple automizer script for ssh connections.
    To run, append the script with hostname, username and password.
    For example:
        $ python auto_ssh.py <hostname> <username> <password>

    Another way to run the script is by hardcoding the paramters in main().
    And then simply run the script as:
        $ python auto_ssh.py

    After the script is run it will make one attempt to connect to the SSH
    server.
    If successful, it will prompt for further attempts.
    You will be prompted to enter number of attempts until you enter ZERO to
    exit.

    And to display this help, run:
        $ python auto_ssh.py -h

    Dependencies
    ============
    * python 2.7
    * paramiko (run: "$ sudo pip install paramiko")
    * progressbar2 (run: "$ sudo pip install progressbar2")
"""

try:
    import sys
    import paramiko
    import progressbar
except ImportError as ie:
    raise ie


def get_input():
    input_msg = "Enter number of login attempts(or zero to exit): "
    err_msg = "Error! Number of attempts must be positive integer."
    try:
        num = int(raw_input(input_msg))
    except Exception as e:
        print err_msg
        isRetry = raw_input("Retry? (y/n):")
        if isRetry.lower() == "y" or isRetry.lower() == "yes":
            num = ""    # cast num as string so its loop till it is int
            while not isinstance(num, int):
                try:
                    num = int(raw_input(input_msg))
                except:
                    print err_msg
        else:
            num = 0
    finally:
        return num


def autoconnect_ssh(hostname, username, password):
    paramiko.util.log_to_file('ssh.log')  # sets up logging

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print ("Connecting: %s@%s" % (username, hostname))
    num = 1     # First login attempt is to test connectivity
    while num > 0:
        bar = progressbar.ProgressBar()
        for i in bar(range(0, num)):
            try:
                ssh.connect(hostname, username=username, password=password)
                # print "Successfully started SSH session."
                stdin, stdout, stderr = ssh.exec_command('ls -l')
            except Exception as e:
                # print "Error! Could not start SSH session."
                raise e
        num = get_input()
    print "Exiting..."


def main(argv):
    if len(argv) == 1 and (argv[0] == '-h' or argv[0] == '--help'):
        print __doc__
        return 0
    elif len(argv) < 3:
        hostname = 'localhost'
        username = 'username'
        password = 'password'
    else:
        hostname = argv[0]
        username = argv[1]
        password = argv[2]

    autoconnect_ssh(hostname, username, password)


if __name__ == '__main__':
    main(sys.argv[1:])