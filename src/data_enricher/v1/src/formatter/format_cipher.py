"""Helper to parse upwork ciphers"""

from src.errors.common_errors import UnparsableCipher


def get_cipher(url: str):
    """"""

    temp = url.split("/")[-1]
    if temp.startswith("~"):
        return temp.strip()

    if "_%7E" in url:
        temp = url.split("_%7E")[-1].split("?")[0]
        temp = "~" + temp
        if len(temp) > 10:
            return temp.strip()

    raise UnparsableCipher(cipher=url)
