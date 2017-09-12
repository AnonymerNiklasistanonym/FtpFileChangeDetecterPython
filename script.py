"""
With this script you can watch for changes of files of an ftp server.
If it's a text file you can even get the new additions.
"""


import difflib
import json
import logging
import os
from datetime import datetime
from ftplib import (FTP_TLS, all_errors, error_perm, error_proto, error_reply,
                    error_temp)

# Gmail API - set true if you want to use the SimplifiedGmailApi
# comment the import if you don't need it
from SimplifiedGmailApiSubmodule.SendGmailSimplified import SimplifiedGmailApi

GMAIL_API = True

# Paths for important directories and files - from home directory
HOME_DIR = os.path.expanduser('~')

# change this to the directory your script is: !!!!!!!!!!!!!!!!!
DIR_OF_SCRIPT = os.path.join(HOME_DIR, "Documents/GitHubBeta/FtpFileChangeDetecterPython")

# default file names
PATH_FOR_FTP_CREDENTIALS = os.path.join(DIR_OF_SCRIPT, "credentials_ftp.json")
PATH_FOR_FTP_FILES = os.path.join(DIR_OF_SCRIPT, "watch_these_ftp_files.json")
DIR_OF_DOWNLOADS = os.path.join(DIR_OF_SCRIPT, "Downloads")
PATH_FOR_LOG = os.path.join(DIR_OF_SCRIPT, "script.log")

# other things
JSON_TAG_MODIFIED_TIME = "last-modified-time"

# Logging file
logging.basicConfig(filename=PATH_FOR_LOG, level=logging.DEBUG)


if GMAIL_API:
    DIR_OF_GMAIL_API_FILES = os.path.join(DIR_OF_SCRIPT,
                                          "SimplifiedGmailApiSubmodule/gmail_api_files")
    PATH_OF_CLIENT_DATA = os.path.join(
        DIR_OF_GMAIL_API_FILES, "client_data.json")
    PATH_OF_CLIENT_SECRET = os.path.join(
        DIR_OF_GMAIL_API_FILES, "client_secret.json")
    GMAIL_SERVER = None
else:
    DIR_OF_GMAIL_API_FILES = None
    PATH_OF_CLIENT_DATA = None
    PATH_OF_CLIENT_SECRET = None
    GMAIL_SERVER = None


def save_string_to_json(date_string, file_path):
    """Convert date to entry in json file

    Args:
    date_string: String of the entry (date)
    tag_name: Name of the json tag
    file_path: Path of the file

    """

    json_data_new_modified_time = {JSON_TAG_MODIFIED_TIME: date_string}

    with open(file_path, 'w') as outfile:
        json.dump(json_data_new_modified_time, outfile,
                  indent=2, ensure_ascii=False)


# load ftp credentials
with open(PATH_FOR_FTP_CREDENTIALS, "r") as file:
    FTP_CREDENTIALS_JSON = json.load(file)

# load ftp files to watch
with open(PATH_FOR_FTP_FILES, "r") as file:
    FTP_FILES_JSON = json.load(file)


# Check if the directory for the tables exists, if not create it
if not os.path.exists(DIR_OF_DOWNLOADS):
    os.makedirs(DIR_OF_DOWNLOADS)


try:
    # connect to ftp server:
    print("Login to " + FTP_CREDENTIALS_JSON["host-address"] + " with " +
          FTP_CREDENTIALS_JSON["username"] + ":")
    FTP_CLIENT = FTP_TLS(FTP_CREDENTIALS_JSON["host-address"])
    FTP_CLIENT.login(
        user=FTP_CREDENTIALS_JSON["username"], passwd=FTP_CREDENTIALS_JSON["password"])
    logging.info("Successfully logged in to " + FTP_CREDENTIALS_JSON["host-address"] + " with " +
                 FTP_CREDENTIALS_JSON["username"])
# exceptions if the connection cannot be established
except error_reply as exception01:
    # Exception raised when an unexpected reply is received from the server.
    print(exception01)
    logging.warning(exception01)
    quit()
except error_temp as exception02:
    # hi
    # Exception raised when an error code signifying a temporary error
    # (response codes in the range 400 - 499) is received.
    print(exception02)
    logging.warning(exception02)
    quit()
except error_perm as exception03:
    # Exception raised when an error code signifying a permanent error
    # (response codes in the range 500 - 599) is received.
    print(exception03)
    logging.warning(exception03)
    quit()
except error_proto as exception04:
    # Exception raised when a reply is received from the server that does not fit the response
    #  specifications of the File Transfer Protocol, i.e. begin with a digit in the range 1 - 5.
    print(exception04)
    logging.warning(exception04)
    quit()
except all_errors as exception05:
    # Other exceptions.
    print(exception05)
    logging.warning(exception05)
    quit()


