"""Module to hold common custom errors"""


class NotLoggedIn(Exception):

    def __init__(self, message: str = "Session not logged in") -> None:
        super().__init__(message)


class UnparsableCipher(Exception):

    def __init__(self, cipher: str) -> None:

        message = "Unparsable Cipher: " + str(cipher)
        super().__init__(message)
