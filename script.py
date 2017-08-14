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
# exceptions if the connection cannot be established
except ftplib.error_reply as e:
    # Exception raised when an unexpected reply is received from the server.
    print(e)
    quit()
except ftplib.error_temp as e:
    # Exception raised when an error code signifying a temporary error (response codes in the range 400 - 499) is received.
    print(e)
    quit()
except ftplib.error_perm as e:
    # Exception raised when an error code signifying a permanent error (response codes in the range 500 - 599) is received.
    print(e)
    quit()
except ftplib.error_proto as e:
    # Exception raised when a reply is received from the server that does not fit the response specifications of the File Transfer Protocol, i.e. begin with a digit in the range 1 - 5.
    print(e)
    quit()
except ftplib.all_errors as e:
    # Other exceptions.
    print(e)
    quit()


# now download and compare each file in the JSON file
for ftp_file in ftp_files:

    print(">> Check the file " + ftp_file["path"])

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
        print("Change detected: First time check")
        save_string_to_json(new_last_modified_time[JSON_TAG_MODIFIED_TIME], CURRENT_LOCAL_PATH_MODIFIED_TIME)
        file_modification_detected = True
    else:

        # check for a file modification date change
        with open(CURRENT_LOCAL_PATH_MODIFIED_TIME, "r") as file:
            current_last_modified_time = json.load(file)

        # if date is another one overwrite all date and save new date
        if current_last_modified_time[JSON_TAG_MODIFIED_TIME] != new_last_modified_time[JSON_TAG_MODIFIED_TIME]:
            print("Change detected: File was modified: new: " + new_last_modified_time[JSON_TAG_MODIFIED_TIME] + " | old: " + current_last_modified_time[JSON_TAG_MODIFIED_TIME])
            save_string_to_json(new_last_modified_time["last-modified-time"], CURRENT_LOCAL_PATH_MODIFIED_TIME)
            file_modification_detected = True

        # if the date is the same do nothing
        else:
            print("No change detected")
            file_modification_detected = False

    # if ftp file is a text file and a change was detected
    if ftp_file["text-file"] is True and file_modification_detected:

        CURRENT_LOCAL_PATH_NEW = os.path.join(DIR_OF_DOWNLOADS, ftp_file["id"] + "_new" + ".txt")
        CURRENT_LOCAL_PATH_OLD = os.path.join(DIR_OF_DOWNLOADS, ftp_file["id"] + "_old" + ".txt")

        # download the file via ftp and save it locally
        print('Getting ' + ftp_file["path"] + " (id=" + ftp_file["id"] + ")")
        local_file = open(CURRENT_LOCAL_PATH_NEW, 'wb')
        ftp.retrbinary('RETR ' + ftp_file["path"], local_file.write, 1024)
        local_file.close()

        # create empty old file if no old file exists
        if not os.path.exists(CURRENT_LOCAL_PATH_OLD):
            file = open(CURRENT_LOCAL_PATH_OLD, 'a').close()

        file_new = io.open(CURRENT_LOCAL_PATH_NEW, 'r', encoding='utf-8')
        file_old = io.open(CURRENT_LOCAL_PATH_OLD, 'r', encoding='utf-8')

        # get the difference between the new and old text file
        # thanks to: https://stackoverflow.com/a/15864963/7827128
        diff = difflib.ndiff(file_new.readlines(), file_old.readlines())
        delta = ''.join("  + " + x[2:] for x in diff if x.startswith('- '))
        print("Additions to the old file:\n" + delta)
        file_old.close()

        # save the new file content to the old file
        content_new = file_new.readlines()
        file_new.close()
        f = codecs.open(CURRENT_LOCAL_PATH_OLD, 'w', "utf-8")
        # no newline thanks to: https://stackoverflow.com/a/7539151/7827128
        f.write('\n'.join(content_new))
        f.close()

# quit the ftp connection
ftp.quit()