# now download and compare each file in the JSON file
for FTP_FILE_JSON in FTP_FILES_JSON:

    info_text = ">> Check the file " + FTP_FILE_JSON["path"]
    print(info_text)
    logging.info(info_text)

    # get modified date from the current ftp file:
    # thanks to: https://stackoverflow.com/questions/20049928/created-date-of-file-via-ftp
    modifiedTime = FTP_CLIENT.sendcmd('MDTM ' + FTP_FILE_JSON["path"])
    CURRENT_MODIFIED_TIME = datetime.strptime(modifiedTime[4:],
                                              "%Y%m%d%H%M%S").strftime("%d %B %Y %H:%M:%S")

    # convert date to JSON object
    dictionary_new = {JSON_TAG_MODIFIED_TIME: CURRENT_MODIFIED_TIME}
    NEW_MODIFIED_TIME = json.loads(json.dumps(dictionary_new))

    # time JSON file path
    CURRENT_LOCAL_PATH_MODIFIED_TIME = os.path.join(DIR_OF_DOWNLOADS,
                                                    FTP_FILE_JSON["id"] + "_time" + ".json")

    # check if the last time save exists / is different to the current modified time
    if not os.path.exists(CURRENT_LOCAL_PATH_MODIFIED_TIME):

        # save date and file because it's the first time
        info_text = "Change detected: First time check"
        print(info_text)
        logging.info(info_text)
        save_string_to_json(NEW_MODIFIED_TIME[JSON_TAG_MODIFIED_TIME],
                            CURRENT_LOCAL_PATH_MODIFIED_TIME)
        file_modification_detected = True
    else:

        # check for a file modification date change
        with open(CURRENT_LOCAL_PATH_MODIFIED_TIME, "r") as file:
            OLD_MODIFIED_TIME = json.load(file)

        # if date is another one overwrite all date and save new date
        if OLD_MODIFIED_TIME[JSON_TAG_MODIFIED_TIME] != NEW_MODIFIED_TIME[JSON_TAG_MODIFIED_TIME]:
            info_text = ("Change detected: File was modified: new: " +
                         NEW_MODIFIED_TIME[JSON_TAG_MODIFIED_TIME] + " | old: " +
                         OLD_MODIFIED_TIME[JSON_TAG_MODIFIED_TIME])
            print(info_text)
            logging.info(info_text)
            save_string_to_json(NEW_MODIFIED_TIME["last-modified-time"],
                                CURRENT_LOCAL_PATH_MODIFIED_TIME)
            file_modification_detected = True

        # if the date is the same do nothing
        else:
            info_text = "No change detected"
            print(info_text)
            logging.info(info_text)
            file_modification_detected = False

    # if ftp file is a text file and a change was detected
    if file_modification_detected:

        if GMAIL_SERVER is None and GMAIL_API:
            # create the email server only if a file modification was spotted
            GMAIL_SERVER = SimplifiedGmailApi(PATH_OF_CLIENT_DATA, PATH_OF_CLIENT_SECRET,
                                              DIR_OF_GMAIL_API_FILES)

        if FTP_FILE_JSON["text-file"]:

            CURRENT_LOCAL_PATH_NEW = os.path.join(DIR_OF_DOWNLOADS, FTP_FILE_JSON["id"] +
                                                  "_new" + ".txt")
            CURRENT_LOCAL_PATH_OLD = os.path.join(DIR_OF_DOWNLOADS, FTP_FILE_JSON["id"] +
                                                  "_old" + ".txt")

            # download the file via ftp and save it locally
            info_text = (
                'Getting ' + FTP_FILE_JSON["path"] + " (id=" + FTP_FILE_JSON["id"] + ")")
            print(info_text)
            logging.info(info_text)
            with open(CURRENT_LOCAL_PATH_NEW, 'wb') as local_file:
                FTP_CLIENT.retrbinary(
                    'RETR ' + FTP_FILE_JSON["path"], local_file.write, 1024)

            # create empty old file if no old file exists
            if not os.path.exists(CURRENT_LOCAL_PATH_OLD):
                file = open(CURRENT_LOCAL_PATH_OLD, 'a').close()

            with open(CURRENT_LOCAL_PATH_NEW, "r", encoding="UTF-8") as f:
                CONTENT_FILE_NEW = f.readlines() #.decode("UTF-8")

            # save the new file content to the old file
            with open(CURRENT_LOCAL_PATH_OLD, 'w+', encoding="UTF-8") as f:
                CONTENT_FILE_OLD = f.readlines() #.decode("UTF-8")
                for line in CONTENT_FILE_NEW:
                    f.write(line) #.encode("UTF-8")

            # get the difference between the new and old text file
            # thanks to: https://stackoverflow.com/a/19128062/7827128
            print("Differences:")
            email_text = "Differences between the old and new file:\n\n"
            for line in difflib.unified_diff(CONTENT_FILE_OLD, CONTENT_FILE_NEW,
                                             fromfile='old file', tofile='new file',
                                             lineterm='', n=0):
                print(line.strip("\n"))
                email_text += line.strip("\n") + "\n"

            # try the following - if Gmail Api was activated and a failure while sending the file
            # happens send a email with only the change of the file as a fallback.
            try:
                if GMAIL_API:
                    # Send email:
                    SUBJECT = (
                        "Change of the file " + FTP_FILE_JSON["id"] + " ("
                        + FTP_FILE_JSON["path"] + ")")
                    TEXT = email_text + \
                        "\n\n(" + NEW_MODIFIED_TIME["last-modified-time"] + ")"
                    GMAIL_SERVER.send_plain(
                        FTP_CREDENTIALS_JSON["email-if-change"], SUBJECT, TEXT)
            except UnicodeEncodeError:
                if GMAIL_API:
                    # Send email:
                    SUBJECT = (
                        "Change of the file " + FTP_FILE_JSON["id"] + " (" + 
                        FTP_FILE_JSON["path"] + ")")
                    TEXT = "Last modified time: " + \
                        NEW_MODIFIED_TIME["last-modified-time"]
                    GMAIL_SERVER.send_plain(
                        FTP_CREDENTIALS_JSON["email-if-change"], SUBJECT, TEXT)

        else:
            print("")

            if GMAIL_API:
                # Send email:
                SUBJECT = ("Change of the file " + FTP_FILE_JSON["id"] + " (" +
                           FTP_FILE_JSON["path"] + ")")
                TEXT = "Last modified time: " + \
                    NEW_MODIFIED_TIME["last-modified-time"]
                GMAIL_SERVER.send_plain(
                    FTP_CREDENTIALS_JSON["email-if-change"], SUBJECT, TEXT)

# quit the ftp connection
FTP_CLIENT.quit()
