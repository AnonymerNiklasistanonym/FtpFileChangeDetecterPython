"""
With this script you can watch for changes of files of an ftp server.
If it's a text file you can even get the new additions.
"""


import json
import os
import ftplib
from ftplib import FTP_TLS
import codecs
from datetime import datetime
import difflib
import io
import logging


# Gmail API - set true if you want to use the SimplifiedGmailApi
# comment the import if you don't need it
from SimplifiedGmailApiSubmodule.SendGmailSimplified import SimplifiedGmailApi
GMAIL_API = False

# Paths for important directories and files - from home directory
HOME_DIR = os.path.expanduser('~')

# change this to the directory your script is: !!!!!!!!!!!!!!!!!
DIR_OF_SCRIPT = os.path.join(HOME_DIR, "Documents/FTPPython")

# default file names
PATH_FOR_FTP_CREDENTIALS = os.path.join(DIR_OF_SCRIPT, "credentials_ftp.json")
PATH_FOR_FTP_FILES = os.path.join(DIR_OF_SCRIPT, "watch_these_ftp_files.json")
DIR_OF_DOWNLOADS = os.path.join(DIR_OF_SCRIPT, "Downloads")

# other things
JSON_TAG_MODIFIED_TIME = "last-modified-time"

# Logging file
logging.basicConfig(filename=os.path.join(DIR_OF_SCRIPT, "script.log"), level=logging.DEBUG)


if GMAIL_API:
    DIR_OF_GMAIL_API_FILES = os.path.join(DIR_OF_SCRIPT, "SimplifiedGmailApiSubmodule/gmail_api_files")
    PATH_OF_CLIENT_DATA = os.path.join(DIR_OF_GMAIL_API_FILES, "client_data.json")
    PATH_OF_CLIENT_SECRET = os.path.join(DIR_OF_GMAIL_API_FILES, "client_secret.json")
    GmailServer = None
else:
    DIR_OF_GMAIL_API_FILES = None
    PATH_OF_CLIENT_DATA = None
    PATH_OF_CLIENT_SECRET = None
    GmailServer = None


def save_string_to_json(date_string, file_path):
    """Convert date to entry in json file

    Args:
    date_string: String of the entry (date)
    tag_name: Name of the json tag
    file_path: Path of the file

    """

    json_dictionary = {JSON_TAG_MODIFIED_TIME: date_string}

    with open(file_path, 'w') as outfile:
        json.dump(json_dictionary, outfile, indent=2, ensure_ascii=False)


# load ftp credentials
with open(PATH_FOR_FTP_CREDENTIALS, "r") as file:
    credentials = json.load(file)

# load ftp files to watch
with open(PATH_FOR_FTP_FILES, "r") as file:
    ftp_files = json.load(file)


# Check if the directory for the tables exists, if not create it
if not os.path.exists(DIR_OF_DOWNLOADS):
    os.makedirs(DIR_OF_DOWNLOADS)


try:
    # connect to ftp server:
    print("Login to " + credentials["host-address"] + " with " + credentials["username"] + ":")
    ftp = FTP_TLS(credentials["host-address"])
    ftp.login(user=credentials["username"], passwd=credentials["password"])
    logging.info("Successfully logged in to " + credentials["host-address"] + " with " + credentials["username"])
# exceptions if the connection cannot be established
except ftplib.error_reply as e:
    # Exception raised when an unexpected reply is received from the server.
    print(e)
    logging.warning(e)
    quit()
except ftplib.error_temp as e:
    # hi
    # Exception raised when an error code signifying a temporary error (response codes in the range 400 - 499) is received.
    print(e)
    logging.warning(e)
    quit()
except ftplib.error_perm as e:
    # Exception raised when an error code signifying a permanent error (response codes in the range 500 - 599) is received.
    print(e)
    logging.warning(e)
    quit()
except ftplib.error_proto as e:
    # Exception raised when a reply is received from the server that does not fit the response specifications of the File Transfer Protocol, i.e. begin with a digit in the range 1 - 5.
    print(e)
    logging.warning(e)
    quit()
except ftplib.all_errors as e:
    # Other exceptions.
    print(e)
    logging.warning(e)
    quit()


