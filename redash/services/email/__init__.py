from redash.services.email.gmail import GmailClient

class MailFacade():

    __instance = None

    def __init__(self):
        self.__instance = GmailClient()

    def get_instance(self):
        return self.__instance
