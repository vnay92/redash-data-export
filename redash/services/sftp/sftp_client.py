import os
import sys
import socket
import logging
import paramiko
import traceback


class SFTPClient():

    __client = None

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def create_connection(self, hostname, port, username, password):
        hostkey = None
        DoGSSAPIKeyExchange = False
        # enable GSS-API / SSPI authentication
        UseGSSAPI = False

        # now, connect and use paramiko Transport to negotiate SSH2 across the connection
        try:
            self.__client = paramiko.Transport((hostname, port))
            self.__client.connect(
                hostkey,
                username,
                password,
                gss_host=socket.getfqdn(hostname),
                gss_auth=UseGSSAPI,
                gss_kex=DoGSSAPIKeyExchange,
            )
            sftp = paramiko.SFTPClient.from_transport(self.__client)

            # dirlist on remote host
            dirlist = sftp.listdir('.')
            self.logger.info('Dirlist: %s' % dirlist)

        except Exception as e:
            self.logger.info('*** Caught exception: %s: %s' % (e.__class__, e))
            traceback.print_exc()
            try:
                self.__client.close()
            except:
                pass

    def close_connection(self):
        self.__client.close()

    def put_file(self, file_path, remote_folder):
        sftp = paramiko.SFTPClient.from_transport(self.__client)
        file_name = os.path.basename(file_path)
        try:
            sftp.mkdir(remote_folder)
        except IOError:
            self.logger.info(f'(assuming {remote_folder} already exists)')

        sftp.put(file_path, f'{remote_folder}/{file_name}')
        self.__client.close()
