import os
import csv
import sys
import logging
import smtplib

from email import encoders
from django.conf import settings
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

class GmailClient():
    __sender = settings.EMAIL.get('username')
    __gmail_password = settings.EMAIL.get('password')
    __COMMASPACE = ', '

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def send_mail(self, recipients=[], attachments=[], subject='Data From Redash'):
        # Create the enclosing (outer) message
        outer = MIMEMultipart()
        outer['From'] = self.__sender
        outer['To'] = self.__COMMASPACE.join(recipients)
        outer['Subject'] = subject
        outer.preamble = 'You will not see this in a MIME-aware mail reader.\n'

        # Add the attachments to the message
        for file in attachments:
            try:
                with open(file, 'rb') as fp:
                    msg = MIMEBase('application', 'octet-stream')
                    msg.set_payload(fp.read())

                encoders.encode_base64(msg)
                msg.add_header('Content-Disposition', 'attachment',
                            filename=os.path.basename(file))
                outer.attach(msg)
            except:
                logging.error(
                    f'Unable to open one of the attachments. Error: {sys.exc_info()[0]}')
                raise

        composed = outer.as_string()

        # Send the email
        try:
            self.logger.info(f'Sending out Mail to {recipients}, from {self.__sender}')
            with smtplib.SMTP('smtp.gmail.com', 587) as s:
                s.ehlo()
                s.starttls()
                s.ehlo()
                s.login(self.__sender, self.__gmail_password)
                s.sendmail(self.__sender, recipients, composed)
                s.close()

            self.logger.info('Email sent!')
        except:
            logging.error(f'Unable to send the email. Error: {sys.exc_info()[0]}')
            raise
