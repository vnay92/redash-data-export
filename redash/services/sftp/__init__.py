from redash.services.sftp.sftp_client import SFTPClient


class SFTPFacade():

    __instance = None

    def __init__(self):
        self.__instance = SFTPClient()

    def get_instance(self):
        return self.__instance
