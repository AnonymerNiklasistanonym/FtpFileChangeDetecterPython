from __future__ import print_function
import httplib2
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import base64
from email.mime.text import MIMEText
import os
from apiclient import errors
import argparse
import logging
import json


class SimplifiedGmailApi:

    def __init__(self, a=None, b=None, c=os.path.join(os.path.expanduser('~'), "GmailCredentialsApi")):
        path_for_gmail_data = a
        # OwnFile: "email","application-name","permission-scope"

        self.PATH_FOR_GMAIL_CLIENT_SECRET_FILE = b
        # GmailFile
        self.DIRECTORY_FOR_GMAIL_API = c
        # directory for permission thing

        if a is None or b is None or c is None:
            print("Something went wrong!!! API will not work!")
            self.SetupOk = False
        else:
            self.SetupOk = True

            with open(path_for_gmail_data, "r") as credentials_file:
                data_file = json.load(credentials_file)

            try:
                self.flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
            except ImportError:
                self.flags = None

            self.SCOPES = data_file["permission-scope"]
            self.APPLICATION_NAME = data_file["application-name"]
            self.EMAIL_ADDRESS = data_file["email"]
            self.EMAIL_ADDRESS_NAME = data_file["email-name"] + " <" + self.EMAIL_ADDRESS + ">"

            credentials = self.__get_credentials()
            http = credentials.authorize(httplib2.Http())
            self.service = discovery.build('gmail', 'v1', http=http)

    def send_plain(self, b="to", c="subject", d="message"):
        return self.__send_mail(b, c, d)

    def send_html(self, b="to", c="subject", d="message"):
        return self.__send_mail(b, c, d, True)

    def __send_mail(self, b="to", c="subject", d="message", html_mail=False):

        if self.SetupOk:

            print("Send email from " + self.EMAIL_ADDRESS_NAME + " to: " + b + ":")
            print("          " + c + " (" + ("html" if html_mail else "plain text") + ")")
            i = 1
            for x in d.split('\n'):
                print("     " + "{0:04}".format(i) + " " + x)
                i += 1

            # create message
            if html_mail:
                message = self.__create_message(b, c, d, True)
            else:
                message = self.__create_message(b, c, d)

            # send the message
            if self.__send_message(message) is not None:
                print("- successfully send to " + b)
                logging.info("email was successfully send to " + b)
                return True
            else:
                print("WARNING - Message could not be send to " + b)
                logging.warning("email was not send to " + b)
                return False
        else:
            print("Something went wrong in the setup. Please check your data.")

            return False

    """
    If you want to implement the Gmail API read this first: https://developers.google.com/gmail/api/quickstart/python
    You first need to activate the API over a Gmail account, then create OAuth client ID credentials and then
    understand (run) the example because of the permission scopes (https://developers.google.com/gmail/api/auth/scopes).
    """

    def __send_message(self, message):
        """Send an email message.

        Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        message: Message to be sent.

        Returns:
        Sent Message.
        """
        try:
            message = (self.service.users().messages().send(userId="me", body=message).execute())
            print('Message Id: %s' % message['id'])
            return message
        except errors.HttpError as error:
            print('An error occurred: %s' % error)
            return None

    def __create_message(self, to, subject, message_text, message_html=False):
        """Create a message for an email.

        Args:
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.

        Returns:
        An object containing a base64url encoded email object.
        """
        # message_text.encode('us-ascii', 'ignore').decode('us-ascii', 'ignore')

        if message_html:
            message = MIMEText(message_text.encode('ascii', 'ignore'), 'html')
        else:
            message = MIMEText(message_text.encode('ascii', 'ignore'))

        message['to'] = to
        message['from'] = self.EMAIL_ADDRESS_NAME
        message['subject'] = subject.encode('ascii', 'ignore')
        print(message)

        # Windows 10 Pycharm EDU:
        # raw = base64.urlsafe_b64encode(message.as_bytes())
        # raw = raw.decode()
        # body = {'raw': raw}
        # return body

        # Raspberry Pi 3 - Python 2.7.9
        return {'raw': base64.urlsafe_b64encode(message.as_string().encode())}

    def __get_credentials(self):
        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """

        credential_dir = self.DIRECTORY_FOR_GMAIL_API
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir, 'gmail_api_.json')

        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.PATH_FOR_GMAIL_CLIENT_SECRET_FILE, self.SCOPES)
            flow.user_agent = self.APPLICATION_NAME
            if self.flags:
                credentials = tools.run_flow(flow, store, self.flags)
            print('Storing credentials to ' + credential_path)
        return credentials