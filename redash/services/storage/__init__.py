from redash.services.storage.s3 import S3Storage

class StorageFacade():

    __instance = None

    def __init__(self):
        self.__instance = S3Storage()

    def get_instance(self):
        return self.__instance
