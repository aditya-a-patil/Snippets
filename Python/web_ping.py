#!/usr/bin/env python

"""Web Ping (web_ping.py)

This script runs in an infinite loop, attempting to ping the given web link
every 1 hour(or any interval specified) and determines if HTML page of the
link has been changed since last ping. If a chnage is detected, an email is
sent to the email address provided with changes and HTML content of updated
page.

When a new website is pinged, SHA256 hash is computed over the HTML and stored
in a file with the name of the webpage. For every subsequent pings,
file with previous hash is read and compared with new hash.
If there is a change detected, an email is sent to alert the changes to the
desired email address provided.


Platform:
* Ubuntu 16.04 running Python2.7.

Usuage:

    web_ping.py -u <url>
               [-s <sender email>]
               [-r <recipient email>]
               [-h]

    <url> must be of format <*>://<*>/<*>
"""

import os
import sys
import getopt
import hashlib
import socket
import urllib
import datetime
import time
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import getpass
import difflib

global WEBLINK
global FILENAME

PING_INTERVAL = 3600          # time interval in seconds

# Hard code email options
sender = ""
recipient = ""
# CAUTION: HARDCODING PASSWORDS CAN BE DENGEROUSLY INSECURE.
#          IT IS HIGHLY RECOMMENDED TO LEAVE PASSWORD BLANK SO AS TO INPUT
#          SECURELY DURING RUNTIME.
password = ""


def print_to_console(msg):
    """Print `msg` to console with current timestamp. """
    print "%s : %s" % (datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S"),
                       msg)


def check_internet_connectivity():
    """Connect to google.com and check if target is reachable or not.

    :return: `True` is internet is accessible else `False`.
    """
    server = "google.com"
    port = 80
    connectivity = False
    try:
        host = socket.gethostbyname(server)
        s = socket.create_connection((host, port), 2)
        connectivity = True
        s.close()
    except:
        pass
    finally:
        return connectivity


def get_password():
    """Get password entry from user for sender email address if
    no password is hardcoded.
    Once the password is input, Begin test email is sent to receipent
    as a verification of credentails and connectivity.

    :return: `True` if email is sent successfully else `False`.
    """
    global password
    if password == "":
        password = getpass.getpass("Password: ")
    try:
        subject = "Begining ping to %s" % FILENAME
        print_to_console(subject)
        email(subject=subject)
        return True
    except Exception as e:
        return False


def email(subject="", body_text="", body_html=""):
    """Send email with subject and body provided.

    :param subject: Subject line of email. (optional)
                    (If left blank default subject line will be used)
    :param body_text: Body of email which will be embedded as plain text.
                      (optional)
    :param body_html: Body of email containing HTML content. (optional)
                      (Though this is body, HTML code will be
                      sent as an attachment)
    """
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    if subject == "":
        msg['Subject'] = "CHANGE to %s" % FILENAME
    else:
        msg['Subject'] = subject

    if body_text != "":
        msg.attach(MIMEText(body_text, 'plain'))
    if body_html != "":
        msg.attach(MIMEText(body_html, 'text'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender, password)
    text = msg.as_string()
    server.sendmail(sender, recipient, text)
    server.quit()


def get_filename():
    """Extract filename from webline provided as: *://WEBLINK/*

    :return: `True` if legal urlis provided else `False`.
    """
    try:
        global FILENAME
        FILENAME = "%s" % WEBLINK.split("://")[1].split("/")[0]
        return True
    except Exception as e:
        return False


def write_file(content, isHTML=False):
    """Write hash to FILENMAE.

    :param content: Hash to write in file.
    :param isHTML: Flag for HTML content. (optional)
                   (`True` if HTML content else `False`)
                   (`False` is no value provided)
    :return: `True` if write is success else `False`.
    """
    if isHTML:
        fname = "%s_html" % FILENAME
    else:
        fname = FILENAME

    try:
        with open(fname, 'w') as f:
            f.write(content)
        f.close
        return True
    except Exception as e:
        return False


def read_hash():
    """Return hash from FILENAME in hex.

    :return: Hash stored in `FILENAME`.
    """
    try:
        with open(FILENAME, 'r') as f:
            stored_hash = f.readlines()[0]
        f.close
    except Exception as e:
        stored_hash = None
    finally:
        return stored_hash


def cmp_hash(old_hash, new_hash, html):
    """Compare new hash with old hash from FILENAME and overwrite
    if not matching.

    :param old_hash: Previous hash stored in file.
    :param new_hash: New hash computed.
    :param html: HTML code of the page.
    """
    if new_hash == old_hash:
        print_to_console("NO CHANGE detected")
    else:
        print_to_console("CHANGE DETECTED")
        print_to_console("New hash\t %s" % new_hash)
        print_to_console("Old hash\t %s" % old_hash)
        write_file(new_hash)

        with open("temp", 'w') as f:
            f.write(html)
        f.close()

        diff = []
        with open("%s_html" % FILENAME, 'r') as file1:
            with open("temp", 'r') as file2:
                diff = difflib.unified_diff(
                    file1.readlines(),
                    file2.readlines(),
                    fromfile="%s_html" % FILENAME,
                    tofile='temp',
                )
            file2.close()
        file1.close()

        difference = "Changes detected are:\n\n"
        for line in diff:
            difference += "%s\n" % line
        difference += "\nPS: Attached is HTML content of updated page."

        os.remove("temp")
        write_file(html, isHTML=True)
        email(body_text=difference, body_html=html)


def calc_hash(msg):
    """Compute and return SHA256 over msg.

    :param msg: Message over which hash is to be computed.
    :return: SHA256 Hex of `msg`.
    """
    return hashlib.sha256(msg).hexdigest()


def begin_ping():
    """Launch infinite pinging of weblink provided. """
    try:
        while True:
            try:
                response = urllib.urlopen(WEBLINK)
                html = response.read()
                html_hash = calc_hash(html)
                if os.path.isfile(FILENAME):
                    stored_hash = read_hash()
                    cmp_hash(stored_hash, html_hash, html)
                else:
                    if write_file(html_hash):
                        if not write_file(html, isHTML=True):
                            print_to_console("Error in writing html to file.")
                    else:
                        print_to_console("Error in writing hash to file.")
            except Exception as e:
                raise e
            finally:
                time.sleep(PING_INTERVAL)
    except (KeyboardInterrupt, SystemExit):
        subject = "Ending ping to %s" % FILENAME
        print_to_console(subject)
        email(subject=subject)


def main(argv):
    """Point of Entry (POE). """
    try:
        opts, args = getopt.getopt(argv, "hu:s:r:", ["url="])
    except getopt.GetoptError:
        print_to_console(__doc__)
        sys.exit(2)

    if len(opts) == 0:
        print __doc__
        sys.exit()

    for opt, arg in opts:
        if opt == '-h':
            print __doc__
            sys.exit()
        elif opt in ("-u", "--url"):
            global WEBLINK
            WEBLINK = arg
            if not get_filename():
                print_to_console("Error. URL must be of format *://*/*")
                sys.exit()
        elif opt in ("-s"):
            global sender
            sender = arg
        elif opt in ("-r"):
            global recipient
            recipient = arg

        if check_internet_connectivity():
            if get_password():
                begin_ping()
            else:
                print_to_console("Error in connecting to email server.")
                sys.exit()
        else:
            print_to_console("Error in connecting to internet.")
            sys.exit()


if __name__ == '__main__':
    main(sys.argv[1:])