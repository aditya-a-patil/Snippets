#! /usr/bin/env python2

"""
    Welcome to auto_ssh.py
    ======================

    This is a simple automizer script for testing ssh connections.
    To run, append the script with hostname and username.
    For example:

        $ python auto_ssh.py <hostname> <username>

    Alternatively parameters can be hardcoded in script.
    And then simply run the script as:

        $ python auto_ssh.py

    Note: Even though passwords can be hardcoded, it is strongly
    advised against to do so as this can be highly insecure.

    After the script is run it will make one attempt to connect to the SSH
    server as a test.
    If successful, it will prompt for further attempts.
    You will be prompted to enter number of attempts until you enter ZERO to
    exit.

    To display this help, run:

        $ python auto_ssh.py -h


    Dependencies
    ============
    * Python 2.7
    * paramiko (run: "$ sudo pip install paramiko")
    * progressbar2 (run: "$ sudo pip install progressbar2")
    * getpass, sys
"""

try:
    import sys
    import paramiko
    import progressbar
    import getpass
except ImportError as ie:
    raise ie

global HOSTNAME
global USERNAME
global PASSWORD

LOGGING = False

# Hard code connection parameters
HOSTNAME = ""
USERNAME = ""
# CAUTION: HARDCODING PASSWORDS CAN BE DENGEROUSLY INSECURE.
#          IT IS HIGHLY RECOMMENDED TO LEAVE PASSWORD BLANK SO AS TO INPUT
#          SECURELY DURING RUNTIME.
PASSWORD = ""


def get_input():
    """Handle user input for number of connection attempts. """
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


def get_password():
    """Input password from user and return it to main(). """
    return getpass.getpass("Password: ")


def autoconnect_ssh():
    """SSH connection module. """
    if LOGGING:
        paramiko.util.log_to_file('ssh.log')  # sets up logging

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print ("Connecting: %s@%s" % (USERNAME, HOSTNAME))
    num = 1     # First login attempt is to test connectivity
    while num > 0:
        bar = progressbar.ProgressBar()
        for i in bar(range(0, num)):
            try:
                ssh.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
                # print "Successfully started SSH session."
                stdin, stdout, stderr = ssh.exec_command('ls -l')
            except Exception as e:
                # print "Error! Could not start SSH session."
                raise e
        num = get_input()
    print "Exiting..."


def main(argv):
    """Point of Entry (POE). """
    global HOSTNAME
    global USERNAME
    global PASSWORD

    if len(argv) == 1 and (argv[0] == '-h' or argv[0] == '--help'):
        print __doc__
        return 0
    elif len(argv) == 2:
        HOSTNAME = argv[0]
        USERNAME = argv[1]
        PASSWORD = get_password()
    elif HOSTNAME == "" or USERNAME == "":
        print "Missing hostname and/or username."
        print "Usage: python auto_ssh.py <hostname> <username>"
        return 0
    elif PASSWORD == "":
        PASSWORD = get_password()

    autoconnect_ssh()


if __name__ == '__main__':
    main(sys.argv[1:])
