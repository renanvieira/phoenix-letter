from getpass import getpass


def get_credentials():
    access_key = getpass("AWS Access Key:")
    secret_key = getpass("AWS Secret Key:")

    return access_key, secret_key