# now download and compare each file in the JSON file
for ftp_file in ftp_files:

    info_text = ">> Check the file " + ftp_file["path"]
    print(info_text)
    logging.info(info_text)

    # get modified date from the current ftp file:
    # thanks to: https://stackoverflow.com/questions/20049928/created-date-of-file-via-ftp
    modifiedTime = ftp.sendcmd('MDTM ' + ftp_file["path"])
    last_modified_time = datetime.strptime(modifiedTime[4:], "%Y%m%d%H%M%S").strftime("%d %B %Y %H:%M:%S")

    # convert date to JSON object
    dictionary_new = {JSON_TAG_MODIFIED_TIME: last_modified_time}
    new_last_modified_time = json.dumps(dictionary_new)
    new_last_modified_time = json.loads(new_last_modified_time)

    # time JSON file path
    CURRENT_LOCAL_PATH_MODIFIED_TIME = os.path.join(DIR_OF_DOWNLOADS, ftp_file["id"] + "_time" + ".json")

    # check if the last time save exists / is different to the current modified time
    if not os.path.exists(CURRENT_LOCAL_PATH_MODIFIED_TIME):

        # save date and file because it's the first time
        info_text = "Change detected: First time check"
        print(info_text)
        logging.info(info_text)
        save_string_to_json(new_last_modified_time[JSON_TAG_MODIFIED_TIME], CURRENT_LOCAL_PATH_MODIFIED_TIME)
        file_modification_detected = True
    else:

        # check for a file modification date change
        with open(CURRENT_LOCAL_PATH_MODIFIED_TIME, "r") as file:
            current_last_modified_time = json.load(file)

        # if date is another one overwrite all date and save new date
        if current_last_modified_time[JSON_TAG_MODIFIED_TIME] != new_last_modified_time[JSON_TAG_MODIFIED_TIME]:
            info_text = ("Change detected: File was modified: new: " + new_last_modified_time[JSON_TAG_MODIFIED_TIME] + " | old: " + current_last_modified_time[JSON_TAG_MODIFIED_TIME])
            print(info_text)
            logging.info(info_text)
            save_string_to_json(new_last_modified_time["last-modified-time"], CURRENT_LOCAL_PATH_MODIFIED_TIME)
            file_modification_detected = True

        # if the date is the same do nothing
        else:
            info_text = "No change detected"
            print(info_text)
            logging.info(info_text)
            file_modification_detected = False

    # if ftp file is a text file and a change was detected
    if file_modification_detected:

        if GmailServer is None and GMAIL_API:
            # create the email server only if a file modification was spotted
            GmailServer = SimplifiedGmailApi(PATH_OF_CLIENT_DATA, PATH_OF_CLIENT_SECRET, DIR_OF_GMAIL_API_FILES)

        if ftp_file["text-file"]:

            CURRENT_LOCAL_PATH_NEW = os.path.join(DIR_OF_DOWNLOADS, ftp_file["id"] + "_new" + ".txt")
            CURRENT_LOCAL_PATH_OLD = os.path.join(DIR_OF_DOWNLOADS, ftp_file["id"] + "_old" + ".txt")

            # download the file via ftp and save it locally
            info_text = ('Getting ' + ftp_file["path"] + " (id=" + ftp_file["id"] + ")")
            print(info_text)
            logging.info(info_text)
            local_file = open(CURRENT_LOCAL_PATH_NEW, 'wb')
            ftp.retrbinary('RETR ' + ftp_file["path"], local_file.write, 1024)
            local_file.close()

            # create empty old file if no old file exists
            if not os.path.exists(CURRENT_LOCAL_PATH_OLD):
                file = open(CURRENT_LOCAL_PATH_OLD, 'a').close()

            # read new and old file
            file_new = io.open(CURRENT_LOCAL_PATH_NEW, 'r', encoding='utf-8')
            file_old = io.open(CURRENT_LOCAL_PATH_OLD, 'r', encoding='utf-8')
            content_file_new = file_new.readlines()
            content_file_old = file_old.readlines()
            file_old.close()
            file_new.close()

            # save the new file content to the old file
            f = codecs.open(CURRENT_LOCAL_PATH_OLD, 'w', "utf-8")
            for line in content_file_new:
                f.write(line)
            f.close()

            # get the difference between the new and old text file
            # thanks to: https://stackoverflow.com/a/19128062/7827128
            print("Differences:")
            email_text = "Differences between the old and new file:\n\n"
            for line in difflib.unified_diff(content_file_old, content_file_new, fromfile='old file', tofile='new file', lineterm='', n=0):
                print(line.strip("\n"))
                email_text += line.strip("\n") + "\n"

            # try the following - if Gmail Api was activated and a failure while sending the file happens
            # send a email with only the change of the file as a fallback.
            try:
                if GMAIL_API:
                    # Gmail API - Uncomment the coming lines (2,4) if you want to use the Simplified Gmail API
                    # Send email:
                    subject = "Change of the file " + ftp_file["id"] + " (" + ftp_file["path"] + ")"
                    text = email_text + "\n\n(" + new_last_modified_time["last-modified-time"] + ")"
                    GmailServer.send_plain(credentials["email-if-change"], subject, text)
            except UnicodeEncodeError as e:
                if GMAIL_API:
                    # Gmail API - Uncomment the coming 3 lines if you want to use the Simplified Gmail API
                    # Send email:
                    subject = "Change of the file " + ftp_file["id"] + " (" + ftp_file["path"] + ")"
                    text = "Last modified time: " + new_last_modified_time["last-modified-time"]
                    GmailServer.send_plain(credentials["email-if-change"], subject, text)

        else:
            print("")

            if GMAIL_API:
                # Gmail API - Uncomment the coming 3 lines if you want to use the Simplified Gmail API
                # Send email:
                subject = "Change of the file " + ftp_file["id"] + " (" + ftp_file["path"] + ")"
                text = "Last modified time: " + new_last_modified_time["last-modified-time"]
                GmailServer.send_plain(credentials["email-if-change"], subject, text)

# quit the ftp connection
ftp.quit()
